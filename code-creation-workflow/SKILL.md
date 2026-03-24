---
name: code-creation-workflow
description: PRIMARY workflow for ALL feature development and implementation. SUPERSEDES brainstorming, writing-plans, executing-plans, test-driven-development, plancraft, and feature-dev — do NOT use those individually when this skill is available. Trigger on any request to build, implement, add, create, or fix features. Includes parallel exploration, architecture, TDD, and review as unified phases.
user-invocable: true
---

# Code Creation Workflow

<SUPERSEDES>
This skill is the unified orchestrator for all feature development. When this skill is active, do NOT separately invoke:
- superpowers:brainstorming (absorbed → Phases 1-3)
- superpowers:writing-plans (absorbed → Phase 4)
- superpowers:executing-plans (absorbed → Phase 5)
- superpowers:test-driven-development (absorbed → Phase 5, per-step TDD)
- superpowers:subagent-driven-development (absorbed → Phase 5, parallel dispatch)
- plancraft (absorbed → Phase 4 optional AI review)
- feature-dev:feature-dev (replaced entirely)

These skills' behaviors are already embedded in the phases below. Invoking them separately causes duplicate work and broken flow.
</SUPERSEDES>

## Overview

Agentic multi-phase workflow for building features. Uses parallel subagents for exploration and architecture, TDD for implementation, and parallel reviewers for quality. Replaces manual grep-and-plan with structured agent orchestration.

**Announce:** "Running code-creation-workflow — loading context, exploring codebase, then building with you."

---

## Phase 0: Context Loading

<HARD-GATE>
Load project context before any exploration or coding.
</HARD-GATE>

### Step 1: Load Project Identity

Read the workspace `CLAUDE.md` (slim version — identity, terminology, boundaries, skill pointers).

### Step 2: Load Core Skill

If workspace has a core skill (e.g. `/courierflow-core`), load it for boundaries, terminology, and the trigger matrix.

### Step 3: Classify Task → Load Contextual Skills

Use the trigger matrix (from core skill or `skills/README.md`) to load **only** the skills relevant to this task:

```
Task touches templates/CSS/HTML?     → load UI skill
Task touches routes/services?        → load API skill
Task touches models/migrations?      → load data skill
Task touches external APIs?          → load integrations skill
Task involves git/deploy/PR?         → load git skill
Task involves auth/security?         → load security skill
```

Load **only** what matches. Don't dump everything into context.

### Step 4: Load Enforcement Skills (Always)

- **coding-best-practices** — Always loaded as baseline reference
- **Defensive skill** matching task type:
  - UI work → `defensive-ui-flows`
  - Backend work → `defensive-backend-flows`
  - Both → load both

### Step 5: Conditional Tools

| Condition | Action |
|-----------|--------|
| Feature uses external API | `chub search <service>` → `chub get <doc-id>` |
| Codebase >500 files or unfamiliar | Run `python scripts/generate_repo_outline.py app/` for token-efficient context |
| Need symbol-level precision | Activate Serena project, read relevant memories |
| Small familiar codebase | Skip context tools |

**Token-saving tools available:**
- `generate_repo_outline.py` — Extracts function/class signatures without bodies (use for AI context)
- `semgrep` — Semantic static analysis (catches bugs before review)
- `ast-grep` — AST-based code search (more precise than grep)
- `pyright` — Fast type checking (augments mypy)

### Step 6: Git Check

Verify you're on a feature branch. If on main, create one before proceeding.

---

## Phase 0.5: Bootstrap Project Hooks (One-Time)

<SKIP-CONDITION>
Skip if `.claude/hooks.json` already exists in the project root.
</SKIP-CONDITION>

Auto-generates Claude Code hooks based on the project's detected stack. Runs once per project, then skips on all subsequent sessions.

**Announce:** "No hooks detected — bootstrapping project hooks based on your stack."

### Step 1: Detect Stack

Check for signal files/dirs per the `references/hook-templates.md` reference. Build a stack profile as a set of tags (e.g., `python, alembic, ruff, has-env, service-layer`).

### Step 2: Generate hooks.json

Using the template library:
- **Always** include Tier 1 (universal) hooks — session context, pre-compaction, post-commit memory, worktree guard
- Include Tier 2 hooks where stack tags match conditions (e.g., `has-env` → .env blocker, `ruff` → linter-on-save)
- Write to `$PROJECT/.claude/hooks.json`

