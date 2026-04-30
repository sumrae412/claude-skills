---
name: "soc2-compliance"
description: "Use when the user asks to prepare for SOC 2 audits, map Trust Service Criteria, build control matrices, collect audit evidence, perform gap analysis, or assess SOC 2 Type I vs Type II readiness."
---

# SOC 2 Compliance

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

SOC 2 preparation for SaaS and service organizations. Covers Trust
Service Criteria selection, control matrix design, gap analysis, evidence
collection, and audit readiness.

This file is a router. Do not keep the full audit doctrine resident.

## When to Use

- Preparing for a SOC 2 Type I or Type II audit
- Choosing which TSC categories apply
- Building or reviewing a control matrix
- Running a gap assessment or readiness review
- Designing evidence collection and continuous compliance workflows

## Load Strategy

1. Identify the user's current need.
2. Load only the matching phase from `phases/`.
3. Load only the referenced material that phase needs.
4. Use scripts for deterministic outputs when structured inputs exist.

Do not preload all TSC details or all audit guidance.

## Phase Map

1. `phases/phase-1-scope-and-tsc.md`
2. `phases/phase-2-control-matrix-and-gaps.md`
3. `phases/phase-3-evidence-and-vendors.md`
4. `phases/phase-4-readiness-and-continuous-compliance.md`

## Reference Map

- TSC details:
  `references/trust_service_criteria.md`
- Evidence patterns:
  `references/evidence_collection_guide.md`
- Type I vs Type II decision support:
  `references/type1_vs_type2.md`

## Script Map

- Control matrix generation:
  `scripts/control_matrix_builder.py`
- Evidence status:
  `scripts/evidence_tracker.py`
- Gap analysis:
  `scripts/gap_analyzer.py`

## Session Rules

- Decide Type I vs Type II early.
- Keep Security mandatory; add other TSCs only when justified.
- Tie every control to owner, evidence, and test method.
- Treat vendor and subservice controls as first-class scope items.

## Deliverables

Produce only what the user needs:

- TSC selection rationale
- control matrix
- gap analysis
- evidence collection plan
- readiness assessment
- continuous compliance plan

## Guardrails

- Do not overscope TSC categories without business need.
- Do not call a program ready if evidence is manual, stale, or incomplete.
- Distinguish designed controls from operating controls.
- Call out missing vendor governance and observation-window gaps
  explicitly.

## Out of Scope

This skill does NOT:
- Run ISO 27001 ISMS scoping or risk assessment—use `information-security-manager-iso27001`.
- Cover GDPR/DSGVO data-subject rights or DPIAs—use `gdpr-dsgvo-expert`.
- Provide FDA medical-device pathway guidance—use `fda-consultant-specialist`.
- Replace an external CPA auditor—planning support only; engage a licensed audit firm for the attestation.
- Audit application source code for vulnerabilities—use `review-pr` or `production-readiness-check`.
