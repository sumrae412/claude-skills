# Phase 2: Mechanical Checks

## Goal

Run deterministic checks for broken links, orphan memories, oversized
index lines, frontmatter schema issues, and stale code references.

## Mechanical Checks

1. Broken links
2. Orphan memories
3. Stale code references
4. Index line length
5. Frontmatter schema
6. Index/description drift — flag files where the body contains a newer date, or a resolution marker (RESOLVED/SHIPPED/CLOSED/re-verified) not reflected in the file's own `description:` frontmatter or its MEMORY.md index line

## Auto-Fixable

- broken links
- orphan memories
- oversized index lines

Use `scripts/slim_memory_index.py <memory_dir> --apply` for oversized
index entries when applicable.

## Rules

- Report proposed fixes before applying them.
- Check 6 is manual-only (never auto-fix): index/description drift needs a human judgment on which surface is current. Origin: two same-night instances (henry project memory, 2026-07-11) where a stale index line drove wasted dispatches while the body was correct — see `agent-vault/agent/memory-index-drift.md`.
- Keep filename matching broad for top-level `*.md`.
- Ignore known exclusions such as `MEMORY.md`, JSON/JSONL, and subdir
  runtime state where the check says to.
- Exclude review/operational artifacts from orphan checks:
  `IMPORT_REVIEW.md`, `REVIEW_QUEUE.md`, `.claude/memory-archives/**`,
  `memory-archives/**`, and `knowledge/**` derived articles.

## Output

Mechanical findings with severity, affected files, and fixability.
