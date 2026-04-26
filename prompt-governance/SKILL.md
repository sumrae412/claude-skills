---
name: prompt-governance
description: "Use when managing prompts in production at scale: versioning prompts, running A/B tests on prompts, building prompt registries, preventing prompt regressions, or creating eval pipelines for production AI features. Triggers: 'manage prompts in production', 'prompt versioning', 'prompt regression', 'prompt A/B test', 'prompt registry', 'eval pipeline'. NOT for RAG pipeline design (use rag-architect). NOT for LLM cost reduction (use llm-cost-optimizer)."
---

# Prompt Governance

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant
  patterns inline instead of loading extra material.

## Overview

Treat prompts as production infrastructure: versioned, evaluated,
reviewed, promoted, monitored, and rolled back like code.

This file is a router. Keep registry, eval, and deployment doctrine in
phases.

## When to Use

- building a prompt registry
- designing eval pipelines
- governing prompt changes in CI/CD
- setting up A/B tests and rollback flows
- preventing prompt regressions in production systems

## Load Strategy

1. Identify whether the gap is registry, evals, governed iteration, or
   policy.
2. Load only the matching phase file from `phases/`.
3. Keep prompt-governance separate from RAG design and cost routing.

## Phase Map

1. `phases/phase-1-registry.md`
2. `phases/phase-2-evals.md`
3. `phases/phase-3-governed-iteration.md`
4. `phases/phase-4-policy-and-rollout.md`

## Session Rules

- Prompts are code.
- Every production prompt should have ownership, versioning, and rollback.
- Eval gates beat intuition.
- A/B tests need predefined success metrics and enough sample size.

## Deliverables

Produce only what the user needs:

- prompt registry design
- eval pipeline design
- governed iteration workflow
- A/B test plan
- rollout / rollback policy

## Guardrails

- Do not bless hardcoded production prompts without calling out the risk.
- Do not recommend prompt deploys without eval or rollback plans.
- Distinguish prompt quality governance from model-cost optimization.
