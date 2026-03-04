---
name: code-creation-workflow
description: Use when creating new features, implementing complex changes, or executing implementation plans. Orchestrates CLAUDE.md context, PlanCraft planning, coding best practices, and branch completion into a single runnable multi-phase workflow.
user-invocable: true
---

# Code Creation Workflow

## Overview

Multi-agent workflow that turns project context (CLAUDE.md) and skills into a repeatable pipeline for creating code. Run this when you want to implement a feature from scratch or execute an existing plan.

**Announce at start:** "I'm running the code-creation-workflow. This will load project context, plan (or execute), apply best practices, and finish the branch."

## Prerequisites

1. **Project context:** If the workspace has `CLAUDE.md`, read it in full before any planning or coding.
2. **PlanCraft:** Verify `~/.claude/scripts/plancraft_review.py` exists and API keys are set (DEEPSEEK_API_KEY, OPENAI_API_KEY) for AI review phases.
3. **Git:** On a feature branch (create one from main if on main).

## Workflow Phases

```text
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 0: Load Context (mandatory)                                       │
│   Read CLAUDE.md → Apply coding-best-practices as reference             │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Plan OR Execute                                                 │
│   • New feature? → Run plancraft (brainstorm → plan → AI review → exec)  │
│   • Existing plan? → Run executing-plans skill directly                 │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 2: Apply Best Practices (throughout)                               │
│   coding-best-practices: TDD, async, migrations, type hints, etc.       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Phase 3: Finish Branch                                                   │
│   finishing-a-development-branch: verify tests → merge/PR/cleanup       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Phase 0: Load Context (Always First)

<HARD-GATE>
Before any planning or coding, load project context.
</HARD-GATE>

1. **Read CLAUDE.md** from the workspace root (e.g. `CLAUDE.md` or `courierflow/CLAUDE.md`).
2. **Extract and apply:**
   - Product identity and scope boundaries
   - Architecture rules (stack, principles, error handling)
   - Code style (Python, JS, UI standards)
   - Data model and terminology
   - Git workflow and boundaries
3. **Load coding-best-practices** skill as a reference. Apply its decision matrix and pre-commit checklist during all code phases.

---

## Phase 1: Plan or Execute

### Path A: New Feature (No Plan Yet)

Use **plancraft** skill for the full flow:

1. **Brainstorm** — Requirements, approaches, design doc, scope
2. **User stories (optional)** — For UI-heavy features, invoke `create-user-stories` from `~/claude_code/skills/create-user-stories/` to generate Gherkin acceptance criteria before or during planning
3. **Writing-Plans** — Invoke `superpowers:writing-plans` with the design doc
4. **AI Review** — DeepSeek + Codex via `plancraft_review.py`
5. **User confirmation** — Present plan, get approval before execution
6. **Execution** — Invoke `superpowers:executing-plans`
7. **Docs cleanup** — Invoke `/docs-cleanup` after execution

**Invoke:** Use the Skill tool with `skill: "plancraft"` (or follow plancraft/SKILL.md step-by-step).

### Path B: Existing Plan (Plan File Present)

If the user points to a plan (e.g. `docs/plans/2026-03-04-merge-home-calendar-plan.md`):

1. **Read the plan** — Verify scope, steps, and file paths
2. **Execute** — Invoke `superpowers:executing-plans` with the plan path
3. **Docs cleanup** — Invoke `/docs-cleanup` after execution

### Optional: Deep Codebase Analysis

For complex or unfamiliar codebases, use subagents before or during planning:

- **code-explorer** — Trace execution paths, map architecture, document dependencies
- **code-architect** — Design feature architecture, component layout, data flow

```text
mcp_task with subagent_type="explore" or "code-architect" when:
  - Codebase is large or unfamiliar
  - Feature touches multiple layers (routes, services, models)
  - User requests architecture review
