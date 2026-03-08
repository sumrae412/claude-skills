# End-to-End Code Shipping Workflow

> **Purpose:** Portable prompt for any AI coding agent (Cursor, Windsurf, Copilot, etc.) to replicate an automated ship-and-review pipeline.
>
> **What it does:** Every time you finish implementing something, this workflow commits your changes, creates a PR, runs a full automated code review, fixes any issues found, runs CI, and merges to main — all without manual intervention.

---

## Scope: Global vs. Project-Level

This prompt has two layers. Set up the **global layer once** (it applies to every project). Customize the **project layer** for each codebase.

### Global Layer (set up once, applies everywhere)

These are universal rules that don't change between projects:

| Component | What It Covers |
|-----------|---------------|
| **The 4-stage pipeline** | Commit → Push → PR → Review (Stages 1-3 + the review structure) |
| **Conventional commits** | `fix:`, `feat:`, `docs:`, `refactor:`, `test:` prefixes |
| **PR format** | Summary bullets, test plan checklist, agent footer |
| **10-step review process** | Eligibility → staleness → sweep → triggers → deep-dive → merge → re-check → fix → CI → ship |
| **Scoring rubric** | 0-100 scale, >= 60 threshold for reporting |
| **False positive filters** | Don't flag pre-existing issues, linter-catchable items, unmodified lines |
| **Finishing options** | Ship it / Keep branch / Discard (3-option menu) |
| **Key principles** | Never ship without review, background when possible, hard CI gate |

**Where to put this:** In Cursor, add to your global `.cursorrules`. In Windsurf, add to global rules. In other tools, add to whatever applies across all your projects.

### Project Layer (customize per codebase)

These change based on the specific project's stack, patterns, and tooling:

| Component | What to Customize | Example (Python/FastAPI) | Example (Node/React) |
|-----------|------------------|--------------------------|---------------------|
| **CI command** | What runs before merge | `./scripts/quick_ci.sh` | `npm run ci` |
| **Test command** | How to verify tests pass | `pytest tests/ -v` | `npm test` |
| **Lint command** | Critical lint check | `flake8 app --select=E9,F63,F7,F82` | `eslint --max-warnings=0` |
| **Defensive patterns (backend)** | Language-specific anti-patterns | Silent `except: pass`, leaked tracebacks | Unhandled promise rejections, missing error middleware |
| **Defensive patterns (frontend)** | UI-specific anti-patterns | Guard clauses without feedback, missing null-checks | Same (framework-agnostic) |
| **CI checks list** | Project-specific validations | SQLAlchemy relationships, migration alignment, template blocks | Type checking, bundle size, E2E tests |
| **Deep-dive triggers** | What patterns warrant git history analysis | CSS visibility/positioning changes | Component render changes, hook dependencies |
| **Base branch** | Where code merges to | `main` | `main`, `develop`, etc. |

**Where to put this:** In Cursor, add to your project-level `.cursorrules`. In Windsurf, add to project rules. Keep it alongside the codebase.

---

## When to Use This

Run this workflow whenever implementation is complete and tests pass. This replaces manual git push, PR creation, and code review steps with a single automated pipeline.

**Trigger phrases:** "ship it", "done", "merge it", "push it", "deliver this", or any indication the user wants to finalize their work.

---

## Prerequisites

Before running this workflow, verify:

1. **Tests pass:** Run the project's CI script (e.g., `./scripts/quick_ci.sh` or equivalent). If it fails, stop and fix before proceeding.
2. **You're on a feature branch:** If on `main`, create a branch first.
3. **GitHub CLI is available:** `gh` must be installed and authenticated.
4. **CodeRabbit CLI is available** (optional but recommended): `coderabbit --version`. Install with `curl -fsSL https://cli.coderabbit.ai/install.sh | sh` if missing.

---

## The Pipeline

### Stage 1: Commit

