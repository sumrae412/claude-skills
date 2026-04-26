---
name: "fda-consultant-specialist"
description: FDA regulatory consultant for medical device companies. Provides 510(k)/PMA/De Novo pathway guidance, QSR (21 CFR 820) compliance, HIPAA assessments, and device cybersecurity. Use when user mentions FDA submission, 510(k), PMA, De Novo, QSR, premarket, predicate device, substantial equivalence, HIPAA medical device, or FDA cybersecurity.
---

# FDA Consultant Specialist

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

Regulatory guidance for medical-device companies across FDA submission
pathways, QSR compliance, HIPAA-adjacent device privacy/security, and FDA
cybersecurity obligations.

This file is a router. Do not keep all pathway and compliance doctrine
resident.

## When to Use

- Choosing between 510(k), De Novo, and PMA
- Planning a 510(k) or premarket submission
- Reviewing QSR / 21 CFR 820 readiness
- Assessing HIPAA implications for a device workflow
- Designing device cybersecurity documentation or process

## Load Strategy

1. Identify the regulatory workflow the user actually needs.
2. Load only the matching phase file from `phases/`.
3. Load only the relevant reference guide.
4. Prefer scripts for deterministic checklists or assessments.

Do not preload all pathway, QSR, HIPAA, and cybersecurity guidance.

## Phase Map

1. `phases/phase-1-pathway-and-submission.md`
2. `phases/phase-2-qsr-and-capa.md`
3. `phases/phase-3-hipaa-and-privacy.md`
4. `phases/phase-4-device-cybersecurity.md`

## Reference Map

- Submission guidance:
  `references/fda_submission_guide.md`
- QSR requirements:
  `references/qsr_compliance_requirements.md`
- HIPAA framework:
  `references/hipaa_compliance_framework.md`
- Device cybersecurity:
  `references/device_cybersecurity_guidance.md`
- CAPA detail:
  `references/fda_capa_requirements.md`

## Script Map

- Submission tracking:
  `scripts/fda_submission_tracker.py`
- QSR compliance:
  `scripts/qsr_compliance_checker.py`
- HIPAA risk assessment:
  `scripts/hipaa_risk_assessment.py`

## Session Rules

- Start with device classification and intended use.
- Separate pathway choice from QSR readiness.
- Treat HIPAA applicability as data-flow dependent, not device-category
  dependent.
- Make cybersecurity expectations explicit for connected devices.

## Deliverables

Produce only what the user needs:

- pathway recommendation
- submission readiness plan
- QSR / CAPA review
- HIPAA applicability assessment
- device cybersecurity plan

## Guardrails

- Do not treat predicates as sufficient without substantial-equivalence
  analysis.
- Call out evidence gaps, missing design controls, and untested response
  plans explicitly.
- Keep regulatory guidance framed as planning support, not legal advice.
