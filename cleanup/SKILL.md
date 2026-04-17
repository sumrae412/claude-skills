---
name: cleanup
description: Branch/worktree teardown — ExitWorktree, session-learnings capture, config/skills repo sync. Use for "clean up", "I'm done", "wrap up", or after shipping. Also the finishing hand-off for /ship and /claude-flow Phase 6B non-ship options.
---

# Cleanup

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

## Pre-flight: detect parallel-agent activity

BEFORE touching any worktree or branch, run:

```bash
# Re-read HEAD and reflog in case another agent moved things mid-session.
git -C <main-repo-path> branch --show-current
git -C <main-repo-path> reflog -20
git -C <main-repo-path> fetch origin --prune
```

If the reflog shows a recent `reset --hard origin/main`, a commit you don't recognize, or a branch switch you didn't initiate — a parallel agent is active. STOP. Confirm with the user before removing any worktrees.

See: `memory/gotcha_parallel_agent_merged_pr_mid_session.md`

## Worktree audit: cross-check squash-merged work

`git cherry origin/main <branch>` returns `+` for every commit of a squash-merged branch — DO NOT use it alone to declare work unshipped.

A worktree is SAFE to remove if ANY of:
1. `gh pr list --state all --head <branch>` reports a MERGED PR.
2. `git cherry origin/main <branch>` reports `-` for all commits.
3. A distinctive subject line from the branch appears in `git log origin/main`.
4. Known-dead-end experiment.

See: `memory/gotcha_git_cherry_squash_merge_false_positive.md`, `memory/gotcha_gh_pr_merge_delete_branch_worktree.md`

## Step 1: Detect Current State

Before presenting options, gather context silently:

```bash
# Are we in a worktree?
git rev-parse --git-common-dir 2>/dev/null  # differs from --git-dir if worktree

# Current branch
git branch --show-current

# Base branch
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null

# Uncommitted changes?
git status --porcelain

# Unpushed commits?
git log @{upstream}..HEAD --oneline 2>/dev/null || git log origin/main..HEAD --oneline

# Has remote tracking branch?
git rev-parse --abbrev-ref @{upstream} 2>/dev/null
```

**If uncommitted changes exist:** Warn the user before proceeding. Offer to commit first or stash.

**If on main/master:** Don't proceed — there's nothing to clean up. Say so and stop.

## Step 1.5: REVIEW.md Compliance Check

If the project has a `REVIEW.md`, run a final check of session changes against its Must Check rules before marking the branch as ready to ship.

## Step 2: Run Tests

```bash
# Use project-appropriate test command
pytest tests/ -v  # or npm test, cargo test, etc.
```

**If tests fail:** Stop. Report failures. Don't offer cleanup options until tests pass (or user explicitly says to discard).

**If tests pass:** Continue.

## Step 3: Present Options

Adapt the options based on detected state:

```
Work on `<branch>` is ready to wrap up. What would you like to do?

1. Merge to <base-branch> and push
2. Push branch and create a PR
3. Keep the branch as-is (I'll handle it later)
4. Discard this work
```

If invoked from `/claude-flow` Phase 6B, Option 1 should not appear (that path goes to `/ship`). Present only Options 2-4.

## Step 4: Execute Choice

### Option 1: Merge and Push

> **Defensive fallback** — Option 1 is suppressed for `/claude-flow` Phase 6B callers (see Step 3). If suppression fails and a `/claude-flow` caller reaches this option, redirect to `/ship` instead — it includes automated review.

```bash
CURRENT_BRANCH=$(git branch --show-current)
BASE_BRANCH=main  # or detected base

git checkout "$BASE_BRANCH"
git pull origin "$BASE_BRANCH"
git merge "$CURRENT_BRANCH"

# Verify tests on merged result
pytest tests/ -v

# If tests pass
git push origin "$BASE_BRANCH"
git branch -d "$CURRENT_BRANCH"
```

**Worktree gotcha:** If main is checked out in the parent repo, `git checkout main` will fail from a worktree. In that case, suggest using `gh pr merge` via GitHub API or switching to `/ship` which handles this correctly.

Then proceed to **Step 5** (session-learnings), **Step 6** (repo sync), and **Step 7** (worktree cleanup).

### Option 2: Push and Create PR

```bash
CURRENT_BRANCH=$(git branch --show-current)

git push -u origin "$CURRENT_BRANCH"

gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

Report the PR URL. Then proceed to **Step 5**, **Step 6**, and **Step 7**.

### Option 3: Keep As-Is

Report: "Keeping branch `<name>` as-is."

**If in a worktree:** Ask whether to also keep the worktree or just the branch:
- Keep both → done, no cleanup
- Keep branch, remove worktree → push branch to remote first (`git push -u origin <branch>`), then proceed to **Step 7** only

**Skip session-learnings** (work isn't integrated yet).

### Option 4: Discard

**Require explicit confirmation:**

```
This will permanently delete:
- Branch: <name>
- Commits: <short log>
- Worktree at: <path> (if applicable)

