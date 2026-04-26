# Phase 2: Promotion Checks

## Goal

Determine whether any variant is promotable using statistical criteria.

## Process

- run CI-aware promotion checks
- inspect consistency, flakiness, and regression status
- block promotions when evidence is unstable

## Rules

- promotion requires significance or CI dominance
- consistency and flakiness can block an otherwise leading prompt

## Output

Promotion decisions with rationale and any blocked promotions called out
explicitly.
