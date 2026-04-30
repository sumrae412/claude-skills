---
name: "information-security-manager-iso27001"
description: ISO 27001 ISMS implementation and cybersecurity governance for HealthTech and MedTech companies. Use for ISMS design, security risk assessment, control implementation, ISO 27001 certification, security audits, incident response, and compliance verification. Covers ISO 27001, ISO 27002, healthcare security, and medical device cybersecurity.
---

# Information Security Manager - ISO 27001

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

ISMS design and governance aligned with ISO 27001:2022, with emphasis on
risk assessment, control selection, certification readiness, and incident
response in healthcare and regulated environments.

This file is a router. Keep only the relevant phase and reference in
context.

## When to Use

- Designing or scoping an ISMS
- Running an ISO 27001 risk assessment
- Selecting or checking ISO 27002-aligned controls
- Preparing for certification audits
- Building or reviewing incident-response capability

## Load Strategy

1. Identify the current objective.
2. Load only the matching phase file from `phases/`.
3. Load only the required reference guide.
4. Use scripts when deterministic assessment output is helpful.

Do not preload all controls, workflows, and examples.

## Phase Map

1. `phases/phase-1-isms-scope-and-context.md`
2. `phases/phase-2-risk-assessment.md`
3. `phases/phase-3-controls-and-soa.md`
4. `phases/phase-4-incident-response-and-readiness.md`

## Reference Map

- Control guidance:
  `references/iso27001-controls.md`
- Risk methodology:
  `references/risk-assessment-guide.md`
- Incident-response guidance:
  `references/incident-response.md`

## Script Map

- Risk assessment:
  `scripts/risk_assessment.py`
- Compliance and gap analysis:
  `scripts/compliance_checker.py`

## Session Rules

- Define scope and context before selecting controls.
- Treat the risk register as the driver of control selection.
- Make the Statement of Applicability explicit.
- Separate design readiness from operating effectiveness.

## Deliverables

Produce only the deliverable the user needs:

- ISMS scope and context
- risk register
- control / SoA guidance
- gap analysis
- incident-response plan
- certification readiness review

## Guardrails

- Do not claim ISO readiness without scope, risk, SoA, audit, and
  management-review evidence.
- Call out unowned assets, untreated high risks, and missing metrics.
- Prefer concrete evidence over policy-on-paper claims.

## Out of Scope

This skill does NOT:
- Cover SOC 2 Trust Service Criteria or audit-evidence collection—use `soc2-compliance`.
- Cover GDPR/DSGVO data-subject rights or DPIAs—use `gdpr-dsgvo-expert`.
- Provide FDA medical-device regulatory pathway guidance—use `fda-consultant-specialist`.
- Audit application source code for OWASP/injection vulnerabilities—use `review-pr` or `production-readiness-check`.
- Run actual external certification audits—engage an accredited certification body.
