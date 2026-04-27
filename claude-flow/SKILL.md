---
name: claude-flow
description: Use when creating new features, implementing complex changes, or executing implementation plans. Agentic workflow with fast, clone, lite, explore, and full paths. Executor/Advisor strategy — Sonnet executes, Opus advises at key decision points.
user-invocable: true
---

# Code Creation Workflow

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Agentic multi-phase workflow for building features. **Executor/Advisor strategy:** Sonnet executor runs the main loop (exploring, drafting, implementing). Opus advisor fires on-demand at 3-5 decision points. Project-agnostic — works for any codebase or greenfield project.

**Announce:** "Running claude-flow — loading context, exploring codebase, then building with you."

---

## Model Assignments

| Role | Model | When |
|------|-------|------|
| **Executor** | **sonnet** | Every turn — exploration, drafting, implementation, all file I/O |
| **Advisor (tiered)** | **sonnet** Phase 2, **opus** Phase 4 | Sonnet for gap-finding, Opus for architecture + plan critique |
| **Lightweight reviewer** | **haiku** | Phase 6 — single batched dispatch (types, API docs, invariants, defensive) |
| **Specialist reviewers** | **sonnet** | Phase 6 — safety (combined), test coverage |

---

## How to Use This Workflow

1. **This file** (router) is always resident.
2. **Load `phases/phase-N-*.md`** only when entering that phase.
3. **Load contract schemas** only when a phase produces or consumes that contract.
4. **Drop the phase file after transition**; keep only the populated contract (`$exploration`, `$requirements`, `$plan`, `$diff`).
5. **Load references lazily** — especially bootstrap/state docs and large review/testing doctrine.
6. **Load diagrams lazily** only when reasoning about path selection, lifecycle, or contract flow.

---

## Flags

Optional flags modify specific phases without changing the path decision.

**Two flag scopes:**
- **Path-scoped** flags pick the whole workflow path — e.g. `--fast`, `--lite`, `--clone`, `--explore`, `--full`. These interact with Phase 1 triage (see Path Decision below) and typically skip later phases entirely.
- **Phase-scoped** flags modify one phase's behavior without changing the path — e.g. `--visual` / `--no-visual` below. Path selection is unaffected; only the named phase runs differently. New phase-scoped flags should name the phase in the `Phase` column of this table so the scope stays obvious.

**Flag propagation:** When claude-flow runs on LITE PATH and dispatches a heavyweight orchestrator subagent (`debate-team`, `research`), propagate `--lite` into the dispatch prompt. Otherwise a nominally lite run fans out into full-tier debate / full-wave research and defeats the purpose.

| Flag | Phase | Effect |
|------|-------|--------|
| `--visual` | Phase 4 | Force the Visual Checkpoint step (Step 6): generate `.excalidraw` mockups under `docs/design/<feature>/mockups/`, pause for user edits, fold drift back into `$plan`. Auto-enabled when `$plan` touches frontend files or the task mentions "UI mockup" / "wireframe" / "visual review". |
| `--no-visual` | Phase 4 | Skip the Visual Checkpoint step even when auto-enable signals fire. The always-emit `architecture.excalidraw` (one-way) still runs. |

---

## Path Decision (Phase 1 Core Logic)

```
BUG? (error report, regression, stack trace, "fix this bug")
  → Invoke /bug-fix skill — EXIT workflow

SMALL? (single file, no schema, no new endpoints)
  → FAST PATH: make change → test → commit → EXIT

HAS PLAN/PRP? (existing plan file or PRP document)
  → PLAN PATH: read plan → Phase 4c verification → Phase 5

NEAR-IDENTICAL FEATURE? (2-3 grep/glob checks)
  → CLONE PATH: clone + adapt → Phase 4c-lite verification → Phase 5

1-2 FILES? (no new endpoints, no schema, no new models)
  → LITE PATH: Phases 2-6 with inline architecture + 4c-lite verification

AUDIT / CLEANUP? ("audit", "cleanup", "tech debt", "find issues in")
  → AUDIT PATH: read-only path, skip Phase 5

EXPLORATORY? ("try this", "spike", "prototype", "proof of concept")
  → EXPLORE PATH: sandbox (60/100 bar, no TDD, no Phase 6)
    Graduate → full workflow from Phase 4
    Archive → /session-handoff --abandon

ELSE → FULL WORKFLOW (all phases)
```

