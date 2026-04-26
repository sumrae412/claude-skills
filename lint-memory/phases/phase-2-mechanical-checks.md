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

## Auto-Fixable

- broken links
- orphan memories
- oversized index lines

Use `scripts/slim_memory_index.py <memory_dir> --apply` for oversized
index entries when applicable.

## Rules

- Report proposed fixes before applying them.
- Keep filename matching broad for top-level `*.md`.
- Ignore known exclusions such as `MEMORY.md`, JSON/JSONL, and subdir
  runtime state where the check says to.

## Output

Mechanical findings with severity, affected files, and fixability.
