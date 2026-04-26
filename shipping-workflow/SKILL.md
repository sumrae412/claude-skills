---
name: shipping-workflow
description: End-to-end ship pipeline — commit, push, PR, 10-step review, fix, CI, merge. Use on "ship it", "done", "merge it", "push it", "deliver this".
license: MIT
metadata:
  author: summerela
  version: "1.1.0"
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
