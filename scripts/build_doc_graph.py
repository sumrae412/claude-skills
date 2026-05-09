#!/usr/bin/env python3
"""Build a doc-graph report for a markdown corpus.

Walks the repo for .md files, extracts cross-references, and emits a
GRAPH_REPORT.md with hubs, orphans, and missing-link suggestions.

Pure stdlib — zero external deps. Designed for the claude-skills repo but
works on any markdown folder. Run from repo root:

    python3 scripts/build_doc_graph.py [--root PATH] [--out PATH]

Defaults: root = cwd, out = .knowledge/GRAPH_REPORT.md

## Mem sync workflow

The current report is mirrored as a Mem note for navigability:

    Note ID:    ce4f5501-2f4f-4901-93c9-9e7f791572e5
    Title:      📊 Doc Graph Report — claude-skills
    Collection: 421a7805-5221-4117-8425-da2dc72a2aa1

After regenerating, ask Claude to update that note via the Mem MCP
(`update_note` requires the current `version` from `get_note`). The script
itself does not push to Mem — MCP tools are only available inside a
Claude Code session, not from a standalone CLI.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

# Skip these dirs entirely
SKIP_DIRS = {".git", ".claude", "node_modules", "htmlcov", ".venv", "venv",
             "__pycache__", ".pytest_cache", "dist", "build", ".knowledge",
             "worktrees"}

# Stop words for keyword extraction (small, intentional — extend as needed)
STOP = set("""a an and are as at be but by for from has have if in into is it its
of on or that the their then there these they this to was were what when where
which who will with you your yours we our us not no can do does did had how use
using used uses see also via not don's is's it's via per use cases case eg ie eg
""".split())

# Template/scaffolding words common in phase/contract files. These are
# structural (every phase doc has "before/load/phase/goal") not semantic — they
# inflate keyword overlap between unrelated skills (soc2 ↔ fda ↔ iso27001).
STRUCTURAL_STOP = set("""phase phases load loads loaded before after goal goals
running run runs running step steps before-running output outputs input inputs
contract contracts schema schemas requirement requirements skill skill.md
reference references docs section sections subsection chapter""".split())
STOP |= STRUCTURAL_STOP

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")
# Inline references — "see `foo/bar.md`" or "`MEMORY.md`" or absolute paths
BACKTICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./~-]+\.md)`")
ABS_PATH_RE = re.compile(
    r"(?:~/claude_code/claude-skills/|~/\.claude/skills/)([A-Za-z0-9_./-]+\.md)"
)
# Skill-name mentions: `slug` or `plugin:slug` or `/slug` (slash-command form)
SKILL_MENTION_RE = re.compile(r"`(?:/)?([a-z][a-z0-9-]+(?::[a-z][a-z0-9-]+)?)`")


def collect_md(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        out.append(p)
    return out


def _resolve(rel_or_abs: str, src: Path, root: Path,
             all_paths: set[Path], basename_index: dict[str, list[Path]]) -> Path | None:
    """Resolve a textual reference to an actual .md path in the corpus."""
    s = rel_or_abs.split("#", 1)[0].split("?", 1)[0].strip()
    if not s or not s.endswith(".md"):
        return None
    # Absolute-ish (~/... or /...) → expand and resolve
    if s.startswith("~/"):
        # Strip either prefix; both resolve to the same repo (symlink)
        cand = (s.replace("~/claude_code/claude-skills/", "")
                 .replace("~/.claude/skills/", ""))
        cand_path = (root / cand).resolve()
        if cand_path in all_paths and cand_path != src:
            return cand_path
        return None
    # Relative → try src.parent first, then root
    for base in (src.parent, root):
        cand_path = (base / s).resolve()
        if cand_path in all_paths and cand_path != src:
            return cand_path
    # Bare basename like `MEMORY.md` → fall back to global basename index
    if "/" not in s:
        matches = basename_index.get(s, [])
        if len(matches) == 1 and matches[0] != src:
            return matches[0]
    return None


def extract_links(md_path: Path, root: Path, all_paths: set[Path],
                  basename_index: dict[str, list[Path]],
                  skill_index: dict[str, Path]) -> set[Path]:
    """Return set of resolved .md paths this file references.

    Catches:
      - markdown links [text](path)
      - backtick-bare paths `foo/bar.md` or `MEMORY.md`
      - absolute prose paths ~/claude_code/claude-skills/x/y.md
      - skill-name mentions `slug` or `plugin:slug` (resolved via skill_index)
    """
    targets: set[Path] = set()
    text = md_path.read_text(errors="ignore")

    for _label, target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        hit = _resolve(target, md_path, root, all_paths, basename_index)
        if hit:
            targets.add(hit)

    for m in BACKTICK_PATH_RE.findall(text):
        hit = _resolve(m, md_path, root, all_paths, basename_index)
        if hit:
            targets.add(hit)

    for m in ABS_PATH_RE.findall(text):
        hit = _resolve("~/claude_code/claude-skills/" + m, md_path, root,
                       all_paths, basename_index)
        if hit:
            targets.add(hit)

    for slug in SKILL_MENTION_RE.findall(text):
        # plugin:skill-name → skill-name; bare skill-name stays as-is
        key = slug.split(":")[-1]
        hit = skill_index.get(key)
        if hit and hit != md_path:
            targets.add(hit)

    return targets


def extract_keywords(md_path: Path, top_n: int = 15) -> set[str]:
    text = md_path.read_text(errors="ignore").lower()
    # Strip code blocks (rough but good enough for keyword signal)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    words = WORD_RE.findall(text)
    counts = Counter(w for w in words if w not in STOP and len(w) > 3)
    return {w for w, _ in counts.most_common(top_n)}


def build_graph(root: Path):
    paths = collect_md(root)
    path_set = set(paths)
    # Indexes for fuzzy resolution
    basename_index: dict[str, list[Path]] = defaultdict(list)
    for p in paths:
        basename_index[p.name].append(p)
    skill_index: dict[str, Path] = {}
    for p in paths:
        # <slug>/SKILL.md at any depth → register slug
        if p.name == "SKILL.md":
            slug = p.parent.name
            # Prefer top-level (skills/<slug>/SKILL.md) over nested
            if slug not in skill_index or len(p.parts) < len(skill_index[slug].parts):
                skill_index[slug] = p
    forward: dict[Path, set[Path]] = {
        p: extract_links(p, root, path_set, basename_index, skill_index) for p in paths
    }
    reverse: dict[Path, set[Path]] = defaultdict(set)
    for src, targets in forward.items():
        for t in targets:
            reverse[t].add(src)
    keywords: dict[Path, set[str]] = {p: extract_keywords(p) for p in paths}
    return paths, forward, reverse, keywords


def find_missing_links(paths, forward, keywords, threshold: int = 6, max_pairs: int = 25):
    """Pairs that share many keywords but don't link either direction.

    Skips boilerplate-heavy filenames (SOURCE.md, LICENSE.md, README.md) that
    share template text rather than semantic content.
    """
    BOILERPLATE = {"SOURCE.md", "LICENSE.md"}
    candidates = [p for p in paths if p.name not in BOILERPLATE]
    suggestions = []
    seen = set()
    for i, a in enumerate(candidates):
        for b in candidates[i + 1:]:
            if b in forward[a] or a in forward[b]:
                continue
            shared = keywords[a] & keywords[b]
            if len(shared) >= threshold:
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                suggestions.append((len(shared), a, b, sorted(shared)))
    suggestions.sort(reverse=True, key=lambda x: x[0])
    return suggestions[:max_pairs]


def rel(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def _is_progressive_disclosure(p: Path, root: Path) -> bool:
    """True if file lives in a skill's references/, phases/, or contracts/ dir
    and the skill has a SKILL.md router. These are typically loaded by the
    Read tool from the router, not by markdown link — flagging them as
    orphans is a false positive.
    """
    parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
    if len(parts) < 3:
        return False
    if parts[1] not in {"references", "phases", "contracts", "diagrams"}:
        return False
    skill_router = root / parts[0] / "SKILL.md"
    return skill_router.exists()


def render_report(root: Path, paths, forward, reverse, missing) -> str:
    total_files = len(paths)
    total_edges = sum(len(v) for v in forward.values())
    hubs = sorted(paths, key=lambda p: len(reverse[p]), reverse=True)[:15]
    raw_orphans = [p for p in paths if not reverse[p] and not forward[p]]
    true_orphans = sorted(p for p in raw_orphans
                          if not _is_progressive_disclosure(p, root))
    pd_orphans = sorted(p for p in raw_orphans
                        if _is_progressive_disclosure(p, root))
    sinks = sorted((p for p in paths if reverse[p] and not forward[p]),
                   key=lambda p: len(reverse[p]), reverse=True)[:10]

    lines = [
        "# Doc Graph Report",
        "",
        f"- **Files scanned:** {total_files}",
        f"- **Cross-references found:** {total_edges}",
        f"- **Hub nodes (top 15 by inbound refs):** see below",
        f"- **True orphans (zero links + not progressive-disclosure):** {len(true_orphans)}",
        f"- **Progressive-disclosure references (Read-loaded, not orphans):** {len(pd_orphans)}",
        f"- **Confidence:** EXTRACTED (explicit markdown links only) — "
        "INFERRED keyword-cluster suggestions in the missing-links section. "
        "Files under `<skill>/references/`, `<skill>/phases/`, `<skill>/contracts/`, "
        "or `<skill>/diagrams/` are loaded by the Read tool from the router "
        "SKILL.md and are NOT counted as orphans even when no markdown link points to them.",
        "",
        "## Hubs (most-referenced files)",
        "",
    ]
    for p in hubs:
        n = len(reverse[p])
        if n == 0:
            continue
        lines.append(f"- **{rel(p, root)}** — {n} inbound")
    lines.append("")

    lines.append("## True orphans (no links in or out, not progressive-disclosure)")
    lines.append("")
    if not true_orphans:
        lines.append("_None._")
    else:
        for p in true_orphans:
            lines.append(f"- {rel(p, root)}")
    lines.append("")

    lines.append("## Sinks (referenced but never link out)")
    lines.append("")
    if not sinks:
        lines.append("_None._")
    else:
        for p in sinks:
            lines.append(f"- **{rel(p, root)}** — {len(reverse[p])} inbound")
    lines.append("")

    lines.append("## Suggested missing cross-links (INFERRED — keyword overlap, no direct link)")
    lines.append("")
    if not missing:
        lines.append("_None above threshold._")
    else:
        for shared_n, a, b, shared in missing:
            terms = ", ".join(shared[:6]) + ("…" if len(shared) > 6 else "")
            lines.append(f"- **{rel(a, root)}** ↔ **{rel(b, root)}** "
                         f"— {shared_n} shared terms ({terms})")
    lines.append("")

    lines.append("## Suggested questions for review")
    lines.append("")
    if hubs and len(reverse[hubs[0]]) > 10:
        lines.append(f"- Is `{rel(hubs[0], root)}` a true hub or should it be split? "
                     f"({len(reverse[hubs[0]])} inbound refs.)")
    if true_orphans:
        lines.append(f"- Should the {len(true_orphans)} true orphan file(s) be linked from "
                     "an index, merged into a hub, or removed?")
    if missing:
        a, b = missing[0][1], missing[0][2]
        lines.append(f"- `{rel(a, root)}` and `{rel(b, root)}` share many terms but never "
                     "cross-reference. Intentional separation or missing link?")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None,
                    help="Optional: dump full graph as JSON for downstream tools")
    ap.add_argument("--missing-threshold", type=int, default=6)
    args = ap.parse_args()

    root = args.root.resolve()
    out = (args.out or root / ".knowledge" / "GRAPH_REPORT.md").resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    paths, forward, reverse, keywords = build_graph(root)
    missing = find_missing_links(paths, forward, keywords,
                                 threshold=args.missing_threshold)
    out.write_text(render_report(root, paths, forward, reverse, missing))
    print(f"wrote {out} — {len(paths)} files, {sum(len(v) for v in forward.values())} edges")

    if args.json:
        data = {
            "root": str(root),
            "files": [rel(p, root) for p in paths],
            "edges": [[rel(s, root), rel(t, root)] for s, ts in forward.items() for t in ts],
            "missing_suggestions": [
                {"a": rel(a, root), "b": rel(b, root), "shared": shared}
                for _, a, b, shared in missing
            ],
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(data, indent=2))
        print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
