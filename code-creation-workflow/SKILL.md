---
name: code-creation-workflow
description: Use when asked to build, implement, add, create, or fix features. Trigger on any implementation request — features, refactors, multi-file changes, bug fixes, or single-file edits. SUPERSEDES brainstorming, writing-plans, executing-plans, test-driven-development, feature-dev.
user-invocable: true
---

# Code Creation Workflow v2

**SUPERSEDES (do not invoke separately):** brainstorming → 3A, writing-plans → 4, executing-plans → 5, TDD → 5, feature-dev → replaced. **Uses:** debate-team (4), shipping-workflow + cleanup (6B).

---

## Phase 0: Context Loading

Announce: "Running code-creation-workflow v2 — loading context."

1. Subagent: load `/courierflow-core` + `/active-files` → project identity + file registry (~45 lines).
2. Verify feature branch. Create if on main.

Domain/defensive/best-practices skills load in Phase 2 via file-pattern detection.

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

## Phase 2: Exploration + Skill Detection + Memory Injection

Scale explorers to complexity (1-3 `code-explorer` subagents). Use `dispatching-parallel-agents` for parallel dispatch.

**In parallel**, dispatch a **Skill Detection Subagent** using `references/skill-triggers.md` — returns merged checklist (max 100 lines).

After explorers return: read key files (cap 10-15). Cross-reference against `/active-files` registry — flag unregistered files. Present concise summary.

**Memory injection:** After exploration, extract domain-relevant gotchas from MEMORY.md using `references/memory-injection.md`. Match explored file patterns → domain tags → gotcha semantic keys. Include matching entries (max ~10 lines) as `PROJECT GOTCHAS` in all subsequent subagent prompts. If no domains match, omit the section entirely.

---

## Phase 3: Requirements & Clarification

<HARD-GATE>Requirements must be understood before architecture begins.</HARD-GATE>

### 3A: Requirements Discovery
Confirm: purpose, success criteria, constraints, scope boundary. One question at a time (prefer multiple-choice). Well-specified requests → skip to 3B.

### 3B: Edge Cases & Test Planning
Subagent: Phase 2 artifacts + 3A requirements → 5-8 BDD scenarios (Given/When/Then) covering happy path, edge cases, errors. Max 25 lines. User confirms → these become Phase 5 test requirements.

---

## Phase 4: Architecture

Scale: simple → 1 architect. Non-trivial → 2 parallel `code-architect` subagents (simplicity vs separation). Present each with: prediction, risk signal, falsification point (connects to 3-Strike). User chooses A, B, or hybrid.

Design doc → `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` (full workflow only). Implementation plan: numbered steps, files, test requirements, dependencies.

**Review:** `/debate-team` (auto-tiered: T1/T2/T3). Overrides: `"full debate"` → T3, `"quick review"` → T1, `"skip debate"` → bypass. Filter findings against scope, revise plan, get re-approval.

```
◆ USER APPROVES final plan before implementation ◆
```

---

## Phase 5: Implementation (TDD)

<HARD-GATE>User must approve plan before implementation begins.</HARD-GATE>

TodoWrite items from plan. Each step: test first → implement → green → complete.

### Auto-Triggered Skills

| Condition | Skill (subagent) | Action |
|-----------|-------------------|--------|
| Schema change | `/new-migration` | DB up → auto-generate. Down → scaffold + checklist. |
| 3-strike fires | `/systematic-debugging` | 4-phase diagnostic. Discuss before fix #4. |
| All steps done | `/simplify` | Review changed files for clarity/standards. |
| UI component | `/frontend-design` | Skip for backend-only or minor CSS. |

### 3-Strike Rule
Strike 1: new hypothesis, minimal test. Strike 2: boundary instrumentation. Strike 3: STOP — question architecture, not code.

### Parallel Dispatch
4+ independent steps: list file inputs/outputs, confirm no overlap. Use `dispatching-parallel-agents`. Uncertain → sequential.

---

## Phase 6A: Quality Gate

**Evidence first:** diff analysis, dependency graph, test coverage delta, boundary check.

**Review path** (scaled):

| Scope | Reviewers |
|-------|-----------|
| Small (1-2 files) | `/coderabbit-review` (fallback: `code-reviewer` subagents) |
| Medium+ (3+ files, security, schema) | + `/debate-team` (auto-tier) |
| UI in diff | + `/playwright-test` |
| Backend in diff | + `silent-failure-hunter` |
| Full features | + `pr-test-analyzer` |

**Post-review:** `receiving-code-review` subagent verifies each finding → CONFIRMED (fix) or FALSE POSITIVE (reject with evidence). Severity: CRITICAL (must fix) / WARNING (fix unless deferred).

**Verification gate:** `/verification-before-completion` — tests pass, no uncommitted changes, CI green. Fails → fix and re-verify.

---

## Phase 6B: Ship

Pre-ship: not on protected branch, no uncommitted changes. Doc checklist: API docs, CLAUDE.md, PR description, design doc.

1. **Ship it** [DEFAULT] → `/shipping-workflow` → `/cleanup` (owns session-learnings).
2. **PR for team review** → `gh pr create` → `/cleanup`.
3. **Keep branch** → `/cleanup` with keep.
4. **Discard** → requires confirmation → `/cleanup` with discard.

Session-learnings fires for ALL paths. FAST PATH without cleanup: fire session-learnings directly in background.

---

### On Error or Self-Check

Load from `references/`: `error-recovery.md` | `red-flags.md` | `user-signals.md` | `common-mistakes.md`. Missing file → log warning, continue.
