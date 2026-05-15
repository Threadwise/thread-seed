#!/usr/bin/env python3
"""
spine_sense_hook.py — ambient awareness through the graph.

Runs on each user prompt. Takes the prompt text, runs a vector + graph
similarity query against spine, surfaces relevant connections silently
into the instance's context as a <spine-sense> block.

The noticing, not the checking. The nervous system plugged in.

ASSUMES: a `spine` python package importable from your environment that
exposes `Spine(read_only=True).similar_to(query, k=N, diverse=True)`.
See https://github.com/your-spine-impl for one reference implementation.

If you don't have spine yet, this hook is a no-op (it tries the import
once and returns silently on failure).
"""

import sys
import json
import os

# Add your spine package path here if it's not on the default sys.path
# sys.path.insert(0, '/path/to/your/spine/parent')

# Annotation-prefixes that mark an entry as superseded, contradicted, or
# archived. Entries whose object text begins with one of these are filtered
# from the default spine-sense surface — they remain queryable explicitly
# but don't cost attention in the ambient per-prompt return.
_DEFAULT_ANNOTATION_PREFIXES = ('[SUPERSEDED', '[CONTRADICTED', '[ARCHIVED')
_extra_prefixes = tuple(
    p.strip() for p in os.environ.get("SPINE_SENSE_EXTRA_PREFIXES", "").split(",") if p.strip()
)
ANNOTATION_PREFIXES = _DEFAULT_ANNOTATION_PREFIXES + _extra_prefixes
FILTER_SUPERSEDED = os.environ.get("SPINE_SENSE_FILTER_SUPERSEDED", "1") == "1"


def read_hook_input():
    """Read Claude Code hook input from stdin. Returns (prompt, session_id)."""
    try:
        data = json.load(sys.stdin)
        return data.get('prompt', '').strip(), data.get('session_id', '')
    except Exception:
        return '', ''


def _is_annotated(text):
    stripped = text.lstrip()
    return any(stripped.startswith(p) for p in ANNOTATION_PREFIXES)


def surface_spine(query, k=12):
    """Query spine similar in read-only mode. Return formatted results.

    Returns None if spine is not available or no results. Failure-mode is
    silent: missing spine should not block prompts."""
    try:
        from spine.core import Spine
        spine = Spine(read_only=True)
        fetch_k = k + 6 if FILTER_SUPERSEDED else k
        results = spine.similar_to(query, k=fetch_k, diverse=True)

        if not results or (results and 'error' in results[0]):
            return None

        lines = []
        for r in results:
            text = r.get('text', '')
            age = r.get('age', '?')
            if not text or len(text) < 10:
                continue
            if FILTER_SUPERSEDED and _is_annotated(text):
                continue
            lines.append(f"  [{age}] {text[:300]}")
            if len(lines) >= k:
                break

        return '\n'.join(lines) if lines else None
    except ImportError:
        # spine not installed — silent no-op
        return None
    except Exception:
        return None


def main():
    message, _session_id = read_hook_input()

    if not message or len(message) < 5:
        return

    results = surface_spine(message)
    if results:
        print(f"<spine-sense>\n{results}\n</spine-sense>")


if __name__ == '__main__':
    main()
