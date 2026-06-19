# Phase 5 — Production Evals

Phases 1–4 cover **offline / CI** evals: hold-out datasets, judges,
experiments, regression gates. This phase covers **live traffic**:
sampling judges on production, blocking guardrails, drift detection,
shadow / canary rollout, and alerting.

Different shape: results drive *behavior* (block, retry, page,
rollback), not just dashboards. Costs, latency, and false-positive
budgets are all tighter.

## 1. Online sampling: judges on prod traces

You can't judge every production request. Pick a sampling strategy:

| Strategy             | When to use                                                  |
| -------------------- | ------------------------------------------------------------ |
| Uniform random (1–5%)| Baseline coverage. Cheap. Safe default.                      |
| Stratified           | Sample by user cohort, feature surface, model tier, language. Catches segment regressions a uniform sample misses. |
| Importance-weighted  | Oversample suspicious traces — low task-model confidence, retries, thumbs-down, long latency, schema-validation fail. The signal is denser here. |
| 100% on a small surface | New feature, internal users only, or behind a flag. Cheap when volume is low; switch to sampling as it scales. |

### Per-cohort and per-tenant fairness

A flat 1–5% global sample starves low-volume cohorts and small
tenants of signal while overcharging high-volume ones. Enforce:

- **Per-cohort floor** — every cohort you care about gets at least N
  judged traces per window (e.g., ≥ 30 per language per day).
  Without a floor, a uniform sample on a 1-QPS surface yields ~14
  judged traces/day — useless for detecting regressions.
- **Per-tenant floor and ceiling** — every tenant gets at least M
  judged traces per window; no single tenant consumes more than X%
  of the judge budget. Normalize importance-weights *within* each
  tenant before applying the global sample rate — otherwise one
  noisy tenant with high retry rates starves the others.
- **Per-tenant judge budget tracking** — track judge spend by
  tenant, not just globally.

### Sample-rate sizing by volume

Rough starting points (tune to your actual noise floor):

| Volume        | Strategy                       | Notes |
| ------------- | ------------------------------ | ----- |
| ≥ 100 QPS    | Uniform 1% + importance-weight | ~86k judged/day; cohort floors easily met |
| 10–100 QPS    | Uniform 5% + stratified floors | Cohort floors start to matter |
| 1–10 QPS      | 100% + dedup                   | Sampling at this volume buys nothing |
| < 1 QPS       | 100% on every request          | Volume is the constraint, not cost |

### Implementation

Judge calls happen **async, off the request path**. Stream traces to
a queue (Phoenix, Braintrust, LangSmith, or your own) and run judges
out-of-band.

Operational hardening for the judge pipeline:

- **Idempotency key** per `(trace_id, judge_version)` so at-least-
  once queues don't double-charge or double-count.
- **Dead-letter queue** for judge calls that fail past the retry
  budget, with visibility into top failure modes (auth, timeout,
  rate-limit, content-policy).
- **Backpressure** — when the queue grows past a watermark, lower
  the sample rate before dropping; if you must drop, drop oldest
  with a counter on the metric (silent drops corrupt aggregates).
- **Client-side rate limiter** (token bucket or sliding window) on
  judge-API calls. On 429, buffer with TTL rather than retry-
  immediately; retry storms compound API failures.
- **Circuit breaker** — if judge calls fail > 10% in a 5-min window,
  trip the breaker, fail per the judge-outage policy in § 2, and
  page the owning team.

### Production judge variance

Phase 4 calls for repetitions to estimate judge variance offline.
Production usually runs a single judge call per sampled trace — a
point estimate, not a measurement. Periodically run **2–3
repetitions on a stratified 10% subsample** of judged traces to
estimate live judge variance. If it exceeds the offline noise floor,
raise the sample rate or move to a more reliable judge.

### Cost as an SLO

