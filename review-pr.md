---
name: review-pr
description: Hybrid PR review — CodeRabbit broad sweep with defensive skill patterns, conditional deep-dive agents for git history and test logic, then auto-fix and ship to main.
---

# Hybrid PR Review

Review a pull request using CodeRabbit for broad sweep, conditional deep-dive agents for high-value checks, then auto-fix issues and ship to main. Reduces agent calls from ~14 to ~3-5 compared to the old multi-agent pipeline.

## Steps

### Step 1: Eligibility Check

Launch a **Haiku** agent to check PR eligibility:

```bash
gh pr view <PR_NUMBER> --json state,isDraft,author,comments
```

**Stop if any of these are true:**
- PR is closed or merged
- PR is a draft
- PR author is a bot
- PR already has a comment containing "Generated with [Claude Code]"

If ineligible, explain why and stop.

### Step 2: Cherry-Pick Staleness Check

Launch a **Haiku** agent:

```bash
# Fetch latest
git fetch origin main
git fetch origin <pr-branch>

# Get changed files
gh pr diff <PR_NUMBER> --name-only
```

For each changed file:
```bash
git diff origin/main..origin/<pr-branch> -- <file>
```

**Classify each file:**

| Diff Result | Classification | Action |
|-------------|---------------|--------|
| Empty diff (no difference) | Already on main | Skip — flag as "already cherry-picked" |
| PR version is OLDER (reintroduces removed patterns) | Regressive | Flag as "stale — PR re-adds code main already removed" |
| PR has genuinely new code | Reviewable | Include in review |

**Also check for out-of-scope deletions:**
```bash
git diff --diff-filter=D --name-only origin/main..origin/<pr-branch>
```
Flag any deleted files that are unrelated to the PR's stated purpose. A PR that "adds feature X" should not also silently delete unrelated files.

**Report classifications before proceeding.**

If ALL files are already on main or regressive → recommend closing the PR, stop.

### Step 3: CodeRabbit + Defensive Skills Sweep

Invoke the **CodeRabbit review** skill (`/coderabbit review`).

Additionally, instruct the CodeRabbit agent to check the diff against these defensive patterns:

**If PR touches JS/HTML/CSS — check for defensive-ui-flows violations:**
- Guard clauses returning without user feedback (silent early returns)
- State flags (`_isSending`, `isLoading`) without try-catch-finally to guarantee reset
- Overlay UIs using external toast instead of inline feedback within the component
- Async catch handlers with no user feedback (empty catch or console-only)
- DOM elements accessed without null-check (`querySelector` result used directly)
- CSS `--ds-*` tokens used but not defined in `_variables.css`
- `style.display` manipulation instead of `classList.add/remove`
- Missing cache-busting `?v=` params on changed static assets
- CSS utility classes introduced from an external framework (Tailwind, Bootstrap) without the framework being installed (no CDN, no build tool, no PostCSS config)

**If PR touches Python — check for defensive-backend-flows violations:**
- Silent `except: pass` or `except SomeError: pass` with no logging
- Exception handlers catching fewer types than callee raises
- Data destruction (NULL/DROP) without copying first
- Constants/configs duplicated across files instead of single source
- Calling `_private` methods from outside the owning module
- Types in signatures without matching imports
- `str(e)` or tracebacks leaked in HTTP responses
- `datetime` compared as strings instead of parsed objects

### Step 3.5: Tri-Model Debate Review (Conditional)

**Trigger:** If the diff touches 3+ files OR includes security-sensitive code (auth, tokens, encryption, PII), run the full debate team.

If triggered:
1. Save the diff to `/tmp/debate_artifact.md`
2. Save the PR description + CLAUDE.md rules to `/tmp/debate_scope.md`
3. Invoke the debate-team skill (`/debate-team`) with `input-type: diff`
4. The debate team runs DeepSeek Bug-Hunter + GPT-4o Architecture + [Haiku Style if frontend]
5. Merge debate findings into the CodeRabbit results in Step 6

If NOT triggered: skip to Step 4 (standard deep-dive triggers).

### Step 4: Determine Deep-Dive Triggers

No agent needed — grep the diff output.

**Git history triggers** (any match → run git history agent):
- `d-none`, `d-md-`, `display:`, `visibility:`, `opacity:`
- `position:\s*(fixed|absolute|sticky)`, `z-index`
- Lines being removed that were recently added

