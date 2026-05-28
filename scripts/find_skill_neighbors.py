#!/usr/bin/env python3
"""Find skills most likely to want a cross-reference to a target skill.

Wraps build_doc_graph.extract_keywords to compute per-pair keyword overlap
between a TARGET skill and every other SKILL.md in the repo. Outputs the
top-N candidates as JSON for use by the skill-linking automation hook.

Usage:
    python3 scripts/find_skill_neighbors.py path/to/SKILL.md [--top 5] [--threshold 2]

Output: JSON to stdout with target keywords, candidates list (name, path,
overlap score, shared keywords, description preview).

Default interpretation of overlap pairs: missing links between
complementary skills, NOT duplicates. Read both files before adding a
cross-reference. See scripts/build_doc_graph.py header for the validation
note on courierflow project-memory (5/5 pairs were complementary).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Reuse the existing keyword extractor and md collector.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_doc_graph import collect_md, extract_keywords  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent


def _description(skill_md: Path) -> str:
    """Pull `description:` from YAML frontmatter; empty string if absent."""
    try:
        text = skill_md.read_text(errors="ignore")
    except OSError:
        return ""
    if not text.startswith("---"):
        return ""
    end = text.find("\n---", 3)
    if end == -1:
        return ""
    for line in text[3:end].splitlines():
        stripped = line.strip()
        if stripped.startswith("description:"):
            return stripped.split(":", 1)[1].strip().strip('"').strip("'")
    return ""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("target", help="Path to the new skill's SKILL.md")
    ap.add_argument("--top", type=int, default=5, help="Number of candidates to return")
    ap.add_argument(
        "--threshold",
        type=int,
        default=2,
        help="Minimum keyword overlap to include a candidate",
    )
    args = ap.parse_args()

    target_path = Path(args.target).resolve()
    if not target_path.exists():
        print(
            json.dumps({"error": f"target not found: {target_path}", "candidates": []}),
            file=sys.stderr,
        )
        return 1
    if target_path.name != "SKILL.md":
        print(
            json.dumps(
                {"error": f"target is not a SKILL.md: {target_path}", "candidates": []}
            ),
            file=sys.stderr,
        )
        return 1

    target_kw = extract_keywords(target_path, top_n=20)
    if not target_kw:
        print(
            json.dumps(
                {
                    "error": "no keywords extracted from target",
                    "target": str(target_path.relative_to(REPO_ROOT)),
                    "candidates": [],
                }
            )
        )
        return 0

    # All SKILL.md files in the repo, minus the target.
    all_skills = [
        p
        for p in collect_md(REPO_ROOT)
        if p.name == "SKILL.md" and p.resolve() != target_path
    ]

    candidates = []
    for p in all_skills:
        kw = extract_keywords(p, top_n=20)
        shared = target_kw & kw
        overlap = len(shared)
        if overlap < args.threshold:
            continue
        candidates.append(
            {
                "name": p.parent.name,
                "path": str(p.relative_to(REPO_ROOT)),
                "overlap_score": overlap,
                "shared_keywords": sorted(shared),
                "description_preview": _description(p)[:200],
            }
        )

    candidates.sort(key=lambda c: (-c["overlap_score"], c["name"]))

    print(
        json.dumps(
            {
                "target": str(target_path.relative_to(REPO_ROOT)),
                "target_keywords": sorted(target_kw),
                "candidate_count": len(candidates),
                "candidates": candidates[: args.top],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
