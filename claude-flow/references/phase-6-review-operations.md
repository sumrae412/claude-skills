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
2b. **Withhold the builder's history.** The critic gets the goal, the bar, the
   named dimensions, and the two artifacts — and nothing else. Not the builder's
   reasoning, not its self-review, not its notes on what it attempted or found
   hard, not the prior round's exchange. Blinding step 2 hides *which artifact is
   ours*; this hides *how ours came to be*, which is the other half and leaks
   through any of those channels. A builder that explains it "chose a minimal
   layout deliberately" has told the critic what to conclude about the layout.
   Per the source method: *"Do not give it the builder's history."* Note this
   cuts against Phase 5's implementer hand-back, which normally carries
   self-review findings forward — for the exemplar reviewer specifically, strip
   them.
3. **Score both on the same rubric**, confined to `reference_exemplar.dimensions`.
   Report both totals. A comparison that ranges outside the named dimensions has
   escaped its bounds — the dimensions are the falsifiability constraint.
4. **Return one gap** per Single-Gap Mode above: the largest dimension-scoped
   deficit, stated as an observable difference.
5. **Unblind only after scoring** to interpret the result.

### The pass bar, and how the loop ends

The bar is: the generated artifact scores at least as high as the exemplar on
every named dimension, and strictly higher on at least one.

**Do not stop the loop on a round count.** An earlier version of this section
capped it at 3 rounds. That was wrong, and the source method
([somethingbig.ai/gauntlet-loop](https://somethingbig.ai/gauntlet-loop)) says so
directly: *"Tell it to keep looping. Do not tell it to do three rounds and stop."*
A round count is arbitrary — it stops a run that is still improving fast and
permits three wasted rounds on a run that stalled after one.

The underlying worry was real, though, and the source does not answer it: it
offers no mechanism for a critic that never passes, and against a genuinely
best-in-class reference that is the expected case, not the edge case. So bound
the loop on **progress and budget**, which is what the source's own informal
stopping conditions ("improvements become too small to matter", "as much compute
as you are willing to spend") amount to when written down:

- **Marginal improvement.** Stop when a round's gap closure stops being material
  — no dimension score improved, or the critic's new largest gap is smaller than
  the one it named last round on a dimension that already passes. Two
  consecutive non-material rounds end the loop. This is what "keep looping"
  should mean in an automated harness: keep going while it is working, not
  forever.
- **Budget.** Name a token or wall-clock ceiling for the benchmark before the
  first round and stop at it, whatever the score.

On exit by either bound, take one of:

- **accept with debt** — record the remaining gap, its dimension, and the score
  delta as a typed known gap; ship
- **revise the bar** — the exemplar was the wrong comparison, or a dimension was
  mis-chosen; fix the contract, do not keep grinding against it
- **escalate to the user** — the gap is real, material, and needs a scope call

Report the round count, the per-round deltas, and which bound ended the loop.
A benchmark that ground several rounds and shipped anyway looks identical to one
that passed on the first unless the count is stated — and "stopped on budget"
and "stopped because it converged" are different results that must not read the
same.

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
5. **drift between independently-built parts of one artifact** (conditional — see
   below)

Skip if all tiers returned clean, **except** for check 5, which has its own
trigger: it fires whenever the artifact was built by multiple agents working on
separate parts, including when every tier came back clean. That exception is the
point of the check — drift is what happens when each part is individually fine.

### Check 5: builder drift

Checks 1-4 look for disagreement between *reviewers*. This one looks for
disagreement between *builders*, which is a different failure and invisible to a
per-part review: split an artifact into pieces, give each its own builder and
critic, and every piece can pass its own bar while the assembled whole reads as
though several people wrote it. The Gauntlet Loop source names this directly —
*"the pieces can become individually good but slightly inconsistent"* — and the
Exemplar Benchmark above makes it more likely, not less, because it rewards each
part for beating its own reference independently.

**Trigger:** more than one builder touched one user-visible artifact. Skip
entirely for single-builder work; there is nothing to reconcile.

**What to look for** — the seams, not the parts:

- **Vocabulary.** The same concept named differently across parts ("tenant" here,
  "resident" there), or the same word meaning different things.
- **Interaction grammar.** Comparable actions behaving differently — one surface
  confirms a destructive action, its sibling does not; one form validates on
  blur, another on submit.
- **Visual and structural rhythm.** Spacing, hierarchy, density, and error
  presentation that shift between parts without a reason a user could infer.
- **Tone.** Copy that changes register mid-artifact — terse in one section,
  chatty in the next.
- **Redundancy.** Two builders independently solving the same sub-problem in
  different places, in different ways.

**Report as a reconciliation list, not findings.** Each item names the parts that
disagree and which one the rest should move toward, because "these three differ"
is not actionable without saying which wins. Pick the version most consistent
with the rest of the artifact, not the one that scored highest in isolation — a
part can win its own benchmark and still be the odd one out.

Severity is normally MEDIUM: drift is a coherence defect, not a correctness one.
Raise to HIGH only where inconsistency changes what a user believes will happen —
a destructive action that confirms in one place and not another is a safety
issue wearing a consistency costume.

**Honest scope note.** This is an extension of an existing reviewer pass, not a
port of the source's distinct smoothing stage, and it has not yet run against a
real multi-builder artifact. If drift turns up that this framing misses, that is
evidence for splitting it into its own pass rather than for adding a sixth bullet
here.

## Post-Review Simplifier

Optional pass before the verification gate.

- Dispatch `code-simplifier:code-simplifier`
- Scope: only files modified in this feature
- Accept changes only if tests still pass afterward
- Skip if total diff churn is small (`$diff.insertions + $diff.deletions < 100`)
