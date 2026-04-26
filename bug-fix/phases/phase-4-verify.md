# Phase 4: Verify

## Goal

Prove the fix works and survives targeted review.

## Process

- run the targeted review subset
- fix high-severity findings and re-run the specific reviewer when needed
- run `verification-before-completion`
- confirm the original failing test now passes
- confirm no unresolved high-severity review findings remain

## Rules

- Verification is about behavior, not code plausibility.
- Do not skip the original reproduction path.

## Output

Verification summary with root cause, fix summary, tests, and review
status.
