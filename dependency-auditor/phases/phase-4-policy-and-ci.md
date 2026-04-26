# Phase 4: Policy and CI

Load `../references/dependency_management_best_practices.md` before
running this phase. Load `../references/vulnerability_assessment_guide.md`
if the pipeline needs security gates.

## Goal

Turn dependency auditing into repeatable policy and automation.

## Ask

- Which findings should fail CI immediately?
- Which should warn only?
- How often should security, license, and upgrade scans run?
- What evidence or artifact format does the team need?

## Build

Define:

- fail/warn thresholds
- scan cadence
- artifact formats
- exception handling process
- ownership and review cycle

## Output

CI / policy design for dependency scanning with thresholds, cadence, and
exception workflow.
