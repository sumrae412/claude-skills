---
name: "migration-architect"
description: "Migration planning toolkit — zero-downtime strategies (expand-contract, parallel schema, blue-green), compatibility analysis for schema/API/data-type changes, and automated rollback runbook generation. Use when planning database or service migrations, assessing breaking changes, or designing rollback procedures."
---

# Migration Architect

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

Migration planning toolkit for zero-downtime strategy, compatibility
analysis, rollback design, and execution validation.

This file is a router. Do not load the full migration doctrine up front.

## When to Use

- Planning a database, service, or infrastructure migration
- Assessing compatibility risk before a change lands
- Designing rollback or cutover procedures
- Building a migration runbook with validation gates

## Load Strategy

1. Classify the migration problem.
2. Load only the matching phase file from `phases/`.
3. Load only the reference files that phase calls for.
4. Use the provided scripts for deterministic outputs where possible.

Do not preload examples, expected outputs, or all references.

## Phase Map

1. `phases/phase-1-scope-and-strategy.md`
2. `phases/phase-2-compatibility.md`
3. `phases/phase-3-rollback-and-runbook.md`
4. `phases/phase-4-validation-and-cutover.md`

## Reference Map

- Migration patterns:
  `references/migration_patterns_catalog.md`
- Zero-downtime techniques:
  `references/zero_downtime_techniques.md`
- Reconciliation and data checks:
  `references/data_reconciliation_strategies.md`

## Script Map

- Planning:
  `scripts/migration_planner.py`
- Compatibility analysis:
  `scripts/compatibility_checker.py`
- Rollback generation:
  `scripts/rollback_generator.py`

## Session Rules

- Classify first: database, service, or infrastructure migration.
- Prefer explicit phases and validation gates over a giant migration plan.
- Design rollback before finalizing cutover.
- Keep business impact visible, not just technical steps.

## Deliverables

Produce only the deliverable the user needs:

- migration strategy
- compatibility report
- rollback runbook
- execution checklist
- cutover / validation plan

## Guardrails

- Do not treat zero downtime as assumed; prove it.
- Call out irreversible steps explicitly.
- Prefer reversible phases over big-bang changes.
- Highlight missing monitoring, rollback, or reconciliation before calling
  a plan ready.

## Out of Scope

This skill does NOT:
- Generate the actual Alembic migration file or run autogenerate—use `new-migration`.
- Decide whether to deprecate vs maintain legacy code—use `deprecation-and-migration`.
- Execute the migration against a production DB—the user runs cutover manually with the runbook.
- Audit dependencies blocking the upgrade—use `dependency-auditor`.
- Run pre-ship readiness checks (secrets, monitoring, backups)—use `production-readiness-check`.
