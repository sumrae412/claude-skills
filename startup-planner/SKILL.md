---
name: startup-planner
description: Heavy, explicit-invocation startup planning workshop — 12 stages spanning Kawasaki Conception (genesis, sweet spot, mantra, business model, cofounder, MATT) and execution planning (Business Model Canvas, TAM/SAM/SOM, MVP/MoSCoW, Go/NoGo, Marp pitch deck). Also houses three optional add-on techniques: PRO/CON debate validation, AI stakeholder-clone rehearsal, and customer segmentation matrix. Heavy skill — ONLY invoke when the user explicitly says "/startup-planner", "run the startup planner", "work the startup planning workshop", or asks for Business Model Canvas / Kawasaki workshop / Marp pitch deck specifically. Do NOT auto-fire on vague phrases like "plan a startup" or "business idea" — use `startup-analysis` for brutal 6-step CLEARFRAME validation instead.
license: MIT
metadata:
  author: summerela
  version: "1.1.0"
---

# Startup Planning Workshop

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

Guided startup-planning workshop for taking one idea from conception
through execution planning. Work through one stage per session. Do not
load all stages up front.

## Invocation Rules

Use only when the user explicitly wants the startup planning workshop,
Business Model Canvas, Kawasaki-style startup planning, or a pitch deck.

Do not auto-fire on vague idea-validation prompts. Use `startup-analysis`
for those.

## Load Strategy

This file is a router only. After reading it:

1. Ask which stage to work on, or start at Stage 1.
2. Load only that stage file from `phases/`.
3. Load only the reference file that stage requires.
4. Offer add-ons only when the current stage benefits from them.

Do not preload reference files "just in case."

## Stage Map

### Conception

1. `phases/stage-01-genesis.md`
2. `phases/stage-02-sweet-spot.md`
3. `phases/stage-03-meaning.md`
4. `phases/stage-04-mantra.md`
5. `phases/stage-05-business-model.md`
6. `phases/stage-06-soul-mates.md`
7. `phases/stage-07-matt.md`

### Execution

8. `phases/stage-08-bmc.md`
9. `phases/stage-09-market-analysis.md`
10. `phases/stage-10-mvp.md`
11. `phases/stage-11-gonogo.md`
12. `phases/stage-12-pitch-deck.md`

## Reference Map

- Stages 1-7: `references/kawasaki-frameworks.md`
- Stages 8-12: `references/business-frameworks.md`
- Starting cold or when product context is fuzzy:
  `references/project-context-template.md`
- Optional add-ons: `phases/add-ons.md`

## Session Rules

- Work through one stage per session.
- Ask one question at a time.
- Push back on weak answers.
- Do not assume facts the user has not given.
- Summarize the output before moving to the next stage.

## Output Format

After completing a stage, provide:

```md
## Stage X: [Name] - COMPLETE

[Output content]

---
Completed: [date]
Next stage: [X+1 name]
```

## Guardrails

- This skill provides frameworks for thinking, not legal, financial, or
  professional business advice.
- Validate market assumptions with real customers, not only framework
  exercises.
- Go/NoGo decisions should involve real stakeholders.