**Test logic triggers** (any match → run test logic agent):
- Files in `tests/` modified or added
- Assertion keywords in diff (`assert`, `assertEqual`, `expect`)
- New test functions/classes added

### Step 5: Run Conditional Deep-Dive Agents (parallel)

Launch 0-2 **Sonnet** agents in parallel based on Step 4 triggers.

**IF git history triggered →** launch Sonnet agent:
- For each triggered file: `git log --oneline -10 -- <file>` and `git blame <file>` around changed lines
- Check if removed code was intentional (look at commit messages, comments)
- Check for layout/positioning conflicts (fixed navs, z-index stacking)
- Self-score each finding 0-100 using the scoring rubric below
- Only return findings scored >= 60

**IF test logic triggered →** launch Sonnet agent:
- Read the test changes in full context
- Check assertion correctness (exact vs partial matching, URL handling)
- Check mock patterns (patching at source module vs import site)
- Check test isolation (shared state, fixture dependencies)
- Self-score each finding 0-100 using the scoring rubric below
- Only return findings scored >= 60

### Step 6: Merge + Deduplicate

Combine CodeRabbit findings + deep-dive findings.

Deduplicate by file + line range (same file + overlapping lines = same issue, keep the higher-scored one).

If zero issues remain → skip to Step 10 and post a "no issues found" comment.

### Step 7: Re-Check Eligibility

Launch a **Haiku** agent to confirm:
- PR is still open
- No "Generated with [Claude Code]" comment has been posted since we started

### Step 8: Fix Issues

For each issue:
1. Read the flagged code in full file context
2. Apply the fix using the Edit tool
3. If fix is unclear or risky, skip and leave as comment-only

Commit all fixes:
```bash
git add -A
git commit -m "fix: address PR review findings"
```

### Step 9: Run quick_ci.sh (Hard Gate)

```bash
./scripts/quick_ci.sh
```

- If failures → fix the failing tests/lint, re-run
- **Must pass before proceeding** — do NOT skip this step
- Loop until passing or escalate to user if stuck after 3 attempts

### Step 10: Ship

Push fix commit to PR branch and cherry-pick to main:

```bash
# Push to PR branch
git push origin <branch>

# Cherry-pick to main
git checkout main && git pull origin main
git cherry-pick <fix-commit-sha>
git push origin main
```

Post PR comment using `gh pr comment`:

```markdown
### Code review

Found N issues (M fixed):

1. <description> (<source>)
   Fixed in commit `<sha>`
   <link to file and line>

2. <description> (<source>)
   Not auto-fixed — <reason>
   <link to file and line>

Generated with [Claude Code](https://claude.ai/code)
```

If zero issues were found:
```markdown
### Code review

No issues found. Checked for bugs, CLAUDE.md compliance, and defensive patterns.

Generated with [Claude Code](https://claude.ai/code)
```

---

## Scoring Rubric

Deep-dive agents self-score each finding inline:

| Score | Meaning |
|-------|---------|
| 0 | False positive, doesn't stand up to scrutiny, or pre-existing |
| 25 | Might be real, not verified, stylistic without CLAUDE.md basis |
| 50 | Verified real but nitpick, not important relative to PR |
| 75 | Very likely real, will be hit in practice, directly impacts functionality or mentioned in CLAUDE.md |
| 100 | Confirmed real, happens frequently, evidence directly confirms |

Only issues scored >= 60 are returned.

## False Positive Filters

Deep-dive agents should NOT flag:
- Pre-existing issues not introduced by the PR
- Linter/typechecker-catchable issues (imports, formatting, type errors)
- General code quality without CLAUDE.md basis
- Issues on lines the PR didn't modify
- Intentional functionality changes related to the PR's purpose

## When to Recommend Closing

Recommend closing the PR (not merging) if:
- ALL files are already on main or regressive
- The only "new" code reintroduces patterns main already removed
- The branch diverged from main before a major cleanup merged

Post:
```markdown
### Code review

All code from this PR is already on main (cherry-picked in prior sessions) or is regressive
(reintroduces patterns main has since removed). Recommend closing this PR.

Files already on main: [list]
Regressive files: [list]

Generated with [Claude Code](https://claude.ai/code)
```
