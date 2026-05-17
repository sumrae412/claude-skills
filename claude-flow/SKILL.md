---
name: claude-flow
description: Use when creating new features, implementing complex changes, building features, adding features, executing implementation plans, or running TDD workflows. Multi-phase agentic build pipeline (Phase 0 context → 1 discovery → 2 exploration → 3 requirements → 4 architecture/plan → 4c verification → 5 TDD implementation → 5.5 reflection → 6 review+ship). Workflow paths: fast, clone, lite, plan, explore, audit, full. Executor/Advisor strategy — Sonnet executes, Opus advises at key decision points. Project-generic router; project-specific skill menu is injected via Phase 0/5 (see references/project-skill-menu.md).
version: 4.1.0
user-invocable: true
metadata:
  hermes:
    tags: [coding, workflow, planning, review, verification]
    related_skills: [smart-exploration, executing-plans, verification-before-completion, coding-best-practices]
---

# Code Creation Workflow

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.

## Phase 5 Subagent Skill Selection

Phase 5 dispatches use **forced single-skill selection** (variant B) by default — set in `run_manifest.py:sync_state_manifest_path` via `state.setdefault("skill_selection_variant", "b")`. Backed by a 60-trial A/B + scale experiment (curated 5-skill menu beat BM25/rerank over 205 skills). See `docs/decisions/2026-04-29-ship-forced-selection-phase5.md` for the decision record and `docs/plans/2026-04-29-skill-selection-*.md` for the experiments. Override with `skill_selection_variant: "a"` only to re-run the A/B.

## Auto-mode discipline

When auto mode is active and the user has approved a plan, do not ask permission for each routine sub-step (commits between approval gates, picking which row to swap, choosing one of two equivalent paths). The user's "yes" is durable until the next gate. If the user says "you select one," make the call and ship — presenting options instead of acting wastes a turn.

Auto mode executes bounded, approved substeps until the next explicit gate. It is not permission to run an unattended backlog loop, invent new scope, or work through an open-ended plan without returning to the user at the defined checkpoint.


Agentic multi-phase workflow for building features. **Executor/Advisor strategy:** Sonnet executor runs the main loop (exploring, drafting, implementing). Opus advisor fires on-demand at 3-5 decision points. **Workflow is project-generic; the Phase 0 trigger matrix and Phase 5 forced-selection menu are project-specific** — see `references/project-skill-menu.md` for the default (CourierFlow) menu and replacement guidance.

**Announce:** "Running claude-flow — loading context, exploring codebase, then building with you."

---

## Model Assignments

| Role | Model | When |
|------|-------|------|
| **Executor** | **sonnet** | Every turn — exploration, drafting, implementation, all file I/O |
| **Advisor (tiered)** | **sonnet** Phase 2, **opus** Phase 4 | Sonnet for gap-finding, Opus for architecture + plan critique |
| **Lightweight reviewer** | **haiku** | Phase 6 — single batched dispatch (types, API docs, invariants, defensive) |
| **Specialist reviewers** | **sonnet** | Phase 6 — safety (combined), test coverage |

**First-party adjacent levers:** `/model opusplan` mirrors this Executor/Advisor split at the main-loop level — use it for interactive plan-then-execute runs (Opus drafts the plan, Sonnet executes). Per-dispatch `model:` parameters still apply for subagent fan-out. Skill `model:`/`effort:` frontmatter, `/context` for size pre-checks, and `/plan` (Shift+Tab) for Plan Mode are all complementary to claude-flow's phase routing.

---

## How to Use This Workflow

> **Maintainer note on the split:** Router + phase + reference layout is intentional — 8 paths × several sub-flows would burn ~30K tokens inline. Decision rationale in `docs/plans/2026-04-29-skill-selection-vs-progressive-disclosure.md`; quarterly health checks (load-frequency, menu drift, stale cross-refs) in `REMINDERS.md`. Reversal threshold: any phase file loading <2× per quarter for two quarters → inline or delete.

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
| `--goal` | Phases 5, 6 | Auto-set `/goal` at phase entry with a condition derived from `$plan.steps[].test_requirements` (Phase 5) or the Verification Ladder + Finish Branch (Phase 6). Auto-clear at phase exit, turn-budget exhaustion, or any subsequent user-approval gate. Off by default — `/goal` is a session-scoped slash command that keeps Claude working across turns until a small fast model confirms the condition; it is NOT permission to run an open-ended backlog. See "Goal-mode auto-injection" below. |
| `--no-goal` | Phases 5, 6 | Disable goal-mode injection even when `--goal` was set on a prior turn. Honors a user's manual `/goal clear`. |

---

## Goal-mode auto-injection (`--goal`)

