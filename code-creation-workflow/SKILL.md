---
name: code-creation-workflow
description: PRIMARY workflow for ALL feature development and implementation. SUPERSEDES brainstorming, writing-plans, executing-plans, test-driven-development, and feature-dev — do NOT use those individually when this skill is available. Uses debate-team for auto-tiered review. Trigger on any request to build, implement, add, create, or fix features. Includes parallel exploration, architecture, TDD, and review as unified phases.
user-invocable: true
---

# Code Creation Workflow

**SUPERSEDES (do not invoke separately):** brainstorming → Phase 3A (requirements discovery, one-Q-at-a-time) + Phase 4 (approaches, design doc), writing-plans → Phase 4, executing-plans → Phase 5, test-driven-development → Phase 5, feature-dev:feature-dev → replaced entirely. **Uses:** debate-team (auto-tiered review in Phase 4).

---

## Phase 0: Context Loading

**Announce:** "Running code-creation-workflow — loading context, then building."

1. Read workspace `CLAUDE.md` (identity, boundaries, terminology, skill pointers).
2. Load core skill if present (e.g. `/courierflow-core`) for trigger matrix and boundaries.
3. Load `/active-files` registry — all file modifications must target registered files or register new ones first.
4. Load **only** the contextual skills that match the task:
   - UI / templates / CSS → UI skill
   - Routes / services → API skill
   - Models / migrations → data skill
   - External APIs → integrations skill
   - Git / deploy / PR → git skill
   - Auth / security → security skill
5. Always load: `coding-best-practices` + the matching defensive skill (`defensive-ui-flows`, `defensive-backend-flows`, or both).
6. Verify you're on a feature branch. If on main, create one before proceeding.

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

**File governance check:** Cross-reference explored files against the `/active-files` registry. Flag any files that need work but aren't registered — they must be added to the registry before implementation begins in Phase 5.

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

## Phase 3: Requirements & Clarification

<HARD-GATE>
Requirements must be understood and ambiguities resolved before architecture work begins.
</HARD-GATE>

### 3A: Requirements Discovery

Before checking for gaps, confirm you understand what you're building:
- **Purpose** — what problem does this solve? What triggers the need?
- **Success criteria** — how will we know it works? What does "done" look like?
- **Constraints** — performance, compatibility, security, or UX requirements?
- **Scope boundary** — what is explicitly NOT included?

Ask clarifying questions **one at a time**. Prefer multiple-choice when possible. Only move on when you understand the user's intent.

**If the request is well-specified and exploration answered all gaps:** state that explicitly and skip to 3B. Do not manufacture questions.

### 3B: Edge Cases & Test Planning

Review exploration findings against requirements. Check for gaps in:
- Edge cases (empty input, duplicates, malformed data)
- Error handling (what does the user see on failure?)
- Integration points (which existing systems are touched?)
- Performance (large datasets, concurrency?) — carry forward as a non-functional requirement for Phase 4
- Backward compatibility (does this change existing behavior?)

Enumerate test scenarios:
- Happy path (expected inputs → expected outputs)
- Edge cases (empty, duplicate, malformed)
- Error scenarios (network failure, invalid state, permission denied)
- Regression scenarios (existing behavior that must not break)

Present the test case list to the user for confirmation. These become the "Test Requirements" section in the Phase 4 plan — Phase 5 consumes this list directly for TDD.

---

## Phase 4: Architecture

Scale to complexity:
- Simple task (clear single approach) → propose one design, explain rationale, get approval.
- Non-trivial task → dispatch 2 parallel `code-architect` subagents:
  - Architect A: Optimize for **simplicity** — reuse existing patterns, minimal new files, fewest moving parts.
  - Architect B: Optimize for **clean separation** — extensibility, testability, clear boundaries.

Each architect returns: files to create/modify, component responsibilities, data flow, trade-offs.

### Hypothesis-Driven Presentation (from systematic-debugging)

Present each architecture as a testable hypothesis, not just a design:

- **Approach A hypothesis:** "If we optimize for simplicity by [specific choice], then [predicted outcome]. This will be validated when [concrete test]."
- **Approach B hypothesis:** "If we optimize for separation by [specific choice], then [predicted outcome]. This will be validated when [concrete test]."

For each, state:
1. **Prediction:** What should be true if this design is correct? (e.g., "Adding a new message type requires changing only 1 file")
2. **Risk signal:** What would indicate this design is wrong? (e.g., "If we need to pass data through 3+ layers, the abstraction is fighting us")
3. **Falsification point:** At what Phase 5 step would we know this isn't working? (Connects to the 3-Strike Rule — if we hit strike 3 on a step, we revisit these predictions.)

