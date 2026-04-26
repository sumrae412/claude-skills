---
name: cleanup
description: Branch/worktree teardown — ExitWorktree, session-learnings capture, config/skills repo sync. Use for "clean up", "I'm done", "wrap up", or after shipping. Also the finishing hand-off for /ship and /claude-flow Phase 6B non-ship options.
---

# Cleanup

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Smart cleanup for branches and worktrees. Detects your current context (worktree vs regular branch, uncommitted changes, unpushed commits) and walks you through the right teardown path.

**Announce at start:** "Using /cleanup to wrap up this work."

## Why This Exists

Finishing work has three concerns that are easy to forget or get wrong:
1. **Git cleanup** — merge, PR, or discard the branch
2. **Config/skills repo sync** — if session-learnings updated skills or config, push those changes to their repos before the worktree disappears
3. **Worktree cleanup** — if you're in a worktree, tear it down so stale worktrees don't pile up

This skill handles all three in one flow, using the native `ExitWorktree` tool for worktree teardown instead of manual `git worktree remove` commands.

## Relationship to Other Skills

- **`/ship` (shipping-workflow):** Handles the full pipeline: commit, push, PR, review, merge. If the user says "ship it", use `/ship` — not this skill. However, `/ship` delegates its final cleanup stage to `/cleanup`.
- **`/claude-flow` Phase 6B:** Options 2-4 delegate here. Option 1 ("Ship it") goes to `/ship`.
- **session-learnings:** This skill triggers session-learnings automatically after Options 1 or 2 (work was integrated). No need to invoke it separately. Note: `/claude-flow` ensures session-learnings fires for ALL paths including FAST PATH (orchestrator fires directly if `/cleanup` is not invoked).

**When to use which:**
| User says | Use |
|-----------|-----|
| "ship it", "merge it", "push it" | `/ship` |
| "clean up", "I'm done", "wrap up" | This skill |
| "exit worktree" | This skill |
| "discard this work" | This skill |

## Workflow

This skill uses progressive disclosure. Load the phase file for the stage you're in; skip the others to keep context lean.

1. **Pre-flight → load [`phases/preflight.md`](phases/preflight.md).**
   Detect parallel-agent activity and cross-check squash-merged work on sibling worktrees before any decision. Skip only if you are certain no parallel agents are running.

2. **Detect state, gate on REVIEW.md, run tests → load [`phases/detect-and-test.md`](phases/detect-and-test.md).**
   Step 1 (current-state detection: worktree vs branch, uncommitted, unpushed), Step 1.5 (REVIEW.md compliance gate), Step 2 (run tests before offering options).

3. **Present options and execute → load [`phases/options.md`](phases/options.md).**
   Step 3 (present 4 options to the user), Step 4 (execute the chosen option): Merge & Push, Push & PR, Keep As-Is, Discard. Contains the full command sequence per option plus the PR body template.

4. **Verify the merge and build (Options 1 & 2) → load [`phases/verify.md`](phases/verify.md).**
   Step 4.4 (every-worktree PR merge sweep), Step 4.5 (current-branch deep PR merge check), Step 4.6 (build verification). Skip entirely for Options 3 & 4.

5. **Sync repos, capture learnings, tear down → load [`phases/sync-and-teardown.md`](phases/sync-and-teardown.md).**
   Step 5 (session-learnings for Options 1 & 2), Step 6 (config + skills repo sync), Step 7 (ExitWorktree). Runs continuously without pausing between steps once the user has picked an option.

## Quick Reference

| Option | Push | Merge | Repo Sync | Worktree | Branch | Session Learnings |
|--------|------|-------|-----------|----------|--------|-------------------|
| 1. Merge & push | origin | main | yes | remove | delete | yes |
| 2. Create PR | branch | — | yes | remove | keep (remote) | yes |
| 3. Keep as-is | — | — | no | keep* | keep | no |
| 4. Discard | — | — | no | remove | force delete | no |

*Option 3 offers to remove worktree while keeping the branch on remote.

## Not in a Worktree?

This skill works for regular branches too — it just skips Step 7. The git cleanup (merge/PR/discard), session-learnings, and repo sync steps work identically regardless of whether you're in a worktree.

## Common Mistakes to Avoid

- **Skipping build verification** — always confirm CI/deploy passes before tearing down the worktree
- **Pausing between steps after shipping** — Steps 4.5→4.6→5→6→7 should flow continuously after the user picks an option. Only Step 7 (worktree removal) needs explicit confirmation
- **Tearing down worktree with unmerged PR** — Always check PR state before removing the worktree. An open PR + removed worktree = orphaned work that no one remembers to merge
- **Skipping cleanup for non-project work** — even if the worktree has no project repo changes (e.g., work was in skills or config repos), still run session-learnings, sync repos, and tear down the worktree
- **Skipping test verification** — always verify before offering options
- **Manual `git worktree remove`** — use `ExitWorktree` tool instead, it handles session state correctly
- **Forgetting to push before removing worktree** — Option 2 must push first or the branch is lost
- **No confirmation for discard** — always require typed "discard"
- **Merging from worktree when main is checked out elsewhere** — use `gh pr merge` or `/ship` instead
- **Removing worktree before session-learnings resolves** — causes "folder no longer exists" error, kills ability to apply proposals
- **Forgetting to sync config/skills repos** — session-learnings updates evaporate on machine switch
