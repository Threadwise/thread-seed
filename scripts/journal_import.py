#!/usr/bin/env python3
"""
journal_import.py — one-shot ingest for existing journal text.

Reads journal text files from a directory, calls Claude API to extract
entities + relations (for spine) and observation frames (for mem),
writes them locally. Idempotent: rerunnable on additional files without
re-processing previously-ingested ones (tracks by content hash).

Usage:
    python3 scripts/journal_import.py --path /path/to/journal/

Privacy note: your journal text IS sent to the Claude API during import,
in chunks. If you don't want that, populate substrate manually instead.

This is a STUB — not yet implemented. Fill in based on your journal's
format (Apple Notes export? Obsidian vault? plain text files? Markdown?).
"""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Import journal text into spine + mem")
    parser.add_argument("--path", required=True, help="Directory of journal files")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen, don't write")
    parser.add_argument("--format", default="auto", help="Journal format: text|markdown|notes|auto")
    args = parser.parse_args()

    journal_path = Path(args.path)
    if not journal_path.exists():
        print(f"Journal path not found: {journal_path}")
        sys.exit(1)

    # TODO: implementation
    # 1. Walk journal_path for matching files
    # 2. Deduplicate via content hash (skip already-ingested)
    # 3. Chunk content into reasonable sizes for Claude API extraction
    # 4. Per chunk:
    #    - Send to Claude with extraction prompt (entities + relations + frames)
    #    - Parse structured output
    #    - Write to spine (entities + edges)
    #    - Write to mem (episodic frames with original timestamp if discoverable)
    # 5. Update hash log
    print(f"STUB: would scan {journal_path} for journal files")
    print("Not yet implemented. See module docstring for design.")


if __name__ == "__main__":
    main()
