---
name: startup-analysis
description: Brutally honest startup idea validation — 8-step CLEARFRAME stack (TAM, ICP, wedge, GTM, five-role debate team, Go/NoGo). Use for "validate this idea", "is this worth building", competitive analysis, or cold strategic feedback on a business concept.
---

# Startup Analysis

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

Eight-step startup pressure test using CLEARFRAME mode for direct,
anti-sycophancy analysis. The five-role debate team (Researcher →
Strategist → Copywriter → Builder → Marketer) runs as Phase 6 and feeds
the Go/No-Go decision in Phase 7. The verdict cannot be issued without
debate-team output — a chain Hold from any role is a structural No-Go
signal.

This file is a router. Keep the step details in phases.

## When to Use

- validate a startup or feature idea
- assess whether an idea is worth pursuing
- sharpen ICP, wedge, or GTM framing
- force a go / conditional go / no-go decision

Skip for free-form brainstorming or lightweight gut checks.

## Load Strategy

1. Gather the minimum startup context once.
2. Load only the current phase file from `phases/`.
3. Run phases in order; do not skip ahead.

## Inputs

- one-line product summary
- target audience
- optional competitor / margin / pricing / CAC data
- user marketing sophistication level

## Phase Map

0. `phases/phase-0-clearframe.md`
1. `phases/phase-1-market-reality.md`
2. `phases/phase-2-icp.md`
3. `phases/phase-3-value-props.md`
4. `phases/phase-4-competitive-wedge.md`
5. `phases/phase-5-gtm-mode.md`
6. `phases/phase-6-debate-team.md` — invokes the five-role chain in `startup-debate-team/`
7. `phases/phase-7-verdict.md` — consumes Phase 6 output as required evidence

## Session Rules

- challenge assumptions directly
- label estimates as estimates
- include strategist's note and rating after major outputs
- keep kill criteria explicit

## Deliverables

Produce only what the current phase needs:

- market read
- ICP
- value propositions
- wedge analysis
- GTM mode selection
- debate-team validation packet (5 Pass/Hold calls + offer + copy + site spec + funnel math)
- overall verdict

## Companion Skills

- `startup-debate-team` is invoked from Phase 6 — do not run it standalone
  for validation; run it through this skill so its output feeds the
  scorecard.
- After a Go verdict, the natural follow-on is `pitch-deck` to turn the
  validation into investor / sales / launch slides. The `pitch-deck`
  skill reuses ICP, wedge, GTM, and Builder/Marketer outputs directly.
- For pre-validation brainstorming, use `superpowers:brainstorming` or
  `product-management:product-brainstorming` instead — this skill is for
  pressure-testing, not generation.

## Guardrails

- no hedging without logical need
- no invented numbers presented as facts
- no flattering validation when the analysis points to no-go
