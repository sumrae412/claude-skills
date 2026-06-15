---
name: "evals"
description: "Use when designing or running evals for an LLM feature — offline (golden datasets, LLM-as-judge / code-based evaluators, experiments comparing prompt/model/architecture versions, regression gates) or online (production sampling, blocking guardrails, drift detection, shadow / canary rollout, eval-based alerting, including the eval signals that gate rollout decisions). Triggers: 'design evals', 'build a golden dataset', 'LLM-as-judge', 'compare prompt versions', 'eval harness', 'regression gate for prompts', 'production evals', 'drift detection for LLM', 'shadow / canary an LLM change', 'block PII / jailbreak / toxicity', 'guardrails for LLM output'. NOT for prompt-registry mechanics or organization-wide governance policy (use prompt-governance — that skill handles approval workflows and registry plumbing; this skill handles the eval signals those policies depend on). NOT for empirical variant promotion across explorers/architects/reviewers (use prompt-optimization). NOT for tuning the wording of a single judge prompt during calibration (use prompt-optimizer — judge prompts are prompts). NOT for RAG retrieval design (use rag-architect)."
---

# Evals

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls.
- If the task is tiny, apply the relevant pattern inline instead of
  loading a phase.

## Overview

Eval toolkit for LLM features: pick what to measure, build a dataset,
write evaluators, run experiments, interpret results, gate regressions.

This file is a router. Do not keep the whole eval catalog resident.

Inspired by the dataset / evaluator / experiment / executor model used
by platforms like Arize Phoenix, but framework-agnostic — the patterns
work whether you run evals in Phoenix, Braintrust, LangSmith, or a
hand-rolled harness.

## When to Use

- Standing up evals for a new LLM feature
- Building or expanding a golden dataset from production traces
- Writing LLM-as-judge or code-based evaluators
- Comparing prompts, models, or architectures with a controlled
  experiment
- Diagnosing why scores moved (variance vs. real regression)
- Wiring an eval into CI as a regression gate

## Load Strategy

1. Identify the current gap: design, dataset, evaluator, run /
   interpretation, or production.
2. Load only the matching phase file from `phases/`.
3. Do not preload the others.

## Phase Map

1. `phases/phase-1-design.md` — what to measure, metric typing,
   success criteria
2. `phases/phase-2-datasets.md` — golden sets, sourcing from traces,
   splits, versioning
3. `phases/phase-3-evaluators.md` — LLM-as-judge prompts, code-based
   checks, calibration
4. `phases/phase-4-running-and-interpreting.md` — batching,
   repetitions, variance, regression gates
5. `phases/phase-5-production-evals.md` — online sampling, blocking
   guardrails, drift, shadow / canary rollout, alerting

## Session Rules

- Define the failure mode before defining the metric. "Quality" is not
  a metric.
- Code-based evaluators beat LLM-judge evaluators whenever ground
  truth exists. Reach for LLM-judge only when the output is open-ended.
- Calibrate every LLM-judge against ≥ 30 human-labeled examples
  for an initial smoke check; production-gating judges need larger
  balanced sets with reported CIs. Report agreement.
- One judge, one criterion. Don't ask a judge to score "helpfulness
  and accuracy and tone" in one call.
- Repetitions matter — LLM scores have variance. A single run is a
  point estimate, not a result. **Pre-commit the repetition count;**
  don't add reps post-hoc on "borderline" examples.
- Score deltas under noise floor are not improvements.
- When comparing two versions on the same examples, use **paired**
  analyses, not independent-sample CIs.
