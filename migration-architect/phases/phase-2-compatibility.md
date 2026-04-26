# Phase 2: Compatibility Analysis

Load `../references/migration_patterns_catalog.md` before running this
phase. Load `../references/data_reconciliation_strategies.md` if data
consistency is central.

## Goal

Identify backward-compatibility, data-shape, and integration risks before
cutover.

## Ask

- Which schemas, APIs, payloads, or contracts are changing?
- Which clients still depend on old behavior?
- Are reads, writes, or both changing?
- Is dual-write, backfill, or format translation required?

## Deterministic Path

Prefer the compatibility script when inputs are available:

- `scripts/compatibility_checker.py`

Use it for schema diffs, interface deltas, or structured before/after
assets.

## Check For

- backward-incompatible schema changes
- non-null or constraint breakage
- type mismatches and parsing drift
- client contract breakage
- derived-data or reconciliation risk

## Output

Compatibility report with:

- breaking changes
- safe intermediate states
- mitigations
- gating conditions before execution
