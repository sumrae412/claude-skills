---
name: executing-plans
description: Use when you have a written implementation plan to execute in a separate session with review checkpoints
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
4. **Main-drift risk for plans touching shared infra:** Before a long-running worktree on shared infra (registries, hook configs, skill files, MEMORY indexes, anything under `skills/` or `~/.claude/`), check for in-flight refactors that could move/delete the paths the plan modifies:

   ```bash
   gh pr list --state open --search "<infra-path>"
   git log origin/main --oneline --since="3 days ago" -- <infra-path>
   ```

   If a structural refactor is in flight (paths being moved/deleted), either ship the current plan faster, OR branch from the in-flight refactor's branch instead of main. See MEMORY `cross_repo_split_brain_salvage.md` for the salvage flow when this guidance was missed.
5. If no concerns: Create TodoWrite and proceed

### Step 2: Execute Batch
**Default: First 3 tasks**

For each task:
1. Mark as in_progress
2. Follow each step exactly (plan has bite-sized steps)
3. Run verifications as specified
4. Mark as completed
5. **Inter-task verification gate:** Before starting the next task, run the full test suite + lint + build check to catch regressions early. If any fail, fix before proceeding. Skip the full suite for the first task in a batch or trivial tasks (config, docs). See `subagent-driven-development` for the full gate protocol.
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
- Announce: "I'm using the finishing-a-development-branch skill to complete this work."
- **REQUIRED SUB-SKILL:** Use superpowers:finishing-a-development-branch
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

## Integration

**Required workflow skills:**
- **superpowers:using-git-worktrees** - REQUIRED: Set up isolated workspace before starting
- **superpowers:writing-plans** - Creates the plan this skill executes
- **superpowers:finishing-a-development-branch** - Complete development after all tasks
