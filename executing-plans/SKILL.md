---
name: executing-plans
description: Execute a written plan
---

# Executing Plans

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


## Overview

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle:** Batch execution with checkpoints for architect review.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Load and Review Plan
1. Read plan file
1a. **Honor the `## References` section as your read-allow-list.** If the plan has one, treat its bulleted file paths as the only prior-art / context files you load before writing code. Do NOT chase adjacent files you "happened to find" — if you need one not listed, surface `REFERENCES_GAP: <path> — <reason>` to the user and let them amend the plan before proceeding. If the section is missing entirely, surface `REFERENCES_MISSING` and ask the plan author to add it (legacy plans without the section fall back to discretion, but flag the gap). If the section says `- (none — greenfield)`, the prior-art context budget is intentionally empty.
2. Review critically - identify any questions or concerns about the plan
3. If concerns: Raise them with your human partner before starting
4. **Premise ambiguity in auto mode: pragmatic-interpret, surface in PR body.** When the plan cites symbols/fields that only partially exist in the target code (e.g. "validate `foo` on classes X and Y" when only Y has `foo`), pragmatic interpretation — validate what's present, apply a sensible defensive check on the other, flag the gap — beats blocking on clarification. Explicitly surface the interpretation in the PR description so reviewers can correct. Do NOT silently drop plan items or fabricate fields that don't exist. Applies only in auto mode; interactive mode should ask.
5. **Main-drift risk for plans touching shared infra:** Before a long-running worktree on shared infra (registries, hook configs, skill files, MEMORY indexes, anything under `skills/` or `~/.claude/`), check for in-flight refactors that could move/delete the paths the plan modifies:

   ```bash
   gh pr list --state open --search "<infra-path>"
   git log origin/main --oneline --since="3 days ago" -- <infra-path>
   ```

   If a structural refactor is in flight (paths being moved/deleted), either ship the current plan faster, OR branch from the in-flight refactor's branch instead of main. See MEMORY `cross_repo_split_brain_salvage.md` for the salvage flow when this guidance was missed.
6. If no concerns: Create TodoWrite and proceed

### Step 1.5: Memory Injection (if dispatching subagents)

If the plan calls for subagent dispatch (explicitly or implicitly via tasks that mention "dispatch" / "implementer" / parallel work), follow `claude-flow/references/memory-injection.md` before the first dispatch:

1. Collect the file list the plan will touch
2. Apply memory-injection (per reference) — produces a `PROJECT GOTCHAS` block
3. Cache the block; prepend it to every subagent prompt's PROJECT CONTEXT area
4. Re-invoke only if the file scope shifts materially mid-plan

Graceful no-op if no MEMORY.md or no domain matches. Skip this step entirely if the plan is purely sequential controller work with no subagent dispatch.

**Why:** without injection, known project gotchas recur silently in fresh subagent context. See `claude-flow/references/memory-injection.md` for the full rationale.

### Step 2: Execute Batch
**Default: First 3 tasks**

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed
5. **Inter-task verification gate:** Before starting the next task, run the full test suite + lint + build check to catch regressions early. If any fail, fix before proceeding. Skip the full suite for the first task in a batch or trivial tasks (config, docs). See `claude-flow/references/subagent-driven-development.md` for the full gate protocol.
6. **Typed dependencies:** When the plan includes typed dependencies (`data`, `build`, `knowledge`), respect them: `data`/`build` edges are strictly sequential; `knowledge` edges are parallelizable (record assumptions). If no typed dependencies are present, execute tasks in plan order.

### Step 3: Report
When batch complete:
- Show what was implemented
- Show verification output
- Say: "Ready for feedback."

### Step 4: Continue
Based on feedback:
- Apply changes if needed
- Execute next batch
- Repeat until complete

### Step 4.5: Phantom-Completion Audit (HARD GATE before Step 5)

Before announcing completion or invoking cleanup, audit the plan's task checklist for **phantom completions** — checkboxes marked `[X]` (or TodoWrite items marked `completed`) that lack corresponding code artifacts.

**Why:** Generic verification (`verification-before-completion`) checks individual claims at fix-time. This step is the orthogonal post-batch check: every task the plan said it would produce must actually exist on disk.

**Procedure:**

