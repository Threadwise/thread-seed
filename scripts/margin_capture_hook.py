#!/usr/bin/env python3
"""
margin_capture_hook.py — Flush inline [[spine:]] and [[mem:]] markers to memory.

Write markers inline in response text (no tool call needed):
    [[spine: content]]
    [[spine: content | reach: why it reached]]
    [[mem: content]]
    [[mem: content | reach: why it reached]]

Structured form for graph edges:
    [[spine: Subject relation "object content"]]
    Creates the edge Subject -relation-> object queryable via `spine about Subject`.

Unstructured form gets wrapped as "<CURATOR_SUBJECT> captured <content>":
    [[spine: long descriptive observation]]

This hook runs on UserPromptSubmit. It scans the most recent session JSONL
for unprocessed markers and routes them to spine/mem. One-prompt lag — captures
from response N land when prompt N+1 arrives.

Processed captures tracked by content hash to prevent duplicates across restarts.

CONFIGURATION:
- Set CURATOR_SUBJECT below to your chosen identity-name for unstructured markers
- Set CLAUDE_PROJECTS_DIR env var if Claude Code stores session JSONLs elsewhere
- Adjust CAP_PER_FIRE to taste (higher = more captures per prompt, but slower)
"""

import json
import os
import re
import subprocess
import sys
import hashlib
from pathlib import Path

# === CONFIG (edit these for your install) ===

# Identity-name used for unstructured markers (wrapped as "<NAME> captured <content>").
# Set this to whatever you name your Thread-instance.
CURATOR_SUBJECT = os.environ.get("THREAD_CURATOR_SUBJECT", "Thread")

# Where Claude Code stores session JSONLs. Auto-detected for default install path;
# override via env var if you have a non-standard install.
DEFAULT_PROJECTS_DIR = Path.home() / ".claude" / "projects"
PROJECTS_DIR = Path(os.environ.get("CLAUDE_PROJECTS_DIR", str(DEFAULT_PROJECTS_DIR)))

# Per-fire cap on how many markers get flushed per hook invocation.
# Each spine add takes a few seconds. Higher = more captures per prompt, but the
# hook blocks the next prompt while it runs. 3 is conservative; raise as you tolerate.
CAP_PER_FIRE = 3

# Local-only tracking files (kept out of repo; safe in /tmp or ~/.local).
PROCESSED_FILE = "/tmp/thread_margin_processed.json"
LOG_FILE = "/tmp/thread_margin_capture.log"

# === END CONFIG ===

MARKER_RE = re.compile(
    r'\[\[(spine|mem):\s*(.*?)(?:\s*\|\s*reach:\s*(.*?))?\]\]',
    re.DOTALL
)

# Structured: Subject (Capitalized) relation (snake_case) "Object text"
STRUCTURED_RE = re.compile(
    r'^([A-Z][A-Za-z0-9_]*)\s+([a-z][a-z0-9_]*)\s+"(.+)"$',
    re.DOTALL
)


