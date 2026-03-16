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
- **Pre-commit:** Hooks run against the full codebase. A commit can fail due to pyright or other errors in unrelated files. Use `--no-verify` only when the failure is confirmed pre-existing or environment-related, not to bypass fixable issues.
- **Worktrees:** A worktree's `.git` is a file pointing at the main repo. Hooks live in the main repo's `.git/hooks`; the worktree uses those hooks when you commit from the worktree.
- **CodeRabbit file limit:** If the PR has more than 150 files (e.g. from main), CodeRabbit may not run. Run the review from a worktree where the diff vs main is only the PR branch files (e.g. 3 files), so the review succeeds.
- **Merge not cleanly createable:** If `gh pr merge <n>` fails with "merge commit cannot be cleanly created", merge main into the branch locally (`git merge origin/main`), push, then retry. If GitHub still reports not mergeable, use `gh pr merge <n> --squash --auto` so the merge runs when checks pass.

**Learned from:** PR 225 (tenant search fix); quick_ci from wrong cwd; CodeRabbit 150-file limit; merge conflict resolution and squash-merge workaround.

## Merge Conflict Resolution

1. Identify conflicting files from git output
2. Open each file and resolve (keep both changes where appropriate)
3. Run tests to verify
4. Stage resolved files and complete merge

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

## Commit Message Format

```
type: short description

Longer explanation if needed.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`
