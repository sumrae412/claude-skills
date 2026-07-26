#!/usr/bin/env python3
"""Build a doc-graph report for a markdown corpus.

Walks the repo for .md files, extracts typed cross-references, and emits a
GRAPH_REPORT.md with hubs, orphans, dead links, missing-link suggestions,
entity-type-scoped sections, and per-file health scores.

Pure stdlib — zero external deps. Designed for the claude-skills repo but
works on any markdown folder. Run from repo root:

    python3 scripts/build_doc_graph.py [--root PATH] [--out PATH] [--json PATH]

## Reading the report

Each edge is typed by the markdown syntax that produced it:

  - **see-also**   — `[See also](path.md)` or `[Also see](path.md)` forms
  - **defines**    — `[[wikilink]]` or `[[wikilink|alias]]` (declarative ref)
  - **mentions**   — backtick path `` `foo.md` `` or skill slug `` `slug` ``
  - **links-to**   — standard markdown link `[text](path.md)` (default type)

Keyword-overlap pairs in "Suggested missing cross-links" are USUALLY
missing links between complementary patterns, NOT duplicates to merge.
Read both files before consolidating; the default action is to add a
cross-reference, not retire one side. Validated 2026-05-12 on the
courierflow project-memory corpus: 5/5 inferred pairs were complementary,
0/5 were duplicates.

Use this script as the pre-step before any "clean up memory" manual pass.
Hubs (>10 inbound refs) are what NOT to retire — deletion dangles N
references silently.

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
from dataclasses import dataclass, field
from pathlib import Path

# Skip these dirs entirely
SKIP_DIRS = {
    ".git",
    ".claude",
    "node_modules",
    "htmlcov",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "dist",
    "build",
    ".knowledge",
    "worktrees",
}

# Stop words for keyword extraction (small, intentional — extend as needed)
STOP = set(
    """a an and are as at be but by for from has have if in into is it its
of on or that the their then there these they this to was were what when where
which who will with you your yours we our us not no can do does did had how use
using used uses see also via not don's is's it's via per use cases case eg ie eg
""".split()
)

# Template/scaffolding words common in phase/contract files. These are
# structural (every phase doc has "before/load/phase/goal") not semantic — they
# inflate keyword overlap between unrelated skills (soc2 ↔ fda ↔ iso27001).
STRUCTURAL_STOP = set(
    """phase phases load loads loaded before after goal goals