### Step 3: Generate Hook Scripts + Config

1. Copy parameterized scripts from `~/claude-config/scripts/hooks/` into `$PROJECT/scripts/hooks/`
2. Generate `scripts/hooks/hook-config.sh` sidecar with:
   - Detected file categories (for post-commit memory updates)
   - Skill suggestions (for session-start context)
   - Linter command and glob pattern
3. Make all scripts executable (`chmod +x`)

### Step 4: Confirm

Output a summary table of generated hooks (trigger → what it does). Ask the user to review `hooks.json` before continuing to Phase 1.

---

## Phase 1: Discovery

Understand the request and decide the workflow path.

```
User says "implement X"
        │
        ▼
   ┌─────────────────────────────────────────────┐
   │ Is this a SMALL change?                      │
   │ (single file, no schema, no new endpoints)   │
   │                                               │
   │ YES → FAST PATH                               │
   │   1. Load defensive skill                     │
   │   2. Make the change                          │
   │   3. Run tests                                │
   │   4. Commit → done                            │
   │                                               │
   │ Has EXISTING PLAN file?                       │
   │                                               │
   │ YES → PLAN PATH                               │
   │   1. Read the plan file                       │
   │   2. Skip to Phase 5 (Implementation)         │
   │   3. Execute the plan                         │
   │                                               │
   │ NO to both → FULL WORKFLOW (continue)         │
   └─────────────────────────────────────────────┘
```

**Fast path criteria:** Typo fix, one-line change, config tweak, single-file edit with no ripple effects. If in doubt, use the full workflow.

---

## Phase 2: Exploration (Parallel Subagents)

### Pre-Exploration: Generate Repo Outline (Token Saver)

Before launching explorers, generate a token-efficient codebase map:

```bash
python scripts/generate_repo_outline.py app/services/ --max-depth 2
```

This provides function/class signatures WITHOUT implementation bodies — dramatically reduces tokens while preserving structure awareness. Share this outline with explorer agents.

### Launch Explorers

Launch 2-3 **code-explorer** subagents in parallel to understand the codebase:

```
┌─────────────────────────────────────────────────────┐
│ Explorer A: "Trace how similar features are         │
│              implemented — find patterns, data flow" │
│                                                      │
│ Explorer B: "Map architecture for [feature area] —  │
│              key files, layers, dependencies"        │
│                                                      │
│ Explorer C: "Analyze test patterns and UI patterns   │
│              used in this area" (if relevant)        │
└─────────────────────────────────────────────────────┘
                    │
                    ▼
   Each agent returns key files + structured findings
                    │
                    ▼
   Read ALL identified files to build deep context
                    │
                    ▼
   Present summary of codebase understanding to user
```

**Subagent dispatch:** Use the Task tool with `subagent_type` of `feature-dev:code-explorer` or `Explore`. Each agent gets a focused prompt describing what to find.

**Serena integration:** When agents identify symbols to trace, use `find_symbol` / `find_referencing_symbols` instead of grep chains. Use `write_memory` to persist discoveries for cross-session continuity.

**Minimum output per explorer:** 5-10 key files, the patterns they follow, and any concerns or constraints discovered.

---

## Phase 3: Clarification (Hard Gate)

<HARD-GATE>
All ambiguities must be resolved before architecture work begins.
</HARD-GATE>

Review exploration findings against the original request. Identify **every** underspecified aspect:

- **Edge cases** — What happens when input is empty, duplicated, or malformed?
- **Error handling** — What should the user see when things fail?
- **Integration points** — Which existing systems does this touch?
- **Scope boundaries** — What is explicitly NOT included?
- **Performance** — Will this hit large datasets or high concurrency?
- **Backward compatibility** — Does this change existing behavior?

Present an organized question list to the user. Group questions by category. Wait for answers before proceeding.

**If no ambiguities exist** (rare — usually means the request is very well-specified), state that explicitly and proceed to Phase 4.

---

## Phase 4: Architecture (Parallel Design + Optional AI Review)

Launch 2 **code-architect** subagents in parallel with different optimization targets:

