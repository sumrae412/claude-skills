---
name: doc-graph
description: Use when consolidating, cleaning up, or auditing a markdown corpus (a skills repo, a docs tree, a project memory dir) — before any manual "merge / dedupe / retire" pass. Builds a cross-reference graph from .md files and emits a report with hubs (never retire), true orphans (real deletion candidates), and INFERRED keyword-overlap pairs (usually missing links, not duplicates). Pure stdlib, zero deps, runs on any markdown folder. Triggers on "clean up docs", "consolidate memory", "find orphan docs", "find missing cross-links", "audit markdown structure", "doc graph".
user-invocable: true
---

# doc-graph

Static analysis of a markdown corpus. Walks `.md` files, extracts cross-references (markdown links, backtick paths, `[[wikilinks]]`, `` `slug` `` skill mentions), and writes a `GRAPH_REPORT.md` to `.knowledge/`.

## When to use

- Before any "clean up memory / docs" manual pass on a corpus >100 files
- When deciding which docs to retire, merge, or split
- When auditing whether sibling skills/docs should cross-reference each other
- When a hub file feels overloaded and you're wondering if it should be split

## When NOT to use

- Single-file edits, small targeted changes — graph signal is noise at small N
- Non-markdown corpora (code, JSON, etc.) — script is `.md`-only by design

## Invoke

The script lives at `scripts/build_doc_graph.py` in this repo. Pure stdlib — no install step.

```bash
python3 /path/to/claude-skills/scripts/build_doc_graph.py [--root PATH] [--out PATH] [--json PATH]
```

- `--root` — corpus root (default: cwd)
- `--out` — report path (default: `<root>/.knowledge/GRAPH_REPORT.md`)
- `--json` — optional full graph dump for downstream tools
- `--missing-threshold N` — min shared keywords for missing-link suggestions (default 6)

Example from a project root:

```bash
python3 ~/claude_code/claude-skills/scripts/build_doc_graph.py --root .
```

## Reading the report

The report has five sections. Treat each one differently:

| Section | Confidence | Default action |
|---|---|---|
| **Hubs (>10 inbound refs)** | EXTRACTED | Do NOT retire. Deletion dangles N references silently. Consider splitting if overloaded. |
| **True orphans** | EXTRACTED | Real deletion candidates — but verify nothing references them implicitly (e.g. CLAUDE.md routing) before deleting. |
| **Sinks** (referenced, never link out) | EXTRACTED | Often leaf nodes (specs, glossaries). Usually fine as-is. |
| **Suggested missing cross-links** | INFERRED (keyword overlap) | **Default: add bidirectional `See also` links, NOT merge.** Read both files first. |
| **Suggested questions for review** | INFERRED | Prompts for the human pass, not action items. |

**The cardinal rule for keyword-overlap pairs:** they are USUALLY complementary patterns missing a bidirectional link, NOT duplicates to merge. Validated across multiple corpora: 5/5 inferred pairs on the courierflow project-memory corpus (2026-05-12) and 4/4 on the claude-skills repo were complementary, 0 were merges.

When you find a pair worth linking, add the cross-reference on both sides — a one-line `See also: [name](path)` per file is enough. Don't consolidate without reading both files end-to-end.

## What the script ignores (excluded asset classes)

The report distinguishes "true orphans" from files that look orphaned but shouldn't be flagged:

- **Progressive-disclosure references** — files under `<skill>/references/`, `<skill>/phases/`, `<skill>/contracts/`, `<skill>/diagrams/` when a `SKILL.md` router exists in the same skill dir. These are loaded by the Read tool from the router, not by markdown link.
- **Command files** — top-level repo-root `.md` files (slash commands, workflow docs, project registries).
- **Archive files** — anything under `archive/` at any depth.
- **Reference dirs** — `audits/`, `perf/`, `runbooks/`, `setup/`, `deployment/`, `templates/`, `prompts/`, `marketing/`, `mockups/`, `evidence/`, `compliance/`, `routines/`, `dev/`, `implementation-notes/`, `superpowers/`, `copilot-canary-*`, `copilot-baseline-*`.
- **Handoff docs** — `plans/*-handoff.md` / `plans/*-session-handoff.md`.

If your corpus has another asset class that's legitimately uncited (e.g. test fixtures), extend `_REFERENCE_DIRS` or add a new `_is_*` predicate in `scripts/build_doc_graph.py`.

## What it catches as a reference

- Standard markdown links: `[text](path.md)`
- Backtick-bare paths: `` `MEMORY.md` `` or `` `foo/bar.md` ``
- Absolute prose paths: `~/claude_code/<repo>/x/y.md`
- Obsidian-style wikilinks: `[[name]]` or `[[name|display alias]]`
- Skill-name mentions: `` `slug` `` or `` `plugin:slug` `` (resolved via `<slug>/SKILL.md` discovery)

Ambiguous matches (multiple files share a basename) are skipped to avoid false edges.

## Limitations

- Markdown only — code-graph / Python-import-graph is a separate problem
- Keyword extraction uses a small built-in stoplist; project-specific jargon may inflate keyword overlap. If you see structural-template words dominating the suggestions, extend `STRUCTURAL_STOP` in the script.
- The script does NOT push to any external system (Mem, Notion). It writes a markdown file to disk. If you want to mirror the report somewhere, do it as a follow-up step.

## See also

- [`lint-memory`](../lint-memory/SKILL.md) — health checks on a single project's memory dir (broken links, orphan memories, stale entries). `doc-graph` is the corpus-wide structural version; `lint-memory` is the per-file hygiene version. Pair them: run `doc-graph` for the structural map, then `lint-memory` for per-file fixes.
- `anthropic-skills:consolidate-memory` — run `doc-graph` FIRST, then let `consolidate-memory` do the manual merge/dedupe pass with the graph in hand.
