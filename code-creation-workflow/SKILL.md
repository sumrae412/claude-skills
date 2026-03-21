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

Dispatch parallel `code-explorer` subagents using the Agent tool. Specialize prompts by change type:

**Frontend** (templates, CSS, JS):
- Explorer A: Trace UI patterns — components, CSS architecture, design system usage.
- Explorer B: Map data flow — how data reaches the template, JS event handlers, Alpine/HTMX bindings.
- Explorer C: Analyze test patterns and accessibility patterns in this UI area.

**Backend** (routes, services, models):
- Explorer A: Trace API/service patterns — route structure, service layer, error handling.
- Explorer B: Map data model — schema relationships, queries, eager-loading patterns.
- Explorer C: Analyze test patterns — fixtures, mocking, integration vs unit approach.

**External API** (integrations, webhooks):
- Explorer A: Trace integration patterns — how other external APIs are called, retry logic.
- Explorer B: Map error handling — timeouts, retries, circuit breakers, webhook verification.
- Explorer C: Analyze auth/security patterns for external service connections.

**Mixed changes** (spans 2+ layers): Combine the most relevant explorers from categories above. For tasks touching all three layers, always use 3 explorers.

**Unknown/unclassifiable:** Fall back to generic prompts — patterns, architecture, tests.

After all agents return: read the identified key files yourself. **Cap at 10-15 files** — if explorers return more, prioritize the most relevant based on their summaries and read others on-demand during implementation. This prevents context window exhaustion.

Present a concise summary of findings to the user before proceeding.

Minimum output per explorer: 5-10 key files, the patterns they follow, any constraints or concerns.

### Identify Applicable Defensive Rules

After explorers return, identify which defensive patterns apply to this change:

| Change type | Scan |
|-------------|------|
| UI (HTML/CSS/JS) | `defensive-ui-flows`: identify which of 31 rules apply |
| Backend (Python) | `defensive-backend-flows`: identify which of 30 rules apply |
| Both | both skills, mark applicable rules from each |

Create a numbered checklist of 5-10 applicable rules (not all 31/30). This checklist is referenced in Phase 5 during implementation and Phase 6 during review.

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
- Test cases — enumerate specific scenarios to test:
  - Happy path (expected inputs → expected outputs)
  - Edge cases (empty, duplicate, malformed)
  - Error scenarios (network failure, invalid state, permission denied)
  - Regression scenarios (existing behavior that must not break)

Present the test case list to the user for confirmation. These become the "Test Requirements" section in the Phase 4 plan — Phase 5 consumes this list directly for TDD.

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

### AI Review (PlanCraft)

**Always triggered when ANY of these apply:**
- Schema changes (new/modified models, migrations)
- External API integration (new service connections, webhook handlers)
- Cross-cutting concerns (auth changes, middleware, shared utilities)
- 3+ files modified across 2+ architectural layers

**Also triggered when:** user requests it ("review the plan", "validate this").

**Prerequisite check:** `python3 -c "import httpx" && test -f ~/.claude/scripts/plancraft_review.py`. If missing: warn user, skip review, note gap as "unreviewed."

If triggered: run `plancraft_review.py` (DeepSeek + Codex in parallel), filter suggestions against scope (ACCEPT in-scope improvements, REJECT scope creep), revise plan, get re-approval.

**When NOT triggered:** Skip. Log: "PlanCraft skipped — single-layer, no schema/API/cross-cutting."

### Optional: Debate-Team Review

```
Plan written → PlanCraft triggers?
  ├─ YES → Run PlanCraft → debate-team triggers?
  │                           ├─ YES → Run debate-team AFTER PlanCraft
  │                           └─ NO → Done
  └─ NO → Skip both
```

Trigger: user says "debate this" OR task touches 3+ files with security-sensitive code (`password`, `token`, `secret`, `credit_card`, auth/middleware patterns).

If triggered: Generator (Sonnet) produces proposal, DeepSeek Bug-Hunter + GPT-4o Architecture run in parallel, optional Haiku Style/UI for frontend. Synthesize as ADOPT/REJECT/DEFER.

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

```
Flow: Pre-Review → Review → Deep-Dives → Deduplicate → Verify (CI retry) → Finish → Document → Learn
```

### 6A: Quality Gate

**Pre-Review Checks:**
- All tests pass locally
- No uncommitted changes that should be included
- Branch not stale (if PR exists: `git fetch origin main && git diff origin/main..HEAD --stat` — stale = overlapping files changed on both branches, not just unrelated commits on main)
- Security grep: no hardcoded secrets in changed files (`API_KEY=`, `password=`, `token=`, `secret=`)

**Review — scale to complexity:**
- Small/targeted change → single reviewer pass (bugs + conventions combined)
- Full feature → 2 parallel `code-reviewer` subagents:
  - Bug & Security Reviewer: bugs, logic errors, security vulnerabilities, race conditions. Classify as CRITICAL/WARNING/INFO.
  - Conventions Reviewer: project conventions, patterns, style, plan adherence. Verify defensive rules checklist from Phase 2. Classify as CRITICAL/WARNING/INFO.

| Severity | Meaning | Action |
|----------|---------|--------|
| CRITICAL | Confirmed bug, security issue, data loss risk | Must fix before shipping |
| WARNING | Impacts functionality or violates conventions | Fix unless user explicitly defers |
| INFO | Cosmetic or nitpick | Do not report — skip |

Only CRITICAL and WARNING are reported. When reviewers disagree: security > efficiency > style.

