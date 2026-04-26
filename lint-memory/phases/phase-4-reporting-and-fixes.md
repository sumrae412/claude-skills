# Phase 4: Reporting and Fixes

## Goal

Produce the final report and apply only allowed auto-fixes.

## Report Shape

- Errors
- Warnings
- Summary

Include:

- findings by check type
- auto-fixed vs manual
- clean yes/no

## Fix Discipline

- Broken links: strip link wrapper, keep visible text
- Orphans: add semantic-key entry to `MEMORY.md`
- Oversized index lines: slim and move detail into topic file when using
  the helper script

## Never Auto-Fix

- stale references
- contradictions
- frontmatter intent

## Output

Final markdown lint report plus any approved auto-fix actions taken.
