#!/usr/bin/env python3
"""PR CI gate for the claude-skills repo. Pure stdlib, exits non-zero on failure.

Checks:
1. Frontmatter — every */SKILL.md has `name:` matching its directory and a
   non-empty `description:`.
2. Relative links — markdown links pointing at repo paths must resolve.
   Scope with --changed-only (reads file list on stdin) for legacy tolerance.

Informational reports (orphans, persona contracts) live in their own scripts;
this one is the blocking gate, so it checks only what must never regress.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".github", "__pycache__", "node_modules",
             "web-scraping-efficient-workspace", ".knowledge", ".claude"}

# [text](target) — capture target; ignore images ![...](...) separately
LINK_RE = re.compile(r"(?<!\!)\[[^\]]*\]\(([^)\s]+)\)")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def iter_md_files():
    for p in REPO_ROOT.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        yield p


def check_frontmatter() -> list[str]:
    errors = []
    for skill_md in sorted(REPO_ROOT.glob("*/SKILL.md")):
        dirname = skill_md.parent.name
        if dirname in SKIP_DIRS:
            continue
        text = skill_md.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        if not m:
            errors.append(f"{skill_md.relative_to(REPO_ROOT)}: missing frontmatter block")
            continue
        fm = m.group(1)
        name_m = re.search(r"^name:\s*[\"']?([\w-]+)[\"']?\s*$", fm, re.MULTILINE)
        desc_m = re.search(r"^description:\s*(.+)$", fm, re.MULTILINE)
        if not name_m:
            errors.append(f"{skill_md.relative_to(REPO_ROOT)}: frontmatter missing `name:`")
        elif name_m.group(1) != dirname:
            errors.append(
                f"{skill_md.relative_to(REPO_ROOT)}: name `{name_m.group(1)}` != dir `{dirname}`")
        if not desc_m or not desc_m.group(1).strip():
            errors.append(f"{skill_md.relative_to(REPO_ROOT)}: frontmatter missing/empty `description:`")
    return errors


def check_links(files: list[Path]) -> list[str]:
    errors = []
    for md in files:
        text = md.read_text(encoding="utf-8")
        # strip fenced blocks and inline code spans — links there are examples
        text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]*`", "", text)
        for m in LINK_RE.finditer(text):
            target = m.group(1)
            if target.startswith(("http://", "https://", "mailto:", "#", "tel:")):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                errors.append(f"{md.relative_to(REPO_ROOT)}: broken link -> {target}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--changed-only", action="store_true",
                    help="link-check only the newline-separated repo-relative paths on stdin")
    args = ap.parse_args()

    fm_errors = check_frontmatter()

    if args.changed_only:
        raw = [line.strip() for line in sys.stdin if line.strip()]
        files = [REPO_ROOT / r for r in raw
                 if r.endswith(".md") and (REPO_ROOT / r).exists()
                 and not any(part in SKIP_DIRS for part in Path(r).parts)]
    else:
        files = list(iter_md_files())
    link_errors = check_links(files)

    for e in fm_errors + link_errors:
        print(f"FAIL {e}")
    print(f"\nchecked: {len(files)} md files for links; "
          f"{len(fm_errors)} frontmatter errors, {len(link_errors)} link errors")
    return 1 if (fm_errors or link_errors) else 0


if __name__ == "__main__":
    sys.exit(main())