This makes the user's choice informed by consequences, not just aesthetics. It also gives Phase 5 clear criteria for when to escalate vs. keep iterating.

Present both designs to the user. User chooses A, B, or hybrid.

```
◆ USER CHOOSES architecture ◆
```

### Write Design & Implementation Plan

After user chooses, write a structured plan directly (no separate skill invocation):

**Design doc** (full workflow only, skip for simple tasks):
- Save to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Cover: purpose, chosen approach with rationale, data flow, error handling, scope boundary
- Commit the design doc before proceeding

**Implementation plan** (always):
- Numbered steps with specific files and line-level changes
- Test requirements per step
- Dependencies between steps marked clearly

### AI Review (debate-team, auto-tiered)

Invoke `/debate-team` which auto-selects the appropriate tier:

- **Tier 3 (Full Debate)** — all plans, bug fix plans (3+ files or cross-service), schema+security, frontend+backend, or user says "full debate"
- **Tier 2 (Dual Critic)** — 3+ files, cross-cutting concerns, external API integration
- **Tier 1 (Scope Check)** — simple 1-2 file changes

**Prerequisite check:** `python3 -c "import httpx" && test -f ~/.claude/scripts/plancraft_review.py`. If missing: warn user, skip review, note gap as "unreviewed."

**Overrides:** `"full debate"` forces Tier 3, `"quick review"` forces Tier 1, `"skip debate"` bypasses entirely.

Filter all findings against scope (ACCEPT in-scope, REJECT scope creep). Revise plan with adopted findings, get user re-approval.

**When complexity gate selects Tier 1:** Log: "Debate-team Tier 1 — scope check only, no schema/API/cross-cutting."

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

### 3-Strike Rule (from systematic-debugging)

If implementation of a single step fails 3 times, the problem is architectural, not implementational.

1. **Strike 1:** Fix fails → form a new hypothesis about why. Test minimally.
2. **Strike 2:** Fix fails again → gather evidence. Add diagnostic logging/instrumentation at component boundaries. Run once to see WHERE it breaks, not just THAT it breaks.
3. **Strike 3:** Fix fails a third time → **STOP. Question the architecture.**
   - Is the Phase 4 design fundamentally sound for this step?
   - Are we fighting the existing codebase's grain?
   - Would a different approach from Phase 4 (the unchosen architecture) solve this more naturally?
   - **Discuss with user before attempting Fix #4.** This is NOT a failed implementation — it's a wrong design.

**Each strike must use the scientific method:** state the hypothesis ("I think X is the root cause because Y"), make the smallest possible change to test it, verify before continuing. Do NOT stack multiple fixes hoping one works.

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
Flow: Pre-Review → Review (subagents + batch) → Deep-Dives → Deduplicate → Verify (CI retry) → Finish → Document → Learn
```

### 6A: Quality Gate

**Evidence Gathering (before review, not after):**

Gather structured evidence BEFORE dispatching reviewers. Reviewers assess evidence, not assumptions.

1. **Diff analysis:** `git diff main..HEAD --stat` — what files changed, how many lines, what categories (test, source, config, migration)?
2. **Dependency graph:** For each changed file, what imports it? What does it import? Are callers affected?
3. **Test coverage delta:** Which changed lines are covered by tests? Which aren't? (Use test output + grep, not assumptions.)
4. **Component boundary check:** For multi-layer changes, verify data flows correctly at each boundary:
   - Route → Service: correct args passed?
   - Service → Model: correct queries, eager-loads?
   - Template → JS: correct data attributes, event bindings?
5. **Before/after state:** For behavioral changes, capture concrete before/after (test output, API response shape, UI state).

This evidence is passed to reviewers as context. Reviewers who see evidence catch real bugs; reviewers who see only code catch style issues.

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

**Batch Review (background, full features only):**

For full features (not small/targeted changes), launch `batch_review.py` in background during pre-review checks:

```bash
# Launch in background before subagent reviewers
python3 ~/.claude/scripts/batch_review.py \
    --mode code-review \
    --artifact-file <diff-file> \
    --scope-file <scope-file> \
    --timeout 300 &
