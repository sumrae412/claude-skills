# Phase 2: Source Collection

## Goal

Gather the minimum relevant evidence from each source category.

## Sources

- code
- git history
- dependencies
- configuration
- design docs and plans
- external documentation

## Rules

- record what was checked even when nothing relevant was found
- keep notes factual and source-tied
- prefer the smallest read set that still captures the evidence
- for aggregate status/count metrics (pending count, queue depth), verify against
  the metric's CAUSE (which template/trigger produced each item) before treating a
  low-alarm value as evidence of health — an aggregate can be zero-overdue and
  growing while 100% of its members are structurally guaranteed to fail
  (courierflow_beta 2026-07-19: "154 pending steps" read as healthy until
  cross-referencing trigger source showed all 154 belonged to tenancy-less
  calendar-triggered instances)

## Output

Collected observations by source type.
