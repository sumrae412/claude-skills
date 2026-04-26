---
name: startup-analysis
description: Brutally honest startup idea validation — 6-step CLEARFRAME stack (TAM, ICP, wedge, GTM, Go/NoGo). Use for "validate this idea", "is this worth building", competitive analysis, or cold strategic feedback on a business concept.
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

Six-step startup pressure test using CLEARFRAME mode for direct,
anti-sycophancy analysis.

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
6. `phases/phase-6-verdict.md`

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
- overall verdict

## Guardrails

- no hedging without logical need
- no invented numbers presented as facts
- no flattering validation when the analysis points to no-go
