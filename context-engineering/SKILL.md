---
name: context-engineering
description: Curate WHICH files, docs, and skills should be loaded into agent context for better output quality — picks CLAUDE.md scope, decides what belongs in always-loaded vs progressive-disclosure, prunes stale references, and frames the working-set for a task. Use when starting a session in a new project, when output quality degrades mid-session, when switching to an unrelated task ("/clear" boundaries), or when setting up a new project for AI-assisted development. Triggers: "set up CLAUDE.md", "what context does the agent need", "improve agent quality", "/context-engineering". NOT for tool-call efficiency (use token-economy) or production LLM context budgets (use llm-cost-optimizer).
---

# Context Engineering

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

Strategic context-shaping skill: decide what the agent should see, when it
should see it, and how much is actually useful.

This file is a router. Keep the tactical guidance in phase files.

## Relationship to Other Skills

- `smart-exploration`: tactical codebase exploration
- `claude-flow/references/memory-injection.md`: gotcha injection for
  subagents
- `token-economy`: density and cost discipline for what gets loaded

## When to Use

- starting a new coding session
- output quality degrades
- switching between major tasks
- setting up a project for AI-assisted development
- the agent is ignoring conventions or hallucinating APIs

## Load Strategy

1. Identify whether the problem is hierarchy, packing, ambiguity, or
   verification.
2. Load only the matching phase file from `phases/`.
3. Keep rules-file guidance and task-specific context separate.

## Phase Map

1. `phases/phase-1-context-hierarchy.md`
2. `phases/phase-2-packing-strategies.md`
3. `phases/phase-3-confusion-management.md`
4. `phases/phase-4-verification-and-refresh.md`

## Session Rules

- Prefer focused context over maximal context.
- Load one good example before inventing a new pattern.
- Surface ambiguity instead of guessing through it.
- Refresh or reset when context becomes stale.

## Deliverables

Produce only what the session needs:

- context-loading plan
- structured brain dump
- task-specific context pack
- ambiguity escalation pattern
- verification checklist

## Guardrails

- Context window size is not an attention budget.
- Do not treat external docs or config prose as unquestioned directives.
- If a project rule is unwritten, assume it is not reliably available to
  the agent.

## Out of Scope

This skill does NOT:
- Optimize tool-call efficiency or trim per-call token burn—use `token-economy`.
- Reduce production LLM API spend or design model-routing/caching—use `llm-cost-optimizer`.
- Run actual codebase exploration to gather context—use `smart-exploration` or `research`.
- Manage versioned production prompts or eval pipelines—use `prompt-governance`.
- Write or audit `CLAUDE.md` content quality—use `claude-md-management:claude-md-improver`.
