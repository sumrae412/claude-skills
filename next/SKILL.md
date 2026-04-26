---
name: next
description: Hand off to the next session — write a self-contained continuation prompt/handoff doc, then ship the current work (commit → PR → review → merge) and run cleanup. Use when the user says "/next", "hand this off", "wrap up and write a continuation prompt", or wants to end one session and prime the next.
---

# /next — hand off, then ship and clean up

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


**Announce at start:** "Using /next to write a handoff doc, then ship and clean up."

Execute in this order. Do NOT interleave. Each step blocks the next.

## Step 1 — Write a continuation prompt

Before anything destructive, capture the handoff so a fresh session can resume cleanly. Write (or append to) a doc under `docs/plans/` — check first with `ls docs/plans/*handoff*.md`. If an existing session-handoff doc covers this work stream, append a new dated execution-log entry. Otherwise create `docs/plans/<YYYY-MM-DD>-session-handoff.md`.

The continuation prompt must be **self-contained** — the next session has zero memory of this conversation. Include:

1. **Goal** — one sentence. What is the next agent being asked to do?
2. **Current state** — what has already shipped this session (branches merged, PR numbers, commit SHAs), what is in-flight (open PRs, unmerged branches, pending reviews), what is untouched.
3. **Exact next task** — the single most-valuable thing to do next. Name the file paths, the operation, the acceptance criteria. If there is a choice between tasks, state the decision and the reasoning so the next agent does not relitigate it.
4. **Template / reference PRs** — link the 1–3 merged PRs that establish the pattern to replicate, if any. Cite by number, not prose.
5. **Pre-flight commands** — the literal commands the next agent should run before touching code: `cd <main-repo>`, `git fetch origin --prune`, `gh pr list --state open`, check for open PRs on recently-merged base branches, read the handoff doc.
6. **Architectural invariants to preserve** — cite by memory-file slug (e.g. `pattern_copilotkit_page_context_readables.md`) or CLAUDE.md section. Do not re-explain the invariants; name them.
7. **Gates** — `./scripts/quick_ci.sh` (or project equivalent), `ruff format --check` on touched files, any test-subset command that isolates the relevant suite.
8. **Ship instructions** — literal: "Ship via `/ship`. Update [specific doc row] with the PR number before merging." If the work is pattern-replication of an already-shipped PR, say so — the next agent should use `/ship`, not `/claude-flow`.
9. **Mode directive** — `Auto mode. Surface premise contradictions only.`

Write the handoff doc, then read it back and ask: "If I had no memory of this session, could I execute the next task from this doc alone?" If not, fill the gap before proceeding.

## Step 2 — Ship the current work

Invoke the `shipping-workflow` skill (i.e. `/ship`). It handles: commit → push → PR → automated review → merge → cleanup delegation.

If there are no uncommitted changes AND no unpushed commits, skip this step and move to Step 3. Do NOT run `/ship` on a clean tree — it has no work to do.

The handoff doc from Step 1 is committed as part of the shipping PR, NOT as a separate commit. This ensures it ships atomically with the state it describes.

## Step 3 — Cleanup

`/ship` delegates its final stage to `/cleanup`, which runs:
- Session-learnings (captures patterns from this session)
- Waits for learnings proposals
- Syncs config/skills/memory repos
- Worktree teardown via `ExitWorktree`

Do not manually invoke session-learnings, sync repos, or remove worktrees — `/cleanup` (triggered by `/ship`) handles all of it.

If Step 2 was skipped (clean tree, nothing to ship), invoke `/cleanup` directly instead.

## Step 4 — Output the continuation prompt

At the end, output ONE fenced block the user can copy into their next session:

```
## Continuation prompt

<5–10 lines: name the goal, point at the handoff doc, state the mode directive>

Reference: docs/plans/<handoff-file>.md
```

The handoff doc is the source of truth; the pasted prompt is the entry point.

## Guardrails

- Step 1 MUST complete before Step 2. If the handoff doc can't be written (no obvious next task, current work is exploratory-only), say so and STOP — do not ship without a handoff.
- If `/ship`'s review stage surfaces issues that block merge, STOP. Do not clean up. Report the blocker and let the user decide.
- If the work is on a branch with an already-open PR, update the PR body (not a new PR) and continue through review → merge → cleanup.
- Never create a handoff doc for a session with no meaningful work to hand off. Session-learnings captures trivial sessions; handoff docs are for active work streams.
