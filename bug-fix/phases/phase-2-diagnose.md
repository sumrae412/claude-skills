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

## Output

Diagnosis with root cause, affected files, blast radius, and minimal fix
approach.