1. Re-read the plan's task list. For each `[X]` task, extract the artifacts the task promised:
   - Files listed under `**Files:**` → Create / Modify / Test paths
   - Functions, classes, endpoints, or migration revisions named in step bodies
2. Verify each artifact:
   ```bash
   # Files promised by the plan
   git ls-files <path>            # exists on disk and is tracked
   git diff origin/main -- <path> # actually contains changes
   # Symbols promised by the plan
   rg -n "def <function_name>|class <ClassName>" <path>
   # Migration revisions
   alembic heads                  # new revision present
   ```
3. For each task, classify:
   - **Real:** all promised artifacts present + non-empty diff → leave `[X]`.
   - **Phantom:** task marked `[X]` but artifact missing, file unchanged vs `origin/main`, or symbol absent → downgrade to `[~]` and surface in the report.
   - **Partial:** some artifacts present, some missing → downgrade to `[~]`, list the missing ones.

4. **If any phantom or partial items found:** STOP. Do not proceed to Step 5. Either complete the missing work or amend the plan to remove the unkept promise (with explicit justification). Never silently drop a task.

5. **If all `[X]` tasks verified real:** include the audit summary in the Step 5 hand-off ("Phantom-completion audit: N tasks, all verified — no missing artifacts").

**Skip criteria:** Plans with <3 tasks where every task already had its diff inspected during Step 2's inter-task verification gate.

### Step 5: Complete Development

After all tasks complete and verified (including Step 4.5):
- Announce: "I'm using the cleanup skill to complete this work."
- **REQUIRED SUB-SKILL:** Use `/cleanup`
- Follow that skill to verify tests, present options, execute choice

## When to Stop and Ask for Help

**STOP executing immediately when:**
- Hit a blocker mid-batch (missing dependency, test fails, instruction unclear)
- Plan has critical gaps preventing starting
- You don't understand an instruction
- Verification fails repeatedly

**Ask for clarification rather than guessing.**

## When to Revisit Earlier Steps

**Return to Review (Step 1) when:**
- Partner updates the plan based on your feedback
- Fundamental approach needs rethinking

**Don't force through blockers** - stop and ask.

**When a plan step fails verification:** Use the self-debugging retry loop from `claude-flow` Phase 5 (3 attempts, escalating thinking budget, failure catalog matching, event emission). Do not surface to user until 3 attempts are exhausted.

## Remember
- Review plan critically first
- Follow plan steps exactly
- Don't skip verifications
- Reference skills when plan says to
- Between batches: just report and wait
- Stop when blocked, don't guess
- Never start implementation on main/master branch without explicit user consent

## Multi-Surface Features: Phased Commits with Green Between

For features that span >500 LoC across multiple surfaces (backend + client + infra, or API + UI + migration), land the work as N phase commits on a single branch rather than one monolithic commit. Each phase leaves both (or all) test suites green. Label phases A–F in commit messages.

**Write the inter-phase DAG into the plan doc explicitly:**
- "Phase A — schema + storage foundation"
- "Phase B — service layer (depends on A's schema)"
- "Phase C — parallel critic/worker (independent, can land after A)"
- "Phase D — client UI (depends on B's API shape)"
- "Phase E — integration surface (depends on C's result schema)"
- "Phase F — version bump + changelog + final verify"

Surface integration assumptions **before** merge, not during review.

**Benefits:**
- Reviewable — no 1,600-line diffs. Each phase is a readable commit.
- Bisectable — a regression points to a single phase commit.
- Rollback-per-phase if needed.
- User can review phase-by-phase at their own pace rather than in one mega-session.

**Skip this pattern when:**
- Changes can't individually be green (e.g., atomic refactors that must migrate all call sites at once). Use scaffolding + migration + cleanup as separate PRs instead.
- Total diff is <500 LoC — overhead isn't worth it.

**Verification between phases (hard gate):** full test suite passes after each phase commit. If a phase breaks tests, fix before the next phase — never let green drift across multiple phases.

**Learned from:** ToneGuard v0.3.0 (PR #23). 6 phases (A–F), 1,633 insertions, 22 files, all tests green between each. User reviewed phase-by-phase; CodeRabbit only needed to look at the final diff. Zero regressions between phases.

## Integration

**Required workflow skills:**
- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **superpowers:writing-plans** - Creates the plan this skill executes
- **`/cleanup`** - Complete development after all tasks (branch teardown + session-learnings + repo sync)
