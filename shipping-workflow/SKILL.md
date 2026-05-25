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

**Update (2026-05-25):** The classifier block is now intermittent rather than universal — [courierflow_beta PR #72](https://github.com/sumrae412/courierflow_beta/pull/72) (single-file additive `docs/plans/*handoff*.md` on `docs/*` branch, +141 / -0, all five fast-path conditions met) auto-merged via `gh pr merge --squash --delete-branch` without classifier intervention. The block from 2026-05-22 (PR #25) may have been input-shape-specific or classifier-tuning has shifted. Continue to surface a one-line summary if the merge IS blocked, but don't pre-assume a block on every fast-path attempt — try the merge first and fall back to the user-prompt path only on classifier failure.

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
