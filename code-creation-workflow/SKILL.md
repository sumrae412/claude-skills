---
name: code-creation-workflow
description: PRIMARY workflow for ALL feature development and implementation. SUPERSEDES brainstorming, writing-plans, executing-plans, test-driven-development, plancraft, and feature-dev — do NOT use those individually when this skill is available. Trigger on any request to build, implement, add, create, or fix features. Includes parallel exploration, architecture, TDD, and review as unified phases.
user-invocable: true
---

# Code Creation Workflow

**SUPERSEDES (do not invoke separately):** brainstorming → Phases 1-3, writing-plans → Phase 4, executing-plans → Phase 5, test-driven-development → Phase 5, plancraft → Phase 4 optional review, feature-dev:feature-dev → replaced entirely.

---

## Phase 0: Context Loading

**Announce:** "Running code-creation-workflow — loading context, then building."

1. Read workspace `CLAUDE.md` (identity, boundaries, terminology, skill pointers).
2. Load core skill if present (e.g. `/courierflow-core`) for trigger matrix and boundaries.
3. Load **only** the contextual skills that match the task:
   - UI / templates / CSS → UI skill
   - Routes / services → API skill
   - Models / migrations → data skill
   - External APIs → integrations skill
   - Git / deploy / PR → git skill
   - Auth / security → security skill
4. Always load: `coding-best-practices` + the matching defensive skill (`defensive-ui-flows`, `defensive-backend-flows`, or both).
5. Verify you're on a feature branch. If on main, create one before proceeding.

---

## Phase 1: Discovery — Choose Workflow Path

Classify the request before doing any exploration:

**FAST PATH** — single-file change, no schema change, no new endpoints, no ripple effects (typo, config tweak, one-liner). If all three are true: load the defensive skill, make the change, run tests, commit. Done.

**PLAN PATH** — an existing plan file was provided. Read it, skip to Phase 5.

**FULL WORKFLOW** — everything else. Continue through all phases below.

When in doubt, use FULL WORKFLOW.

---

## Phase 2: Exploration

Scale subagent count to task complexity:
- Focused task (1 area of codebase) → 1 explorer
- Broad task (multiple layers/areas) → 2 explorers
- Unfamiliar area + broad task → 3 explorers

Dispatch parallel `code-explorer` subagents using the Agent tool. Each gets a distinct, focused prompt:

- Explorer A: Trace how similar features are implemented — patterns, data flow, key files.
- Explorer B (if needed): Map architecture for the feature area — layers, dependencies, entry points.
- Explorer C (if needed): Analyze test patterns and UI conventions used in this area.

After all agents return: read the identified key files yourself. **Cap at 10-15 files** — if explorers return more, prioritize the most relevant based on their summaries and read others on-demand during implementation. This prevents context window exhaustion.

Present a concise summary of findings to the user before proceeding.

Minimum output per explorer: 5-10 key files, the patterns they follow, any constraints or concerns.

---

## Phase 3: Clarification

<HARD-GATE>
All ambiguities must be resolved before architecture work begins.
</HARD-GATE>

Review exploration findings against the request. Check for gaps in:
- Edge cases (empty input, duplicates, malformed data)
- Error handling (what does the user see on failure?)
- Integration points (which existing systems are touched?)
- Scope boundary (what is explicitly NOT included?)
- Performance (large datasets, concurrency?) — if flagged, carry forward as a non-functional requirement for Phase 4
- Backward compatibility (does this change existing behavior?)

**If the request is well-specified and exploration answered all gaps:** state that explicitly and proceed to Phase 4. Do not manufacture questions.

**If ambiguities exist:** Group questions by dependency. Ask independent questions together in one message (max 3). Only serialize when an answer materially changes what you ask next.

---

## Phase 4: Architecture

Scale to complexity:
- Simple task (clear single approach) → propose one design, explain rationale, get approval.
- Non-trivial task → dispatch 2 parallel `code-architect` subagents:
  - Architect A: Optimize for **simplicity** — reuse existing patterns, minimal new files, fewest moving parts.
  - Architect B: Optimize for **clean separation** — extensibility, testability, clear boundaries.

Each architect returns: files to create/modify, component responsibilities, data flow, trade-offs.

Present both designs to the user. User chooses A, B, or hybrid.

```
◆ USER CHOOSES architecture ◆
```

### Write Implementation Plan

After user chooses, write a structured plan directly (no separate skill invocation):
- Numbered steps with specific files and line-level changes
- Test requirements per step
- Dependencies between steps marked clearly

### Optional AI Review (PlanCraft)

Trigger when: user requests it, OR task meets any two of: 3+ architectural layers, schema changes, external API integration.

If triggered: run `plancraft_review.py`, present critique, revise plan if needed, get re-approval.

```
◆ USER APPROVES final plan before implementation ◆
```

---

## Phase 5: Implementation (TDD)

<HARD-GATE>
User must approve the plan before any implementation begins.
</HARD-GATE>

Create TodoWrite items from the plan. Mark each complete as you finish.

