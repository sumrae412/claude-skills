# Phase 1: Scope and Modes

## Goal

Locate the memory directory and choose full vs quick lint mode.

## Determine

- memory directory containing `MEMORY.md`
- whether the run is:
  - full lint: checks 1-6
  - quick lint: checks 1, 2, 5, 6 only

## Rules

- If no memory directory exists, report a graceful no-op.
- Top-level memory files are scanned differently from `knowledge/`
  articles; keep that distinction explicit.

## Output

Chosen mode, target memory directory, and check set to run.
