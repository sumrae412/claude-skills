# Phase 4: Validation and Cutover

Load `../references/data_reconciliation_strategies.md` and
`../references/zero_downtime_techniques.md` before running this phase.

## Goal

Define how the migration is validated during and after cutover.

## Ask

- What technical signals prove the migration worked?
- What business signals prove customers are unaffected?
- How long must both systems run in comparison mode?
- What is the decision point for decommissioning the old path?

## Validate

Cover these areas:

- row or object counts
- checksums or sampled reconciliation
- business-query parity
- latency and error-rate deltas
- customer-facing KPI impact

## Cutover Design

- define traffic-shift plan
- define pause points
- define rollback thresholds
- define post-cutover observation window

## Output

Validation and cutover plan with metrics, alert thresholds, and
decommission criteria.
