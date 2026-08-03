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

### Single-Gap Mode

The loop above returns a triaged findings list. That is correct for
correctness-gating review, where every HIGH+ finding must clear before ship.

It is the wrong shape for *comparative quality* review — the Exemplar Benchmark
below, or any pass asking "is this good enough" rather than "is this right."
There, a list invites shotgun rework: the builder fixes six nitpicks and the
artifact is no closer to the bar. Switch the reviewer's return contract to:

- exactly **one** gap — the single largest distance from the bar
- stated as an observable difference, not a preference
- with the dimension it belongs to, so the next round is scoped

One gap per round, refixed and rechecked, converges on the thing that actually
moves quality. Six parallel nitpicks do not.

Do not use single-gap mode for security, correctness, or accessibility findings.
Those are gates, not gradients — every one ships or none do.

## Exemplar Benchmark

Run when `$requirements.reference_exemplar` is present. Skip entirely when it is
absent — this is opt-in and most runs will not have it.

Scored rubrics grade an artifact against itself: they detect drift from a
project's own conventions but cannot tell you the whole convention is mediocre.
An exemplar benchmark supplies an external anchor.

### Procedure

1. **Confirm the exemplar is inspectable.** Open the `locator`. If it 404s, is
   paywalled, or requires auth the reviewer does not have, STOP and report
   `exemplar-unreachable`. Do not proceed from a remembered impression of the
   reference — that is grading against a hallucination.
2. **Blind the comparison.** Present the two artifacts to the reviewer as
   `Candidate A` and `Candidate B` in randomized order, withholding which is
   generated. A reviewer who knows it is grading the team's own work grades it
   differently, and this is a larger effect than the conciseness and familiarity
   biases the Judge Bias Guard already covers.
3. **Score both on the same rubric**, confined to `reference_exemplar.dimensions`.
   Report both totals. A comparison that ranges outside the named dimensions has
   escaped its bounds — the dimensions are the falsifiability constraint.
4. **Return one gap** per Single-Gap Mode above: the largest dimension-scoped
   deficit, stated as an observable difference.
5. **Unblind only after scoring** to interpret the result.

### The pass bar, and its cap

The bar is: the generated artifact scores at least as high as the exemplar on
every named dimension, and strictly higher on at least one.

**Cap the loop at 3 rounds.** Strict domination over a best-in-class reference is
frequently unreachable, and an uncapped "keep going until the critic passes" loop
has no stopping condition — the critic can always find one more gap. After the
third round, stop and take one of:

- **accept with debt** — record the remaining gap, its dimension, and the score
  delta as a typed known gap; ship
- **revise the bar** — the exemplar was the wrong comparison, or a dimension was
  mis-chosen; fix the contract, do not keep grinding against it
- **escalate to the user** — the gap is real, material, and needs a scope call

Report the round count and the final delta either way. A benchmark that quietly
ran three rounds and shipped anyway looks identical to one that passed on the
first, unless the count is stated.

### Where it applies

Anywhere the deliverable has an openable best-in-class equivalent: UI surfaces,
landing and marketing pages, READMEs and generated docs, CLI output formats,
error-message copy, onboarding flows. For UI specifically, run this alongside the
scored audit in `references/phase-6-design-review.md` — the rubric catches
system drift, the benchmark catches "consistent with our system, and our system
is behind."

It does not apply to internal logic with no comparable surface. A migration, a
service refactor, or a bug fix has no exemplar; that is why the contract field is
optional.

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