1. Run `git status` and `git diff HEAD` to see all changes.
2. Generate a commit message using [Conventional Commits](https://www.conventionalcommits.org/) format:
   - `fix:` for bug fixes
   - `feat:` for new features
   - `docs:` for documentation
   - `refactor:` for restructuring without behavior change
   - `test:` for test additions/changes
3. Stage files **by name** (never `git add -A` or `git add .` — avoid committing secrets or unintended files).
4. Commit. End the message with a co-author line for traceability:
   ```
   Co-Authored-By: <Agent Name> <noreply@example.com>
   ```

### Stage 2: Push

1. If on `main`, create a branch: `git checkout -b fix/descriptive-name` or `feat/descriptive-name`.
2. Push with tracking: `git push -u origin <branch-name>`.

### Stage 3: Create PR

Create a pull request using `gh pr create`:

```bash
gh pr create --title "<short title under 70 chars>" --body "$(cat <<'EOF'
## Summary
- <bullet 1: what changed>
- <bullet 2: why>
- <bullet 3: any notable decisions>

## Test plan
- [ ] <verification step 1>
- [ ] <verification step 2>

Generated with [AI Agent]
EOF
)"
```

Capture the PR number from the output — you'll need it for Stage 4.

### Stage 4: Automated Code Review

This is the core of the pipeline. Run these 10 steps on the PR you just created.

**If your framework supports background/parallel execution**, run this stage in the background so the user can continue working. If not, run it inline.

**If your framework supports isolated workspaces** (git worktrees, separate checkouts), run this in an isolated copy to avoid conflicting with the user's working directory.

---

## The 10-Step Review Process

### Step 1: Eligibility Check

```bash
gh pr view <PR_NUMBER> --json state,isDraft,author,comments
```

**Stop the review if:**
- PR is closed or merged
- PR is a draft
- PR author is a bot
- PR already has a comment containing "Generated with [" (already reviewed)

### Step 2: Staleness Check

Verify the PR's changes are actually new relative to main:

```bash
git fetch origin main
git fetch origin <pr-branch>
gh pr diff <PR_NUMBER> --name-only
```

For each changed file, compare:
```bash
git diff origin/main..origin/<pr-branch> -- <file>
```

Classify each file:

| Diff Result | Classification | Action |
|-------------|---------------|--------|
| Empty diff (identical to main) | Already merged | Skip |
| PR version is older than main | Regressive | Flag as stale |
| Genuinely new code | Reviewable | Include in review |

Also check for out-of-scope deletions:
```bash
git diff --diff-filter=D --name-only origin/main..origin/<pr-branch>
```

Flag any deleted files unrelated to the PR's purpose.

**If ALL files are already on main or regressive:** Recommend closing the PR. Post a comment explaining why and stop.

### Step 3: Broad Code Review Sweep

Run a code review tool if available (e.g., CodeRabbit: `coderabbit review --plain`).

Additionally, check the diff for defensive patterns. **The patterns below are examples — customize for your stack.**

> **🔧 PROJECT-LEVEL:** Replace these checklists with your project's language and framework-specific anti-patterns.

**For JavaScript/HTML/CSS changes:**
- Guard clauses that return without user feedback (silent early returns)
- State flags (`_isSending`, `isLoading`) without try-catch-finally to guarantee reset
- Overlay UIs using external toast instead of inline feedback
- Async catch handlers with no user feedback (empty catch or console-only)
- DOM elements accessed without null-check (`querySelector` result used directly)
- CSS tokens used but not defined in the design system variables
- `style.display` manipulation instead of `classList.add/remove`
- Missing cache-busting params on changed static assets

**For Python changes:**
- Silent `except: pass` or `except SomeError: pass` with no logging
- Exception handlers catching fewer types than callee raises
- Data destruction (NULL/DROP) without copying first
- Constants/configs duplicated across files instead of single source
- Calling private methods from outside the owning module
- Types in signatures without matching imports
- `str(e)` or tracebacks leaked in HTTP responses
- `datetime` compared as strings instead of parsed objects

### Step 4: Determine Deep-Dive Triggers

> **🔧 PROJECT-LEVEL:** The trigger patterns below are examples. Add your own based on what causes bugs in your codebase.

Grep the diff for patterns that warrant deeper analysis:

**Git history triggers** (any match → run git history analysis):
- `d-none`, `display:`, `visibility:`, `opacity:`
- `position:\s*(fixed|absolute|sticky)`, `z-index`
- Lines being removed that were recently added

**Test logic triggers** (any match → run test analysis):
- Files in `tests/` modified or added
- Assertion keywords (`assert`, `assertEqual`, `expect`)
- New test functions/classes added

### Step 5: Conditional Deep-Dive Analysis

Run 0-2 focused analyses based on Step 4 triggers. These can run in parallel.

**If git history triggered:**
- For each triggered file: `git log --oneline -10 -- <file>` and `git blame <file>` around changed lines
- Check if removed code was intentional
- Check for layout/positioning conflicts
- Score each finding 0-100 (only report findings >= 60)

**If test logic triggered:**
- Read test changes in full context
- Check assertion correctness (exact vs partial matching)
- Check mock patterns (patching at correct location)
- Check test isolation (shared state, fixture dependencies)
- Score each finding 0-100 (only report findings >= 60)

**Scoring rubric:**

| Score | Meaning |
|-------|---------|
| 0 | False positive or pre-existing issue |
| 25 | Might be real, not verified |
| 50 | Real but nitpick |
| 75 | Likely real, impacts functionality |
| 100 | Confirmed, happens frequently |

### Step 6: Merge and Deduplicate Findings

Combine all findings from Steps 3-5. Deduplicate by file + line range (same file + overlapping lines = same issue; keep higher-scored one).

**If zero issues remain:** Skip to Step 10 and post a clean review comment.

### Step 7: Re-Check Eligibility

Before making changes, confirm:
- PR is still open
- No review comment has been posted since we started

### Step 8: Fix Issues

For each issue found:
1. Read the flagged code in full file context
2. Apply the fix
3. If fix is unclear or risky, skip and leave as comment-only

Commit all fixes:
```bash
git add <fixed-files>
git commit -m "fix: address PR review findings"
```

### Step 9: Run CI (Hard Gate)

> **🔧 PROJECT-LEVEL:** Replace with your project's CI command.

Run the project's CI/test suite:

```bash
./scripts/quick_ci.sh   # or: pytest, npm test, cargo test, etc.
```

**This is a hard gate:**
- If failures → fix them, re-run
- Must pass before proceeding
- Loop up to 3 attempts, then escalate to user

### Step 10: Ship to Main

Push fixes and merge to main:

```bash
# Push to PR branch
git push origin <branch>

# Cherry-pick to main
git checkout main && git pull origin main
git cherry-pick <fix-commit-sha>
git push origin main
```

Post a PR comment summarizing the review:

```markdown
### Code review

Found N issues (M fixed):

1. <description> (<source: CodeRabbit/defensive-patterns/git-history/test-logic>)
   Fixed in commit `<sha>`

2. <description> (<source>)
   Not auto-fixed — <reason>

Generated with [AI Agent]
```

If zero issues:
```markdown
### Code review

No issues found. Checked for bugs, project rule compliance, and defensive patterns.

Generated with [AI Agent]
```

---

## False Positive Filters

Do NOT flag:
- Pre-existing issues not introduced by the PR
- Linter/typechecker-catchable issues (let tools handle those)
- General code quality without project rule basis
- Issues on lines the PR didn't modify
- Intentional functionality changes related to the PR's purpose

---

## Integration with Development Workflow

This shipping pipeline should be the **final step** of any development workflow:

```
Feature work complete
        │
        ▼
  Run test suite → must pass
        │
        ▼
  Present options to user:
    1. Ship it (default) → runs this entire pipeline
    2. Keep branch as-is
    3. Discard work
        │
        ▼
  User says "ship it" (or equivalent)
        │
        ▼
  Stage 1: Commit (conventional commits)
  Stage 2: Push (feature branch)
  Stage 3: Create PR (gh pr create)
  Stage 4: 10-step review (background if possible)
        │
        ▼
  Code is on main, PR is documented
```

---

## Adapting to Your Framework

| Capability | If Available | If Not Available |
|-----------|-------------|-----------------|
| Background agents | Run Stage 4 in background | Run Stage 4 inline |
| Isolated workspaces | Use git worktree for review | Review in same workspace (careful with conflicts) |
| CodeRabbit CLI | Use for Step 3 broad sweep | Use manual diff review |
| `gh` CLI | Use for PR creation/comments | Create PR through web UI |
| Parallel execution | Run deep-dives in parallel | Run sequentially |

---

## Quick CI Checks (Adapt to Your Project)

The CI gate (Step 9) should cover at minimum:

1. **Syntax validation** — no broken imports or syntax errors
2. **Critical lint** — undefined names, syntax errors (not style)
3. **Core tests** — unit and integration tests pass
4. **Model/schema validation** — database models match migrations
5. **Template/UI validation** — no orphaned scripts, valid block names

Adapt the specific checks to your project's stack and tooling.

---

## Key Principles

1. **Never ship without review.** The review runs automatically — no manual trigger needed.
2. **Background when possible.** The user should be free to continue working while review runs.
3. **Fix what you find.** Don't just comment — fix issues automatically when the fix is clear.
4. **Hard CI gate.** CI must pass. No exceptions. No skipping.
5. **Score and filter.** Not every finding is worth reporting. Score rigorously, report only meaningful issues.
6. **Cherry-pick to main.** Don't leave code sitting in PR branches. Get it to main.
7. **Document everything.** Every PR gets a review comment, even if no issues were found.