- Every failed example is dataset material.
- **For any evals-infra COST reduction PR, run a cost-audit subagent BEFORE writing code — produces per-suite $ attribution (`suite × N_calls × model × tokens × $/MTok`) and identifies the dominant driver.** Pin Anthropic pricing in the subagent prompt to avoid web-fetch drift. Without the audit, the natural failure mode is to optimize the visible cost (judge calls) when the real driver is the silent one (uncached SUT prefix resends). Validated 2026-05-30 on [courierflow_beta PR #147](https://github.com/sumrae412/courierflow_beta/pull/147): audit surfaced ~$7.6/run from uncached `SYSTEM_INSTRUCTIONS + tools` resent on ~175 Charlie calls; judge cost was <1% of total. Composes with the existing `/debate-team --harden` rule for evals-infra PRs — Tier 0 surfaces 5+ hardening repairs (wiring + telemetry + preflight + CI gate + decision record) that ALL belong in one PR.

## Deliverables

Produce only what the user needs:

- eval plan (metrics + success criteria)
- dataset (golden, with splits)
- evaluator(s) (prompt or code)
- experiment results with confidence framing
- regression gate spec for CI

## Sibling skills

- `courierflow-copilot-evals` — concrete domain implementation:
  grader-selection decision tree, four-property LLM-judge contract,
  YAML eval case schemas. Read this when you want a worked example.
- `prompt-governance` (`phases/phase-2-evals.md`) — registry and
  approval / rollback policy framing. This skill produces the eval
  signals that policy gates on; that skill handles the workflow,
  ownership, and registry plumbing.
- `prompt-optimization` — *different* skill from `prompt-optimizer`
  below. Use when empirically promoting prompt variants across
  reviewer agents (explorers, architects, reviewers).
- `prompt-optimizer` — use when iterating the wording of a single
  judge prompt during calibration. Judge prompts are prompts.
- `token-economy` — apply when running large eval batches; parallelize
  judge calls, delegate dataset sourcing to cheap subagents.
- `rag-architect` (`references/rag_evaluation_framework.md`) — RAG has
  its own metric family (Precision@K, MRR, NDCG, faithfulness). Use
  alongside this skill for retrieval features.
- `llm-cost-optimizer` — eval runs are an LLM-spend surface. Use for
  the combined-cost-meter rationale ("cost gates that meter only one
  call path are theater"), the cache-the-stable-SUT-prefix pattern
  (the uncached `system + tools` prefix resent across every SUT call
  is usually the dominant eval-run cost — judge calls are often <1%),
  and the cross-provider calibration gotcha (two correctly-functioning
  providers can disagree ~2× on the same input — agreement measures
  similarity, not correctness).
- `debate-team` (`references/critic-calibration.md`) — the
  three-critic / critic-concordance rule for validating eval
  *artifacts* (see Guardrails below). Calibrating critic agents is
  the meta-evaluation case of calibrating judges.

## References

- `references/judge-calibration.md` — ADOPT/REJECT cadence,
  noisiness detection, gold-like-bias check (generalized from
  debate-team critic calibration).
- `references/outcome-grader.md` — separate-model grader pattern
  for managed-agent / production workflows where self-verification
  is insufficient.
- `references/eval-philosophy.md` — methodological frame from
  Andrew Ng (orthogonalization, single optimizing metric), Hamel
  Husain ("Look at the Data™", impact hierarchy), Eugene Yan (EDD,
  scientific cycle, faithfulness vs helpfulness). Read when
  designing the eval *practice*, not picking tactics.
- `references/eval-tool-prior-art.md` — Shredmetal/llmtest
  (behavioral-assert form factor; "treat the LLM as a closed-source
  third-party library") and google/litmus (GCP-native eval platform
  with Ragas / DeepEval backends). Read before standing up a new
  eval surface — borrow the vocabulary even when you keep your own
  runner. Composes with the "tune system prompt, not eval QUESTIONS"
  anti-pattern in `~/.claude/CLAUDE.md` § Evals — Nouha Dziri's
  "jagged intelligence" framing (pattern matching vs reasoning;
  dense RL rewards beat sparse correct/incorrect signals) is the
  theoretical grounding for why retuning questions papers over
  model variance rather than fixing it ([Open Data Science, ODSC AI
  East 2026 keynote](https://opendatascience.com/nouha-dziri-on-jagged-intelligence-and-the-limits-of-llm-reasoning/)).

## Guardrails

- Do not ship an LLM-judge evaluator without a calibration report.
- Do not compare two prompt versions with N<30 examples and call it a
  result.
- Default to a *different* model family than the task model when
  judging open-ended quality. Same-model judging is acceptable
  only with explicit bias measurement against a human-labeled
  set — not a rule waiver by default.
- Do not let the dataset drift to only easy cases. Track failure-mode
  coverage explicitly.
- Order evaluator cost: cheap deterministic checks first, expensive
  LLM-judge second, human review last.
- **Critic concordance on statistical/methodological claims is weak
  evidence — run a cross-family third critic.** When two reviewers with
  overlapping training corpora agree on a numeric or methodological
  claim in an eval design (sample size, power, CI interpretation, paired
  vs. independent analysis), do *not* treat the agreement as
  confirmation. Statistical errors are the highest-value third-critic
  finding and not every model family catches them. Validated on this
  skill's own [PR #118](https://github.com/sumrae412/claude-skills/pull/118):
  R1 + R2 (same family) both missed a 10× sample-size bug; only a
  cross-family R3 caught it. This is the meta-evaluation case — you are
  calibrating the evaluators of your eval. See
  `debate-team/references/critic-calibration.md`.
- **When introducing a *new* judge model family as a baseline, calibrate
  it against a 30–50-example human-labeled gold set first** — don't
  promote it on agreement with the old judge. Two correctly-functioning
  providers can disagree ~2× on the same input; agreement measures
  similarity, not correctness. See `llm-cost-optimizer` (cross-provider
  agreement gotcha).

## Cost-discipline triad for stochastic eval surfaces

**Cost-discipline triad for any stochastic eval surface that runs nightly or on `workflow_dispatch`:**

1. **Combined cost meter** — every API call (SUT + judge + structured-output retries) tallies against ONE cumulative `cost_usd_total` checked before the next call. See `llm-cost-optimizer` "Cost gates that meter only one call path are theater." **Before optimizing, cache the stable SUT prefix** — the uncached `system + tools` block resent on every SUT call is routinely the dominant driver (judge calls often <1%); wrap it with prompt caching and log `cache_creation_input_tokens` / `cache_read_input_tokens → cacheHitRate` per call so the meter proves the cache is hitting.
2. **Repetition-count cap on nightly multi-sample paths** — flag like `--memory-depths {3,5,8,10}` with a default that caps the replay matrix; PR-gate runs use a leaner default than nightly to keep iteration cheap (composes with the existing PR-gate vs nightly threshold split).
3. **Path-trigger negation on PR workflows** — `paths:` with `!`-prefixed negations to exclude high-cost surfaces from PR triggers; reserve them for nightly + manual dispatch. See `vault/agent/ci-and-deploys.md` "paths AND paths-ignore in the same trigger block is forbidden" for the syntax constraint.

Validated 2026-05-30 on courierflow_beta [PR #157](https://github.com/sumrae412/courierflow_beta/pull/157) after a $60 day where 5 of 6 `suite=all` Layer B dispatches failed mid-run, each burning partial budget through an uncapped SUT path. Triad addresses each leak independently — none alone is sufficient.

## Cost-meter honesty fields — `unmeteredSurfaces: []`

Eval runners with multiple LLM call sites need explicit per-surface cost accumulation AND an `unmeteredSurfaces` honesty field in the results artifact, not just a `totalCostUsd` field. A `totalCostUsd` that secretly meters only one surface is the same anti-pattern the cost-discipline triad above guards against — judge-only metering is theater for `totalCost` the same way it is for a cost ceiling.

**Pattern for the results artifact:**

```jsonc
"summary": {
  "judgeCostUsd": 0.0,           // metered (0 here = no LLM judge)
  "classifierCostUsd": 0.0123,   // metered from response.usage
  "totalCostUsd": 0.0123,        // = sum of per-surface fields
  "unmeteredSurfaces": []        // explicit honesty list
}
```

The `unmeteredSurfaces: []` empty list is the load-bearing field. It tells reviewers "we believe nothing on this eval surface is silently unmetered" — and if a future change introduces a new `anthropic.messages.create()` call site on this code path, the developer MUST either add a new `<surface>CostUsd` field or name the surface in `unmeteredSurfaces`. Reviewers cross-check the runner's call sites against the array; any unlisted call site is a bug.

Validated 2026-06-07 on courierflow_beta [PR #332](https://github.com/sumrae412/courierflow_beta/pull/332) `tools/inbound/run_inbound_eval.py` — first downstream use of the courierflow_beta CLAUDE.md "totalCostUsd is judge-only" lesson (PR #322). The Gate D runner's `judgeCostUsd` is fixed-zero (no LLM judge in this regime), `classifierCostUsd` is metered from the bypass route's `usage` field, `totalCostUsd` = sum, `unmeteredSurfaces: []` is the explicit honesty signal.

Composes with the cost-discipline triad above (same family, scoped to artifact schema rather than runtime metering).
