# Phase 3: Review and CI

Load `../reference.md` before running this phase.

## Goal

Run the review pipeline, fix meaningful findings, and clear CI.

## Process

- run the 10-step review process from `reference.md`
- scope-filter findings before triage
- use rate-limit fallback only when CodeRabbit is unavailable
- fix real issues and re-run targeted checks
- wait for or clear CI gates

## Rules

- review is not optional
- CI is a hard gate
- behavior verification matters in addition to code review

## Output

Review status, remaining findings, and CI result.

## Babysit loop discipline

When waiting on CI to finish (PR open, checks running, CodeRabbit comments may land), use `ScheduleWakeup` to pace re-entry rather than polling in a tight loop. Pattern adapted from [openhuman `.claude/commands/ship-and-babysit.md` Phase 4](https://github.com/tinyhumansai/openhuman/blob/main/.claude/commands/ship-and-babysit.md):

- **`delaySeconds: 270`** — stays inside the 5-min prompt-cache TTL, so the next tick reads conversation context warm. 300s pays the full cache miss without amortizing it; 60s burns the cache 5× per cycle.
- **`tickCount` echoed in `reason`** — pass `"tick 5/12: waiting on CI for PR #123"` so the counter survives across ticks and can't drift on ticks that produce no commits. Increment on every loop entry, regardless of whether work happened.
- **Hard cap: 12 ticks (~60 min)** — after the cap, stop the loop and ask the user, including PR URL, current CI snapshot, and any unresolved CodeRabbit threads. Don't extend silently.
- **Exit condition is conjunctive — all true to stop:**
  - All required checks are `SUCCESS`. **`PENDING` keeps the loop running, no exceptions** — never claim "green" while CI is mid-run.
  - No unresolved CodeRabbit review threads.
  - No new CodeRabbit issue comments since the last tick. Track this by remembering the highest CodeRabbit issue-comment `id` seen on the previous tick (GitHub issue-comment ids are monotonic) and only treating ids strictly greater than that marker as new on the current tick.
- **When exiting, do NOT call `ScheduleWakeup`** — return a final one-line summary with the PR URL and current status. Calling Wakeup at the exit path produces a wasted tick that re-enters the loop only to discover it's already done.

If the loop hits a blocker that needs human input (auth failure, ambiguous CodeRabbit suggestion, conflicting feedback, merge conflict), stop and ask — don't guess past it just to keep the loop ticking.