**For each step:**
1. Write the test first — test expected behavior, not implementation. Include edge cases from Phase 3.
2. Implement to make the test pass. Follow patterns from Phase 2. Apply defensive patterns:
   - UI: guard clauses, loading/error/success states, no silent failures
   - Backend: input validation, log or re-raise errors, no silent swallows
3. Run tests → verify green before moving to the next step.
4. Mark the TodoWrite item complete.

**Parallel dispatch** (for 4+ independent steps with no shared state): Before dispatching, explicitly list each step's file inputs/outputs and confirm no overlap. If uncertain, default to sequential. Dispatch parallel implementation agents using the Agent tool — each follows the same TDD + defensive pattern. Merge results when all complete.

Rationale for 4+ threshold: 3 steps is common for small features where agent coordination overhead exceeds the parallelism benefit.

**Best practices throughout:**

| When | Apply |
|------|-------|
| Writing code | Type hints, async patterns, service layer |
| Changing schema | Migration checklist, foreign keys, backfill paired with forward fix |
| Adding endpoints | Route naming, HTTP methods, rate limiting |
| Modifying JS | Null checks, event handlers, cache bust |
| UI flows | defensive-ui-flows: guard feedback, state flags, overlay inline |
| Backend errors | defensive-backend-flows: no silent swallows, log or re-raise |
| Data migrations | defensive-backend-flows: copy before delete, reversible ops |

---

## Phase 6: Quality + Ship

### Parallel Review

Scale to complexity:
- Small/targeted change → single reviewer pass (bugs + conventions combined)
- Full feature → 2 parallel `code-reviewer` subagents:
  - Reviewer A: Bugs, logic errors, security vulnerabilities, race conditions.
  - Reviewer B: Adherence to project conventions, patterns, style, and the plan.

Each reviewer gets: the diff + the plan + project conventions. Fix all issues found, including pre-existing bugs (fix-what-you-find policy).

### Verification Gate

Run `verification-before-completion` skill. All must be true before proceeding:
- All tests pass (including pre-existing failures fixed)
- CI passes clean (no `--no-verify` workarounds)
- No unintended file changes
- Implementation matches the original request
- No regressions in existing functionality

### Ship (With User Confirmation)

After verification passes, ask: "Verification clean. Ready to ship — shall I run `/ship`?"

When confirmed, invoke `/ship` directly (not `finishing-a-development-branch` menu). `/ship` handles:
1. Commit with conventional message
2. Push and create PR
3. Launch background review agent
4. Session learnings capture

**Why confirmation instead of auto-ship:** Verification confirms correctness, not intent. The user may want to review the diff, adjust the PR description, or batch changes. One question is low ceremony and preserves control.

### Capture Learnings

Invoke `session-learnings` skill:
- What patterns were discovered?
- What defensive rules were applied or should be added?
- Any gotchas to persist in MEMORY.md?

---

## Quick Reference

| Phase | Name | Key Pattern | Gate |
|-------|------|-------------|------|
| 0 | Context | Load CLAUDE.md + relevant skills only | None |
| 1 | Discovery | Fast-path / plan-path / full-workflow | Auto |
| 2 | Exploration | 1-3 parallel explorers (scaled to complexity) | None |
| 3 | Clarification | Batch independent questions; fast-track if well-specified | User answers |
| 4 | Architecture | 1 or 2 architects (scaled); user chooses; plan written | User approves plan |
| 5 | Implementation | TDD per step; parallel dispatch at 4+ independent steps | Tests pass |
| 6 | Quality + Ship | Scaled reviewers; verify; confirm with user; `/ship` | User confirms |

## Error Recovery

| Situation | Action |
|-----------|--------|
| Explorer returns poor results | Re-dispatch with narrower prompt, or explore manually with Grep/Glob/Read |
| Both architectures rejected | Ask what's missing or wrong, re-run with new constraints |
| Tests fail during implementation | Fix immediately — do not proceed to the next step |
| Reviewer finds critical issue | Fix before finishing, re-run verification |
| User wants to stop mid-workflow | Stop. Summarize: current phase, what's done, what remains, next step to resume |
| Wrong architecture chosen | Revert uncommitted work, re-architect with new constraints |
| Subagent task fails or times out | Re-dispatch with a more constrained prompt; fall back to manual if it fails again |
| Context window pressure mid-workflow | Compress completed phases into a structured summary (key patterns, files, decisions); keep plan + current step only |
| Plan references missing files | Grep for actual file paths before assuming the plan is wrong |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Phase 0 context loading | Always load project context first |
| Exploring sequentially | Use parallel explorer subagents |
| Coding before clarification | Phase 3 is a hard gate — resolve ambiguities first |
| Single architecture for non-trivial tasks | Present 2 options (simplicity vs separation) |
| Writing tests after code | TDD — test first, then implement |
| Not finishing the branch | Always run Phase 6 to completion |
| Spinning 7 subagents for a small change | Scale agent count to complexity — fast-path and small tasks need 0-1 agents |
| Manufacturing clarification questions | Skip clarification entirely if the request is well-specified |
| Auto-shipping without user review | Always confirm before invoking `/ship` |
