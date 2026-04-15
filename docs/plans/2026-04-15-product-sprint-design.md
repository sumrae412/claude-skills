# Product Sprint Skill Design

**Date**: 2026-04-15
**Status**: Approved (v2 — expanded to 7 stages)

## Overview

A 7-stage guided product sprint that takes an idea from raw insight to validated, stakeholder-tested vision in ~30 minutes. Combines Marily Nika's AI-Enhanced PM Cycle (research, PRD, prototype, pitch, judging) with Hiten Shah's stakeholder cloning and Personal OS workflows. Adapted for native Claude execution with cross-skill connections to deeper product management tools.

## Architecture

Single skill directory with progressive disclosure (router + reference files).

```
product-sprint/
├── SKILL.md                          # Router (~3K tokens)
└── references/
    ├── debate-technique.md           # Pro/con agent debate framework
    ├── stakeholder-clone.md          # Stakeholder persona construction
    ├── prd-template.md               # PRD structure template
    ├── prototype-patterns.md         # React+Tailwind and HTML/CSS patterns
    └── pitch-script-template.md      # Video storyboard + pitch + rehearsal
```

## Stages

### Stage 1: Rapid User Research (The Debate Technique)
- WebSearch for real user opinions, then pro vs. con debate (10+ rounds)
- Output: **Minimum Feature Set** required to convince skeptics
- Exits: `/competitive-brief`, `/startup-analysis`

### Stage 2: Context-Primed PRD Generation
- Context priming step: absorb domain frameworks before generating
- Three targeted questions + structured PRD with MoSCoW prioritization
- Exits: `/startup-planner` Stage 8+, `product-management:write-spec`

### Stage 3: Stakeholder Persona (Clone Your Decision-Maker)
- Build an AI persona of the key stakeholder (boss, investor, board)
- Gather: decision style, communication preference, NO triggers, YES accelerators
- Connected: `/personal-coach` Stage 3 for personality-framework analysis

### Stage 4: Interactive Prototype
- React+Tailwind or HTML/CSS standalone (user choice)
- PRD-driven visual cues and realistic sample data
- Connected: `frontend-design:frontend-design`, `/image-generation`

### Stage 5: Vision Pitch + Stakeholder Rehearsal
- Part A: Elevator pitch + storyboard + key messaging
- Part B: Simulate pitching to the Stage 3 stakeholder persona with realistic pushback
- Connected: `sc-marketing-scripts`

### Stage 6: Personal OS Lens (Optional)
- Personality-aware reflection on the sprint — blind spots, stakeholder compatibility, energy management
- Quick behavioral sketch if no formal frameworks taken
- Connected: `/personal-coach` for full personality coaching system

### Stage 7: Demo Judge (Optional)
- Evaluate pitches on Innovation/Impact/Feasibility/Storytelling (25% each)
- Scorecard + rankings for multiple pitches

## Cross-Skill Connection Graph

```
product-management:product-brainstorming  ──→  Stage 1
startup-analysis (TAM/market data)        ──→  Stage 1
product-management:competitive-brief      ──→  Stage 1

product-management:write-spec             ──→  Stage 2
startup-planner Stages 8-10              ←──→  Stage 2 (handoff)

personal-coach Stage 3                    ──→  Stage 3

image-generation                          ──→  Stage 4
frontend-design:frontend-design           ──→  Stage 4

sc-marketing-scripts                      ──→  Stage 5

personal-coach (full system)              ──→  Stage 6
```

**Principle**: product-sprint is the fast lane. Other skills are deep dives offered as exits when user wants more rigor.

## Key Design Decisions

1. **Native Claude execution** — no external tool prompts; WebSearch for research, direct PRD generation, code output for prototypes
2. **Debate technique** is the signature innovation in Stage 1 — surfaces objections a PM would miss
3. **Stakeholder cloning** (Stages 3+5) adds rehearsal before real pitches — based on Hiten Shah's "WWMD" workflow
4. **Context priming** (Stage 2) operationalizes domain frameworks — based on Shah's two-step pattern of teaching framework then applying to specific context
5. **Personal OS lens** (Stage 6) adds personality-aware reflection — blind spot detection and energy forecasting
6. **Each stage feeds the next** — output artifacts chain forward
7. **Any stage can be entered directly** if user brings their own input
8. **Professional help boundaries**: Stage 6 personality insights and Stage 7 judging include appropriate disclaimers

## Sources

- **Marily Nika** — AI-Enhanced PM Cycle: debate technique, rapid PRD, v0 prototyping, video pitch, NotebookLM judging
- **Hiten Shah** — "What Would Morgan Do" stakeholder cloning, Personal OS self-coaching, framework operationalization pattern
