# Phase 1: Preflight and Commit

## Goal

Confirm the work is ready to ship and create the commit cleanly.

## Check

- tests already pass
- branch strategy is valid
- git/gh tooling is available
- repo state is not confused by parallel-agent activity
- **`git fetch origin && git log HEAD..origin/main --oneline`** — surfaces merges since branch creation. A related fix may have merged to main while your branch was open and obsoleted any LOCAL DEV ONLY workarounds you stacked on top. If so, drop the workaround in a final commit rather than carrying it through merge. Validated 2026-05-22: [courierflow_beta PR #4](https://github.com/sumrae412/courierflow_beta/pull/4) merged mid-flight and obsoleted an `app.ts` bypass on the [PR #5](https://github.com/sumrae412/courierflow_beta/pull/5) branch.

## Process

- inspect git status and diff
- choose the ship tier
- stage by file name only
- write a conventional commit

## Output

Commit-ready scope or explicit blocker if preflight fails.
