# Phase 3: Data Subject Rights

Load `../references/gdpr_compliance_guide.md` before running this phase.

## Goal

Handle GDPR Articles 15-22 request workflows correctly and on time.

## Ask

- Which right is being exercised?
- Has identity been verified proportionately?
- Which systems hold the relevant data?
- Are there exemptions, conflicts, or legal-retention constraints?

## Deterministic Path

Prefer:

- `scripts/data_subject_rights_tracker.py`

## Check For

- deadline risk
- incomplete system search
- over-collection during verification
- failure to document decisions

## Output

Rights-handling workflow or case plan with deadline, status, response
shape, and unresolved blockers.
