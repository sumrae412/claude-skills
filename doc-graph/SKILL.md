---
name: doc-graph
description: Use when consolidating, cleaning up, or auditing a markdown corpus (a skills repo, a docs tree, a project memory dir) — before any manual "merge / dedupe / retire" pass. Builds a cross-reference graph from .md files and emits a report with hubs (never retire), true orphans (real deletion candidates), and INFERRED keyword-overlap pairs (usually missing links, not duplicates). Pure stdlib, zero deps, runs on any markdown folder. Triggers on "clean up docs", "consolidate memory", "find orphan docs", "find missing cross-links", "audit markdown structure", "doc graph".
user-invocable: true
---

# doc-graph

Static analysis of a markdown corpus. Walks `.md` files, extracts cross-references (markdown links, backtick paths, `[[wikilinks]]`, `` `slug` `` skill mentions), and writes a `GRAPH_REPORT.md` to `.knowledge/`. Also exports a full JSON graph dump with **typed relations**, **entity-type scoping**, and **per-file health composites** — inspired by Potpie's context-graph architecture, without the semantic embedding or daemon overhead.

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
- `--entity-type TYPE` — filter output to files matching a specific entity type (e.g. `plan`, `skill`, `ledger`, `memory`, `routing`, `general`). Useful for scoped reviews: "show me only the plan files" or "any orphaned memory files?"

Example from a project root:

```bash
python3 ~/claude_code/claude-skills/scripts/build_doc_graph.py --root .
```

## Features

### Typed relations

Every cross-reference carries a type. The script auto-detects four relation types from markdown syntax:

| Relation type | Syntax triggers | Meaning |
|---|---|---|
| `mentions` | `` `slug` ``, `[[wikilink]]`, backtick path | General reference — "this file talks about that one" |
| `links-to` | `[text](path.md)`, `[text](path.md#anchor)` | Active hyperlink — "reader can click to go there" |
| `defines` | `[defines: term](path.md)` | Term ownership — "this file is the canonical definition" |
| `see-also` | `[see-also: context](path.md)` | Related reading — "read this alongside" |

The JSON export (`--json`) includes every edge with its type. The report counts types per file and globally.

### Entity-type scoping

Every file in the corpus is assigned a semantic entity type based on path patterns:

| Entity type | Path pattern | Example |
|---|---|---|
| `skill` | Under `skills/` subdirectory | `skills/doc-graph/SKILL.md` |
| `decision` | Contains `decisions/` | `docs/decisions/2026-07-01-foo.md` |
| `memory` | Contains `memory/` | `memory/charlie.md` |
| `phase` | Contains `phases/` | `phases/phase-3-requirements.md` |
| `contract` | Contains `contracts/` | `contracts/plan-schema.md` |
| `reference` | Contains `references/` | `references/agent-architecture.md` |
| `config` | Contains `config/` or is `AGENTS.md`/`CLAUDE.md` | `AGENTS.md` |
| `readme` | Named `README.md` | `README.md` |
| `ledger` | Contains `ledger/` | `ledger/2026-07-26.md` |
| `plan` | Contains `plans/` or `plan` in filename | `docs/plans/2026-07-01-plan.md` |
| `routing` | `routing` in filestem | `PRIORITIES.md`, `DECISIONS.md`, `ROUTINES.md` |
| `general` | Catch-all | Any other `.md` file |

Use `--entity-type <type>` to scope the report to one type for targeted reviews (e.g. "show me orphaned plan files" or "which skill files have no inbound references?").

### Per-file health composite

Every file gets a numeric **signal score** (0 to ~50+) built from multiple signals:

- **Inbound refs:** each unique reference from another file adds +1 (decayed at long tail)
- **Outbound refs:** each link out adds +1 (up to a cap)
- **Entity-type bonus:** routing/decision/config files get +2 (expected to be hubs), plans +1, general files +0
- **Dead-link penalty:** -2 per broken markdown link (a file that links to nothing that exists)

Use the score to quickly find files that need attention:
- **Score = 0**: likely orphan — no one references it, it references nothing, and it's not a recognized hub type
- **Score 1–5**: periphery — may be a legit leaf node or may need connecting
- **Score 6–15**: normal connected file
- **Score 16+**: hub — well-connected, handle with care before deleting

The JSON export includes `file_health` key with full signal breakdown per file.

