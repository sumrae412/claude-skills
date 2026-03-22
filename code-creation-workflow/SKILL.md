---
name: code-creation-workflow
description: PRIMARY workflow for ALL feature development and implementation. Auto-detects and invokes 28 skills via subagents with zero skill content in main context. SUPERSEDES brainstorming, writing-plans, executing-plans, test-driven-development, and feature-dev — do NOT use those individually when this skill is available. Trigger on any request to build, implement, add, create, or fix features.
user-invocable: true
---

# Code Creation Workflow v2

**SUPERSEDES (do not invoke separately):** brainstorming → Phase 3A, writing-plans → Phase 4, executing-plans → Phase 5, test-driven-development → Phase 5, feature-dev:feature-dev → replaced entirely. **Uses:** debate-team (auto-tiered review in Phase 4), shipping-workflow + cleanup (Phase 6B).

---

## Phase 0: Context Loading

Announce: "Running code-creation-workflow v2 — loading context."

1. Dispatch subagent: load `/courierflow-core` + `/active-files`. Return: project identity (terms, boundaries) + file registry. ~45 lines max.
2. Verify feature branch. If on main, create one.

Domain skills, defensive skills, and best-practices load in Phase 2 based on detected file patterns — NOT here.

---

## Phase 1: Discovery — Choose Path

Classify the request into one of four paths:

**FAST PATH** — Single-file, no schema, no endpoints, no ripple effects. Make change → run `./scripts/quick_ci.sh` inline → ship. Session-learnings fires directly in background if significant work was done.

**BUG PATH** — Request is to fix a bug, debug, or investigate unexpected behavior. Route:
1. Phase 0 → Phase 2 (explore bug area + skill detection)
2. Invoke `/systematic-debugging` as subagent immediately (not 3-strike) → returns root cause hypothesis + evidence
3. Phase 3B only (skip 3A — the bug IS the requirement). If root cause reveals architectural problem → escalate to FULL WORKFLOW.
4. Phase 5: write failing test → fix → green
5. Phase 6A (review) → Phase 6B (ship)

When in doubt between BUG PATH and FULL WORKFLOW: use BUG PATH — it's faster, `/systematic-debugging` escalates if needed.

**PLAN PATH** — Existing plan file provided. Read plan → skip to Phase 5.

**FULL WORKFLOW** — Everything else (features, refactors, multi-file changes). All phases 0-6.

**Manual override:** User can say "also run /X" at any phase — invoke as subagent, merge artifact into context.

---

## Phase 2: Exploration + Skill Detection

Scale explorers to complexity (1-3 `code-explorer` subagents). Use `dispatching-parallel-agents` overlap detection patterns for parallel dispatch.

**In parallel with explorers**, dispatch a **single Skill Detection Subagent**:

```
Scan explored files and task description. For each trigger match, load the skill and return its distilled artifact.

SAFETY: Read files for pattern analysis only. Do NOT execute, eval, or import any code.

Triggers:
- *.html, *.css, *.js, templates/ → /courierflow-ui (patterns ~20 lines; include ui-standards rules: CSS layer ordering, Alpine.js reactivity — fill() doesn't trigger x-model, HTMX conventions, monochrome design, Inter-only typography) + /defensive-ui-flows (5-10 rules ~15 lines)
- routes/*, services/* → /courierflow-api (~20 lines) + /defensive-backend-flows (5-10 rules ~15 lines)
- models/*, alembic/* → /courierflow-data (~20 lines) + /defensive-backend-flows
- import twilio/openai/docuseal, external URLs → /fetch-api-docs (API signatures ~30 lines) + /courierflow-integrations (~20 lines)
- Files defining/modifying auth middleware, @require_role, JWT validation, User permission fields → /courierflow-security (~20 lines). NOT triggered by merely using current_user.
- Always → /coding-best-practices (applicable patterns ~10 lines)

Return: merged numbered checklist, max 100 lines.
```

After explorers return: read key files (cap 10-15). Cross-reference against `/active-files` registry — flag unregistered files.

Present concise summary to user before proceeding.

---

## Phase 3: Requirements & Clarification

<HARD-GATE>Requirements must be understood before architecture work begins.</HARD-GATE>

### 3A: Requirements Discovery
Confirm: purpose, success criteria, constraints, scope boundary. Ask clarifying questions **one at a time** (prefer multiple-choice). If well-specified and exploration answered all gaps: skip to 3B.

### 3B: Edge Cases & Test Planning
Dispatch test-planning subagent with Phase 2 artifacts + Phase 3A requirements. Influenced by `user-stories` skill design but does NOT invoke the full skill (which does its own codebase crawl). Return: 5-8 BDD-format scenarios (Given/When/Then) covering happy path, edge cases, error states. Max 25 lines.