```

---

## Phase 2: Apply Best Practices (Throughout)

The **coding-best-practices** skill applies at every code touchpoint:

| When | Apply |
|------|-------|
| Writing code | Type hints, async, service layer, TDD |
| Changing schema | Migration, foreign_keys, overlaps |
| Adding endpoints | Route name, HTTP method, rate limiting |
| Modifying JS | Null checks, event handlers, cache bust `?v=N` |
| **Modifying UI flows** | **defensive-ui-flows** — guard feedback, state flags try-catch, overlay inline feedback, multi-step reset |
| **Fixing a UI bug** | **defensive-ui-flows** — update the skill with the bug pattern and fix so it won't recur |
| **Writing backend error handling** | **defensive-backend-flows** — no silent swallows, catch all raised types, copy before delete |
| **Writing data migrations** | **defensive-backend-flows** — copy data before NULL/DROP, reversible downgrade, atomic operations |
| **Cross-module service calls** | **defensive-backend-flows** — respect encapsulation (no `_private` calls), one source of truth for constants |
| **Fixing a backend bug** | **defensive-backend-flows** — update the skill with the bug pattern and fix so it won't recur |
| Before commit | Pre-commit checklist from skill |

Reference: `~/.claude/skills/coding-best-practices/SKILL.md`, `~/.claude/skills/defensive-ui-flows/SKILL.md`, `~/.claude/skills/defensive-backend-flows/SKILL.md`

---

## Phase 3: Finish Branch

After implementation and tests pass:

1. **Verify tests** — `pytest tests/ -v` (or project equivalent)
2. **E2E / UI verification (optional):**
   - **Playwright from stories** — If user stories exist, use `playwright_from_stories.md` from `~/claude_code/skills/` to generate Playwright tests
   - **Website tester** — For full functional checks, run `~/claude_code/skills/website-tester/scripts/test_website.py` against staging URL
3. **Invoke finishing-a-development-branch** skill
4. **Present options** — Merge, PR, keep, discard
5. **Execute choice** — Merge/push, create PR, or cleanup
6. **Cleanup worktree** — If a worktree was used, remove it

---

## How to Run

### Option 1: Invoke by Description

Say one of:

- "Run the code creation workflow for [feature description]"
- "Use code-creation-workflow to implement [plan name]"
- "Create a feature for [X] using the full workflow"

### Option 2: With Existing Plan

- "Execute the plan at docs/plans/2026-03-04-merge-home-calendar-plan.md"
- "Run code-creation-workflow on the merge home calendar plan"

### Option 3: Quick Start (Minimal)

- "Start code-creation-workflow" — Agent will ask what to build

---

## Project-Specific Skills (~/claude_code/skills and ~/claude_code/courierflow/skills)

Skills in these directories are incorporated into the workflow:

| Skill | Location | Use When |
|-------|----------|----------|
| **create-user-stories** | `~/claude_code/skills/create-user-stories/` | UI-heavy features — generate Gherkin acceptance criteria before/during planning |
| **playwright_from_stories** | `~/claude_code/skills/playwright_from_stories.md` | After implementation — convert user stories to Playwright E2E tests |
| **user_stories_from_context** | `~/claude_code/skills/user_stories_from_context.md` | Requirements phase — generate stories from app context |
| **website-tester** | `~/claude_code/skills/website-tester/` | Verification — functional CRUD/form testing against live URL |
| **courierflow-startup-planner** | `~/claude_code/skills/courierflow-startup-planner/` | Strategy/discover phase — business model, mantra, MATT (not code creation) |

If `~/claude_code/courierflow/skills/` exists, load any SKILL.md files there as additional project-specific skills. Includes **defensive-ui-flows** — guard clauses with feedback, state flags with try-catch, overlay inline feedback, multi-step state reset.

### Global Defensive Skills (~/.claude/skills/)

| Skill | Trigger | Core Question |
|-------|---------|---------------|
| **defensive-ui-flows** | Interactive UI with async buttons, modals, multi-step flows | "What does the user see if this fails?" |
| **defensive-backend-flows** | Error handling, data migrations, service functions, cross-module calls, constants | "What happens to the data if this fails halfway?" |

Both skills follow the same update pattern: when you find a new bug, add it to the skill's `evidence.md` and run RED/GREEN testing via `update-skill.md`.

---

## Project-Specific: CourierFlow

When the workspace is CourierFlow (`courierflow/` or similar):

- **CLAUDE.md** is at repo root — read it first
- **Key constraints:** No scope creep, service layer, UserScopedQuery, design system variables only
- **Test command:** `pytest tests/ -v`
- **Skills to use:** `/pre-deploy` before deploy, `/new-migration` for schema changes, `/testing` for test patterns
- **Project skills:** `~/claude_code/skills/` contains create-user-stories, website-tester, playwright_from_stories — use for UI features and E2E verification
- **Archived:** Never touch `_archived/`

---

## Checklist Before Starting

- [ ] CLAUDE.md read (if present)
- [ ] On feature branch (not main)
- [ ] PlanCraft script + API keys verified (for new features with AI review)
- [ ] User has stated what to build or which plan to execute

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping CLAUDE.md | Always load project context first |
| Coding without a plan for complex work | Use plancraft for features with multiple files |
| Ignoring coding-best-practices | Reference it during implementation |
| Not finishing the branch | Always run finishing-a-development-branch at end |
| Executing without user confirmation | PlanCraft requires explicit approval before execution |
| Writing `except: pass` in backend code | Apply defensive-backend-flows — every except must log or re-raise |
| Calling `_private` methods cross-module | Apply defensive-backend-flows — create a public wrapper |