Before finalizing `fast`, `clone`, or `lite`, run a provisional risk screen.
Signals like `auth`, `privacy`, `money`, `data_loss`,
`external_side_effects`, or `public_api` can force the task onto the full path
even when the diff is small.

Load `phases/phase-1-discovery.md` for full criteria. Canonical path and
transition metadata lives in `workflow-profiles.json`.

---

## Phase Transition Map

Canonical transitions and iteration limits live in `workflow-profiles.json`.
Hot-path phase files should cite that file instead of carrying duplicate tables.

---

## External Systems Access Policy

When a phase reaches outside the workspace (API docs, deployment logs, PR operations, DB introspection, error search), prefer access in this order:

1. **MCP server** if one is connected — portable across clients, standardized auth, semantics cheaper than piping CLI output through the model
2. **CLI** for local-first tools without an MCP equivalent (e.g., `ruff`, `pytest`, `semgrep`, project scripts)
3. **Direct HTTP / web fetch** only as fallback when neither exists

Examples: GitHub ops → `gh` CLI is fine locally; prefer GitHub MCP when dispatching subagents to remote clients. Railway → use `mcp__railway-mcp-server__*` (memory: `reference_config_repos`). Sentry → `sentry:seer` or `mcp__sentry-*`. Supabase → `mcp__30db93f5-*`. Before fetching public web docs, check whether the service has an MCP server that exposes introspection — avoids the staleness problem `/fetch-api-docs` exists to solve.

**Programmatic tool calling for bulk/deterministic work:** If a tool returns a large JSON payload and you need to filter/aggregate/transform deterministically, do it in a Python script (see `scripts/select_reviewers.py`, `aggregate_reviewer_findings.py`) rather than piping raw output through the executor. Saves tokens and eliminates a class of LLM parsing errors.

---

## Phase Output Contracts

| Contract | Schema File | Produced By | Consumed By |
|----------|-------------|-------------|-------------|
| `$exploration` | `contracts/exploration.schema.md` | Phase 2 | Phases 3, 4, advisors |
| `$requirements` | `contracts/requirements.schema.md` | Phase 3 | Phases 4, 4c, 5, 6 |
| `$plan` | `contracts/plan.schema.md` | Phase 4b | Phases 4c, 4d, 5, 6 |
| `$diff` | `contracts/diff.schema.md` | Phase 5 | Phase 6 |

Contracts are the interface between phases. When dispatching subagents, pass the named contract — not raw conversation. See each schema file for field definitions and notes.

**Never pass to subagents:** advisor transcripts, rejected architecture details, Phase 0 skill loading decisions, raw clarification Q&A (pass `$requirements` instead).

**Authoring-time verification:** Phase 3 audits self-answerable questions; Phase 5 injects deterministic lookups (alembic, routes, columns, CSS, React) and runs a visual-drift gate. Optional deps graceful-skip — never block the workflow. See concept: `knowledge/concepts/authoring-time-verification.md`.

---

## Quick Reference

