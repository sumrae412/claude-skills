---
name: ship
description: Ship current work end-to-end — commit, push, create PR, run full review-pr pipeline, merge to main. Use when user says "ship it", "done", "merge it", or wants to deliver finished work.
---

# Ship It

Automated end-to-end pipeline: commit → push → PR → review → merge to main.

**"Shipped" means merged to main.** Do not report work as "shipped" or "done" until the PR is merged into main and main is updated on the remote. Creating a PR is Stage 3 — shipping is not complete until the review agent merges (or the user merges manually).

**Announce at start:** "I'm using the /ship skill to deliver this work."

## Prerequisites

Before starting, verify:
1. You're on a feature branch (not main). If on main, create one first.
2. There are changes to commit (staged or unstaged).
3. `gh` CLI is available and authenticated.

## Stage 1: Commit

1. Run `git status` and `git diff HEAD` to see all changes.
2. Stage files **by name** (never `git add -A` or `git add .`).
3. Generate a conventional commit message (`fix:`, `feat:`, `docs:`, `refactor:`, `test:`).

**If nothing to commit** (already committed): Skip to Stage 2.

## Stage 2: Push

```bash
git push -u origin <branch-name>
```

**If already pushed:** Skip to Stage 3.

## Stage 3: Create PR

```bash
gh pr create --title "<short title under 70 chars>" --body "$(cat <<'EOF'
## Summary
- <what changed>
- <why>

## Test plan
- [ ] <verification steps>

Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Capture the PR number from the output.

**If PR already exists:** Get the PR number with `gh pr view --json number -q .number`.

## Stage 4: Launch Review Agent

Launch the full review-pr workflow in a **background agent using an isolated worktree**:

```
Task tool:
  subagent_type: general-purpose
  isolation: worktree
  run_in_background: true
  prompt: |
    Run the full /review-pr skill on PR #<NUMBER>.
    Follow every step of the review-pr.md workflow:
    1. Eligibility check
    2. Staleness check
    3. CodeRabbit + defensive patterns sweep
    4. Deep-dive triggers
    5. Conditional deep-dive agents
    6. Merge + deduplicate findings
    7. Re-check eligibility
    8. Fix issues found
    9. Run ./scripts/quick_ci.sh (hard gate — must pass)
    10. Ship: push fixes, cherry-pick to main, post PR comment
```

**Important:** The review agent runs in the background so the user can continue working.

## Stage 5: Report Status

After launching the review agent:

1. Report to user:
   ```
   PR #<NUMBER> created: <URL>
   Review agent launched in background — it will:
   - Run CodeRabbit + defensive pattern checks
   - Fix any issues found
   - Run CI (hard gate)
   - Cherry-pick to main and post review comment
   ```

2. **Delegate cleanup to `/cleanup`.** Invoke the `/cleanup` skill, which handles the remaining steps in order:
   - Session learnings (background agent for skill/doc updates)
   - Wait for session-learnings proposals to resolve (user input required)
   - Sync config/skills/memory repos (commit+push any changes from session-learnings)
   - Worktree teardown via `ExitWorktree` tool

**IMPORTANT:** Do not manually clean up the worktree or run session-learnings separately. `/cleanup` handles the correct ordering to avoid the "folder no longer exists" error.

## Error Handling

| Problem | Action |
|---------|--------|
| Tests not run yet | Run `./scripts/quick_ci.sh` first, stop if it fails |
| On main branch | Create feature branch: `git checkout -b fix/descriptive-name` |
| PR already exists | Skip PR creation, get existing PR number |
| Already committed | Skip Stage 1 |
| Already pushed | Skip Stage 2 |
| gh not available | Tell user to install/authenticate `gh` CLI |
| `index.lock` error | Stale lock from crashed git: `rm -f .git/worktrees/<name>/index.lock` |
| Can't checkout main from worktree | `main` is already checked out in main repo. `cd` to main repo path first, then cherry-pick from there |
| `gh pr merge` fails in worktree ("'main' is already used by worktree") | Use GitHub API directly: `gh api -X PUT repos/{owner}/{repo}/pulls/{number}/merge -f merge_method=squash` |
| "Folder no longer exists" | Worktree was cleaned up before session-learnings resolved. Start new session; proposals must be reconstructed from git diff |

## Key Principles

1. **Never ship without review.** The review agent runs automatically.
2. **Background when possible.** User should be free to continue working.
3. **Hard CI gate.** CI must pass in the review agent before merging to main.
4. **Document everything.** Every PR gets a review comment.
5. **Don't clean up early.** Worktree stays until session-learnings are resolved (applied/skipped).
6. **No silent shortcuts.** If you need to deviate from or skip any stage/step in this skill, STOP and tell the user: (a) which step you are skipping, (b) why, (c) what coverage would be lost. Let the user decide. Never silently abbreviate the pipeline.
