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
- **Before fixing a failing eval, ask: does it measure what the user actually wants to measure?** A persistently-failing eval is often the wrong instrument, not a broken one. Validated 2026-05-27 on courierflow_beta correctness rubric ([PR #108](https://github.com/sumrae412/courierflow_beta/pull/108), commit `d0a795a`): semantic-consistency suite was failing across PRs #91/#95/#99; reframe from "fix the eval" → "replace with a correctness rubric" came when user stated measurement intent directly ("I just want to measure that the agent is giving consistently correct answers"). The failing semantic-consistency metric measured reply-to-reply similarity; what the user wanted was correctness-against-policy. **Apply when:** an eval has been "fixed" 2+ times and is failing again, OR the eval's pass/fail doesn't map cleanly to a sentence the user would say about model quality. Composes with the existing "don't tune eval questions to make tests pass" anti-pattern in `~/.claude/CLAUDE.md` — that rule says don't paper over model variance; this rule says don't paper over instrument mismatch either.

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
