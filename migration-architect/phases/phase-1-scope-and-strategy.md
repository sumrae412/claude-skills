# Phase 1: Scope and Strategy

Load `../references/migration_patterns_catalog.md` and
`../references/zero_downtime_techniques.md` before running this phase.

## Goal

Choose the right migration pattern and define the phase plan.

## Classify

Determine whether this is primarily:

- database migration
- service migration
- infrastructure migration

Then classify the change shape:

- schema evolution
- data move
- API/service replacement
- cloud or environment migration

## Ask

- What is changing?
- What must stay available?
- What is the blast radius if this goes wrong?
- What dependencies and downstream consumers exist?
- Which steps are reversible and which are not?

## Pattern Selection

Choose the smallest viable pattern:

- Expand-contract
- Parallel schema
- CDC / incremental sync
- Strangler fig
- Parallel run
- Canary
- Blue-green

## Output

Migration strategy with:

- migration type
- chosen pattern
- phase breakdown
- success gates
- business-impact summary
