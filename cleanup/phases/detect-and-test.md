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

