---
name: prompt-optimization
description: A/B-style optimizer for the claude-flow subagent prompt registry — analyzes prompt performance across explorers (Phase 2), architects (Phase 4), and reviewers (Phase 6) using win/loss telemetry, promotes winners to default, and generates challenger variants for the next round. Use when user says "optimize prompts", "tune the registry", "/prompt-optimization", or after a `session-learnings` run flags a prompt as underperforming. Reads from `prompt-registry.json` and writes versioned challengers. NOT for production LLM prompt versioning (use prompt-governance) or general prompt writing (use claude-api skill).
user-invocable: true
---

# Prompt Optimization

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

Closed-loop optimization for prompt variants across explorers,
architects, and reviewers.

This file is a router. Keep metrics math, promotion logic, and challenger
drafting in phase files.

## When to Use

- session-learnings detected new prompt-performance events
- user invokes `/prompt-optimization`
- prompt variants need reporting, promotion, or challenger generation

## Load Strategy

1. Determine whether the task is reporting, promotion, or challenger work.
2. Load only the matching phase file from `phases/`.
3. Prefer the tracker and statistical scripts for deterministic output.

## Phase Map

1. `phases/phase-1-metrics-and-reporting.md`
2. `phases/phase-2-promotion-checks.md`
3. `phases/phase-3-trace-analysis-and-challengers.md`
4. `phases/phase-4-summary-and-next-steps.md`

## Data Map

- `memory/procedural/prompt-variants.json`
- `memory/episodic/exploration-events.jsonl`
- `memory/episodic/architect-events.jsonl`
- `memory/episodic/reviewer-events.jsonl`

## Script Map

- `~/.claude/scripts/prompt-tracker.py`
- `scripts/stat-eval.py`

## Session Rules

- Use tracker output and stats before prose interpretation.
- Promotion requires evidence, not score vibes.
- Challenger drafting should target observed failure buckets, not only the
  winner's surface style.

## Deliverables

Produce only what the run needs:

- performance report
- promotion decision
- challenger proposal
- milestone summary

## Guardrails

- Do not promote unstable or flaky variants.
- Do not draft challengers without enough trace signal when the workflow
  expects it.
- Keep manual review focused on earliest observable failure, not
  downstream noise.

## Out of Scope

This skill does NOT:
- Govern production LLM prompts (versioning, A/B in user traffic, rollback)—use `prompt-governance`.
- Write general-purpose prompts for new Claude API features—use `claude-api`.
- Tune model selection or routing for cost—use `llm-cost-optimizer`.
- Run the claude-flow exploration phase itself—use `smart-exploration` (this skill optimizes its prompts post-hoc).
- Capture session learnings or memory updates—use `anthropic-skills:session-learnings`.
