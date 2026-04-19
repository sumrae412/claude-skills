---
name: courierflow-git
description: Git workflow, branching, deploys, PRs. Load when committing, deploying, or managing branches.
---

# CourierFlow Git Workflow

## Branch Rules

**Each chat session works on its own branch.**

1. **Create feature branch at session start:**
   ```bash
   git checkout main && git pull origin main
   git checkout -b <descriptive-branch-name>
   ```

2. **Check current branch before any work** — If on `main`, create branch first

3. **Cherry-pick to main when complete:**
   ```bash
   git checkout main && git pull origin main
   git cherry-pick <commit-sha>
   git push origin main
   ```

4. **Do NOT create PRs** unless user explicitly asks

## Pre-Deploy Protocol

**Before every deployment:**

1. Pull latest: `git fetch origin main`
2. Merge: `git merge origin/main`
3. Resolve conflicts before proceeding
4. Run `/pre-deploy`
5. Only then `/deploy`

## Worktree Cleanup (Mandatory)

**Gotcha:** A worktree cannot check out `main` if the main repo already has it checked out. When using `gh pr merge` from a worktree, the post-merge branch cleanup may show an error — this is harmless; the merge itself succeeds. Verify with `gh pr view <number> --json state`.

**`gh pr merge --delete-branch` + worktrees:** If the branch being merged is any worktree's HEAD, the remote delete succeeds but the local delete fails:

```
✗ failed to delete local branch <name>:
  Cannot delete branch '<name>' checked out at '/path/to/worktree'
```

Workaround: switch the worktree off the branch BEFORE merging, or skip `--delete-branch` and delete deliberately in a teardown step (`git worktree remove … && git branch -d …`). See `memory/gotcha_gh_pr_merge_delete_branch_worktree.md`.

If you used a worktree, clean it up:

```bash
# From main repo (not worktree)
git worktree remove --force .claude/worktrees/<name>
git branch -D <worktree-branch>
```

## Worktree Development Warning

When developing in a worktree, a running `uvicorn` server in the main repo will NOT serve worktree code. Either:
1. Stop the main repo server and start one from the worktree, or
2. Test via `pytest` rather than live requests

This caused confusion during debugging when production-like errors could not be reproduced locally because the server was running from the wrong directory.

## Railway SSH Debugging Gotchas

- **Quoting:** `railway ssh` does not handle complex quoting well. For multi-line Python scripts, base64-encode the script and pipe: `echo <b64> | base64 -d | python3`.
- **Missing packages:** The Railway SSH container may not have all pip packages installed. Common missing: `asyncpg`. Install with `pip3 install <package>` before running scripts.
- **Internal DB URL:** The `DATABASE_URL` uses an internal hostname (`*.railway.internal`). Use `railway ssh` to run DB commands from inside the Railway network.
- **Column existence:** PostgreSQL only errors on missing columns when it actually reads them. A `SELECT *` may return 0 rows without error if no rows match, masking a missing-column bug.

## Version Tags

```bash
# List tags
git tag -l

# Revert to tag
git checkout pre_alpha_v1

# Create new tag
git tag -a <tag-name> -m "Description"
git push origin <tag-name>
```

## CI and pre-commit gotchas

- **quick_ci.sh:** Must be run from the repository root. Running from a worktree subdirectory or wrong cwd causes `FileNotFoundError`, "App directory not found", or `ModuleNotFoundError: No module named 'app'`. Always `cd` to repo root (or use absolute path) before `./scripts/quick_ci.sh`.
- **Pre-commit:** Hooks run against the full codebase. A commit can fail due to pyright or other errors in unrelated files. **Fix the root cause** — pre-existing bugs are still bugs. Use `--no-verify` only for confirmed environment-related failures (e.g. missing local tool, DB not running), never to skip fixable code issues.
- **Worktrees:** A worktree's `.git` is a file pointing at the main repo. Hooks live in the main repo's `.git/hooks`; the worktree uses those hooks when you commit from the worktree.
- **CodeRabbit file limit:** If the PR has more than 150 files (e.g. from main), CodeRabbit may not run. Run the review from a worktree where the diff vs main is only the PR branch files (e.g. 3 files), so the review succeeds.
- **Merge not cleanly createable:** If `gh pr merge <n>` fails with "merge commit cannot be cleanly created", merge main into the branch locally (`git merge origin/main`), push, then retry. If GitHub still reports not mergeable, use `gh pr merge <n> --squash --auto` so the merge runs when checks pass.

