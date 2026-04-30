---
name: "gdpr-dsgvo-expert"
description: GDPR and German DSGVO compliance automation. Scans codebases for privacy risks, generates DPIA documentation, tracks data subject rights requests. Use for GDPR compliance assessments, privacy audits, data protection planning, DPIA generation, and data subject rights management.
---

# GDPR/DSGVO Expert

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

Privacy compliance toolkit for GDPR and German BDSG/DSGVO workflows:
codebase assessments, DPIAs, data-subject request handling, and
Germany-specific compliance checks.

This file is a router. Do not keep all privacy doctrine resident.

## When to Use

- Running a GDPR compliance assessment on a system or codebase
- Determining whether a DPIA is required
- Handling data-subject rights requests
- Checking German-specific BDSG obligations
- Designing privacy remediation or compliance tracking

## Load Strategy

1. Identify the user's current privacy workflow.
2. Load only the matching phase file from `phases/`.
3. Load only the relevant reference guide.
4. Prefer scripts for deterministic scans, reports, and trackers.

Do not preload all rights, legal-basis, and BDSG guidance.

## Phase Map

1. `phases/phase-1-processing-assessment.md`
2. `phases/phase-2-dpia.md`
3. `phases/phase-3-data-subject-rights.md`
4. `phases/phase-4-german-bdsg.md`

## Reference Map

- GDPR implementation guidance:
  `references/gdpr_compliance_guide.md`
- DPIA methodology:
  `references/dpia_methodology.md`
- German BDSG requirements:
  `references/german_bdsg_requirements.md`

## Script Map

- Codebase/privacy scan:
  `scripts/gdpr_compliance_checker.py`
- DPIA generation:
  `scripts/dpia_generator.py`
- Data-subject request tracking:
  `scripts/data_subject_rights_tracker.py`

## Session Rules

- Start from the actual processing activity, not generic policy text.
- Separate legal basis questions from technical-control questions.
- Treat DPIA threshold assessment explicitly, not implicitly.
- Keep Germany-specific BDSG obligations separate from baseline GDPR
  duties.

## Deliverables

Produce only what the user needs:

- privacy risk assessment
- DPIA recommendation or report
- data-subject request workflow
- BDSG applicability review
- remediation plan

## Guardrails

- Do not treat a high compliance score as proof of legal sufficiency.
- Call out missing legal basis, retention rules, or deletion paths
  explicitly.
- Treat special-category data and employee data as elevated-risk areas.

## Out of Scope

This skill does NOT:
- Provide binding legal advice or replace a Data Protection Officer—ask the user to engage qualified counsel.
- Cover SOC 2 Trust Service Criteria or audit-evidence collection—use `soc2-compliance`.
- Run ISO 27001 ISMS design or security risk assessment—use `information-security-manager-iso27001`.
- Cover FDA/HIPAA medical-device privacy specifics—use `fda-consultant-specialist`.
- File submissions with supervisory authorities or respond to data-subject requests on the user's behalf—the user must act.
