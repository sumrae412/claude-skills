---
name: shipping-workflow
description: End-to-end ship pipeline — commit, push, PR, 10-step review, fix, CI, merge. Use on "ship it", "done", "merge it", "push it", "deliver this".
license: MIT
metadata:
  author: summerela
  version: "1.2.0"
---

# Shipping Workflow

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant
  patterns inline instead of loading extra material.

## Overview

End-to-end ship pipeline: commit, push, PR, review, CI, merge, cleanup.
This file is a router; detailed review and branch-handling doctrine stays
in phases and `reference.md`.

## When to Use

- implementation is complete
- tests already pass
- user wants to ship, merge, push, or deliver

## Tiering

- tiny mechanical follow-up: inline ship may be enough
- normal pattern-replication or backend follow-up: use this workflow
- novel design work: finish through `claude-flow` before shipping
- **session-handoff doc: use the Handoff-doc fast path below — auto-merge, no review**

## Handoff-doc fast path

When `/next` (or any caller) ships a session-handoff doc, **skip review/CI and auto-merge to main**. Future sessions need handoff docs discoverable on main, not stranded in open PRs.

**Conditions for auto-merge (ALL must hold):**

- PR diff is exactly one file (verify with `gh pr view <N> --json files --jq '.files | length'` returns `1`)
- File path matches `docs/plans/*handoff*.md` (case-insensitive `handoff` substring in the basename)
- File is functionally additive: `changeType: "ADDED"` OR (`changeType: "MODIFIED"` AND the file path matches `docs/plans/*handoff*.md` AND `deletions <= 5`). Rationale: refreshing the bottom continuation prompt of an existing handoff doc to reflect current shipped/in-flight state commonly produces small deletions (the prior prompt is rewritten in place). [courierflow_beta PR #40](https://github.com/sumrae412/courierflow_beta/pull/40) shipped at `+91 / -3` (the 3 deletions were the stale bottom prompt) — well within spirit. The `<=5` cap keeps substantive rewrites on the normal review path. Substantive prompt rewrites that delete more than 5 lines (e.g. [courierflow_beta PR #50](https://github.com/sumrae412/courierflow_beta/pull/50) at `+37 / -7` — the deletions were a continuation-prompt rewrite reflecting an intervening merge) intentionally fall through to normal review; the cap is not raised for them, because rewriting the next-session entry point deserves a human read.
- Branch name is doc-prefixed (e.g. `docs/...`)
- PR base branch is `main`

**When all hold:** after Phase 2 opens the PR, **immediately** run:

```bash
env -u GH_TOKEN gh pr merge <N> --squash --delete-branch
```

Skip Phase 3 (review + CI) entirely. Phase 4 verifies the merge state and hands off to `/cleanup` as usual.

**When any condition fails:** fall through to the normal Phase 3 review flow — the PR is treated as ordinary doc work, not a handoff.

**Why narrow:** the conditions exist to catch the exact handoff-doc shape (`/next` writes single-file additive docs under `docs/plans/*handoff*.md`). A multi-file PR, a doc that also touches code, a non-`docs/` branch, or a deletion-bearing diff all fall back to the normal review path. The fast path never auto-merges substantive changes.

**Why auto-merge is safe for this case:** handoff docs are write-once continuation prompts. No executable code, no schema, no security surface. The review gate exists to catch issues in code/config changes — for doc-only continuation prompts it just delays the next session from finding the doc. Validated 2026-05-22 on [courierflow_beta PR #18](https://github.com/sumrae412/courierflow_beta/pull/18) (Task 4 handoff doc) which sat open until manually merged into commit `598fd11` — exactly the failure mode this fast path prevents.

**Auto-mode classifier blocks the fast-path merge even when all conditions match.** In auto-mode sessions, the harness classifier flags `gh pr merge <N> --squash --delete-branch` as "self-squash-merging to main without explicit user authorization" and pauses for approval — even when the fast-path's five conditions all hold. The skill's fast-path logic doesn't translate to the classifier (there's no per-PR signal saying "this is a handoff doc, fast-path eligible"). When the merge is blocked: surface a one-line summary to the user ("PR #N matches handoff-doc fast path — approve merge?") rather than falling through to Phase 3 review. Hit 2026-05-22 on [courierflow_beta PR #25](https://github.com/sumrae412/courierflow_beta/pull/25). Long-term fix is a classifier-side signal — out of scope for this skill.

**Update 2026-05-28** — validated on [courierflow_beta PR #109](https://github.com/sumrae412/courierflow_beta/pull/109) (handoff doc `docs/plans/2026-05-28-correctness-rubric-phase5d1-handoff.md` on branch `docs/correctness-rubric-phase5b-handoff`): fast-path merge executed in auto-mode WITHOUT classifier interception. All five fast-path conditions held (single file, `docs/plans/*handoff*.md`, ADDED, doc-prefixed branch, base=main). Either the classifier was updated to recognize the handoff-doc shape, or the trigger surface is narrower than originally documented. Refined guidance: **attempt the fast-path merge directly when all five conditions hold**; if the classifier blocks, fall through to the one-line user surface as before. Don't pre-emptively skip the merge attempt on the assumption that it will be blocked.

## No-review-wired-up fast path

Some repos (notably docs-style ones — claude-skills is the canonical example) have no CodeRabbit, no `.github/workflows/`, and no human reviewers attached to PRs. A PR there is effectively ready-to-merge the moment it opens; waiting for review feedback that will never come is dead time and confuses handoff docs that assume CR is a gate.

**Detection (run before entering Phase 3):**

```bash
env -u GH_TOKEN gh pr view <recent-merged-PR-#1> --json reviews,statusCheckRollup
env -u GH_TOKEN gh pr view <recent-merged-PR-#2> --json reviews,statusCheckRollup
```

Pick the two most recently merged PRs in the same repo. If `reviews` is `[]` AND `statusCheckRollup` is `[]` on BOTH → no review wiring exists. Confirm by checking the tree: `ls .github/workflows/ 2>/dev/null` returns nothing and there's no `.coderabbit.yaml` / `.coderabbit.yml`.

**When detected:** skip Phase 3's wait-for-review step. Phase 3's self-review checklist (the "10-step review") still runs as a self-audit, but stops blocking on external signal. Proceed to Phase 4 merge as soon as self-review passes.

**Explicit no-CI approval still enters cleanup.** If Summer explicitly approves a no-CI merge for a repo with no reported checks, merge with the required approval marker, verify the merge, then continue to Phase 4 cleanup. The no-CI approval replaces only the external CI/review gate; it does not skip session-learnings, repo sync, or worktree teardown.

**Distinct from the handoff-doc fast path above:** that one fires on PR shape (single-file, additive, `docs/plans/*handoff*.md`). This one fires on REPO shape (no review automation). They compose — a handoff doc in a no-CR repo hits both.

**Why this matters:** validated 2026-05-27 on [claude-skills PR #118](https://github.com/sumrae412/claude-skills/pull/118) — handoff doc treated "address CodeRabbit feedback" as a gating Phase 3 step. CodeRabbit had never been wired up in this repo; PRs #117 and #114 each had `reviews: []` and `statusCheckRollup: []`. Without this detection step, the resumer waits indefinitely for review that won't fire.

**Composes with `next` skill's §5a "Re-verify on resume"** — that section makes the CR/CI check part of the resumer's preflight, so the no-review-wired-up state is known before Phase 3 starts.

## Load Strategy

1. Verify the work is actually ready to ship.
2. Load only the current phase file from `phases/`.
3. Load `reference.md` only when running or adapting the review stage.
4. Keep worktree-specific caveats out of context unless the session is in
   a worktree.

## Phase Map

1. `phases/phase-1-preflight-and-commit.md`
2. `phases/phase-2-push-and-pr.md`
3. `phases/phase-3-review-and-ci.md`
4. `phases/phase-4-merge-and-cleanup.md`

## Core Rules

- Never ship without review.
- CI must pass before merge.
- Confirm merge state before cleanup.
- `/cleanup` owns final session-learnings, sync, and teardown.

## Deliverables

Produce only what the current shipping phase needs:

- commit-ready scope
- pushed branch and PR
- review / CI status
- merged PR and cleanup handoff

## Guardrails

- No force-push to main/master.
- No silent shortcut around review or CI.
- If a workflow step must be skipped, tell the user exactly which step and
  what risk remains.
