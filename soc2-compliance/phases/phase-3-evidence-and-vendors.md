# Phase 3: Evidence and Vendor Management

Load `../references/evidence_collection_guide.md` before running this
phase.

## Goal

Define how evidence will be collected and how third-party risk will be
handled.

## Ask

- What evidence exists already, and where is it stored?
- Which controls still rely on manual screenshots or one-off exports?
- Which vendors access, store, or process customer data?
- Are subservice organizations handled via carve-out or inclusive logic?

## Deterministic Path

Use `scripts/evidence_tracker.py` when a control matrix already exists.

## Build

The plan should cover:

- evidence type per control
- collection cadence
- automation opportunities
- vendor inventory and risk tiering
- ownership and review schedule

## Output

Evidence collection and vendor-governance plan with automation targets
and unresolved evidence risks.