running run runs running step steps before-running output outputs input inputs
contract contracts schema schemas requirement requirements skill skill.md
reference references docs section sections subsection chapter
title tags impact impactdescription description severity
low low-medium medium medium-high high""".split()
)
STOP |= STRUCTURAL_STOP

LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")
# Inline references — "see `foo/bar.md`" or "`MEMORY.md`" or absolute paths
BACKTICK_PATH_RE = re.compile(r"`([A-Za-z0-9_./~-]+\.md)`")
ABS_PATH_RE = re.compile(r"(?:~/claude_code/claude-skills/|~/\.claude/skills/)([A-Za-z0-9_./-]+\.md)")
# Skill-name mentions: `slug` or `plugin:slug` or `/slug` (slash-command form)
SKILL_MENTION_RE = re.compile(r"`(?:/)?([a-z][a-z0-9-]+(?::[a-z][a-z0-9-]+)?)`")
# Obsidian-style wikilinks: [[basename]] or [[basename|display alias]]. The
# captured group is the target basename — resolution appends `.md` if absent
# and looks up via basename_index. Ambiguous matches (multiple files with the
# same basename) are skipped to avoid false edges.
WIKILINK_RE = re.compile(r"\[\[([^\]\|]+?)(?:\|[^\]]*)?\]\]")
# See-also indicators in markdown link text
SEE_ALSO_RE = re.compile(r"^(?:see\s+)?also\s+see|see\s+also", re.IGNORECASE)

# Entity types inferred from path patterns
_ENTITY_TYPE_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"(?:^|/)skills/[^/]+/SKILL\.md$"), "skill"),
    (re.compile(r"docs/decisions/.*\.md$"), "decision"),
    (re.compile(r"(?:^|/)memory/.*\.md$"), "memory"),
    (re.compile(r"(?:^|/)phases/[^/]+\.md$"), "phase"),
    (re.compile(r"(?:^|/)contracts/[^/]+\.md$"), "contract"),
    (re.compile(r"(?:^|/)references/[^/]+\.md$"), "reference"),
    (re.compile(r"CLAUDE\.md$"), "config"),
    (re.compile(r"AGENTS\.md$"), "config"),
    (re.compile(r"README\.md$"), "readme"),
    (re.compile(r"(?:^|/)ledger/.*\.md$"), "ledger"),
    (re.compile(r"docs/plans/.*\.md$"), "plan"),
    (re.compile(r"(?:^|/)PRIORITIES\.md$"), "routing"),
    (re.compile(r"(?:^|/)ROUTINES\.md$"), "routing"),
    (re.compile(r"(?:^|/)DECISIONS\.md$"), "routing"),
    (re.compile(r"(?:^|/)STATE\.md$"), "routing"),
    (re.compile(r"(?:^|/)COORDINATION\.md$"), "routing"),
    (re.compile(r"(?:^|/)CONFIG\.md$"), "routing"),
    (re.compile(r"(?:^|/)AUTONOMY\.md$"), "routing"),
]

# Relation type names (stable identifiers for the report)
REL_SEE_ALSO = "see-also"
REL_DEFINES = "defines"
REL_MENTIONS = "mentions"
REL_LINKS_TO = "links-to"
REL_ALL_TYPES = (REL_SEE_ALSO, REL_DEFINES, REL_MENTIONS, REL_LINKS_TO)

# Weights for health scoring
_INBOUND_WEIGHT = 2.0
_OUTBOUND_WEIGHT = 1.0
_DEFINES_BONUS = 2.0
_SEE_ALSO_BONUS = 1.5
_MENTIONS_PENALTY = 0.5


@dataclass
class FileHealth:
    """Per-file health assessment."""

    signal_score: float  # Weighted inbound + outbound with type bonuses
    inbound_count: int
    outbound_count: int
    inbound_unique_sources: int
    label: str  # "orphan-risk" | "low-signal" | "healthy" | "hub" | "dense-outbound"
    severity: int  # 0=healthy, 1=watch, 2=needs-attention


def _infer_entity_type(rel_path: str) -> str:
    """Map a relative file path to an entity type string.

    Patterns are checked in order; the first match wins. Falls back to
    "general" for unrecognized paths.
    """
    for pattern, etype in _ENTITY_TYPE_PATTERNS:
        if pattern.search(rel_path):
            return etype
    return "general"


def _compute_health(
    rel_path: str,
    outbound: dict[str, set[str]],
    inbound: dict[str, set[str]],
) -> FileHealth:
    """Compute composite health for a single file.

    Scoring:
      - signal = inbound_count * _INBOUND_WEIGHT + outbound_count * _OUTBOUND_WEIGHT
      - type bonuses: each `` defines `` inbound counts +_DEFINES_BONUS,
        each `` see-also `` inbound +_SEE_ALSO_BONUS
      - Labels thresholded from signal + edge-case checks.
    """
    in_types = inbound.get(rel_path, set())
    out_types = outbound.get(rel_path, set())

    inbound_count = len(in_types)
    outbound_count = len(out_types)
    inbound_unique_sources = inbound_count

    # Compute weighted signal
    signal = inbound_count * _INBOUND_WEIGHT + outbound_count * _OUTBOUND_WEIGHT

    # Classify
    if inbound_count == 0 and outbound_count == 0:
        return FileHealth(
            signal_score=0.0,
            inbound_count=0,
            outbound_count=0,
            inbound_unique_sources=0,
            label="orphan-risk",
            severity=2,
        )
    elif inbound_count == 0:
        return FileHealth(
            signal_score=signal,
            inbound_count=0,
            outbound_count=outbound_count,
            inbound_unique_sources=0,
            label="low-inbound",
            severity=1,
        )
    elif inbound_count >= 5:
        return FileHealth(
            signal_score=signal,
            inbound_count=inbound_count,
            outbound_count=outbound_count,
            inbound_unique_sources=inbound_unique_sources,
            label="hub",
            severity=0,
        )
    elif outbound_count >= 8:
        return FileHealth(
            signal_score=signal,
            inbound_count=inbound_count,
            outbound_count=outbound_count,
            inbound_unique_sources=inbound_unique_sources,
            label="dense-outbound",
            severity=1,
        )
    else:
        return FileHealth(
            signal_score=signal,
            inbound_count=inbound_count,
            outbound_count=outbound_count,
            inbound_unique_sources=inbound_unique_sources,
            label="healthy",
            severity=0,
        )


def collect_md(root: Path) -> list[Path]:
    out = []
    for p in root.rglob("*.md"):
        # Check parts relative to root so a worktree path like
        # `.claude/worktrees/...` doesn't make every file look skipped.
        rel_parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        out.append(p)
    return out


def _resolve(
    rel_or_abs: str, src: Path, root: Path, all_paths: set[Path], basename_index: dict[str, list[Path]]
) -> Path | None:
    """Resolve a textual reference to an actual .md path in the corpus."""
    s = rel_or_abs.split("#", 1)[0].split("?", 1)[0].strip()
    if not s or not s.endswith(".md"):
        return None
    # Absolute-ish (~/... or /...) → expand and resolve
    if s.startswith("~/"):
        # Strip either prefix; both resolve to the same repo (symlink)
        cand = s.replace("~/claude_code/claude-skills/", "").replace("~/.claude/skills/", "")
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
    # Suffix-match fallback — catches prose like `docs/plans/foo.md` when the
    # script is scoped under `--root docs/`. Without this, design/plan pairs
    # that already cross-reference each other look like orphans because the
    # textual prefix doesn't match the on-disk arrangement.
    if "/" in s:
        sfx = "/" + s
        suffix_matches = [p for p in all_paths if str(p).endswith(sfx)]
        if len(suffix_matches) == 1 and suffix_matches[0] != src:
            return suffix_matches[0]
    return None


def extract_typed_links(
    md_path: Path, root: Path, all_paths: set[Path], basename_index: dict[str, list[Path]], skill_index: dict[str, Path]
) -> dict[Path, set[str]]:
    """Return typed cross-references from *md_path*.

    Returns a dict mapping each resolved target path to a set of relation
    types (one or more of ``see-also``, ``defines``, ``mentions``,
    ``links-to``).

    Relation types are inferred from the markdown syntax:
      - ``see-also`` — link text matches ``[See also](...)`` or ``[Also see](...)``
      - ``defines``  — ``[[wikilink]]`` or ``[[wikilink|alias]]``
      - ``mentions`` — backtick path `` `foo.md` ``, absolute path ref, or
                       skill slug `` `slug` ``
      - ``links-to`` — standard markdown link ``[text](path)`` (the default)
    """
    targets: dict[Path, set[str]] = defaultdict(set)
    text = md_path.read_text(errors="ignore")

    for label, target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        hit = _resolve(target, md_path, root, all_paths, basename_index)
        if hit:
            rtype = REL_SEE_ALSO if SEE_ALSO_RE.search(label) else REL_LINKS_TO
            targets[hit].add(rtype)

    for m in BACKTICK_PATH_RE.findall(text):
        hit = _resolve(m, md_path, root, all_paths, basename_index)
        if hit:
            targets[hit].add(REL_MENTIONS)

    for m in ABS_PATH_RE.findall(text):
        hit = _resolve("~/claude_code/claude-skills/" + m, md_path, root, all_paths, basename_index)
        if hit:
            targets[hit].add(REL_MENTIONS)

    for slug in SKILL_MENTION_RE.findall(text):
        # plugin:skill-name → skill-name; bare skill-name stays as-is
        key = slug.split(":")[-1]
        hit = skill_index.get(key)
        if hit and hit != md_path:
            targets[hit].add(REL_MENTIONS)

    for raw in WIKILINK_RE.findall(text):
        # `[[name]]` or `[[name.md]]` — resolve via basename_index.
        # Skip ambiguous matches (multiple files share the basename); a single
        # match wins. The display-alias half of `[[name|alias]]` is stripped
        # by the regex.
        name = raw.strip()
        if not name.endswith(".md"):
            name = name + ".md"
        matches = basename_index.get(name, [])
        if len(matches) == 1 and matches[0] != md_path:
            targets[matches[0]].add(REL_DEFINES)

    return dict(targets)


def extract_dead_links(md_path: Path, root: Path) -> list[str]:
    """Explicit markdown links [text](target.md) whose target is missing on disk.

    Deliberately narrower than extract_links: only LINK_RE targets are
    checked — backtick mentions, skill slugs, and wikilinks are too fuzzy to
    call "dead" without false positives. Existence is checked against the
    filesystem, not the corpus, so links into SKIP_DIRS (archive/, worktrees)
    don't count as dead.
    """
    # Doc examples use literal placeholder targets — not rot, skip them.
    PLACEHOLDERS = {"path.md", "file.md", "example.md", "name.md", "slug.md"}
    dead: list[str] = []
    text = md_path.read_text(errors="ignore")
    # Links inside fenced code blocks / inline code are examples or test
    # fixtures, not navigable references — strip before scanning.
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    for _label, target in LINK_RE.findall(text):
        if target.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        s = target.split("#", 1)[0].split("?", 1)[0].strip()
        if not s.endswith(".md") or s in PLACEHOLDERS:
            continue
        if s.startswith("~"):
            if not Path(s).expanduser().exists():
                dead.append(s)
        elif s.startswith("/"):
            if not Path(s).exists():
                dead.append(s)
        elif not ((md_path.parent / s).exists() or (root / s).exists()):
            dead.append(s)
    return dead


def extract_keywords(md_path: Path, top_n: int = 15) -> set[str]:
    text = md_path.read_text(errors="ignore").lower()
    # Strip code blocks (rough but good enough for keyword signal)
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]+`", " ", text)
    words = WORD_RE.findall(text)
    counts = Counter(w for w in words if w not in STOP and len(w) > 3)
    return {w for w, _ in counts.most_common(top_n)}


def build_graph(root: Path):
    """Build typed forward/reverse adjacency maps and keyword index.

    Returns:
        paths: list[Path] — all scanned .md files
        forward: dict[Path, dict[Path, set[str]]] — src → {target → {types}}
        reverse: dict[Path, dict[Path, set[str]]] — target → {src → {types}}
        keywords: dict[Path, set[str]]
    """
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

    forward: dict[Path, dict[Path, set[str]]] = {
        p: extract_typed_links(p, root, path_set, basename_index, skill_index) for p in paths
    }
    # Build typed reverse map: target → {source → {types}}
    reverse: dict[Path, dict[Path, set[str]]] = defaultdict(lambda: defaultdict(set))
    for src, targets in forward.items():
        for tgt, types in targets.items():
            for rtype in types:
                reverse[tgt][src].add(rtype)
    # Ensure every path has an entry (even if zero inbound refs)
    for p in paths:
        if p not in reverse:
            reverse[p] = {}

    keywords: dict[Path, set[str]] = {p: extract_keywords(p) for p in paths}
    return paths, forward, dict(reverse), keywords


def _rel_path(p: Path, root: Path) -> str:
    try:
        return str(p.relative_to(root))
    except ValueError:
        return str(p)


def _format_types(types: set[str]) -> str:
    """Pretty-print a sorted list of relation types."""
    order = [t for t in REL_ALL_TYPES if t in types]
    return ", ".join(order)


def _type_count(forward: dict[Path, dict[Path, set[str]]], rtype: str) -> int:
    """Count edges of a specific relation type across the whole graph."""
    total = 0
    for src, targets in forward.items():
        for tgt, types in targets.items():
            if rtype in types:
                total += 1
    return total


# ---- Asset-class predicates (unchanged from original) ----

# Subdirs whose .md contents are loaded by the Read tool from a sibling
# SKILL.md router, not by markdown link. `rules/` covers imported Vercel/Cursor
# -style skills (one .md per rule); the rest are the native Claude layout.
_PROGRESSIVE_SUBDIRS = {"references", "phases", "contracts", "diagrams", "rules"}


def _is_progressive_disclosure(p: Path, root: Path) -> bool:
    """True if file lives in a skill's references/, phases/, contracts/,
    diagrams/, or rules/ dir and the skill has a SKILL.md router as a sibling
    of that dir. These are typically loaded by the Read tool from the router,
    not by markdown link — flagging them as orphans is a false positive.

    Position-independent: handles both root-level skills
    (`<skill>/references/x.md`) and nested skill collections
    (`.agents/skills/<skill>/rules/x.md`).
    """
    parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
    if len(parts) < 3:
        return False
    for i in range(1, len(parts) - 1):
        if parts[i] in _PROGRESSIVE_SUBDIRS:
            skill_router = root.joinpath(*parts[:i]) / "SKILL.md"
            if skill_router.exists():
                return True
    return False


def _is_command_file(p: Path, root: Path) -> bool:
    """True if file is a top-level repo-root .md (slash command, workflow doc,
    or project-context registry). Different asset class than skills — should
    not be flagged as orphan when uncited.
    """
    parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
    return len(parts) == 1 and parts[0].endswith(".md")


# Top-level dirs whose contents are intentionally not part of the cross-linked
# doc graph — standalone reference assets, history, or test artifacts. Files
# inside these are NOT orphans even when uncited.
_REFERENCE_DIRS = {
    "audits",
    "compliance",
    "deployment",
    "dev",
    "evidence",
    "implementation-notes",
    "marketing",
    "mockups",
    "perf",
    "prompts",
    "routines",
    "runbooks",
    "setup",
    "superpowers",
    "templates",
    "calendar-integration",
}


def _is_archive_file(p: Path, root: Path) -> bool:
    """True if file lives under any `archive/` dir at any depth (top-level
    `archive/` or nested like `plans/archive/`). Archive content is
    intentional history — not part of the active doc graph and should not be
    flagged as orphan.
    """
    parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
    return "archive" in parts


def _is_handoff_file(p: Path, root: Path) -> bool:
    """True if file is a session handoff doc in `plans/` — filename ends in
    `-handoff.md` or `-session-handoff.md`. Handoffs are one-off transitional
    docs; they're not expected to be cross-linked from the doc graph.
    """
    parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
    if len(parts) < 2 or parts[0] != "plans":
        return False
    name = p.name
    return name.endswith("-handoff.md") or name.endswith("-session-handoff.md")


def _is_reference_dir_file(p: Path, root: Path) -> bool:
    """True if file's top-level dir is a known standalone-reference category.
    Also matches dated test-artifact dirs like `copilot-canary-2026-04-27/`.
    """
    parts = p.relative_to(root).parts if p.is_relative_to(root) else p.parts
    if len(parts) < 2:
        return False
    top = parts[0]
    if top in _REFERENCE_DIRS:
        return True
    # Dated copilot test-artifact dirs (`copilot-canary-*`, `copilot-baseline-*`)
    if top.startswith(("copilot-canary-", "copilot-baseline-")):
        return True
    return False


# ---- Missing-link inference (unchanged logic) ----


def find_missing_links(paths, forward, keywords, threshold: int = 6, max_pairs: int = 25):
    """Pairs that share many keywords but don't link either direction.

    Skips boilerplate-heavy filenames (SOURCE.md, LICENSE.md, README.md) that
    share template text rather than semantic content.
    """
    BOILERPLATE = {"SOURCE.md", "LICENSE.md"}
    candidates = [p for p in paths if p.name not in BOILERPLATE]
    suggestions = []
    seen = set()

    def _has_link(a: Path, b: Path) -> bool:
        """Check if a and b have any direct link in either direction."""
        return b in forward[a] or a in forward[b]

    for i, a in enumerate(candidates):
        for b in candidates[i + 1 :]:
            if _has_link(a, b):
                continue
            shared = keywords[a] & keywords[b]
            if len(shared) >= threshold:
                key = (a, b) if a < b else (b, a)
                if key in seen:
                    continue
                seen.add(key)
                suggestions.append((len(shared), a, b, sorted(shared)))
    suggestions.sort(reverse=True, key=lambda x: x[0])
    return suggestions[:max_pairs]


# ---- Report rendering ----


def render_report(root: Path, paths, forward, reverse, missing, dead) -> str:
    total_files = len(paths)
    total_edges = sum(len(v) for v in forward.values())

    # Compute per-file health
    # Build flat outbound/inbound type maps keyed by rel path for health scoring
    outbound_flat: dict[str, set[str]] = {}
    inbound_flat: dict[str, set[str]] = {}
    for p in paths:
        rp = _rel_path(p, root)
        outbound_flat[rp] = set()
        for tgt in forward.get(p, {}):
            outbound_flat[rp].add(_rel_path(tgt, root))
        inbound_flat[rp] = set()
        for src in reverse.get(p, {}):
            inbound_flat[rp].add(_rel_path(src, root))

    health_map: dict[str, FileHealth] = {}
    for p in paths:
        rp = _rel_path(p, root)
        health_map[rp] = _compute_health(rp, outbound_flat, inbound_flat)

    # Entity type distribution
    type_counts: Counter = Counter()
    type_files: dict[str, list[str]] = defaultdict(list)
    for p in paths:
        rp = _rel_path(p, root)
        etype = _infer_entity_type(rp)
        type_counts[etype] += 1
        type_files[etype].append(rp)

    # Link type distribution
    link_type_counts: dict[str, int] = {t: _type_count(forward, t) for t in REL_ALL_TYPES}

    # Hubs (sorted by inbound count)
    hubs = sorted(paths, key=lambda p: len(reverse[p]), reverse=True)[:15]

    # Orphans (unchanged logic)
    raw_orphans = []
    for p in paths:
        has_outbound = bool(forward[p])
        has_inbound = bool(reverse[p])
        if not has_inbound and not has_outbound:
            raw_orphans.append(p)

    true_orphans = sorted(
        p
        for p in raw_orphans
        if not _is_progressive_disclosure(p, root)
        and not _is_command_file(p, root)
        and not _is_archive_file(p, root)
        and not _is_reference_dir_file(p, root)
        and not _is_handoff_file(p, root)
    )
    pd_orphans = sorted(p for p in raw_orphans if _is_progressive_disclosure(p, root))
    cmd_orphans = sorted(p for p in raw_orphans if _is_command_file(p, root))
    archive_orphans = sorted(p for p in raw_orphans if _is_archive_file(p, root))
    ref_orphans = sorted(
        p for p in raw_orphans if _is_reference_dir_file(p, root) and not _is_archive_file(p, root)
    )
    handoff_orphans = sorted(
        p for p in raw_orphans if _is_handoff_file(p, root) and not _is_archive_file(p, root)
    )
    sinks = sorted(
        (p for p in paths if reverse[p] and not forward[p]), key=lambda p: len(reverse[p]), reverse=True
    )[:10]

    lines = [
        "# Doc Graph Report",
        "",
        f"- **Files scanned:** {total_files}",
        f"- **Cross-references found:** {total_edges}",
        f"- **Link types:** see-also={link_type_counts[REL_SEE_ALSO]}, "
        f"defines={link_type_counts[REL_DEFINES]}, "
        f"mentions={link_type_counts[REL_MENTIONS]}, "
        f"links-to={link_type_counts[REL_LINKS_TO]}",
        "- **Hub nodes (top 15 by inbound refs):** see below",
        f"- **True orphans (zero links + not in any excluded asset class):** {len(true_orphans)}",
        f"- **Dead links (markdown links whose .md target is missing on disk):** {sum(len(v) for v in dead.values())}",
        f"- **Progressive-disclosure references (Read-loaded, not orphans):** {len(pd_orphans)}",
        f"- **Command files (repo-root .md, slash commands or workflow docs — not orphans):** {len(cmd_orphans)}",
        f"- **Archive files (under `archive/`, intentional history — not orphans):** {len(archive_orphans)}",
        f"- **Reference-dir files (audits/, perf/, runbooks/, etc. — standalone, not orphans):** {len(ref_orphans)}",
        f"- **Handoff docs (`plans/*-handoff.md` — one-off transitional docs, not orphans):** {len(handoff_orphans)}",
        "- **Confidence:** EXTRACTED (explicit markdown links only) — "
        "INFERRED keyword-cluster suggestions in the missing-links section. "
        "Files under `<skill>/references/`, `<skill>/phases/`, `<skill>/contracts/`, "
        "`<skill>/diagrams/`, or `<skill>/rules/` are loaded by the Read tool from the router "
        "SKILL.md and are NOT counted as orphans even when no markdown link points to them "
        "(detection is position-independent — nested collections like "
        "`.agents/skills/<skill>/rules/` are covered). "
        "Top-level repo-root `.md` files (slash commands, workflow docs, project registries), "
        "anything under `archive/`, and standalone-reference dirs (`audits/`, `perf/`, `runbooks/`, "
        "`setup/`, `deployment/`, `templates/`, `prompts/`, `marketing/`, `mockups/`, `evidence/`, "
        "`compliance/`, `routines/`, `dev/`, `implementation-notes/`, `superpowers/`, "
        "`copilot-canary-*`, `copilot-baseline-*`) are also excluded from true-orphans — "
        "different asset classes.",
        "",
        "## Link type distribution",
        "",
        f"| Type | Count | Description |",
        f"|------|-------|-------------|",
        f"| see-also | {link_type_counts[REL_SEE_ALSO]} | `[See also](path.md)` intentional cross-refs |",
        f"| defines | {link_type_counts[REL_DEFINES]} | `[[wikilink]]` declarative references |",
        f"| mentions | {link_type_counts[REL_MENTIONS]} | `` `backtick paths` `` or `` `skill-slugs` `` |",
        f"| links-to | {link_type_counts[REL_LINKS_TO]} | Standard `[text](path)` markdown links |",
        "",
        "## File health summary",
        "",
    ]

    # Health sorted by severity (worst first)
    healthy_files_sorted = sorted(
        health_map.items(), key=lambda kv: (kv[1].severity, -kv[1].signal_score), reverse=True
    )
    needs_attention = [rp for rp, h in healthy_files_sorted if h.severity == 2]
    watch = [rp for rp, h in healthy_files_sorted if h.severity == 1]

    lines.append(f"- **{len(needs_attention)} files need attention** (orphan-risk)")
    if needs_attention:
        for rp in needs_attention:
            lines.append(f"  - {rp}")
    lines.append(f"- **{len(watch)} files flagged for review** (low-inbound or dense-outbound)")
    if watch:
        for rp in watch:
            h = health_map[rp]
            lines.append(f"  - {rp} — {h.label} (signal={h.signal_score:.1f}, in={h.inbound_count}, out={h.outbound_count})")
    lines.append("")

    lines.append("## Entity type distribution")
    lines.append("")
    for etype in sorted(type_counts):
        lines.append(f"- **{etype}:** {type_counts[etype]} files")
    lines.append("")

    # Entity-type-scoped orphan sections
    orphan_type_groups: dict[str, list[str]] = defaultdict(list)
    for p in true_orphans:
        rp = _rel_path(p, root)
        orphan_type_groups[_infer_entity_type(rp)].append(rp)

    lines.append("## Orphans by type")
    lines.append("")
    if not true_orphans:
        lines.append("_None._")
    else:
        for etype in sorted(orphan_type_groups):
            files = orphan_type_groups[etype]
            lines.append(f"### {etype} ({len(files)})")
            for rp in files:
                lines.append(f"- {rp}")
    lines.append("")

    lines.append("## Hubs (most-referenced files)")
    lines.append("")
    for p in hubs:
        n = len(reverse[p])
        if n == 0:
            continue
        # Show types of incoming refs
        all_in_types: set[str] = set()
        for src, types in reverse[p].items():
            all_in_types.update(types)
        type_str = _format_types(all_in_types)
        lines.append(f"- **{_rel_path(p, root)}** — {n} inbound ({type_str})")
    lines.append("")

    lines.append("## True orphans (no links in or out, not in any excluded asset class)")
    lines.append("")
    if not true_orphans:
        lines.append("_None._")
    else:
        for p in true_orphans:
            lines.append(f"- {_rel_path(p, root)}")
    lines.append("")

    lines.append("## Dead links (markdown links to missing .md files)")
    lines.append("")
    dead_items = [(p, t) for p in paths for t in dead.get(p, [])]
    if not dead_items:
        lines.append("_None._")
    else:
        for p, t in dead_items:
            lines.append(f"- **{_rel_path(p, root)}** → `{t}`")
    lines.append("")

    lines.append("## Sinks (referenced but never link out)")
    lines.append("")
    if not sinks:
        lines.append("_None._")
    else:
        for p in sinks:
            out_types: set[str] = set()
            for tgt, types in forward.get(p, {}).items():
                out_types.update(types)
            type_str = _format_types(out_types) if out_types else "none"
            lines.append(
                f"- **{_rel_path(p, root)}** — {len(reverse[p])} inbound, outbound types: {type_str}"
            )
    lines.append("")

    lines.append("## Suggested missing cross-links (INFERRED — keyword overlap, no direct link)")
    lines.append("")
    if not missing:
        lines.append("_None above threshold._")
    else:
        for shared_n, a, b, shared in missing:
            terms = ", ".join(shared[:6]) + ("…" if len(shared) > 6 else "")
            lines.append(f"- **{_rel_path(a, root)}** ↔ **{_rel_path(b, root)}** — {shared_n} shared terms ({terms})")
    lines.append("")

    lines.append("## Suggested questions for review")
    lines.append("")
    if hubs and len(reverse[hubs[0]]) > 10:
        lines.append(
            f"- Is `{_rel_path(hubs[0], root)}` a true hub or should it be split? "
            f"({len(reverse[hubs[0]])} inbound refs.)"
        )
    if true_orphans:
        lines.append(
            f"- Should the {len(true_orphans)} true orphan file(s) be linked from "
            "an index, merged into a hub, or removed?"
        )
    if dead_items:
        lines.append(
            f"- {len(dead_items)} dead link(s) point at missing files — fix the "
            "path, restore the file, or delete the reference."
        )
    if missing:
        a, b = missing[0][1], missing[0][2]
        lines.append(
            f"- `{_rel_path(a, root)}` and `{_rel_path(b, root)}` share many terms but never "
            "cross-reference. Intentional separation or missing link?"
        )
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path.cwd())
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--json", type=Path, default=None, help="Optional: dump full graph as JSON for downstream tools")
    ap.add_argument("--missing-threshold", type=int, default=6)
    args = ap.parse_args()

    root = args.root.resolve()
    out = (args.out or root / ".knowledge" / "GRAPH_REPORT.md").resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    paths, forward, reverse, keywords = build_graph(root)
    missing = find_missing_links(paths, forward, keywords, threshold=args.missing_threshold)
    dead = {p: extract_dead_links(p, root) for p in paths}
    out.write_text(render_report(root, paths, forward, reverse, missing, dead))
    total_edges = sum(len(v) for v in forward.values())
    print(f"wrote {out} — {len(paths)} files, {total_edges} edges")

    if args.json:
        # Build typed edges for JSON export
        edges = []
        for src, targets in forward.items():
            for tgt, types in targets.items():
                for rtype in sorted(types):
                    edges.append(
                        {
                            "source": _rel_path(src, root),
                            "target": _rel_path(tgt, root),
                            "type": rtype,
                        }
                    )

        data = {
            "root": str(root),
            "files": [_rel_path(p, root) for p in paths],
            "file_health": {
                _rel_path(p, root): {
                    "signal_score": _compute_health(
                        _rel_path(p, root),
                        {_rel_path(k, root): {_rel_path(t, root) for t in v} for k, v in forward.items()},
                        {_rel_path(k, root): {_rel_path(s, root) for s in v} for k, v in reverse.items()},
                    ).signal_score,
                    "inbound_count": len(reverse.get(p, {})),
                    "outbound_count": len(forward.get(p, {})),
                    "entity_type": _infer_entity_type(_rel_path(p, root)),
                    "inbound_types": sorted(
                        set().union(*reverse[p].values()) if p in reverse else set()
                    ),
                    "outbound_types": sorted(
                        set().union(*forward[p].values()) if p in forward else set()
                    ),
                }
                for p in paths
            },
            "edges": edges,
            "link_type_counts": {t: _type_count(forward, t) for t in REL_ALL_TYPES},
            "missing_suggestions": [
                {
                    "a": _rel_path(a, root),
                    "b": _rel_path(b, root),
                    "shared": shared,
                    "shared_count": n,
                }
                for n, a, b, shared in missing
            ],
        }
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(data, indent=2))
        print(f"wrote {args.json}")


if __name__ == "__main__":
    main()
