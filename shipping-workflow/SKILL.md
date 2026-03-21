---
name: shipping-workflow
description: End-to-end code shipping pipeline — commit (conventional), push, create PR, run automated 10-step code review, fix issues, run CI, merge to main. Use when implementation is complete and the user wants to finalize work (e.g. "ship it", "done", "merge it", "push it", "deliver this") or when creating a PR and running full review-and-ship.
---

# Shipping Workflow

Automated ship-and-review pipeline: commit → push → PR → 10-step review → fix → CI → merge → session-learnings. Run when tests already pass and the user indicates they want to ship.

## When to Use

- Implementation is complete and tests pass.
- User says "ship it", "done", "merge it", "push it", "deliver this", or similar.
- You are finishing a branch and the user chooses "Ship it" (from finishing-a-development-branch).

## Prerequisites

Before starting:

1. **Tests pass** — Run project CI (e.g. `./scripts/quick_ci.sh`). If it fails, stop and fix first.
2. **Feature branch** — If on `main`, create a branch: `git checkout -b fix/name` or `feat/name`.
3. **GitHub CLI** — `gh` installed and authenticated.
4. **CodeRabbit CLI** (optional) — `coderabbit --version`. Install: `curl -fsSL https://cli.coderabbit.ai/install.sh | sh`.

## The 4-Stage Pipeline

### Stage 1: Commit

1. Run `git status` and `git diff HEAD` to see changes.
2. Commit message: [Conventional Commits](https://www.conventionalcommits.org/) — `fix:`, `feat:`, `docs:`, `refactor:`, `test:`.
3. Stage **by file name** (never `git add -A` or `git add .`).

### Stage 2: Push

- If on `main`, create branch first. Then: `git push -u origin <branch-name>`.

### Stage 3: Create PR

```bash
gh pr create --title "<short title under 70 chars>" --body "$(cat <<'EOF'
## Summary
- <what changed>
- <why>
- <notable decisions>

## Test plan
- [ ] <step 1>
- [ ] <step 2>

Generated with [AI Agent]
EOF
)"
```

Capture the PR number for Stage 4.

### Optional: Monitor CI with `/loop`

After pushing, use `/loop` to poll CI without context-switching:

```text
/loop 5m check the GitHub Actions status on PR #<number>
```

Fires in the background and reports when CI passes or fails. Session-scoped — stops when you exit.

### Stage 4: Automated Code Review

Run the **10-step review process** on the PR. Prefer running this in the background or in an isolated workspace (e.g. git worktree) so the user can keep working.

**Full procedure:** See [reference.md](reference.md) for the 10 steps (eligibility → staleness → sweep → deep-dive triggers → conditional analysis → merge findings → re-check → fix → CI gate → ship), scoring rubric, false positive filters, and project-level customization (CI command, defensive patterns, deep-dive triggers).

### Stage 5: Session Learnings

After merge (or after review if merge is deferred), invoke the `session-learnings` skill to capture what was learned:
- New patterns, defensive rules, or gotchas discovered
- Skill or CLAUDE.md updates needed
- Memories to persist

This runs in the background and does not block the user.

## Key Principles

1. **Never ship without review** — Review runs automatically; no manual skip.
2. **Background when possible** — User can continue while review runs.
3. **Fix what you find** — Auto-fix when clear; comment-only when risky or unclear.
4. **Hard CI gate** — CI must pass before merge. No exceptions.
5. **Score and filter** — Report only meaningful issues (e.g. score ≥ 60).
6. **Cherry-pick to main** — Push fixes to PR branch, then cherry-pick to main and push.
7. **Document** — Post a review comment on the PR (issues found/fixed or "No issues found").
8. **Always capture learnings** — Run `session-learnings` after every ship. No silent skips.
9. **Skills are contracts** — Follow every step as written. If you need to deviate (skip a step, substitute a lighter tool, reduce scope), pause and tell the user: (a) which step, (b) why skipping, (c) what you would miss. Let the user decide. No silent shortcuts.

## Integration with Finishing Options

When implementation is complete, present:

1. **Ship it** (default) → Run this full pipeline.
2. **Keep branch** — No commit/PR/ship.
3. **Discard** — Revert or abandon work.

Only run the pipeline after the user chooses "Ship it" (or equivalent).

## Project-Level Customization

Per-repo settings live in project rules or in the reference. Customize: CI command, test/lint commands, defensive-pattern checklists (backend/frontend), deep-dive trigger patterns, base branch. See [reference.md](reference.md) for the checklist and examples (Python/FastAPI, Node/React).
