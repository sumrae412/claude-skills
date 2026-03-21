---
name: finishing-a-development-branch
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for merge, PR, or cleanup
---

# Finishing a Development Branch

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Present options → Execute choice → Push to main → Clean up worktree.

**Announce at start:** "I'm using the finishing-a-development-branch skill to complete this work."

## Relationship to Other Skills

- **code-creation-workflow Phase 6B** delegates Options 2-4 to this skill. Option 1 ("Ship it") goes to `/ship` instead.
- **shipping-workflow / ship.md** handle the full pipeline (commit, push, PR, review, merge). This skill handles non-ship finishing (PR without auto-merge, keep branch, discard).
- Do NOT run this skill for Option 1 when invoked from code-creation-workflow — that path belongs to `/ship`.

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:** Stop. Don't proceed to Step 2.

**If tests pass:** Continue to Step 2.

### Step 2: Determine Base Branch

```bash
git merge-base HEAD main 2>/dev/null || git merge-base HEAD master 2>/dev/null
```

Or ask: "This branch split from main - is that correct?"

### Step 3: Present Options

Present exactly these 4 options:

```
Implementation complete. What would you like to do?

1. Merge to <base-branch> and push to origin
2. Push and create a Pull Request
3. Keep the branch as-is (I'll handle it later)
4. Discard this work

Which option?
```

### Step 4: Execute Choice

#### Option 1: Merge and Push to Origin

**Note:** If invoked from code-creation-workflow Phase 6B, Option 1 should not reach this skill — it routes to `/ship` for the full review pipeline. If a user selects "merge and push" directly (bypassing code-creation-workflow), this path skips automated review. Consider suggesting `/ship` instead.

```bash
# Get worktree path before switching
WORKTREE_PATH=$(pwd)

# Switch to base branch
git checkout <base-branch>

# Pull latest
git pull origin <base-branch>

# Merge feature branch
git merge <feature-branch>

# Verify tests on merged result
<test command>

# If tests pass, push to origin
git push origin <base-branch>

# Delete local feature branch
git branch -d <feature-branch>
```

Then: Cleanup worktree (Step 5)

#### Option 2: Push and Create PR

```bash
# Get worktree path before cleanup
WORKTREE_PATH=$(pwd)

# Push branch
git push -u origin <feature-branch>

# Create PR
gh pr create --title "<title>" --body "$(cat <<'EOF'
## Summary
<2-3 bullets of what changed>

## Test Plan
- [ ] <verification steps>
EOF
)"
```

Then: Cleanup worktree (Step 5)

#### Option 3: Keep As-Is

Report: "Keeping branch <name>. Worktree preserved at <path>."

**Don't cleanup worktree.**

#### Option 4: Discard

**Confirm first:**
```
This will permanently delete:
- Branch <name>
- All commits: <commit-list>
- Worktree at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation.

If confirmed:
```bash
WORKTREE_PATH=$(pwd)
git checkout <base-branch>
git branch -D <feature-branch>
```

Then: Cleanup worktree (Step 5)

### Step 5: Session Learnings

After shipping (Options 1 or 2), invoke the `session-learnings` skill to capture patterns, gotchas, and corrections discovered during development. This is not optional — every shipped branch should capture what was learned. Runs in the background.

### Step 6: Cleanup Worktree

**For Options 1, 2, 4:**

**IMPORTANT:** Always clean up worktrees when work is complete.

```bash
# Navigate to main repo first
cd <main-repo-path>

# Remove the worktree
git worktree remove <worktree-path> --force
```

**For Option 3:** Keep worktree.

## Quick Reference

| Option | Merge | Push to Origin | Cleanup Worktree | Cleanup Branch |
|--------|-------|----------------|------------------|----------------|
| 1. Merge and push | ✓ | ✓ | ✓ | ✓ |
| 2. Create PR | - | ✓ (branch) | ✓ | - |
| 3. Keep as-is | - | - | - | - |
| 4. Discard | - | - | ✓ | ✓ (force) |

## Common Mistakes

**Skipping test verification**
- **Fix:** Always verify tests before offering options

**Not pushing after merge**
- **Fix:** Option 1 always pushes to origin after merge

**Leaving worktrees around**
- **Fix:** Clean up worktree for Options 1, 2, and 4

**No confirmation for discard**
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Merge without verifying tests on result
- Delete work without confirmation
- Leave worktrees around after completion

**Always:**
- Push to origin after merging to main
- Clean up worktree after PR creation
- Get typed confirmation for Option 4