```

**Prerequisite:** `python3 -c "import anthropic"` succeeds and `ANTHROPIC_API_KEY` is set.
Merge batch findings with subagent reviewer findings in the deduplication step. If batch hasn't completed by deduplication: skip (graceful degradation). This adds a Claude model perspective at 50% batch discount without blocking the review pipeline.

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
| 3 | Requirements & Clarification | 3A: intent/success criteria (one Q at a time) → 3B: edge cases + test plan | User answers + confirms tests |
| 4 | Architecture | Architects + debate-team (auto-tiered review) | User approves plan |
| 5 | Implementation | TDD per step; parallel dispatch at 4+ independent steps | Tests pass |
| 6A | Quality Gate | Severity review + deep-dive triggers + CI retry (3 attempts) | Verification |
| 6B | Finish & Ship | Finishing options + doc checklist + session learnings | User choice |

**Skills integrated:**

| Skill | Where used |
|-------|-----------|
| systematic-debugging | Phase 4 (hypothesis-driven architecture), Phase 5 (3-Strike Rule), Phase 6A (evidence-before-action). Red Flags + User Signals tables. |
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
| Tests fail during implementation | RETRY | Fix immediately — do not proceed to next step. Use scientific method: hypothesis → minimal test → verify. |
| Tests fail 3+ times on same step | PAUSE | **3-Strike Rule.** Stop. Question the Phase 4 architecture, not the code. Ask user: design wrong or test wrong? |
| Reviewer finds critical issue | RETRY | Fix before finishing, re-run verification |
| Reviewer finds pre-existing bug | RETRY | Fix it (fix-what-you-find). Log as pre-existing in commit |
| CI fails after fix | RETRY | Check `git status` between attempts (ruff may modify files). Re-run up to 3 attempts. Same error twice → escalate immediately |
| CI passes locally, fails in PR | PAUSE | Check env-specific issues. Fix root cause, don't `--no-verify` |
| User wants to stop | PAUSE | Summarize: phase, what's done, what remains, next step to resume |
| Wrong architecture chosen | RETRY | Revert uncommitted work, re-architect with new constraints |
| debate-team API fails | DEGRADE | Continue with available reviewers. Note gap. If all fail → "unreviewed" |
| Subagent produces conflicting results | DEGRADE | Evaluate each finding against codebase evidence. ADOPT only verified |
| Context window pressure | DEGRADE | Compress completed phases into structured summary; keep plan + current step |
| Plan references missing files | RETRY | Grep for actual paths before assuming the plan is wrong |
| Batch review times out or fails | DEGRADE | Proceed with subagent reviewers only. Note "batch unavailable" in deduplication. No blocking |

**Resolution types:** RETRY = fix and re-run. PAUSE = stop and ask user. DEGRADE = continue with reduced capability.

## Red Flags — STOP and Check Yourself

If you catch yourself thinking any of these, you're rationalizing. STOP and follow the process.

| Thought | Reality |
|---------|---------|
| "This is basically a fast-path" | If you're justifying it, it's not. Use full workflow. |
| "I don't need 2 architects for this" | Complexity hides behind familiarity. Do the scale check. |
| "Tests can come after, I know this works" | TDD is Phase 5's hard gate. No exceptions. |
| "User seems impatient, skip clarification" | Phase 3 exists because skipping costs more time later. |
| "I'll just start coding and figure it out" | That's Phase 5 without Phase 2-4. You'll rework it. |
| "The exploration was enough, skip requirements" | Exploration answers WHAT exists. Phase 3 answers WHAT to build. Different questions. |
| "One more implementation attempt" (after 2+ failures) | 3 failures = wrong architecture, not wrong code. See 3-Strike Rule. |
| "I'll fix the review findings later" | CRITICAL/WARNING findings block shipping. Fix now or escalate. |
| "Skip the evidence gathering, I can see the problem" | Seeing symptoms ≠ understanding root cause. Gather evidence first. |

## User Signals You're Off Track

Watch for these signals — they mean your approach needs correction, not just your code.

| Signal | Meaning | Action |
|--------|---------|--------|
| "Can you just..." | User wants simpler. You're over-engineering. | Revisit Phase 4, pick the simpler architecture. |
| "What about X?" | Missed requirement. Phase 3 was incomplete. | Return to Phase 3A, address the gap. |
| "That's not what I meant" | Intent mismatch. Requirements misunderstood. | Restart Phase 3A from scratch. Restate what you think they want. |
| "This is taking too long" | Process overhead exceeding value. | Check: are you on full workflow when fast-path applies? Scale down. |
| "Stop, let me think" | You're moving faster than the user's decision pace. | PAUSE. Wait for explicit direction before next action. |
| "Is that not happening?" | You assumed without verifying. | Return to evidence gathering. Don't assume — check. |
| "We're stuck" (frustrated tone) | Your approach isn't working. | STOP. Question the architecture (3-Strike Rule), don't add more fixes. |

**When you see any of these:** acknowledge the signal, name what went wrong, adjust approach. Do NOT continue on the same path.

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
