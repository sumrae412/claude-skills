---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to finish a development branch. Project-level override that integrates /ship for automatic review + merge.
---

# Finishing a Development Branch (CourierFlow Override)

This overrides the superpowers plugin version to integrate the `/ship` pipeline.

## The Process

### Step 1: Verify Tests

Run the project test suite before proceeding:

```bash
./scripts/quick_ci.sh
```

**If checks fail:** Stop. Fix failures before proceeding. Do not offer options.

**If checks pass:** Continue to Step 2.

### Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null
```

Base branch is `main` unless otherwise specified.

### Step 3: Present Options

```
Implementation complete. What would you like to do?

1. Ship it (commit → push → PR → review → merge to main)
2. Keep the branch as-is (I'll handle it later)
3. Discard this work

Which option?
```

**Option 1 is the default.** If the user says "ship it", "done", "merge it", "push it", or anything suggesting they want to deliver — use Option 1.

### Step 4: Execute Choice

#### Option 1: Ship It

Run the `/ship` command. This handles everything end-to-end:
1. Stage and commit with conventional commit message
2. Create branch if on main, push to origin
3. Create PR with summary and test plan
4. Launch background review agent (isolated worktree) running the full review-pr workflow
5. Review agent handles: CodeRabbit, defensive patterns, deep-dives, fix issues, quick_ci.sh, cherry-pick to main, post PR comment

**Do NOT manually run git push, gh pr create, or /review-pr separately.** The `/ship` command handles all of it.

Then: Cleanup worktree (Step 5).

#### Option 2: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 3: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation. If confirmed:
```bash
git checkout main
git branch -D <feature-branch>
```

Then: Cleanup worktree (Step 5).

### Step 5: Cleanup Worktree

**For Options 1 and 3:**

Check if in worktree:
```bash
git worktree list | grep $(git branch --show-current)
```

If yes:
```bash
git worktree remove <worktree-path>
```

**For Option 2:** Keep worktree.

## Key Difference From Plugin Version

This project-level skill replaces the separate "push + create PR" step with the unified `/ship` pipeline, which automatically runs the full review-pr workflow in the background. This ensures code is never shipped without review.
