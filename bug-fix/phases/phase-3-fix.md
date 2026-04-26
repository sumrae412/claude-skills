# Phase 3: Fix

## Goal

Take the reproducing failure to green with the smallest defensible change.

## Process

- confirm the reproducing test is still red
- implement the minimal fix
- apply defensive patterns appropriate to the surface
- rerun the reproducing test to green
- run broader regression tests and static checks on changed files

## Rules

- Fix the diagnosed root cause only.
- If regressions appear, revisit the blast-radius analysis before adding
  more code.

## Output

Diff and test status for the implemented fix.
