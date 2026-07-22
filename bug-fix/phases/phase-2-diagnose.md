# Phase 2: Diagnose

## Goal

Find the root cause and estimate blast radius before touching code.

## Process

- check memory for relevant gotchas
- trace from symptom to root cause
- dispatch `investigator` only if the bug is multi-file, unclear, or
  environment-specific
- assess blast radius and likely side effects

## Rules

- No symptom-only fixes.
- If a memory gotcha seems relevant, verify it against current code before
  acting on it.
- When the bug turns on a field's possible values (status, severity, tier,
  type), blast radius is *every producer and every consumer* of that field —
  not the one site the symptom pointed at. Grep all assignment sites before
  gating or deleting. See `agent/regression-patterns.md` in the agent vault:
  a PR that deleted a value's only producer left its consumer running in
  production against input that could never arrive, and CI stayed green.

## Output

Diagnosis with root cause, affected files, blast radius, and minimal fix
approach.
