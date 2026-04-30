---
name: synthetic-persona
description: Build a "synthetic person" from public data for product reviews, brainstorming, pitch rehearsals, or interpersonal analysis. Use for "what would [name] think", "build a persona", "rehearse a pitch", "role-play as".
---

# Synthetic Persona

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

Build one public-data persona, then use it for review, brainstorming,
rehearsal, or interpersonal analysis.

This file is a router. Do not keep all stage logic, prompts, and
multi-persona features resident.

## Hard Boundary

Use public data or user-provided material only. Never use confidential or
private information to construct the persona.

## When to Use

- Building a persona from a real person's public footprint
- Reviewing a product through that persona's lens
- Rehearsing a pitch or conversation
- Analyzing interpersonal dynamics with a known person

## Load Strategy

1. Ask which stage is needed, or start at Stage 1.
2. Load only the matching phase file from `phases/`.
3. Load only the referenced material that phase needs.
4. Keep Stages 3-4 reusable for an already-saved persona.

Do not preload all stages or all prompt templates.

## Phase Map

1. `phases/stage-1-research-and-build.md`
2. `phases/stage-2-product-scan.md`
3. `phases/stage-3-interactive-session.md`
4. `phases/stage-4-findings-report.md`
5. `phases/multi-persona.md`

## Reference Map

- Research and persona-card method:
  `references/research-guide.md`
- Review modes and reporting:
  `references/review-prompts.md`
- UX / usability schema:
  `references/ux-persona-schema.md`

## Session Rules

- Work through one main stage per session.
- Ask one question at a time.
- Push back on vague or weak evidence.
- Flag low-confidence inferences explicitly.
- Save persona artifacts to memory when Stage 1 is complete.

## Deliverables

Produce only what the user needs:

- persona card
- persona prompt
- product map
- in-character session
- findings report
- multi-persona comparison or feature verdict

## Guardrails

- This is pre-vetting, not a substitute for real human feedback.
- Surface thin evidence and unknowns explicitly.
- If dynamics analysis crosses into harassment, crisis, or mental-health
  territory, stop at communication advice and point toward real human
  support.

## Out of Scope

This skill does NOT:
- Run alpha/beta usability testing with a diverse synthetic user population—use `personas`.
- Use confidential, private, or non-public information to construct the persona—public data only.
- Replace real customer interviews or user research—pre-vetting only.
- Provide therapy, mediation, or mental-health guidance—stop and point to real human support.
- Build product UI/UX mockups for the persona to react to—use `design-audit` or `excalidraw-canvas` for the artifact, then bring it here.
