---
name: executing-plans
description: Execute a written plan
---

# Executing Plans

## Overview

Load plan, review critically, execute tasks in batches, report for review between batches.

**Core principle:** Batch execution with checkpoints for architect review.

**Announce at start:** "I'm using the executing-plans skill to implement this plan."

## The Process

### Step 1: Load and Review Plan
1. Read plan file
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

### Step 5: Complete Development

After all tasks complete and verified:
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
