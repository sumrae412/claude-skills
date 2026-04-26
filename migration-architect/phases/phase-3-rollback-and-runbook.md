# Phase 3: Rollback and Runbook

Load `../references/zero_downtime_techniques.md` and
`../references/data_reconciliation_strategies.md` before running this
phase.

## Goal

Design rollback first, then produce the migration runbook.

## Ask

- What is the rollback trigger?
- What state must be preserved to roll back safely?
- Which cutover steps are one-way?
- What monitoring confirms success or rollback conditions?

## Deterministic Path

Prefer the provided scripts when possible:

- `scripts/migration_planner.py`
- `scripts/rollback_generator.py`

Use the generated artifacts as scaffolding, then tighten them for the
real system.

## Build

The runbook should include:

- pre-migration checks
- ordered execution steps
- validation checkpoints
- rollback conditions
- rollback procedures
- communications checkpoints

## Output

Rollback-aware migration runbook with explicit triggers, owners, and
checkpoints.