| Phase | Name | Model | Key Pattern | Gate |
|-------|------|-------|-------------|------|
| 0 | Context | executor | Trigger matrix → load relevant skills only | None |
| 1 | Discovery | executor | 8-path triage (bug/fast/clone/plan/lite/audit/explore/full) | Auto |
| 2 | Exploration | executor + **sonnet advisor** | Executor explores → advisor reviews gaps + scores quality gate | Advisor confirms |
| 3 | Requirements | executor | Ambiguities + $requirements (quality gate skipped if Phase 2 passed) | User approves |
| 4 | Architecture + Plan | executor + **opus advisor** | 2 options → advisor critiques → plan → advisor stress-tests | User approves plan |
| 4c | Plan Verification | executor + scripts | Mechanical ref check + coverage/scope verification | Verified plan |
| 5 | Implementation | executor (+ advisor optional) | TDD per step, defensive patterns, parallel dispatch | Tests + lint pass |
| 5.5 | Reflection | executor | RARV self-check before expensive reviews | Auto |
| 6 | Quality + Finish | sonnet/haiku | Risk-budgeted review cascade → verify → commit → retrospective | Verification |

**Pattern vocabulary:** See `references/multi-agent-patterns.md` for which multi-agent pattern each phase implements. Load when designing a new phase or debating whether a phase's coordination approach is the right fit.

**Phase 6 optional follow-up:** `/personas` — synthetic beta test (bugs, UI snags, usefulness ratings), offered non-gating when `$diff` touches user-facing flows. See `phases/phase-6-quality.md` §Optional follow-up.

---

## Error Recovery

| Situation | Action |
|-----------|--------|
| Exploration misses key area | Re-explore; call advisor again with new findings |
| Advisor identifies critical gap | Investigate the gap before proceeding |
| Architecture options both rejected | Ask user for different constraints, executor re-drafts |
| Tests fail during implementation | Fix immediately, don't proceed to next step |
| Reviewer finds critical issue | Fix → re-run that specific reviewer → max 3x → escalate |
| User wants to stop | Stop. Summarize state (phase, done, remaining). |
| Wrong architecture chosen | Revert to plan, re-architect with new constraints |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping Phase 0 context loading | Always load project context first |
| Exploring without checking prior knowledge | Step 0: check MEMORY.md, PRPs, Serena before exploring |
| Skipping Phase 4c plan verification | Plans reference Phase 2 findings — codebase can drift |
| Jumping to fixes without evidence | Use `/investigator` for complex TDD failures |
| Calling advisor every turn | 2-4 calls per workflow, not every step |
| Using Opus for Phase 2 exploration review | Sonnet handles gap-finding; Opus reserved for Phase 4 |
| Running all Phase 6 tiers when Tier 1 is clean | Early exit: if CodeRabbit finds no HIGH+ issues, skip Tiers 2-4 |
| Dispatching 4 separate haiku reviewers | Batch into single `lightweight-reviewer` with combined checklist |
| Letting Opus 4.7 under-parallelize reviewer/researcher fan-outs | Explicitly name the fan-out in the dispatch prompt; emit all tool-use blocks in a single message |
| Initializing state machine for fast/lite paths | Skip — single-session linear flows don't need cross-session resume |
| Re-running Phase 3 quality gate when Phase 2 scored it | Carry scores forward — skip redundant re-check |
| Coding before clarification | Phase 3 is a hard gate |
| Single architecture proposal | Always present 2 options |
| Passing full conversation to subagents | Use named contracts ($plan, $requirements, etc.) |
| Using full workflow for 1-2 file changes | Use Lite path |
| Writing tests after code | TDD — test first |
| Guessing external API patterns | Hard gate: `/fetch-api-docs` before any API code |
| Not tagging workflow failures | Apply taxonomy tags (see `references/failure-taxonomy.md`) |
| Letting context grow unbounded | Tool-result clearing at ~50K, compaction at ~80% |
| Running 10-step plans without context breaks | Fresh context for subagents at 5+ steps |
| Carrying stale session context across unrelated tasks | `/clear` at task boundaries — auto-compaction only fires at ~80%; a small new task on top of a large done one pays for irrelevant history on every turn |
| Running silent-failure-hunter and security-reviewer separately | Use merged `safety-reviewer` (Tier 2) — they're consolidated |
