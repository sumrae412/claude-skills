# Review Budgets

Canonical path defaults live in `../workflow-profiles.json`.

This reference explains how Phase 6 should scale reviewer cost to actual change
risk.

## Budget Levels

| Budget | Typical Paths | Default Reviewers |
|--------|----------------|-------------------|
| `low` | `clone`, `lite` | `coderabbit`, `lightweight-reviewer` |
| `medium` | `plan`, `audit`, default `full` | low budget plus `safety-reviewer`, `test-coverage-analyzer` |
| `high` | any path escalated by high-risk signals | medium budget plus `curmudgeon-review`, `adversarial-breaker`, high-risk specialists |

## Escalation Signals

Promote budget based on deterministic signals, not gut feel:

- file count grows beyond a contained change
- migrations or schema changes
- auth or security-sensitive files
- deploy / CI / infra changes
- external API integration signals

## Budget Intent

`low` exists to keep Phase 6 cheap for contained work without skipping review
entirely.

`medium` is the default floor for substantial work.

`high` is reserved for diffs where a missed issue would be materially more
expensive than extra review calls.