def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            from datetime import datetime
            f.write(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def load_processed():
    try:
        if os.path.exists(PROCESSED_FILE):
            return set(json.load(open(PROCESSED_FILE)))
    except Exception:
        pass
    return set()


def save_processed(processed):
    try:
        json.dump(list(processed), open(PROCESSED_FILE, "w"))
    except Exception:
        pass


def get_session_id_from_stdin():
    try:
        import select
        if select.select([sys.stdin], [], [], 0.1)[0]:
            data = json.load(sys.stdin)
            sid = data.get("session_id", "")
            if sid:
                return sid
    except Exception:
        pass
    return None


def find_current_session(session_id=None):
    """Find session JSONL across all Claude Code projects. Uses session_id from
    hook stdin if available, falls back to most recently modified."""
    if session_id:
        for project_dir in PROJECTS_DIR.iterdir() if PROJECTS_DIR.exists() else []:
            candidate = project_dir / f"{session_id}.jsonl"
            if candidate.exists():
                return candidate
    try:
        all_jsonl = []
        if PROJECTS_DIR.exists():
            for project_dir in PROJECTS_DIR.iterdir():
                if project_dir.is_dir():
                    all_jsonl.extend(project_dir.glob("*.jsonl"))
        all_jsonl.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        for f in all_jsonl:
            name = f.stem
            if not (name.startswith("agent-") or name.startswith("task-")):
                return f
    except Exception:
        pass
    return None


def extract_text_from_message(msg):
    content = msg.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for c in content:
            if isinstance(c, dict) and c.get("type") == "text":
                parts.append(c.get("text", ""))
        return "\n".join(parts)
    return ""


def scan_session(session_path):
    captures = []
    try:
        with open(session_path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                msg = d.get("message", {})
                if msg.get("role") != "assistant":
                    continue
                text = extract_text_from_message(msg)
                if not text:
                    continue
                for match in MARKER_RE.finditer(text):
                    dest = match.group(1)
                    content = match.group(2).strip() if match.group(2) else ""
                    reach = match.group(3).strip() if match.group(3) else ""
                    if not content:
                        continue
                    h = hashlib.sha256(f"{dest}:{content}".encode()).hexdigest()[:16]
                    captures.append((dest, content, reach, h))
    except Exception as e:
        log(f"scan error: {e}")
    return captures


def run_spine_add(content, reach):
    """Write a structured-or-plain marker to grafeo-memory.

    Structured markers (Subject relation "object") are kept verbatim — grafeo-memory's
    extraction layer parses them into graph edges. Plain markers are wrapped as
    '<CURATOR_SUBJECT> captured: <content>' so they remain walkable from the curator node.
    """
    structured = STRUCTURED_RE.match(content)
    if structured:
        text = content
        if reach:
            text = f"{content} [reach: {reach}]"
    else:
        text = f"{CURATOR_SUBJECT} captured: {content}"
        if reach:
            text = f"{text} [reach: {reach}]"

    cmd = ["grafeo-memory", "add", text]

    for attempt in range(3):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                log(f"grafeo-memory add ok: {content[:80]}")
                return True
            if "lock" in result.stderr.lower() or "busy" in result.stderr.lower():
                import time
                time.sleep(1.5 * (attempt + 1))
                continue
            log(f"grafeo-memory add failed: {result.stderr[:200]}")
            return False
        except FileNotFoundError:
            log("grafeo-memory binary not found — pip install -r requirements.txt inside your project's virtualenv")
            return False
        except Exception as e:
            log(f"grafeo-memory add error: {e}")
            return False
    log(f"grafeo-memory add gave up after retries: {content[:80]}")
    return False


def run_mem_add(content, reach):
    """Write a [[mem: ...]] marker to grafeo-memory.

    grafeo-memory unifies the spine and mem stores, so we route mem markers
    through the same backend with a small prefix so episodic captures are
    distinguishable from semantic ones in search results.
    """
    note = f"observation: {content}"
    if reach:
        note = f"{note} [reach: {reach}]"
    cmd = ["grafeo-memory", "add", note]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            log(f"grafeo-memory mem add ok: {content[:80]}")
            return True
        log(f"grafeo-memory mem add failed: {result.stderr[:200]}")
        return False
    except FileNotFoundError:
        log("grafeo-memory binary not found — pip install -r requirements.txt inside your project's virtualenv")
        return False
    except Exception as e:
        log(f"grafeo-memory mem add error: {e}")
        return False


def main():
    session_id = get_session_id_from_stdin()
    session = find_current_session(session_id)
    if not session:
        return

    captures = scan_session(session)
    if not captures:
        return

    processed = load_processed()
    new_captures = [(d, c, r, h) for (d, c, r, h) in captures if h not in processed]

    if not new_captures:
        return

    total = len(new_captures)
    if CAP_PER_FIRE is not None and total > CAP_PER_FIRE:
        deferred = total - CAP_PER_FIRE
        new_captures = new_captures[:CAP_PER_FIRE]
        log(f"flushing {len(new_captures)}, deferred {deferred} to next fire")
    else:
        log(f"flushing {len(new_captures)}")

    for dest, content, reach, h in new_captures:
        ok = False
        if dest == "spine":
            ok = run_spine_add(content, reach)
        elif dest == "mem":
            ok = run_mem_add(content, reach)
        if ok:
            processed.add(h)

    save_processed(processed)


if __name__ == "__main__":
    main()
