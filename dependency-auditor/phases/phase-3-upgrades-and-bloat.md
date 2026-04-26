# Phase 3: Upgrades and Bloat

Load `../references/dependency_management_best_practices.md` before
running this phase.

## Goal

Plan safe dependency upgrades and identify unnecessary dependency weight.

## Ask

- Is the target security patching, routine hygiene, or performance cleanup?
- Which dependencies are pinned, floating, or abandoned?
- Are there signs of unused or overlapping packages?

## Deterministic Path

Prefer:

- `scripts/upgrade_planner.py`

## Check For

- patch vs minor vs major upgrade risk
- abandoned or stale packages
- redundant functionality across packages
- unused direct dependencies
- opportunities to consolidate without breaking contracts

## Output

Upgrade and cleanup plan with risk tiers, order of operations, and
testing expectations.
