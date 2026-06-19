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

### `pass@k` vs `pass^k` — pick the right aggregation

Once you run k trials per task, a single mean pass-rate hides which
reliability question you're answering. Name it:

- **`pass@k`** — at least **one** of k trials succeeds. A *capability
  ceiling*: "can the agent ever do this?" Rises with k. Use for
  capability evals where retries/sampling are allowed at serving time.
- **`pass^k`** — **all** k trials succeed. A *reliability floor*:
  "can the agent do this every time?" Falls with k. Use for
  regression/reliability gates where one bad run is a user-visible
  failure.

The two move in opposite directions as k grows, so always report which
one and at what k. A change that lifts `pass@k` while dropping `pass^k`
made the agent more capable *and* less reliable — the mean alone hides
that. Match the metric to the serving regime: retries allowed →
`pass@k`; one-shot → `pass^k`.

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

### The harness is a confound

When you compare *models* (not prompts), the harness — system prompt,
tool descriptions, scaffold — is a hidden variable. A fixed harness
tuned on one model can quietly favor it; a long system prompt may sit
better in one model's latent space than another's. So:

- **Hold the harness fixed** across arms for a fair, reproducible
  comparison — but know it likely **under-elicits** some models. A
  fixed harness measures "model + this scaffold," not "model."
- **Per-model harness tuning** (the Cursor approach) maximizes each
  model's elicited performance but destroys comparability and is a
  bottomless time sink. Pick one stance and **report which** — a
  ranking from a fixed neutral harness and a ranking from per-model
  tuning can disagree.
- Harness tuning **does not transfer across versions**: a scaffold
  tuned for model vN often under-serves vN+1 in the same family. Re-eval
  the harness on a model upgrade; don't assume last version's prompt is
  still optimal.

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

### Where the eval signal meets the rest of the test suite

Evals are not the whole test layer — they're the non-deterministic half
of a **two-layer** split. Keep them separate so a stochastic judge
never gates a deterministic assertion:

- **Layer A — deterministic** (Playwright / unit / integration): runs on
  every PR, blocking, fast, binary pass/fail. Owns "did the wiring fire,
  did the route return 200, did the tool get invoked."
- **Layer B — non-deterministic** (the evals in this skill): LLM-judge
  and quality metrics, run on a **nightly** cadence (or a leaner PR
  smoke set), thresholds not binary asserts. Owns "was the answer
  faithful / helpful / correctly-toned."

Tag failures by which layer (and which sub-cause) so triage is cheap —
e.g. context-assembly failures (the wrong inputs reached the model) vs.
execution failures (right inputs, wrong output). A regression gate
(above) is the Layer-B-into-CI bridge; it should run a *smoke subset*,
never the full nightly matrix, so PR latency stays low. The eval owns
the *signal*; the test architecture owns *what blocks the merge*.

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

### Recipe-not-rendered for large inputs

When the eval input itself is large — long context, multi-document
RAG, image-heavy multimodal — storing the rendered prompt per result
row balloons a single sweep into gigabytes. Store the **recipe**
instead:

- Per-row: source identifier (haystack hash / dataset slice), seed,
  insertion indices, sampling parameters — everything needed to
  regenerate the exact input deterministically.
- Provide a separate `reconstruct` step that walks the recipe and
  produces a byte-identical input string for the row. Used for
  debugging individual failures without re-running the whole sweep.
- Keeps artifact size linear in row count, not in prompt size.
- Composes with the version-pinning rule above — recipe + pinned
  dependencies = full reproducibility.

Pattern from
[gkamradt/needle-in-a-haystack v2](https://github.com/gkamradt/needle-in-a-haystack)
result schema.

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

## Eval harness implementation pitfalls

When you build or run a custom eval-loop harness (multi-iteration
benchmark, baseline-vs-candidate comparison), four things bite silently:

- **Directory / field-name contracts are load-bearing.** Aggregators
  routinely glob a strict prefix (e.g. `eval-*/`) — a descriptively
  named dir matches nothing and is silently skipped. Result files often
  need specific summary keys (`pass_rate`, `passed`, `failed`, `total`);
  a missing key blocks aggregate math without a clear error. Verify the
  harness's expected layout before naming dirs or writing results.
- **Baseline drift across iterations is noise, not signal.** When the
  eval prompts themselves change between iterations, the baseline
  pass-rate fluctuates even though the system-under-test is unchanged.
  **Compare baseline-vs-candidate *within* one iteration** — never
  baseline-iter-N vs baseline-iter-M. The within-iteration delta is the
  only honest comparison.
- **Validate a fix by holding prompts fixed and expanding assertions,
  then re-running** — not by editing the questions until it passes (see
  the "tune the system prompt, not the eval QUESTIONS" anti-pattern in
  `references/eval-tool-prior-art.md`).
- **Wall-clock convergence speed is a secondary signal.** A harness that
  converges faster isn't better if its pass-rate semantics shifted;
  read the per-item rationale diff before trusting an aggregate move.

## Failure → dataset → next iteration

The loop closes here. Failure analysis is where the bulk of eval
effort pays off — budget for it, don't rush to re-run.

**First, triage what kind of failure it is** before tagging it as an
agent miss:

- **Infra failure** — timeout, rate limit, pipeline bug, flaky network.
  Rule these out first; they masquerade as agent errors.
- **Grader failure** — the agent was right, the grader was wrong (brittle
  match, mis-calibrated judge, ambiguous task). Fix the grader, not the
  agent. "Failures should seem fair" — if a failure looks unfair on
  inspection, suspect the grader.
- **Task failure** — a genuine agent miss. Only these become regression
  cases.

For genuine misses, **walk the trace to where the failure *originates*,
not where it surfaced** — a wrong answer on the last step often traces
to a bad tool call three steps earlier. As misses accumulate, group them
into a **ranked failure taxonomy** (a named vocabulary of what breaks,
ordered by frequency × severity) so you fix classes of failure, not
one-offs.

For every example that regressed or scored low:

1. Inspect the trace.
2. If it's a new failure mode, tag it and add to coverage tracking.
3. If it's a clear bug, add it to the dataset (with reference if you
   know the right answer).
4. Iterate the prompt / model / architecture and re-run.

Capture a one-line root cause before writing the regression case (bad
retrieval / wrong tool / prompt gap / model limitation / stale context).
The case should encode the cause, not just the input → output pair: name
it after the failure mode, put the diagnosis in metadata, and assert the
specific behavior that broke. A case that only pins the old bad output
regresses silently when the symptom shifts but the cause persists. Every
diagnosed failure becomes one permanent, root-cause-tagged regression
case — that is what keeps the gate honest as the system changes
underneath it.

