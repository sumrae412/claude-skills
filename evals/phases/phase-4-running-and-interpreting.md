# Phase 4 — Running & Interpreting

## Experiment shape

An experiment is `(dataset, task_fn, [evaluators], repetitions) →
results`.

- `task_fn(input) -> output` wraps the system under test. Keep it thin
  — just the call you're evaluating, no extra logic.
- Run all evaluators on every example.
- Persist per-example results with a stable example ID, dataset
  version, task version (prompt hash + model), and judge version.

The schema must support per-example regression queries — that's
what makes a result reproducible vs. just a number.

## Concurrency & batching

Naive serial runs make eval slow enough that people skip it. Use a
bounded concurrent executor:

- Cap concurrency to respect provider rate limits.
- Retry on transient errors (429, 5xx) with exponential backoff.
- Fail loudly on persistent errors per example — don't silently fill
  in `null` scores.
- Phoenix / Braintrust / LangSmith expose this as a built-in executor;
  in a hand-rolled harness use `asyncio.Semaphore` or equivalent.

Tie runtime targets to **CI budget fraction**, not absolute seconds —
e.g., "smoke must not consume more than 20% of PR-blocking CI time;
full set runs nightly with no wall-clock cap." Absolute caps (60s / 10
min) are useful as a starting point but unattainable for large models
under strict rate limits and too lax for tiny setups. Tune batch size
and concurrency to provider limits.

## Repetitions

LLM outputs are non-deterministic. A single-run score is a point
estimate.

- **Stochastic task model** (temperature > 0): run each example 3–5
  times. Report mean and stddev.
- **Stochastic judge** (always assume yes for LLM-judge): even with a
  deterministic task, repeat the judge ≥ 3 times.
- For binary judges, repetitions also let you compute a confidence
  on the rate (Wilson or bootstrap CI).

**Pre-commit the repetition count before the run, applied uniformly
to every example.** Adding repetitions post-hoc on "borderline"
examples is p-hacking — you can re-run until any case passes. The
right interventions for borderline cases are tighter judge prompts,
better calibration, or a more capable judge — not extra rolls of the
dice.

Skip repetitions only when both task and judge are deterministic
(code-based eval on temperature-0 task).

## Interpreting deltas

Before celebrating a score increase:

1. **Is it above the noise floor?** Compute a 95% CI on the **paired
   difference** between arms (paired bootstrap, paired t-test, or a
   permutation test). When the two arms score the *same* examples —
   the common case offline and in shadow mode — paired analyses have
   substantially more power than treating arms independently and
   comparing two separate CIs. The decision rule is "does the CI of
   the paired difference exclude zero?", not "do the per-arm CIs
   overlap?" (CI overlap is overconservative — they can overlap while
   the paired difference is highly significant). Use independent
   tests only when arms see *different* examples (e.g., live canary
   on disjoint traffic).
2. **Is the dataset unchanged?** Compare against the *baseline rerun
   on the current dataset*, not against a score from an older
   dataset version.
3. **Did any example flip the other way?** Look at per-example
   diffs, not just the mean. A 0.85 → 0.87 mean with 8 regressions
   and 10 improvements is a different story than a 0.85 → 0.87 with
   2 regressions and 4 improvements.
4. **Failure-mode breakdown.** Report scores split by
   `metadata.failure_mode`. A win on average that's actually a loss
   on the hardest cohort is not a win.

### Noise floor is dynamic

Recompute the noise floor whenever the judge model, task model, or
dataset changes significantly. To estimate: run the same experiment
twice on the same dataset with the same task and judge — the
difference between runs is your floor. If the floor exceeds 50% of
the expected effect size, the experiment is underpowered; raise N or
repetitions before drawing conclusions.

## Regression gate in CI

Pattern:

```
on PR:
  run smoke set (20–50 examples) against the PR's prompt/model
  compare to main's score on the same set
  fail if regression > X pts on any tracked metric
  fail if any failure-mode cohort drops > Y pts
  post per-example diff as a PR comment
```

Tune `X` and `Y` to your noise floor. If your CI gate fires on noise,
people start ignoring it.

Cache evaluator results by `(example_id, dataset_version,
task_version, judge_version)` so re-runs on unchanged code are free.
**Include `dataset_version` (or a content hash of the example) in the
key** — if a reference output is edited while `example_id` stays
stable, a key without `dataset_version` silently serves stale scores
and the gate corrupts.

The smoke set's regression threshold should be derived from the same
noise floor as the production canary's halt criteria (see
`phases/phase-5-production-evals.md` § 4). Typical mapping: CI uses
**2× noise floor** (small sample, want tight gate); canary uses **3×
noise floor** (live variance is larger). When CI passes but canary
halts (or vice versa), investigate — don't dismiss as a fluke.

## Reporting

A complete eval result has:

- dataset version (hash or ID)
- task version (prompt hash + model + params)
- evaluator versions (judge prompt hash + judge model, code eval
  commit, **embedding model + version** for any embedding-based
  evaluator — embedding service updates silently shift scores even
  if `code eval commit` is unchanged)
- per-example results (id, output, score, label, judge reasoning)
- aggregate metrics with CIs (and the **paired** CI when comparing
  two versions on the same dataset)
- failure-mode breakdown
- calibration summary for any LLM-judge

Without those, the result isn't reproducible and shouldn't drive
decisions.

### Access control

Eval results are a privacy surface:

- **Aggregate metrics** (mean scores, CIs, failure-mode rates) are
  low-sensitivity. Share freely.
- **Per-example results** (input, output, judge reasoning) are
  high-sensitivity — judge reasoning often quotes user inputs
  verbatim. Encrypt at rest, role-gate (eval owner + team lead),
  retain ≤90 days unless explicitly reviewed and de-identified.
- Include the eval dataset and result store in the system's
  data-processing register. See `phases/phase-5-production-evals.md`
  § 6 for the privacy surface in production sampling.

## Failure → dataset → next iteration

The loop closes here. For every example that regressed or scored low:

1. Inspect the trace.
2. If it's a new failure mode, tag it and add to coverage tracking.
3. If it's a clear bug, add it to the dataset (with reference if you
   know the right answer).
4. Iterate the prompt / model / architecture and re-run.