When `--goal` is set, the executor invokes the `/goal` slash command at Phase 5 entry and Phase 6 entry — not before, not mid-phase. `/goal` "starts a turn immediately, with the condition itself as the directive" (see [Claude Code docs § /goal](https://code.claude.com/docs/en/goal)), so injecting mid-phase disrupts whatever the executor is doing.

**Scope rules:**

- **Only after user-approval gates.** Phase 5 goal injects AFTER the user approves `$plan` in Phase 4b. Phase 6 goal injects AFTER `$diff` is produced and the executor enters the review cascade. Never inject during Phase 2/3/4 — those phases have user-approval gates that a goal would attempt to autopilot through.
- **One goal at a time.** `/goal` permits one active goal per session. Before injecting, check status via `/goal` (no arg). If a user-set goal is already active, surface it and ask before replacing — do not silently overwrite.
- **Auto-clear at phase exit.** When Phase 5 transitions to Phase 5.5, OR Phase 6 transitions to `complete`, OR the iteration limit in `workflow-profiles.json` is hit, the executor runs `/goal clear` before the next phase begins. The Phase 5.5 reflection step must not run under an active Phase 5 goal.
- **Resume hygiene.** A `/goal` carries over on `--resume`/`--continue`, but the workflow's phase context does not. On resume, check `state.phase` in the run manifest against the active goal's phase tag; if they disagree, `/goal clear` and let the user re-engage explicitly.
- **Anti-cheat clauses are mandatory.** The evaluator (Haiku) can't run tools — it only judges what the executor has surfaced. A naive "tests pass" condition is gameable by `pytest.skip`, deleting tests, or mocking `db.execute` to mask WHERE-clause bugs. Every injected goal MUST include:
  - "no new `pytest.skip` / `xfail` / `skipif` markers in `$diff`"
  - "no test file deletions in `$diff` unless paired with replacements"
  - "phantom-completion audit shows 0 MUST-FIX"
  - turn budget from `workflow-profiles.json:goal_turn_budgets[<path>][<phase>]`

**Off-limits paths:** `--goal` is rejected on FAST, EXPLORE, AUDIT, and BUG paths. FAST is single-turn; EXPLORE has no falsifiable end state; AUDIT produces a report (not a green-CI gate); BUG hands off to `/bug-fix` which owns its own loop. The flag is silently a no-op on CLONE PATH (Phase 5 only — Phase 6 still applies).

**Composition:** `--goal` composes with `--lite` (smaller turn budget) and with auto mode (auto mode handles per-tool prompts; goal handles per-turn prompts). Per the docs, the combination is the canonical unattended-execution mode.

**Risk surfacing:** Per the Path Decision risk screen below — if the task hits `auth`, `privacy`, `money`, `data_loss`, `external_side_effects`, or `public_api`, `--goal` is downgraded with a warning. The user can confirm to keep it; default is "skip goal-mode, keep gates manual" because evaluator misses on these classes are the most expensive.

**Manifest persistence:** Every goal-mode lifecycle event (`set` / `clear` / `achieved` / `budget_exhausted` / `replaced`) is recorded via `scripts/run_manifest.py record-goal`, which appends an entry to `manifest.goal_runs[]` (hashed condition, turn budget, path, phase) and mirrors `state.flags.goal` so the flag round-trips across `--resume`. The condition text itself is NOT persisted — only its SHA256 — so post-hoc inspection compares hashes against the canonical condition templates in the phase files. See `record-goal` in the CLI help.

---

## Path Decision (Phase 1 Core Logic)

```
DIRECT-ROUTE? ("synthetic beta test", "alpha test with personas",
                "assess usability with simulated users", "run persona-based eval")
  → Invoke /personas skill — EXIT workflow

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

**Streaming watches via the `Monitor` tool:** When a phase needs one-notification-per-occurrence (PR check progression, prod log errors during deploy soak, dev-server errors during UI verification, long-running test loops), use `Monitor` instead of polling via Bash. Each stdout line is a conversation event; the executor keeps working in parallel. See `references/monitor-tool-patterns.md` for filter discipline (silence is not success — include failure signatures, not just success markers), Phase 5 / Phase 6 recipes, and decision rules vs. `Bash run_in_background`. Load only when a phase actually needs a streaming watch.

---

## Phase Output Contracts

| Contract | Schema File | Produced By | Consumed By |
|----------|-------------|-------------|-------------|
| `$exploration` | `contracts/exploration.schema.md` | Phase 2 | Phases 3, 4, advisors |
| `$requirements` | `contracts/requirements.schema.md` | Phase 3 | Phases 4, 4c, 5, 6 |
| `$design_context` | `contracts/design-context.schema.md` | Phase 0/4 UI preflight | Phases 4, 5, 6 |
| `$plan` | `contracts/plan.schema.md` | Phase 4b | Phases 4c, 4d, 5, 6 |
| `$diff` | `contracts/diff.schema.md` | Phase 5 | Phase 6 |

Contracts are the interface between phases. When dispatching subagents, pass the named contract — not raw conversation. See each schema file for field definitions and notes. If success depends on a specific skill, docs source, MCP server, CLI, or browser/testing tool, name it explicitly in the dispatch prompt instead of assuming the subagent will discover or choose it.

For UI-affecting work, `$design_context` carries the project design system and
the task-specific design brief; project-local UI instructions override generic
frontend-design guidance.

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

---

## Notes

- **`--lite` for same-session-validated plans (single observation, 2026-05-13):** When the user invokes `--lite` on a task where the plan was validated in-session (tier-0 review done, drafts in the diff being shipped, edit anchors already verified), Phase 1–3 router content is largely unused. Validated once on PR #668 (~10 tool calls start-to-PR; router/path-decision content mostly bypassed in favor of direct apply). If this pattern recurs, consider an `--apply-only` flag that skips Phase 1–3 and goes straight to apply + ship. Single observation; not a confirmed pattern. TodoWrite firing 3 times in a 10-step linear task was also noisy at that scale.