Type 'discard' to confirm.
```

Wait for exact confirmation. Then:

```bash
CURRENT_BRANCH=$(git branch --show-current)
git checkout main 2>/dev/null || true
git branch -D "$CURRENT_BRANCH"
# Delete remote tracking branch if it exists
git push origin --delete "$CURRENT_BRANCH" 2>/dev/null || true
```

Proceed to **Step 7** (worktree cleanup). **Skip session-learnings and repo sync.**

## Step 4.5: PR Merge Verification (Options 1 & 2 only)

<HARD-GATE>Before tearing down a worktree, verify any associated PR was actually merged — not just created.</HARD-GATE>

After executing Option 1 or 2, check if the current branch has an open PR:

```bash
# Check for open PR on this branch
BRANCH=$(git branch --show-current)
PR_STATE=$(gh pr view "$BRANCH" --json state --jq '.state' 2>/dev/null || echo "NONE")
```

- **MERGED** → safe to proceed with build verification and teardown.
- **OPEN** (Option 1 — was supposed to merge) → Something went wrong. Attempt merge or warn user.
- **OPEN** (Option 2 — PR was just created) → **Warn explicitly:**
  "PR #N is open but unmerged. If this session ends, the work may be orphaned. The session-start hook will flag it, but consider merging now if ready."
  Wait for user acknowledgment before proceeding to worktree teardown.
- **NONE** → No PR exists (e.g., direct merge). Proceed normally.
- **CONFLICTING** (mergeable check returns this immediately on push) → main has moved under the worktree. Do NOT exit-remove. Salvage flow:
  1. `git branch backup/feat-X-pre-rebase HEAD` — backup before any destructive op
  2. Inspect what main changed: `git diff --name-only $(git merge-base HEAD origin/main)..origin/main`
  3. If main DELETED files this branch still has (typical for repo-split refactors): `git reset --hard origin/main` then selective `git checkout backup -- <files>` for the files that still belong here
  4. Adjust cross-repo path references (e.g., persona files now in another repo via `~/.claude/skills` symlink)
  5. Recreate logical commits, `git push --force-with-lease`
  6. Open companion PR in the other repo for files that moved out

  See MEMORY `cross_repo_split_brain_salvage.md`. The skill's normal in-place conflict resolution does not apply when the conflict is structural.

**Why this exists:** PR #286 was created via Option 2, the worktree was torn down, and the session ended. The PR sat unmerged for days because no one checked. This gate ensures cleanup never silently walks away from unmerged work.

## Step 4.6: Build Verification (Options 1 & 2 only)

After pushing code, verify the build succeeds before proceeding to cleanup:

1. **CI pipeline:** If the project has CI (GitHub Actions), check it:
   ```bash
   # Check latest workflow run on the branch
   gh run list --branch "<branch>" --limit 1 --json status,conclusion
   # If status is "in_progress", wait and re-check (up to 2 minutes)
   ```

2. **Railway deploy** (if applicable):
   ```bash
   # Use Railway MCP: list-deployments tool
   # Check latest deployment status for FAILED vs SUCCESS
   ```

3. **Gate logic:**
   - **Build passes** → proceed to Step 5
   - **Build fails** → **STOP.** Report the failure with logs/error details. Do NOT proceed to session-learnings or worktree teardown. The user needs the worktree to fix the issue. Offer to help diagnose.
   - **Build pending (>2 min)** → Ask user: wait longer, proceed anyway, or keep worktree until build confirms.

**Why this matters:** Tearing down the worktree before confirming a successful build means you lose the local environment needed to iterate on fixes. A failed deploy with no worktree forces a full context rebuild.

---

## Step 5: Session Learnings

**After Options 1 or 2 only** (work was shipped or PR'd):

Invoke `/session-learnings` in the background. Every shipped branch should capture what was learned — patterns, gotchas, corrections discovered during development.

**Wait for session-learnings to resolve** before proceeding to Step 6. Session-learnings may propose edits to skills, CLAUDE.md, or config files — those changes need to land in their repos (Step 6) before the worktree is torn down (Step 7).

## Step 6: Sync Config and Skills Repos

**After session-learnings resolves (Options 1 or 2), or after /ship's review agent completes.**

Session-learnings and review agents often update files in `~/.claude/skills/` and `~/.claude/` (config, memory). These directories are separate git repos that need their own commit+push cycle — changes there are invisible to the project repo.

Check each repo for uncommitted changes and push them:

```bash
# 1. Claude skills repo
cd ~/.claude/skills
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  git add -A
  git commit -m "update skills from session-learnings"
  git push
fi

# 2. Claude config/memory repo (if it's a git repo)
cd ~/.claude
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  git add -A
  git commit -m "update config from session-learnings"
  git push
fi

# 3. Project memory repo (separate from project repo)
MEMORY_DIR=~/.claude/projects/-Users-summerrae-courierflow/memory
cd "$MEMORY_DIR"
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  git add -A
  git commit -m "update memory from session-learnings"
  git push
fi
```

**Why this matters:** Without this step, skill/config improvements discovered during a session evaporate when the worktree is removed, or worse, sit uncommitted and get lost when you switch machines.

**If no changes detected:** Skip silently — don't report "nothing to sync" unless the user asks.

## Step 7: Worktree Cleanup

**Only if currently in a worktree.** If on a regular branch, skip this step entirely.

**When all prior steps are complete and nothing remains to be done, ask the user:**

```
All cleanup is finished. Would you like me to delete the branch and worktree?
```

Wait for the user's answer before proceeding. If they say yes, use `ExitWorktree` with the appropriate action. If they say no, leave everything in place.

Use the `ExitWorktree` tool — it handles directory switching and cleanup correctly:

| Option chosen | ExitWorktree action |
|--------------|---------------------|
| 1 (Merged) | `action: "remove"` |
| 2 (PR created) | `action: "remove"` |
| 3 (Keep) | Do not call ExitWorktree |
| 4 (Discard) | `action: "remove", discard_changes: true` |

The `ExitWorktree` tool will:
- Switch the session back to the original working directory
- Remove the worktree directory and branch (for `"remove"`)
- Refuse to remove if there are uncommitted changes (unless `discard_changes: true`)

If `ExitWorktree` reports uncommitted changes and you're on Option 1 or 2 (work already pushed), set `discard_changes: true` since the work is safely on the remote.

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