**Deep-Dive Triggers** — auto-detect by grepping the diff:

| Pattern | Deep-dive |
|---------|-----------|
| `d-none`, `display:`, `visibility:`, `opacity:` | Git history analysis on affected files |
| `position: fixed/absolute/sticky`, `z-index` | Git blame for layout conflicts |
| Files in `tests/` modified | Test logic analysis (assertions, mocks) |
| Lines removed that were recently added | Git log: why were they added? |
| SQL/migration files changed | Data integrity + rollback review |

Run 0-2 matching deep-dives in parallel. Classify findings as CRITICAL/WARNING only.

**Debate-Team Review** (high-complexity only) — for 3+ files with security-sensitive code, replace standard review with debate-team protocol: DeepSeek Bug-Hunter + GPT-4o Architecture + optional Haiku Style/UI. Synthesize as ADOPT/REJECT/DEFER. Max 2 auto-fix cycles.

**Deduplicate** findings from review + deep-dives. Fix all CRITICAL and WARNING. Pre-existing bugs: fix per fix-what-you-find, note in commit.

**Verification Gate (CI Retry):**
1. Run tests + CI (`./scripts/quick_ci.sh`) → must pass
2. Check: no unintended file changes, implementation matches request, no regressions
3. If CI fails: check `git status` (ruff may modify files), fix root cause, re-run. Same error twice → escalate immediately. Max 3 attempts then PAUSE for user.

### 6B: Finish & Ship

After verification passes, present options:

1. **Ship it** (commit → push → PR → review → merge) **[DEFAULT]**
2. **Create PR for team review** (no auto-merge) — **Warning:** bypasses automated review agent. Ensure team review covers bugs, conventions, defensive patterns.
3. **Keep branch as-is** (handle later)
4. **Discard** (requires typed "discard" confirmation)

Option 1: invoke `/ship`. Options 2-4: delegate to `finishing-a-development-branch` skill.

**Documentation checklist** (before Option 1 or 2):
- [ ] API docs updated (required if new/modified endpoints)
- [ ] CLAUDE.md updated (required if new conventions or gotchas discovered)
- [ ] PR description includes test plan (required for features)
- [ ] Design doc reflects final implementation (if diverged)

**Capture Learnings:** Invoke `session-learnings` in background. The skill handles cross-reference auditing and policy detection — see `session-learnings/SKILL.md`. When complete, present summary: "N updates across M targets." User approves which to apply. Pay attention to contradictions flagged between skills.

---

## Quick Reference

| Phase | Name | Key Pattern | Gate |
|-------|------|-------------|------|
| 0 | Context | Load CLAUDE.md + relevant skills only | None |
| 1 | Discovery | Fast-path / plan-path / full-workflow | Auto |
| 2 | Exploration | Specialized explorers + defensive rule checklist | None |
| 3 | Clarification | Ambiguities + test case enumeration | User answers + confirms tests |
| 4 | Architecture | Architects + PlanCraft (always-on for schema/API) + optional debate-team | User approves plan |
| 5 | Implementation | TDD per step; parallel dispatch at 4+ independent steps | Tests pass |
| 6A | Quality Gate | Severity review + deep-dive triggers + CI retry (3 attempts) | Verification |
| 6B | Finish & Ship | Finishing options + doc checklist + session learnings | User choice |

**Skills integrated:**

| Skill | Where used |
|-------|-----------|
| debate-team | Phase 4 (optional architecture review), Phase 6A (high-complexity review) |
| finishing-a-development-branch | Phase 6B (Options 2-4 execution) |
| shipping-workflow reference | Phase 6A (scoring, deep-dives, CI retry patterns) |

## Error Recovery

| Situation | Resolution | Action |
|-----------|------------|--------|
| Explorer returns poor results | RETRY | Re-dispatch with narrower prompt, or explore manually |
| Explorer times out | RETRY | Re-dispatch with narrower scope (single concern) |
| Both architectures rejected | PAUSE | Ask user what's missing, re-run with new constraints |
| Only one viable architecture (3+ files or cross-cutting) | PAUSE | Present with trade-offs, ask if user wants a second option |
| Tests fail during implementation | RETRY | Fix immediately — do not proceed to next step |
| Tests fail 3+ times on same step | PAUSE | Stop TDD loop. Read test + impl together. Ask user: test wrong or approach wrong? |
| Reviewer finds critical issue | RETRY | Fix before finishing, re-run verification |
| Reviewer finds pre-existing bug | RETRY | Fix it (fix-what-you-find). Log as pre-existing in commit |
| CI fails after fix | RETRY | Check `git status` between attempts (ruff may modify files). Re-run up to 3 attempts. Same error twice → escalate immediately |
| CI passes locally, fails in PR | PAUSE | Check env-specific issues. Fix root cause, don't `--no-verify` |
| User wants to stop | PAUSE | Summarize: phase, what's done, what remains, next step to resume |
| Wrong architecture chosen | RETRY | Revert uncommitted work, re-architect with new constraints |
| PlanCraft/debate-team API fails | DEGRADE | Continue with available reviewers. Note gap. If both fail → "unreviewed" |
| Subagent produces conflicting results | DEGRADE | Evaluate each finding against codebase evidence. ADOPT only verified |
| Context window pressure | DEGRADE | Compress completed phases into structured summary; keep plan + current step |
| Plan references missing files | RETRY | Grep for actual paths before assuming the plan is wrong |

**Resolution types:** RETRY = fix and re-run. PAUSE = stop and ask user. DEGRADE = continue with reduced capability.

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
