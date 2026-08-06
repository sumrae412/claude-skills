#!/usr/bin/env python3
"""Heading-aware markdown chunker — ported from Refact's VecDB strategy.

Splits .md files into chunks with full heading ancestry, preserving
YAML frontmatter as a standalone chunk. Pure stdlib + PyYAML.

Usage:
    python3 scripts/markdown_chunker.py [--max-tokens N] [--overlap N] <file.md>

Output: JSON array of Chunk objects, one per line (streaming).
"""

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None


HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)(?:\s+#+\s*)?$", re.MULTILINE)
FENCED_RE = re.compile(r"```[\s\S]*?```")


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def strip_fenced(content: str, placeholder: str = "\0") -> str:
    """Replace fenced code blocks with placeholder characters to avoid
    heading matches inside code blocks."""
    return FENCED_RE.sub(lambda m: placeholder * len(m.group()), content)


def parse_frontmatter(content: str):
    """Extract YAML frontmatter (--- ... ---). Returns (fm_dict, body_start)."""
    if not content.startswith("---"):
        return {}, 0
    end = content.find("---", 3)
    if end == -1:
        return {}, 0
    fm_text = content[3:end].strip()
    body_start = end + 3
    if yaml:
        try:
            return yaml.safe_load(fm_text) or {}, body_start
        except Exception:
            return {}, body_start
    # Minimal fallback: just parse created/review_after/status
    fm = {}
    for line in fm_text.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            fm[k.strip()] = v.strip()
    return fm, body_start


def chunk_markdown(content: str, max_tokens: int = 512, overlap_lines: int = 3):
    """Split markdown into heading-aware chunks.

    Yields dicts with: text, symbol_path (heading ancestry), 
    estimated_tokens, section_start_line.
    """
    # Parse frontmatter
    fm, body_start = parse_frontmatter(content)
    body = content[body_start:]

    if fm:
        fm_text = content[:body_start]
        # Clean placeholder chars from frontmatter fence stripping
        chunk_text = fm_text.strip()
        if chunk_text:
            yield {
                "text": chunk_text,
                "symbol_path": "frontmatter",
                "estimated_tokens": estimate_tokens(chunk_text),
                "section_start_line": 0,
            }

    # Split body by headings
    stripped_body = strip_fenced(body)
    heading_matches = list(HEADING_RE.finditer(stripped_body))

    if not heading_matches:
        # No headings — one chunk for entire body
        text = body.strip()
        if text:
            yield {
                "text": text,
                "symbol_path": "",
                "estimated_tokens": estimate_tokens(text),
                "section_start_line": body_start,
            }
        return

    heading_stack: list[tuple[str, str]] = []  # [(level, text), ...]

    def level_of(match) -> int:
        return len(match.group(1))

    def heading_text(match) -> str:
        return match.group(2).strip()

    for i, match in enumerate(heading_matches):
        level = level_of(match)
        text = heading_text(match)

        # Pop stack to correct depth
        while heading_stack and level_of(
            # Dummy match with same level; we compare by heading level int
            type("m", (), {"group": lambda self, _: "#" * heading_stack[-1][0]})()
        ) >= level:
            heading_stack.pop()
        heading_stack.append((level, text))

        # Determine section boundaries
        start = match.end()
        end = heading_matches[i + 1].start() if i + 1 < len(heading_matches) else len(body)

        section_text = body[start:end].strip()
        if not section_text:
            continue

        # Build symbol path from ancestry
        symbol_path = " > ".join(h[1] for h in heading_stack).strip()

        # Split oversized sections
        if estimate_tokens(section_text) > max_tokens:
            lines = section_text.splitlines(keepends=True)
            for j in range(0, len(lines), max(1, max_tokens * 4 - overlap_lines)):
                chunk = "".join(lines[j : j + max_tokens * 4])
                if not chunk.strip():
                    continue
                yield {
                    "text": chunk.strip(),
                    "symbol_path": symbol_path,
                    "estimated_tokens": estimate_tokens(chunk),
                    "section_start_line": body_start + start,
                }
        else:
            yield {
                "text": section_text,
                "symbol_path": symbol_path,
                "estimated_tokens": estimate_tokens(section_text),
                "section_start_line": body_start + start,
            }


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Heading-aware markdown chunker (Refact VecDB style)"
    )
    parser.add_argument("file", type=str, help="Path to .md file")
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Max estimated tokens per chunk (default: 512)",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=3,
        help="Line overlap for oversized sections (default: 3)",
    )
    args = parser.parse_args()

    path = Path(args.file)
    if not path.exists():
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    content = path.read_text(encoding="utf-8")
    for chunk in chunk_markdown(content, args.max_tokens, args.overlap):
        print(json.dumps(chunk))


if __name__ == "__main__":
    main()
