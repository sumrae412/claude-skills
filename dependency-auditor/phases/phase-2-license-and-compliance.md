# Phase 2: License and Compliance

Load `../references/license_compatibility_matrix.md` before running this
phase.

## Goal

Assess license compatibility, legal risk, and policy violations.

## Ask

- Is the software distributed externally or used internally only?
- Which license classes are disallowed by policy?
- Are there dual-licensed or unknown-license packages?
- Which dependencies are direct vs transitive?

## Deterministic Path

Prefer:

- `scripts/license_checker.py`

## Check For

- strong copyleft contamination risk
- incompatible license combinations
- unknown or ambiguous licenses
- packages missing license metadata
- policy violations needing explicit exception handling

## Output

License risk report with conflict severity, affected packages, and
recommended actions.
