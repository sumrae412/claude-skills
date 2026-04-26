# Phase 2: Control Matrix and Gap Analysis

Load `../references/trust_service_criteria.md` before running this
phase.

## Goal

Map controls to TSC criteria and identify design or implementation gaps.

## Ask

- Which controls already exist?
- Which owners and frequencies are defined?
- What evidence currently exists for each control?
- Which criteria have no meaningful control coverage?

## Deterministic Path

Prefer scripts when structured control inputs exist:

- `scripts/control_matrix_builder.py`
- `scripts/gap_analyzer.py`

## Check For

- missing controls
- partial coverage
- vague ownership
- missing evidence mapping
- Type II operating-effectiveness gaps

## Output

Control matrix and gap report with:

- mapped criteria
- missing or weak controls
- remediation priorities
- owners and deadlines
