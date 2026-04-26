# Phase 1: Processing Assessment

Load `../references/gdpr_compliance_guide.md` before running this phase.

## Goal

Assess a processing activity or codebase for GDPR risk and baseline
compliance gaps.

## Ask

- What personal data is processed?
- What is the legal basis?
- Are special-category, financial, or employee data involved?
- Where are retention, deletion, consent, and logging handled?

## Deterministic Path

Prefer:

- `scripts/gdpr_compliance_checker.py`

## Check For

- risky personal-data patterns
- missing consent or legal-basis logic
- indefinite retention
- unencrypted sensitive data
- missing deletion or restriction flows

## Output

Privacy risk assessment with findings, affected areas, and remediation
priorities.