## Reading the report

The report has six sections. Treat each one differently:

| Section | Confidence | Default action |
|---|---|---|
| **Hubs (>10 inbound refs)** | EXTRACTED | Do NOT retire. Deletion dangles N references silently. Consider splitting if overloaded. |
| **True orphans** | EXTRACTED | Real deletion candidates — but verify nothing references them implicitly (e.g. CLAUDE.md routing) before deleting. |
| **Dead links** (markdown links to missing .md files) | EXTRACTED | Fix the path, restore the file, or delete the reference. Checked against disk, so links into excluded dirs (archive/) are NOT flagged. Corpus-wide complement to `lint-memory`'s per-dir broken-link check. |
| **Sinks** (referenced, never link out) | EXTRACTED | Often leaf nodes (specs, glossaries). Usually fine as-is. |
| **Suggested missing cross-links** | INFERRED (keyword overlap) | **Default: add bidirectional `See also` links, NOT merge.** Read both files first. |
| **Suggested questions for review** | INFERRED | Prompts for the human pass, not action items. |

**The cardinal rule for keyword-overlap pairs:** they are USUALLY complementary patterns missing a bidirectional link, NOT duplicates to merge. Validated across multiple corpora: 5/5 inferred pairs on the courierflow project-memory corpus (2026-05-12) and 4/4 on the claude-skills repo were complementary, 0 were merges.

When you find a pair worth linking, add the cross-reference on both sides — a one-line `See also: [name](path)` per file is enough. Don't consolidate without reading both files end-to-end.

## What the script ignores (excluded asset classes)

The report distinguishes "true orphans" from files that look orphaned but shouldn't be flagged:

- **Progressive-disclosure references** — files under `<skill>/references/`, `<skill>/phases/`, `<skill>/contracts/`, `<skill>/diagrams/`, or `<skill>/rules/` when a `SKILL.md` router exists as a sibling of that dir. These are loaded by the Read tool from the router, not by markdown link. Detection is position-independent, so nested skill collections like `.agents/skills/<skill>/rules/` (imported Vercel/Cursor-style skills) are recognized too — not just root-level skills.
- **Command files** — top-level repo-root `.md` files (slash commands, workflow docs, project registries).
- **Archive files** — anything under `archive/` at any depth.
- **Reference dirs** — `audits/`, `perf/`, `runbooks/`, `setup/`, `deployment/`, `templates/`, `prompts/`, `marketing/`, `mockups/`, `evidence/`, `compliance/`, `routines/`, `dev/`, `implementation-notes/`, `superpowers/`, `copilot-canary-*`, `copilot-baseline-*`.
- **Handoff docs** — `*-handoff.md` / `*-session-handoff.md` in any `plans/` dir. Position-independent, so repos that nest plans under `docs/plans/` are covered too.
- **Daily logs** — files whose stem is a bare ISO date (`ledger/2026-07-03.md`, `journal/2026-07-03.md`). Append-only entries indexed by filename date, never cross-linked by design. Also excluded from the keyword-overlap pass: two entries in the same log share vocabulary by construction (same actors, same repos, same status fields), and "link Tuesday's entry to Thursday's" is never an action.
- **README-indexed files** — numeric-prefix stems (`plans/004-view-render-hardening.md`) whose ID is cited in a sibling `README.md`, typically as a status-table row rather than a markdown link.

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
- Entity-type inference uses path patterns; files in unusual locations may be misclassified as `general`. Extend `_infer_entity_type()` in the script for project-specific patterns.
- Signal score is heuristic — it's a triage tool, not a precise quality metric. A score of 0 doesn't mean "delete this file," it means "look at this file."
- The script does NOT push to any external system (Mem, Notion). It writes a markdown file to disk. If you want to mirror the report somewhere, do it as a follow-up step.

## See also

- [`lint-memory`](../lint-memory/SKILL.md) — health checks on a single project's memory dir (broken links, orphan memories, stale entries). `doc-graph` is the corpus-wide structural version; `lint-memory` is the per-file hygiene version. Pair them: run `doc-graph` for the structural map, then `lint-memory` for per-file fixes.
- `anthropic-skills:consolidate-memory` — run `doc-graph` FIRST, then let `consolidate-memory` do the manual merge/dedupe pass with the graph in hand.
