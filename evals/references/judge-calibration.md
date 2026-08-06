# Judge Calibration

Calibration is not a one-time check. After the initial κ ≥ 0.6 gate
(see `phases/phase-3-evaluators.md`), judges drift as the dataset
shifts, the task model changes, or the judge prompt evolves. This
reference covers ongoing tuning.

Generalized from `debate-team/references/critic-calibration.md`,
which applies the Anthropic Cookbook's
[Building Evals](https://github.com/anthropics/claude-cookbooks/blob/main/misc/building_evals.ipynb)
and
[Tool Evaluation](https://github.com/anthropics/claude-cookbooks/blob/main/tool_use/tool_evaluation.ipynb)
patterns to reviewer agents. The cadence and bias-detection
heuristics generalize to any LLM-as-judge.

## The eval signal is already in your loop

If a human (or trusted senior judge) is overriding the LLM-judge's
verdict during review, those overrides *are* your eval signal. Track:

```
Per judge, per criterion, track over time:
  - ADOPT rate:  % of judge's "pass" verdicts the human accepts
  - REJECT rate: % of judge's verdicts overridden (false positive
                 or false negative)
  - DEFER rate:  % where human couldn't decide quickly — judge
                 surfaced something ambiguous

Healthy judge:  >60% ADOPT, <25% REJECT
Noisy judge:    <40% ADOPT, >40% REJECT  → tune the prompt
Silent judge:   rarely produces interesting verdicts → may not add
                value, consider removing
```

No separate eval infrastructure required — the override log is the
ground truth.

## When to tune

Aggregate over ≥5 runs, then act on the dominant pattern:

| Signal                                                | Action |
| ----------------------------------------------------- | ------ |
| REJECT rate > 40% over 5+ runs                        | Judge is generating noise. Review the prompt for over-broad patterns. Add `Only flag if you are >80% confident this is a real issue.` |
| Same false-positive type recurring                    | Add an explicit exclusion to the judge prompt: `Do NOT flag [pattern] — this is acceptable in this context.` |
| Missing real issues caught later                      | Judge is under-sensitive. Add the missed pattern to the prompt's checklist with a concrete example. |
| ADOPT rate < 30%                                      | Demote the judge to conditional use (skip on easy cases) or replace with a more targeted prompt. |
| REJECTed verdicts cluster around aesthetic adjectives | See **gold-like bias** below. |

## Gold-like bias (the calibration trap)

LLM-judges trained on RLHF data have a learned preference for outputs
that *look* clean, concise, canonical, well-organized — independent of
whether they're correct or complete. Watch for it.

**Symptom:** when you read the REJECTed judge verdicts, the
explanations cluster around words like *"too complex"*, *"not
minimal"*, *"over-engineered"*, *"unclean"*, *"verbose"*, *"could be
simpler"* — without citing a concrete risk (correctness,
maintainability, latency, cost, user impact).

**Cause:** the judge is scoring aesthetics, not the criterion you
defined.

**Fix:** tune the prompt so any complexity/minimality finding must
cite concrete downstream risk. Pattern:

```
Do NOT flag something as "too complex", "verbose", or "over-engineered"
unless you can name the specific risk it creates: a correctness bug, a
maintainability cost, a latency/cost regression, or a user-visible
problem. Style preferences alone are not findings.
```

Recheck calibration after the prompt change.

## Calibration cadence

Don't tune after every run. Pattern:

1. Run the eval for **≥5 cycles** with the current judge.
2. Compute ADOPT / REJECT / DEFER rates per judge per criterion.
3. Identify the noisiest judge (highest REJECT rate above the
   threshold).
4. Read its last 5 REJECTed verdicts. What pattern do they share?
5. Check whether the cluster reflects gold-like bias.
6. Make **ONE** prompt change.
7. Run ≥3 cycles with the new prompt to confirm improvement before
   tuning anything else.


## Grading method priority

When automating the ADOPT/REJECT signal itself (i.e., grading the
judge):

1. **Code-based grading (preferred)** — If the judge's finding
   references a specific code pattern, grep for it. If the pattern
   doesn't exist in the artifact, it's a false positive. Zero cost.
2. **Trusted-model grading** — A stronger model (or a model with
   different training) checks the weaker judge's verdicts. Useful
   when human bandwidth is limited.
3. **Human grading (gold standard)** — When a human overrides the
   judge, capture it. This is the highest-quality signal and the only
   one that catches *structural* judge failures (wrong criterion
   entirely).

## Speculative-finding rule

Judges sometimes produce findings of the form *"there may be a
second issue elsewhere"* without naming it concretely. **DEFER
these by default.** Speculative findings adopted preemptively tend
to mask the real failure mode when it eventually surfaces — and
the real failure usually surfaces within the next cycle anyway,
with a concrete shape you can act on.

A finding must name what's wrong and where.

## When calibration fails

When agreement is below your target (κ < 0.6 for measurement
judges, or precision/recall below the guardrail thresholds from
Phase 3), don't reflexively iterate the judge prompt. Walk this
checklist first — the cause is often not the prompt:

1. **Check human-rater consistency.** Have two humans label the
   same 10 examples and compute inter-rater agreement. If humans
   disagree with each other, the **rubric is ambiguous**; fix the
   rubric before touching the judge. Iterating the judge prompt
   against an ambiguous rubric is shadow-boxing.
2. **Check label imbalance.** If 90% of calibration examples are
   one class, κ is inflated by chance agreement (the kappa
   paradox). Compute **PABAK, class-balanced F1, or precision and
   recall** in addition to κ. Rebalance the calibration set —
   stratified sampling, oversampling the minority class — before
   reading any agreement statistic on imbalanced data.
3. **Check judge model capability.** If a 7B-class judge is being
   asked to score nuanced faithfulness or multi-hop reasoning, the
   model may be structurally under-capable. Try a stronger judge
   model on the same prompt before iterating prompt wording — if
   agreement jumps, the prompt was fine; the model was the bottleneck.
4. **Check for gold-like bias.** Read the judge's reasoning on a
   handful of false positives. If the cited reasons cluster around
   aesthetic adjectives ("too complex", "verbose", "over-engineered",
   "could be simpler") without naming concrete downstream risk,
   apply the gold-like-bias fix above.

Treat a κ < 0.6 result as a diagnostic, not a dead end. The
diagnosis usually points at one of the four above; only after
ruling them out is "iterate the judge prompt" the right move.

## Calibration edge cases

A few situations where the standard procedure misleads:

- **Zero-variance human labels** — if every human-labeled example
  is the same class (e.g., all "faithful"), κ is undefined or
  near-zero by construction. Report **raw agreement** instead and
  flag that the calibration set may not cover the score range.
  Add examples from the missing class before drawing conclusions.
- **Systematic disagreement on a critical failure mode** — judge
  and human may agree on 90% of examples while disagreeing
  systematically on the 10% that matters most (e.g., always missing
  a specific jailbreak shape). Compute **per-failure-mode κ** in
  addition to overall κ; if a judge passes overall but fails on a
  critical mode, it's not ready.
- **Rare failure modes** — for failure modes that appear in < 10%
  of traffic, N=30 may have only a handful of positive examples.
  Accept **N ≥ 15** as a working minimum for rare modes but
  **report a confidence interval on κ** (bootstrap or
  asymptotic) — a point estimate at small N is meaningless.

## Meta-evaluation: can you trust the labels?

The sections above tune a judge from aggregate signal over many runs.
This section is the other half: building a labeled benchmark and
measuring, per item, whether the judge's labels can be trusted at all.
An evaluator produces a label; that label is not automatically correct.

Source: DeepLearning.ai evals course, Module 3. The evaluator-selection
and rubric-authoring half of the same module is in
`evaluator-selection-and-rubrics.md`.

### Benchmark construction

Collect traces the agent has already produced and have human reviewers
label them against the rubric. Two requirements the standard
`phases/phase-3-evaluators.md` § Calibration procedure does not cover:

- **Stratify the split.** If the failure class is rare, a random split
  puts almost no failing examples in the test half. Stratify so both
  classes appear in both halves in proportion.
- **Hold out the blind test set *before* tuning anything.** Split the
  labeled examples before you make a single change. The held-out set is
  for final measurement only. Tune on it and the resulting agreement
  number is optimistic and untrustworthy.

In production, split three ways — **train / validation / final test**.
The validation set absorbs every iteration; the final test set stays
clean for one measurement at the end. A two-way split is enough for a
first pass, but the moment you start iterating it collapses into
tuning-on-test.

### Read precision and recall on the failure class

Two statistics, and the failure class is where you read both.

**`classification_report`-style precision / recall / F1 per class.**
Report the failure class (`non_compliant`, `fail`, `unsafe`), not
overall accuracy — accuracy on an imbalanced set is satisfied by a judge
that predicts the majority class and catches nothing.

- **Recall on the failure class** — of the traces that actually violated
  the criterion, what fraction did the judge catch? Low recall means it
  is missing real violations.
- **Precision on the failure class** — of the traces the judge flagged,
  what fraction actually were violations? Low precision means false
  alarms.

**Cohen's κ** corrects agreement for chance: two raters assigning labels
at random still agree some of the time, and κ removes that baseline.
Statistic selection by label type (plain / weighted / PABAK) is in
`phases/phase-3-evaluators.md` § Calibration.

**κ measures agreement, not accuracy.** The judge and the reviewer can
agree and both be wrong — if both misread the rubric the same way, κ is
high and the labels are still incorrect. Read κ alongside precision,
recall, and the specific traces where the labels disagree. No single
number tells the whole story, and there is no κ threshold that
substitutes for reading the disagreements.

### Diagnosing a disagreement: three sources, not one

When the judge and the human label a trace differently, the instinct is
to blame the judge. That instinct is wrong often enough to be a rule.
There are three possible sources:

1. **Judge error** — the judge applied the rubric inconsistently.
2. **Rubric gap** — a criterion is ambiguous. Both the judge and the
   reviewer applied the rubric as written; the rubric does not clearly
   cover this case.
3. **Bad reference label** — the reviewer made a mistake, applied the
   rubric differently than intended, or missed a detail in the trace.

**Apply the rubric to the trace yourself.** Read the trace, read the
criterion, decide what the label should be, *then* attribute the
disagreement to one of the three. Change one thing, then measure.

This is per-item and complements § "When calibration fails" above, which
diagnoses a *low aggregate* agreement number (ambiguous rubric,
imbalanced set, under-capable judge model, gold-like bias). Run this one
on the individual disagreements; run that one on the run.

**Human labels are not automatically ground truth.** Reviewers miss
details, interpret criteria differently, and make mistakes. The goal is
not to reproduce any individual reviewer's first decisions — it is to
align the judge with labels that have been carefully reviewed against a
clear rubric. That review is what makes a benchmark worth trusting, and
a benchmark needs a workflow for *correcting* a bad reference label and
recomputing the metrics, not just for collecting labels.

### Confidence bias

The rubric is not the only source of judge error — the response itself
can fool the judge. The most dangerous failures sound calm, detailed,
and helpful: an agent invents a return process and presents it with
complete confidence, and the judge mistakes polished delivery for a
correct answer. That is **confidence bias**.

When inspecting disagreements, weight the convincing answers that still
break the criterion — a fluent wrong answer is much harder to catch than
an obviously wrong one, and it is exactly the shape that reaches
production.

Sibling to **gold-like bias** above, and worth keeping distinct:
gold-like bias is the judge preferring outputs that *look* clean on
style grounds; confidence bias is the judge reading fluency as
correctness on a substantive criterion.

### After you change something

- Test the revised evaluator on **new labeled examples you did not use
  to tune it** — the validation set, not the held-out final test set.
- Do not re-run on the blind test set to check whether a fix worked.
  That is test-set leakage, and it silently converts your final number
  into a training number.
- Change one thing per cycle (same discipline as § Calibration cadence
  above), so the measured move is attributable.

### Terminology that keeps this precise

- **"agreement"**, not "consistent," for the judge-vs-human statistic —
  "consistent" describes a judge reliably applying rules; agreement is
  the inter-rater property κ actually measures.
- **"validated against carefully reviewed human labels"**, not
  "calibrated," when the claim is about label quality rather than the
  tuning procedure.
- **"judge error, rubric gap, or bad reference label"** — never "rubric
  bugs, not judge bugs," which forecloses two of the three diagnoses.
- **"test on new labeled examples you did not use to tune"**, not
  "re-run on the blind set."

## Calibration set drift

The calibration set itself becomes stale. Human labels collected
six months ago against a task model that's since been upgraded may
no longer represent the current failure surface — a judge that
*was* calibrated may now be silently mis-calibrated.

Refresh cadence:

- **Every 6 months**, or whenever the task model has a major
  upgrade, **or whenever the judge prompt or model changes**.
- Periodically (e.g., monthly) sample 10 new examples from current
  production traffic and have a human label them. Compare the
  **label distribution** to the existing calibration set — a
  significant shift (e.g., more "unfaithful" examples than the
  calibration set contained) means the set is stale.
- If the judge's ADOPT rate drops below 40% on the new examples,
  re-collect 30 fresh examples and re-calibrate.

The calibration set is a living artifact. Budget for the labeling
work; don't treat it as a one-time investment.
