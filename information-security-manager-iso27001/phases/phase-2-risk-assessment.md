# Phase 2: Risk Assessment

Load `../references/risk-assessment-guide.md` before running this phase.

## Goal

Create or review the risk register and treatment priorities.

## Ask

- Which assets matter most?
- What threats and vulnerabilities are most credible?
- What is the impact if each asset is compromised or unavailable?
- Which risks already have treatments, and which are still unowned?

## Deterministic Path

Prefer:

- `scripts/risk_assessment.py`

Use templates when the domain is healthcare, cloud, or general.

## Check For

- missing asset ownership
- shallow threat models
- unmapped vulnerabilities
- inconsistent scoring
- untreated high or critical risks

## Output

Risk register with scoring, owners, treatment direction, and residual-risk
notes.