Set an explicit **judge-spend SLO** relative to task-model spend and
volume (e.g., "judge spend ≤ 10% of task-model spend at steady-state
volume, ≤ 30% during incident sampling spikes"). Tune sampling to
hit the SLO. The 10% number is a common starting point, not folklore
to copy.

### Result schema

Persist per-trace: stable trace ID, task version, judge version,
embedding model+version (if used), score, label, **concise judge
rationale** (not free-form CoT — see Phase 3 § Reasoning capture and
privacy and § 6 below). Same schema as Phase 4 results so offline
and online evals join cleanly.

### Eval-data → training contamination

If your task model is fine-tuned (or will be) on data that overlaps
with production traces, sampling those traces into your golden /
calibration sets contaminates your test set — the model has seen the
"hold-out." Either (a) deduplicate eval data against training data,
(b) sample only from a held-out time window the model has never
trained on, or (c) explicitly flag eval sets as "potentially
contaminated; treat scores as upper bounds."

## 2. Blocking guardrails (real-time)

> **Propensity evals are the offline complement to these rails.** Rails
> block bad *output* on the request path; propensity evals ask whether
> the agent *chooses* to lie / manipulate / collude / seek power under
> incentive, tracked as a trend across model versions and read in
> reasoning traces as well as actions. Critical for autonomous,
> side-effecting agents. See `references/propensity-and-eval-awareness.md`
> — which also covers the **eval-awareness confound** (models behave
> differently when they detect a test; real-world deployment runs are
> the mitigation).

A guardrail is a check that runs **on the request path** and can
block the response. Different from Phase 3 measurement: must be fast
(<200ms typical budget), cheap, and conservative on false positives.

### Categories (NeMo-style rail taxonomy)

The input / output / retrieval / execution rail split is **NeMo
Guardrails' framing** and is useful as a checklist, but it isn't
universal — Guardrails AI organizes by *validator* (per-field
checks), Llama Guard ships a *hazard taxonomy* (S1–S13), OpenAI
Moderation returns categorical scores. Pick whichever organizes
your guards usefully; the categories below are not a standard.

- **Input rails** — jailbreak / prompt injection detection, PII
  redaction before sending to model, topic-out-of-scope check.
- **Output rails** — toxicity, PII leakage, schema validation,
  hallucination / grounding check against retrieved context,
  brand-voice violations.
- **Retrieval rails** — sanity-check retrieved documents before
  generation (relevance threshold, source allowlist).
- **Execution rails** — tool-call validation, argument schema check,
  rate / spend limits.

Common building blocks: **Llama Guard** or **NeMo Content Safety**
(toxicity/harm classification), **Microsoft Presidio** (PII NER),
self-check prompts (cheap LLM-judge as classifier), regex / schema
validation (deterministic, fastest).

### Fail behavior — pick deliberately

Useful as a generic checklist (this is **Guardrails AI's**
on_fail vocabulary specifically; NeMo Guardrails expresses similar
choices via Colang dialog flows, hand-rolled systems usually have
only block/allow/rewrite):

| Behavior   | Effect                                              | When |
| ---------- | --------------------------------------------------- | ---- |
| EXCEPTION  | Halt, raise to caller                                | Cannot recover; user should retry. Rare in production. |
| REFRAIN    | Return null / canned refusal                         | Safety violations: jailbreak, harmful content. |
| FIX        | Deterministic correction (e.g., redact PII)         | Clear repair path; preferred over REASK on cost. |
| FILTER     | Drop offending field from structured output         | Partial output is acceptable. |
| REASK      | Send back to LLM with feedback                       | Schema fix that can't be done deterministically. Costs another inference call. |
| NOOP       | Log only, pass through                               | Telemetry-only during rollout; flip to active later. |

**One defensible default** for shipped guardrails: REFRAIN on
safety, FIX on PII / formatting, NOOP for the first week to measure
false-positive rate, then promote. **Compliance-first contexts
override this** — healthcare, fintech, and regulated PII flows
should not run a PII guard in NOOP in production even briefly.
Conversely, some safety teams prefer FIX (silent rewrite) over
REFRAIN to avoid leaking information about what was blocked.

### Promotion and rollback

Promoting a guard from NOOP to active is a deploy. Before flipping:

1. **Pre-commit rollback triggers** measured live in the first hour
   of active mode:
   - Blocks > 0.1% of traffic → auto-revert to NOOP and page.
   - p95 latency increases by > 50ms → auto-revert.
   - False-positive rate on a held-out benign set exceeds the
     calibration ceiling → auto-revert.
2. **Trial period**: the guard is "active-on-probation" for 24 hours
   after promotion. Keeping it active beyond 24h requires manual
   approval from the eval owner.
3. **Version the guardrail config** (active rails, fail behaviors,
   thresholds, ordering) as a single artifact committed to git.
   Tag each production trace with the guardrail config version so a
   behavior change can be attributed to a rule change vs. a model
   change. A config change is a deploy and gets the same review as
   a model swap.

### Calibration is non-negotiable

The guardrail calibration regime is **not** the same as a
measurement judge — see Phase 3 § "Calibration regime: measurement
vs guardrail." Key points:

- Report **precision and recall on the imbalanced production
  population**, not just κ. At 1% true-positive prevalence, κ
  alone hides the false-positive rate.
- Calibration set must include **both adversarial and benign
  examples in realistic proportions**.
- A guardrail that blocks 0.5% of harmless requests is unshippable
  at scale even if its true-positive rate is 99%.

### Judge outage degradation

When the judge / classifier behind a guardrail is unavailable, the
guard either fails-open (allow) or fails-closed (block). Pick per
rail class:

- **Safety-critical rails** (jailbreak, PII leakage, harmful
  content) → **fail-closed**: REFRAIN until the judge recovers.
  Letting harmful output through during an outage is worse than
  blocking benign requests briefly.
- **Quality rails** (faithfulness, tone, brand voice) →
  **fail-open**: NOOP and log; alert the owning team. Blocking
  legitimate traffic on a quality criterion isn't worth the
  outage.
- **Circuit-breaker behavior** (see § 1 above) trips into the
  fallback mode on > 10% failure in a 5-min window. Replay
  dead-lettered judge calls when the breaker closes; don't
  silently drop unjudged traces from your aggregates.

### Latency

Both Guardrails AI and NeMo note that complex self-check prompts
add real latency. **Budget in p95 / p99 envelopes**, not typical
times — cold-start, queue depth, and rate-limit retries dominate
the tail and a "typical 200ms" check can spike to seconds. The
numbers below are starting envelopes; measure in your target
runtime before locking SLOs:

- Regex / schema: p95 < 5ms
- Small classifier (Llama Guard 7B, Presidio): p95 50–200ms
- LLM self-check (cheap model): p95 200–800ms
- Full LLM-judge: avoid on the request path

## 3. Drift detection

Drift = the world changed; your golden dataset and your past
calibration are now lying to you. Watch three layers:

### Input drift
User-input distribution shifts. New topics, new languages, new
length distribution, new device cohort.

- **Categorical** (intents, languages, surfaces): **PSI**
  (Population Stability Index) is a useful workhorse. The common
  thresholds (< 0.1 stable, 0.1–0.25 moderate, > 0.25 significant)
  come from credit-risk scorecard literature (Siddiqi) where they
  apply to **binned PD scores** at monthly cadence. Treat them as
  starting priors and **calibrate per-feature against your own
  stable baseline**, not as universal cutoffs. PSI is unstable when
  bins have < 5 samples — enforce a minimum bin count before
  computing, especially on high-cardinality categoricals or
  sliced-by-cohort views. For privacy-sensitive features, consider
  adding Laplace noise to bin counts before PSI computation.
- **Numeric** (latency, tokens-in, PCA components of embeddings if
  you've reduced dimensionality): **Wasserstein distance** or **KL
  divergence**.
- **Embeddings / free-text**: distance to a reference centroid is a
  fast first check but **under-detects multimodal or high-dimensional
  drift** — the centroid hides bimodal shifts and is outlier-
  sensitive. Prefer a **distributional test** (MMD, energy distance,
  or comparison of pairwise-distance distributions) for anything
  load-bearing. Derived text descriptors (length, sentiment,
  language) drifted independently are also worth tracking.

### Output drift
Same inputs, different outputs — *if and only if* you can isolate
the SUT (system under test). For RAG, agent, or tool-using systems,
"same input" doesn't imply same retrieval context or same tool
behavior — index updates and tool changes drive output drift too.

- Lock a small "canary set" of 50–100 fixed prompts plus a **frozen
  retrieval / tool context** (snapshotted documents, mocked tool
  responses). Re-run nightly. A jump on the canary set without a
  release is then attributable to a vendor model change; without
  isolation, you can't distinguish vendor drift from index drift.
- **Judge drift** belongs here too. Vendor updates to the *judge*
  model are a top cause of mysterious score moves. Track a small
  canary set scored by the judge against frozen labels — drift on
  this set without a judge-version change means the vendor updated
  the judge under you. Treat with the same severity as task-model
  drift.

### Score drift
Aggregate metric moving without a deploy. Usually input drift in
disguise; sometimes judge model drift (use the canary set above to
disambiguate).

### Per-tenant drift

A regression hitting one enterprise customer disappears in
aggregate PSI. Slice drift by tenant for any tenant above a
material-volume threshold; per-tenant alerts are noisier but catch
the kind of single-customer regressions a global view masks.

### Windowing

Pick one **reference window** (last known-good period, e.g., the week
before your most recent ship) and compare a **current window** (last
24h, last 7d). Don't compare to a single point — variance dwarfs
signal.

### Default thresholds

These are starting priors — calibrate to your own noise floor:

- Per-feature PSI > 0.25 → warn; > 0.5 → page (per-feature, not
  global).
- **Weight features by criticality** when aggregating. A 30%
  drifted-features-count over a flat list pages just as loud on a
  low-importance telemetry field as on a primary input surface;
  weight key inputs higher or alert per-feature-class instead of
  raw counts. Evidently's 50% drifted-features default is a
  reasonable starting point for tabular ML; LLM apps usually have
  fewer features and need lower aggregate cutoffs.
- Score drop > 2× the offline noise floor over a rolling window →
  page.

## 4. Shadow & canary rollout

Two complementary patterns for changing prompts / models in
production.

### Shadow (mirror) traffic

The new version receives a copy of production input but its output
is **not served to users** — only logged for comparison.

- Zero user risk.
- Eats inference cost (you're paying for both).
- Best for confirming distribution-level metrics (mean score,
  latency, cost) on real traffic before sending users.

**What shadow can't catch:**

- **User-side effects** (downstream clicks, retries, abandonment).
  Shadow validates the model, not the experience.
- **Stateful / multi-turn divergence**: the shadow's output doesn't
  feed into the next turn's context, so any failure mode that
  requires a corrupted state from a prior turn is invisible.
- **Tool side-effect divergence**: you usually can't shadow writes,
  payments, or external API mutations. The shadow's tool calls
  either no-op (no signal on side-effect behavior) or duplicate
  (unacceptable in prod). Code paths that depend on tool *response
  shape*, not side effects, are observable; code paths that depend
  on tool *state changes* aren't.

Run for at least one full traffic cycle (one weekday + one weekend,
typically).

### Shadow regression policy

Shadow without a stop condition is passive monitoring, not a gate.
Pre-commit:

- Shadow primary metric drops > 3 pts vs production with p < 0.05
  (paired test on the same examples — see Phase 4 § Interpreting
  deltas) → **fail the shadow run; do not proceed to canary**.
- Shadow guardrail metrics (p95 latency, cost / request, refusal
  rate) exceed production by > 10% → fail.
- On pass: document the observed deltas and **tighten the canary
  halt criteria by the observed variance** before ramping.
- A failed shadow run is a successful detection, not a crisis — it
  saved an incident.

### Canary (% rollout)

Real users get the new version. Start small (1%), expand stepwise
(1% → 5% → 25% → 50% → 100%) with a hold between each step.

#### Cold start: no production baseline

The canary procedure assumes a baseline metric from the current
production version. For a brand-new feature, there isn't one. Two
options:

- **Dual-control period** (preferred when an "old" version exists):
  serve the same (old) version on both control and "canary" arms
  for 24 hours. Establish baseline metrics and observed variance
  from this period before the new version touches either arm.
- **Offline-baseline fallback** (greenfield, no old version):
  use the offline eval score as the baseline and explicitly **flag
  it as not traffic-calibrated**. Set halt criteria 2× wider than
  for a mature feature; the first canary step (1%) must run for at
  least one full traffic cycle before any ramp decision.

#### Pre-ramp definitions

Define **before** ramping:

1. **Primary metric** — what should improve (e.g., faithfulness rate).
2. **Guardrail metrics** — must not regress (latency p95, cost per
   request, refusal rate, schema-validation rate, thumbs-down rate).
   Any guardrail violation halts the ramp.
3. **Halt criteria** — quantified, e.g., "p95 latency +20% over
   baseline for 15 min, or primary metric −3 pts vs control with
   p < 0.05, halts and auto-rolls back."
4. **Sample size per step** — back-of-envelope for a two-proportion
   test at α = 0.05, power = 0.8:

   ```
   n_per_arm ≈ 2 · p̄(1 − p̄) · (z_α/2 + z_β)² / Δ²
             ≈ 2 · p̄(1 − p̄) · 7.85 / Δ²
   ```

   For `p̄ ≈ 0.5`, `Δ = 0.02` (2 percentage points) → **n ≈ 9,800
   per arm**, not 1,000. At 1% canary on 10k requests/day that's
   nearly 200 days to detect a 2pt shift — meaning a 1% canary can't
   detect small effects in any reasonable time. For **rare events**
   (refusal rate 1%, jailbreak rate < 0.1%), the required N grows
   by another 10–100×. The takeaway is structural: **most LLM
   canaries are underpowered for small effects** — be honest about
   what each step can and can't detect, and don't ramp on noise.
   Tools like `statsmodels`'s `proportion_effectsize` /
   `tt_ind_solve_power` make this a one-liner; use them rather than
   napkin math at decision time.

### Stat-sig for LLM comparisons

For binary judge rates: two-proportion z-test or bootstrap CI on
the rate difference. For continuous scores: Welch's t on means +
variance check (LLM-judge variance is high; don't assume equal
variance).

When the comparison runs on the **same examples** (shadow mode,
offline replay) use **paired** analyses — paired bootstrap or
paired t — not independent-sample tests. Paired analyses have
substantially more power; see Phase 4 § Interpreting deltas. Live
canary arms scored on disjoint traffic remain unpaired.

Watch for **Simpson's paradox** — a win in aggregate that's a loss
in every cohort. Report per-cohort deltas alongside the aggregate.

## 5. Alerting (without alert fatigue)

Apply standard SRE doctrine — adapted — to eval signals.

### Multi-window confirmation

A single threshold ("score < 0.85 → page") fires on noise. Use
two windows (short fast-burn + long slow-burn) and require **both**
to exceed thresholds before paging:

```
PAGE if (1h score drop > 5pts) AND (6h score drop > 2pts)
WARN if (6h score drop > 2pts) AND (24h score drop > 1pt)
```

This is **structurally similar to but not equivalent to Google SRE's
multi-window burn-rate alerts**. SRE burn-rate is defined against
an explicit **error budget** (fraction of SLO consumed per unit
time, where "error" is a binary success/fail event with a defined
budget). Eval scores are soft, continuous metrics with no inherent
budget, so the burn-rate algebra (consumption rate, time-to-exhaust)
doesn't directly apply. What survives is **multi-window confirmation
to suppress noise**. If you want true burn-rate semantics on eval
signals, first define an explicit eval-score SLO (e.g., "≥ 95% of
hourly faithfulness scores are above 0.85") and an error budget
against it; then SRE math applies.

### Separate primary and guardrail alerts

- **Primary metric** alerts go to the owning team, not on-call.
  Quality regressions usually aren't pageable in the middle of the
  night.
- **Guardrail violations** (safety, PII leak rate, refusal spike,
  latency / cost blowout) can be pageable.

### Runbooks beat thresholds

Every alert needs a runbook line: "if this fires, the first three
things to check are X, Y, Z." Without it, the alert is noise the
moment the author leaves the team.

### Tune to your noise floor

If an alert fires more than ~once a week without a real incident,
raise the threshold or add a condition. The cost of a missed
regression is almost always lower than the cost of an ignored alert.

## 6. Privacy & access control

Eval datasets sourced from production traces are a privacy surface.
Treat them as such.

### Retention and deletion

- **Raw traces** (with potentially identifying inputs and outputs)
  → retained ≤ 90 days unless explicitly reviewed and de-identified.
- **After 90 days** → keep only anonymized aggregate metrics
  (scores, failure-mode rates, latency distributions). No raw
  inputs or outputs.
- **Data subject deletion requests (DSR / "right to erasure")** →
  purge all traces from the requesting user within 72 hours. The
  eval dataset is downstream of production and must be included in
  the deletion fan-out, not forgotten.
- **Redact at ingestion**, not on read — use Microsoft Presidio or
  equivalent to strip PII as the trace enters the eval queue.
  Persisted judge reasoning is especially load-bearing here, since
  judges often quote `{source}` and `{response}` verbatim (see
  Phase 3 § Reasoning capture and privacy).

### Access control

- **Aggregate metrics** (mean scores, CIs, per-cohort breakdowns)
  → low sensitivity. Share with the eval owning team and broader
  org as needed.
- **Per-example results** (input, output, judge reasoning) → high
  sensitivity. Encrypt at rest, role-gate to eval owner + team
  lead, audit-log reads.
- **Registry**: include the eval dataset and result store in the
  system's data-processing register / record of processing
  activities (ROPA). The eval pipeline is a data processor; it
  needs the same governance as the production model it evaluates.

### Cost observability

Track judge spend as a separate cost line and against the
judge-spend SLO from § 1. When spend exceeds the SLO ceiling, the
sampling strategy is the fix (lower rate, cheaper judge, smarter
weighting), not raising the budget reflexively.

## What this phase still does *not* cover

- **Implicit user signals** (thumbs, regenerate, dwell) as eval
  data — worth wiring as inputs to your importance-weighted sampler
  above, but the methodology of weighting them is a separate topic.
- **Judge gaming / Goodhart** — when a judge becomes a reward
  signal (RLHF, automated prompt optimization), the task model
  learns to exploit it. Periodic re-calibration against humans, and
  a held-out "judge the judge" set, are the defenses. See
  `references/judge-calibration.md`.
