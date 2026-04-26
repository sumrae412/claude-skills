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
