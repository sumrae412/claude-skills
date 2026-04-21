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