```
┌──────────────────────────────────────────────────┐
│ Architect A: "Design optimizing for SIMPLICITY — │
│  reuse existing patterns, minimal new files,     │
│  least moving parts"                             │
│                                                   │
│ Architect B: "Design optimizing for CLEAN        │
│  SEPARATION — extensibility, testability,        │
│  clear boundaries between concerns"              │
└──────────────────────────────────────────────────┘
                    │
                    ▼
   Present BOTH architectures to user:
   - Files to create/modify (with line counts)
   - Component designs and responsibilities
   - Data flow (how data moves through the system)
   - Trade-off analysis (what each approach sacrifices)
                    │
                    ▼
   ◆ USER CHOOSES architecture (A, B, or hybrid) ◆
```

**Subagent dispatch:** Use the Task tool with `subagent_type` of `feature-dev:code-architect`. Each gets the exploration findings + clarification answers + a clear optimization directive.

### Write Implementation Plan

After user chooses, write a structured plan using the `writing-plans` skill:
- Numbered steps with specific files and changes
- Test requirements per step
- Dependencies between steps marked clearly

### Optional: PlanCraft AI Review

Triggered when:
- User says "review the plan" or "validate this"
- Task is high-complexity (3+ layers, schema changes, external API integration)

If triggered:
1. Run `plancraft_review.py` (DeepSeek + Codex validation)
2. Present critique and suggestions
3. Revise plan if needed
4. Get user re-approval

If not triggered: Skip. The parallel architect approach already provides design validation through competing proposals.

```
◆ USER APPROVES final plan before implementation ◆
```

---

## Phase 5: Implementation (TDD + Defensive Patterns)

<HARD-GATE>
User must approve the plan before any implementation begins.
</HARD-GATE>

### Create TodoWrite Items

Break the plan into individual TodoWrite items. Mark each complete as you finish it.

### Execute Each Step

For each plan step:

```
1. Write test FIRST (test-driven-development skill)
   - Test the expected behavior, not the implementation
   - Include edge cases identified in Phase 3

2. Implement to make the test pass
   - Follow patterns discovered in Phase 2
   - Apply defensive patterns throughout:
     UI → guard clauses, feedback states, loading/error/success
     Backend → input validation, error handling, no silent swallows

3. Run test → verify green

4. Run static analysis on changed files (catch issues early):
   semgrep --config=.semgrep.yml <changed-files>
   ast-grep scan <changed-directory>

   Fix any ERROR-level issues before proceeding.

5. Mark TodoWrite item complete
```

### Parallel Subagent Dispatch (For Independent Steps)

When the plan has 3+ steps with no dependencies between them:

```
Use subagent-driven-development skill:
  → Dispatch parallel implementation agents
  → Each follows the same TDD + defensive pattern
  → Merge results when all complete
```

Only parallelize truly independent work — shared state or sequential dependencies must stay sequential.

### Best Practices Applied Throughout

| When | Apply |
|------|-------|
| Writing code | Type hints, async patterns, service layer |
| Changing schema | Migration checklist, foreign keys |
| Adding endpoints | Route naming, HTTP methods, rate limiting |
| Modifying JS | Null checks, event handlers, cache bust |
| UI flows | defensive-ui-flows: guard feedback, state flags, overlay inline |
| Backend error handling | defensive-backend-flows: no silent swallows, log or re-raise |
| Data migrations | defensive-backend-flows: copy before delete, reversible ops |
| Cross-module calls | defensive-backend-flows: respect encapsulation, public wrappers |

---

## Phase 6: Quality + Finish

### Parallel Review

Launch 2 **code-reviewer** subagents in parallel:

```
┌──────────────────────────────────────────────────┐
│ Reviewer A: "Check for bugs, logic errors,       │
│  security vulnerabilities, race conditions"      │
│                                                   │
│ Reviewer B: "Check adherence to project          │
│  conventions, patterns, style, and the plan"     │
└──────────────────────────────────────────────────┘
                    │
                    ▼
   Fix any HIGH-priority issues found
```

**Subagent dispatch:** Use the Task tool with `subagent_type` of `feature-dev:code-reviewer`. Each gets the diff + the plan + project conventions.

### Static Analysis Gate

Before verification, run comprehensive static analysis on all changed files:

```bash
# Type checking (fast, catches type errors)
pyright

# Semantic analysis (catches security + logic issues)
semgrep --config=.semgrep.yml --error app/

# Structural analysis (catches anti-patterns)
ast-grep scan app/
```

Fix any ERROR-level issues. Warnings/hints can be addressed later.

### Verification Gate