**Learned from:** PR 225 (tenant search fix); quick_ci from wrong cwd; CodeRabbit 150-file limit; merge conflict resolution and squash-merge workaround.

## Merge Conflict Resolution

1. Identify conflicting files from git output
2. Open each file and resolve (keep both changes where appropriate)
3. Run tests to verify
4. Stage resolved files and complete merge

## Squash-Merge Branch Recovery

When a parent PR is squash-merged into main but your branch has commits from before the squash, a normal rebase fails with many conflicts (because git replays all original commits against the squash). Use `--onto` to replay only your new commits:

```bash
# Only replay the last N commits (your fixes) onto main
git rebase --onto origin/main HEAD~1
```

**When to use:** Your branch was based on a feature branch that got squash-merged. `git log` shows the original feature commits plus your fix commits, but main only has the single squash commit.

### Stacked-PR: foundation merged mid-session

When a foundation PR (#A) is squash-merged with `--delete-branch` while you're still shipping the follow-up (#B), `gh pr create --base feat/A` fails with `Base ref must be a branch` — the remote branch is gone. Plain `git rebase origin/main` produces conflict hell (the squash has a different patch ID than each individual pre-fork commit). Surgical fix: capture the foundation tip SHA **before starting the follow-up**, then use the three-argument form to replay only commits strictly after the fork point:

```bash
# <A-tip-sha> = the foundation branch's tip at the moment you branched off
git rebase --onto origin/main <A-tip-sha> <B-branch>
git push --force-with-lease
gh pr create --base main --head <B-branch> ...
```

See `memory/pattern_rebase_onto_recovery_stacked_pr_base_deleted.md`.

## Dev Session Monitoring with `/loop`

Use Claude Code scheduled tasks to poll long-running ops without leaving your session:

```text
# Watch a Railway deploy
/loop 2m check if the Railway deploy finished and report status

# Monitor CI after push
/loop 5m check the GitHub Actions status on PR #<number>

# One-time reminder
remind me in 30 minutes to review the migration
```

Tasks are session-scoped (gone when you exit). Use for deploy watching, CI babysitting, and time-boxed reminders — not for app-level scheduling.

## Railway Commands

```bash
# Run Python script on Railway
railway run python /path/to/script.py
```

## Release Automation

```bash
# Create release (auto-detects version bump from commits)
python scripts/release.py --auto --dry-run
python scripts/release.py --patch  # or --minor, --major

# Rollback deployment
python scripts/rollback.py deploy --dry-run
python scripts/rollback.py migration --steps 1 --dry-run
python scripts/rollback.py both --steps 1

# Canary deployment
python scripts/canary_deploy.py \
    --production-url https://app.courierflow.com \
    --canary-url https://canary.courierflow.com \
    --duration 600 --dry-run

# Vulnerability scan
python scripts/vulnerability_scan.py --severity-threshold high --format json
```

## PR Shape: Foundation + One Worked Example

When rolling out a pattern that will apply to N call-sites, prefer the **foundation + one worked example** PR shape — ship the primitive plus one representative caller in PR 1; follow-up per-site PRs become tiny mechanical diffs. Validated on PRs #384/#385. See `memory/pattern_foundation_plus_one_worked_example_pr_shape.md`.

## Commit Message Format

```
type: short description

Longer explanation if needed.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`