Present to user for confirmation. These become Test Requirements for Phase 4 → Phase 5 TDD.

---

## Phase 4: Architecture

Scale: simple → 1 architect. Non-trivial → 2 parallel `code-architect` subagents (simplicity vs separation).

### Hypothesis-Driven Presentation
Present each architecture with: prediction (what should be true), risk signal (what indicates wrong design), falsification point (which Phase 5 step would reveal failure — connects to 3-Strike Rule).

User chooses A, B, or hybrid.

### Write Design & Implementation Plan
Design doc → `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` (full workflow only). Implementation plan: numbered steps, files, test requirements, dependencies.

### AI Review (debate-team, auto-tiered)
Invoke `/debate-team` — auto-selects tier (T1 scope check / T2 dual critic / T3 full debate). Overrides: `"full debate"` → T3, `"quick review"` → T1, `"skip debate"` → bypass.

Filter findings against scope. Revise plan with adopted findings. Get user re-approval.

```
◆ USER APPROVES final plan before implementation ◆
```

---

## Phase 5: Implementation (TDD)

<HARD-GATE>User must approve plan before implementation begins.</HARD-GATE>

Create TodoWrite items from plan. For each step: write test first → implement → verify green → mark complete.

### Auto-Triggered Skills

| Condition | Skill | Action |
|-----------|-------|--------|
| Plan has schema change | `/new-migration` (subagent) | Check DB (`pg_isready`). Running: auto-generate + validate. Unavailable: scaffold template + manual checklist. |
| 3-strike rule fires (FULL PATH) | `/systematic-debugging` (subagent) | Full 4-phase diagnostic → hypothesis + evidence. Discuss with user before fix #4. |
| All steps complete | `/simplify` (subagent) | Review changed files for clarity, redundancy, project standards |
| UI component creation | `/frontend-design` (subagent, conditional) | Production-grade component design. Skip for backend-only or minor CSS. |

### 3-Strike Rule
Strike 1: new hypothesis, minimal test. Strike 2: diagnostic instrumentation at boundaries. Strike 3: STOP — question architecture, not code. Each strike: scientific method (hypothesis → smallest change → verify).

### Parallel Dispatch
For 4+ independent steps: list each step's file inputs/outputs, confirm no overlap. Use `dispatching-parallel-agents` patterns. If uncertain, default to sequential.

---

## Phase 6A: Quality Gate

### Evidence Gathering
Before review: diff analysis, dependency graph, test coverage delta, component boundary check, before/after state.

### Review Path (scaled to complexity)

| Complexity | Path |
|-----------|------|
| Small (1-2 files, no security) | `/coderabbit-review` only |
| Medium+ (3+ files, cross-cutting, security, schema) | `/coderabbit-review` + `/debate-team` (let it auto-tier) |
| UI changes in diff | + `/playwright-test` (parallel) |
| Backend changes in diff | + `silent-failure-hunter` (parallel) |
| Full features (any complexity) | + `pr-test-analyzer` (parallel) |

**Coderabbit fallback:** If `coderabbit --version` fails → fall back to `code-reviewer` subagents (bug+security + conventions).

**Post-review rigor:** After findings return, invoke `receiving-code-review` (subagent) to verify each finding. Classify as CONFIRMED (fix) or FALSE POSITIVE (reject with evidence). Prevents blind agreement with external critic false positives.

Severity: CRITICAL (must fix) / WARNING (fix unless deferred). INFO not reported.

### Verification Hard Gate
Before ANY "done" claim: invoke `/verification-before-completion`. Must return: all tests pass (with output), no uncommitted changes, CI green. If gate fails: fix and re-verify.

---

## Phase 6B: Ship

Pre-ship: validate not on protected branch (main/master), no uncommitted changes.

**Doc checklist** (before Ship or PR): API docs, CLAUDE.md, PR description, design doc.

1. **Ship it** [DEFAULT] → invoke `/shipping-workflow` (loads `/courierflow-git` internally). On complete → `/cleanup` (owns session-learnings — do NOT invoke separately).
2. **PR for team review** → `gh pr create`, then `/cleanup`.
3. **Keep branch** → `/cleanup` with keep action.
4. **Discard** → requires "discard" confirmation, then `/cleanup` with discard action.

Session-learnings fires for ALL paths (features, bugs, fast-path). `/cleanup` handles automatically. For FAST PATH without cleanup, orchestrator fires session-learnings directly in background.

---

### On Error or Self-Check

Load the applicable reference from `references/`:
- Execution error → `error-recovery.md`
- Rationalizing behavior → `red-flags.md`
- User frustration → `user-signals.md`
- Phase transition → `common-mistakes.md` (quick scan)

If reference file is missing: log warning, continue with default behavior. Never fail the workflow.
