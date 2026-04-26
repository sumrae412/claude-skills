# Phase 1: Reproduce

## Goal

Capture the bug in a failing test or equivalent reproducible signal.

## Rules

- A bug without reproduction is a guess.
- Write the failing test before investigating.
- If the bug is UI-specific, exercise the deepest reliable testable
  surface.

## Process

- understand the symptom
- write a failing test
- run it and confirm it fails
- if local reproduction is impossible, inspect logs and environment
  signals
- if only the user can reproduce, add throwaway instrumentation and use
  their runtime output to localize the failure

## Output

Bug report with symptom, expected behavior, reproduction path, and
affected area.