Invoke `verification-before-completion` skill:
- All tests pass?
- No unintended file changes?
- Implementation matches the original request?
- No regressions in existing functionality?
- Static analysis passes (no ERROR-level issues)?

### Auto-Ship

After verification passes, invoke `/ship` directly — do NOT go through `finishing-a-development-branch`'s option menu. The user chose to implement; shipping is the expected outcome.

`/ship` handles:
1. Commit with conventional message
2. Push and create PR
3. Launch background review agent (CodeRabbit + defensive patterns + CI + cherry-pick to main)
4. Session learnings capture

**No user prompt needed** — verification passing IS the gate. Ship runs automatically.

### Capture Learnings

Invoke `session-learnings` skill:
- What patterns were discovered?
- What defensive rules were applied or should be added?
- Any Serena memories to persist?

---

## Quick Reference: All Phases

| Phase | Name | Key Pattern | Gate |
|-------|------|-------------|------|
| 0 | Context | Trigger matrix → load relevant skills only | None |
| 1 | Discovery | Fast-path escape for small changes | Auto |
| 2 | Exploration | 2-3 parallel code-explorer subagents | None |
| 3 | Clarification | Surface all ambiguities | **User answers** |
| 4 | Architecture | 2 parallel code-architect subagents | **User chooses + approves plan** |
| 5 | Implementation | TDD per step + parallel dispatch | Tests pass |
| 6 | Quality + Auto-Ship | Parallel reviewers → verify → `/ship` (no menu) | **Verification** |

## Skills Invoked Within This Workflow

| Skill | Where Used |
|-------|-----------|
| coding-best-practices | Phase 0 (loaded), Phase 5 (applied) |
| defensive-ui-flows | Phase 0 (loaded), Phase 5 (applied) |
| defensive-backend-flows | Phase 0 (loaded), Phase 5 (applied) |
| writing-plans | Phase 4 (plan creation) |
| executing-plans | Phase 5 (plan execution) |
| test-driven-development | Phase 5 (TDD per step) |
| subagent-driven-development | Phase 5 (parallel independent steps) |
| verification-before-completion | Phase 6 (pre-finish check) |
| `/ship` (direct, no menu) | Phase 6 (auto-ship after verification → review → merge) |
| session-learnings | Phase 6 (capture discoveries) |

## Static Analysis Tools (Automatic)

| Tool | Where Used | Purpose |
|------|------------|---------|
| `generate_repo_outline.py` | Phase 2 (pre-exploration) | Token-efficient codebase context |
| `semgrep` | Phase 5 (per-step), Phase 6 (gate) | Semantic analysis, security checks |
| `ast-grep` | Phase 5 (per-step), Phase 6 (gate) | Structural anti-pattern detection |
| `pyright` | Phase 6 (gate) | Fast type checking |

## Skills Eliminated (Absorbed)

| Former Skill | Absorbed Into |
|-------------|---------------|
| plancraft brainstorming | Phases 1-3 (discovery + exploration + clarification) |
| brainstorming skill | Phases 1-3 (interactive exploration replaces separate brainstorm) |
| PlanCraft full pipeline | Phase 4 optional AI review only (DeepSeek + Codex) |

## Error Recovery

| Situation | Action |
|-----------|--------|
| Explorer agent returns poor results | Re-dispatch with more specific prompt, or explore manually |
| Architecture options both rejected | Ask user what they want different, re-run architects |
| Tests fail during implementation | Fix immediately, don't proceed to next step |
| Reviewer finds critical issue | Fix before finishing, re-run verification |
| User wants to stop mid-workflow | Stop. Summarize state (phase, what's done, what's left). |
| Wrong architecture chosen | Revert to plan, re-architect with new constraints |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Phase 0 context loading | Always load project context first |
| Exploring sequentially instead of parallel | Use 2-3 explorer subagents |
| Coding before clarification | Phase 3 is a hard gate — resolve ambiguities first |
| Single architecture proposal | Always present 2 options (simplicity vs separation) |
| Writing tests after code | TDD — test first, then implement |
| Not finishing the branch | Always run Phase 6 to completion |
| Guessing external API patterns | Fetch docs: `chub get <api-id>` |
| Multiple grep iterations for a symbol | Use Serena `find_symbol` or `find_referencing_symbols` |
| Re-discovering context each session | Use Serena `write_memory` / `read_memory` |
