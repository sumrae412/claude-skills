#!/usr/bin/env python3
"""Parse a session-loaded skills listing into a corpus JSONL.

Input format (one skill per line, blank lines and `- ` prefix tolerated):

    - <slug>: <description>
    - <plugin>:<slug>: <description>

Output: one JSON record per line with {slug, name, description}.

Usage:
    build_skill_corpus.py --in skills_raw.txt --out skill_corpus.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKILL_LINE = re.compile(r"^\s*-\s*([\w:-]+):\s*(.+?)\s*$")


def parse(text: str) -> list[dict]:
    skills: list[dict] = []
    seen: set[str] = set()
    for line in text.splitlines():
        m = SKILL_LINE.match(line)
        if not m:
            continue
        slug, description = m.group(1), m.group(2)
        # Strip trailing ellipsis or "…" markers
        description = re.sub(r"\s*[…\.]{2,}\s*$", "", description).strip()
        if slug in seen:
            continue
        seen.add(slug)
        # Display name: drop plugin prefix for shorter labels
        name = slug.split(":")[-1]
        skills.append({"slug": slug, "name": name, "description": description})
    return skills


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--in", dest="input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)

    skills = parse(args.input.read_text())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for s in skills:
            f.write(json.dumps(s) + "\n")
    print(f"parsed {len(skills)} skills → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
