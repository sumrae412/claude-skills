---
name: lint-memory
description: Run health checks on project memory files — broken links, orphan memories, stale entries, contradictions, oversized index lines
user-invocable: true
---

# Lint Memory

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant
  patterns inline instead of loading extra material.

## Overview

Memory hygiene workflow for checking broken references, orphan files,
stale code pointers, contradictions, oversized index entries, and
frontmatter schema issues.

This file is a router. Do not keep all six check definitions resident.

## When to Use

- Running `/lint-memory`
- After reorganizing memory files
- Before committing memory updates
- During session-learnings or memory cleanup work

## Load Strategy

1. Determine whether the run is full or quick.
2. Load only the phase files needed for that mode.
3. For mechanical checks, prefer deterministic scanning.
4. Only load semantic contradiction guidance when running the full lint.

## Phase Map

1. `phases/phase-1-scope-and-modes.md`
2. `phases/phase-2-mechanical-checks.md`
3. `phases/phase-3-semantic-checks.md`
4. `phases/phase-4-reporting-and-fixes.md`

## Companion tooling — `build_doc_graph.py`

For dense corpora (>100 source files), pair this skill with periodic runs
of `scripts/build_doc_graph.py` (available in `claude-skills/scripts/` and
`courierflow/scripts/`). The graph is the durable maintenance lever:

- **Hubs (>10 inbound refs):** flag what NOT to retire — deleting a hub
  dangles N references silently.
- **True orphans:** real deletion candidates.
- **Keyword-overlap "missing-link" suggestions:** treat as missing links
  between complementary patterns BY DEFAULT, NOT as duplicates to merge.
  Validated 2026-05-12 on a 254-file corpus: 5/5 inferred pairs were
  complementary, 0/5 were duplicates. Read both files before consolidating;
  default action is to add a cross-reference, not retire one side.
- **Obsidian-style `[[wikilinks]]` resolve via `basename_index`** (added in
  [claude-skills PR #124](https://github.com/sumrae412/claude-skills/pull/124)):
  vaults and memory dirs using `[[name]]` cross-references lint correctly.
  Ambiguous basenames (multiple files same name) are silently skipped to
  avoid false edges. Cross-corpus links via external URLs
  (`https://github.com/...`) are filtered as external — per-corpus linting
  only. See
  [`~/claude_code/agent-vault/agent/doc-graph-tooling.md`](https://github.com/sumrae412/agent-vault/blob/main/agent/doc-graph-tooling.md).

Run it before manual consolidation and after every batch of memory adds. The script is wrapped as the [`doc-graph`](../doc-graph/SKILL.md) skill — same script, with read-the-report and interpretation guidance for direct user invocation.

## Check Map

- Mechanical, auto-fixable:
  broken links, orphan memories, oversized index lines
- Mechanical, manual:
  frontmatter schema, stale code references
- Semantic, manual:
  contradictions

## Session Rules

- Graceful no-op if no memory directory exists.
- Report proposed auto-fixes before applying them.
- Do not commit changes from this skill.
- Resolve links relative to the memory directory; resolve code references
  relative to the project root.

## Deliverables

Produce:

- full lint report, or
- abbreviated quick-lint report

Include errors, warnings, auto-fixes applied, and clean yes/no summary.

## Guardrails

- Do not auto-fix stale references or contradictions.
- Keep quick lint mechanical; avoid expensive grep or LLM judgment unless
  full mode explicitly calls for it.
