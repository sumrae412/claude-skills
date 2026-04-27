# Phase 6 Review Operations

Load this reference only when:

- `lightweight-reviewer` is selected
- Tier 1 produced HIGH+ findings
- you need the review-fix-recheck loop
- you want optional strategic pre-review, synthesis, or simplifier passes

Keep it out of the default hot path when Tier 1 exits clean.

## Batched Lightweight Review

Instead of multiple separate Haiku passes, send one `lightweight-reviewer`
dispatch with a combined checklist built from the diff.

Checklist construction:

1. Models, schemas, or types changed:
   - type design
   - encapsulation
   - invariants
2. Routes, APIs, or endpoints changed:
   - API doc accuracy
   - schemas
   - error maps
3. Models, services, or routes changed:
   - project invariants
   - client sync
   - eager loading
   - column-name correctness
4. Templates, static assets, routes, or services changed:
   - defensive patterns
   - guard clauses
   - error feedback
   - state management

Prompt shape:

```text
This feature touched [file summary].
Check these specific areas:
[only applicable checklist items]
Skip checking:
[irrelevant categories]
```

Why batch:

- same diff read once
- one round-trip instead of several
- lower token cost for the same surface coverage

## Review-Fix-Recheck Loop

When any reviewer returns HIGH+ findings:

1. collect and deduplicate findings
2. triage by severity
3. fix one HIGH+ finding at a time
4. rerun only the reviewer that raised it
5. if the finding clears, move on
6. if it fails again, retry up to 3 times
7. after 3 failures, escalate to the user

Design-review Blocker/High-Priority findings follow the same loop.

Keep MEDIUM/LOW findings informational unless the user chooses to treat them as
blocking.

## Strategic Pre-Review

Optional, for full-path complex features only.

Dispatch Opus with:

- `$diff`
- `$requirements`

Question:

`Does this fulfill the original requirements?`

Skip for routine contained work.

## Cross-Cutting Synthesis

After review tiers complete and fixes are applied, a sonnet general-purpose
agent may synthesize only issues not already captured by individual reviewers.

Use it to check:

1. contradictions between reviewers
2. fixes that create problems in another domain
3. architectural concerns no single reviewer catches
4. overall ship readiness

Skip if all tiers returned clean.

## Post-Review Simplifier

Optional pass before the verification gate.

- Dispatch `code-simplifier:code-simplifier`
- Scope: only files modified in this feature
- Accept changes only if tests still pass afterward
- Skip if total diff churn is small (`$diff.insertions + $diff.deletions < 100`)
