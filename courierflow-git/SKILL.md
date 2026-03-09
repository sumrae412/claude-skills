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
