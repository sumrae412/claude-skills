# Design Spike — GOAP Resume-from-State Replanning for claude_flow

**Date:** 2026-06-26
**Status:** NO-GO (as described in ruflo) — GO-WITH-SCOPE on the extractable idea (see recommendation)
**Skill:** [`claude-flow/SKILL.md`](../../claude-flow/SKILL.md)
**Prompted by:** ruflo repo (ruvnet/ruflo) marketing claim: "the planner re-runs A* from current state when something changes mid-run instead of restarting"

---

## The question

Should claude_flow adopt GOAP-style "resume-from-current-state" replanning? When a mid-build step fails or a requirement changes, claude_flow currently escalates to the user after 3 retry attempts and has no checkpoint-resume mechanic. Could we borrow an A*-style world-state model to replan from the mid-flight state instead of asking the user to restart?

---

## What ruflo actually does (vs. what it claims)

The ruflo README is marketing-forward. Actual source audit found three distinct components that together constitute the claim:

### 1. A* planner — `goapPlanner.ts` (real, but static)

A textbook A* implementation (`v3/goal_ui/src/lib/goapPlanner.ts`). The `plan(currentState, goalState, userGoal)` function takes a world-state as input — meaning you *can* call it mid-execution with an updated state. That part is real.

What does NOT exist:
- Any automated trigger that detects "an action failed" and calls `plan()` again
- Any resumable plan object that tracks "we are at step N"
- Any mechanism to sync real-world execution results back into `WorldState`

The planner is a pure function. It produces a sequence. Once that sequence is handed off to the agent, the planner is done — there is no feedback loop.

### 2. "Adaptive replanning" — LLM steering, not algorithmic

The goal-planner agent (`plugins/ruflo-goals/agents/goal-planner.md`) instructs Claude (the LLM) to notice failures in tool output, decide a replan is needed, and call the planner again with updated state. The "replanning" is the LLM's judgment, not a programmatic event loop. The system cannot detect that action 4 of 7 failed and recompute — Claude has to read the text output, decide the action failed, and manually construct the new `currentState` JSON to feed back in.

### 3. Planning checkpoints — prompt injection every N turns

In the GAIA benchmark loop (`gaia-agent.ts`), every 4 tool-use turns the system injects:

> "Briefly summarize what you have learned. State whether your current approach is making progress. If NOT making progress, switch strategy."

This is **prompt injection** — telling Claude to reconsider, not recomputing any state-space search. It is the LLM equivalent of asking a person "are you still on track?" every few steps.

### The gap

| Claim | Reality |
|---|---|
| "Planner re-runs A* from current state on failure" | Plan() accepts currentState ✅, but no failure trigger exists ❌ |
| "Failures become replanning inputs" | Failure is detected by Claude reading text output (no code) |
| "Resume from current state instead of restarting" | No resumable plan object; each replan is a fresh call to plan() |
| "Adaptive replanning" | LLM-steered, not algorithmic |

---

## How claude_flow currently handles mid-build changes

From reading the phase pipeline:

| Situation | Current response |
|---|---|
| Step test fails once | Fix locally, re-verify in same step |
| Step test fails a second time | Load explain-before-fix gate; understand before iter-3 |
| Step test fails 3+ times | Escalate to user; set status `failed` |
| New requirement discovered mid-Phase 5 | Surface in Phase 5.5/6 OR stop and hand to user |
| Architecture doesn't fit mid-implementation | Not covered; expected to be caught in Phase 4c before Phase 5 |
| Full plan restart needed | Not a built-in flow; user must manually restart or handoff |

claude_flow's design philosophy treats Phase 4 (plan + advisor critique + user approval) as the failure-prevention gate. Mid-phase requirement changes are handled locally (retry ladder) or escalated — there is no checkpoint-resume mechanic.

**Relevant gate (Phase 5):**
> "If iteration limit is reached, set status to 'failed' and surface it to the user."

---

## What GOAP resume-from-state would concretely mean for claude_flow

If we were to implement the idea properly — not borrow ruflo's marketing, but implement actual resume-from-state replanning — here is what it would require:

### The world-state model problem

A* needs a `WorldState` object that can be (a) serialized, (b) updated when an action succeeds or fails, and (c) used to recompute a plan. For ruflo's toy planning scenarios, `WorldState` is a simple boolean flag dict: `{ "auth_token_obtained": true, "file_written": false }`.

For claude_flow's plan→build loop, `WorldState` would need to encode:
- Which plan steps are complete (with evidence)
- Which files have been created/modified
- Which tests pass
- What discoveries Phase 2 made that are still load-bearing
- What the Phase 3 acceptance criteria are
- What the Phase 4 plan structure is

This is not a flag dict. It is the full project context. The state-space is enormous and non-enumerable.

### The action definition problem

A* needs a set of actions with preconditions and effects. In ruflo, actions are things like "obtain auth token" with `precondition: { browser_open: true }` and `effect: { auth_token: true }`. These are narrow, enumerable, and deterministic.

claude_flow's "actions" are LLM-driven plan steps: "implement the UserAuth component," "add the tenancy schema migration," "write tests for the billing module." Their preconditions and effects are:
- Probabilistic (LLM output is not deterministic)
- Not statically enumerable (the plan is generated per-task)
- Interdependent in ways that are discovered during execution, not known upfront

A* over this space would be nominal at best — the search graph cannot be constructed before the plan is known.

### The trigger problem

For automatic replanning, something must detect that an action failed and initiate a replan. In ruflo, this is done by the LLM noticing failure in text output (not by code). For claude_flow, the same is already true — the retry ladder in Phase 5 is already detecting failure (test doesn't pass) and attempting local recovery.

The question is whether the local recovery should include "recompute the plan from here" rather than "fix the current step." For most failures (a test fails because of a type error, a missing import, a wrong function signature), local repair is better — replanning would waste cycles reordering steps that don't need reordering.

For the minority of failures that require replanning (the Phase 4 architecture doesn't fit the discovered constraints), replanning is already surfaced correctly — to the user, because the decision of how to replan involves deliberate product choices.

---

## What the extractable idea actually is

Strip the A*/GOAP branding from ruflo's planning checkpoints and the extractable idea is:

> **Every N steps in a long implementation loop, inject a structured status check: "are you still on track, or has something changed that invalidates the remaining plan?"**

This is an honest, useful, low-cost idea. It maps to something claude_flow already does implicitly in Phase 5.5 (RARV reflection) and Phase 6 (quality review), but those run at the END of implementation — not mid-flight.

The ruflo version (planning checkpoint every 4 tool calls in GAIA) is coarser. A claude_flow version would be:

- After every N plan steps (where N is configurable, default 3-5 for a multi-step plan)
- Run a structured "plan coherence check" prompt:
  1. Which steps are complete with passing tests?
  2. Have any discoveries invalidated a remaining step's preconditions?
  3. Is the approved plan still the right path, or should we surface a proposed amendment to the user?

This requires no A* implementation, no world-state model, no action graph. It is a prompt injection at step-N intervals, same as ruflo's GAIA checkpoints.

---

## Risks

1. **False-positive replanning signal.** A mid-plan coherence check might flag "architecture changed" when the actual issue is a one-line fix. This adds a round-trip to the user for noise. Mitigation: coherence check only surfaces to user if the agent flags a plan-invalidating discovery; local fixes stay local.

2. **Context bloat.** Adding a mid-plan reflection step loads more content into Phase 5's already-long context. Mitigation: the coherence check is a compact prompt (no phase file load), 100-200 tokens.

3. **Scope creep in the "check."** A coherence check that tries to be too clever (re-derive the plan from scratch, re-run Phase 4 analysis) becomes the replanning overhead problem we identified above. Mitigation: the check is bounded — three questions, no new subagent, result is binary (continue / surface-to-user).

4. **No test coverage for mid-plan pivots.** claude_flow has no current eval for "detects plan-invalidating discovery mid-Phase 5." Adding this mechanic without evals means we can't verify it helps. Mitigation: add a synthetic eval case (plan step 3 of 5 discovers the DB schema is wrong; does the check surface it?).

   **Validation status — parser fixed; clean re-run pending.**
   Date fixed: 2026-06-29.

   **What happened on the first validation attempt (2026-06-26):** the one-time run
   produced a "50% FAIL / detection-weakness-found" result that triggered a
   "prompt too aggressive / fails to detect" auto-caveat. This was a MEASUREMENT
   ARTIFACT — NOT a genuine detection weakness. Three compounding causes:

   1. **Parser gap (now fixed).** `parse_verdict` required the VERDICT label and
      the verdict keyword on the **same line** (`[^\n]*` in the regex). The model
      correctly emitted `**3. VERDICT**\nContinue.` (label on one line, keyword on
      the next), but the old pattern returned `"unknown"` for that format. All 6
      clean-state ("continue") samples were misclassified — the model judgment was
      sound; the parser was wrong. Fix: extended `_CONTINUE_PATTERN` and
      `_SURFACE_PATTERN` in `coherence_check.py` to match keyword on the next line
      after a standalone VERDICT label, including trailing punctuation and prose
      (`Continue.` / `Continue. Steps 3 and 4 are valid.` /
      `Surface — step 4 invalidated.`). Regression tests added in
      `test_coherence_check.py` (`test_continue_verdict_next_line_format`,
      `test_continue_verdict_next_line_with_trailing_prose`,
      `test_surface_verdict_next_line_with_trailing_prose`).

   2. **Dead model-id (now fixed).** Script pinned `claude-sonnet-4-5-20251022`,
      which 404'd on the live API. Updated to `claude-sonnet-4-6`.

   3. **Small-N noise.** N=3 samples per fixture means a single misclassified
      sample drops one fixture below the 2/3 pass threshold. Bumped default to
      N=10 to reduce small-sample variance on the clean re-run.

   **What the raw model outputs confirmed:** on the negative fixtures (clean state),
   the model answered `**3. VERDICT**\nContinue.` — correct reasoning, wrong parser.
   The positive fixtures (plan-invalidating discovery) were NOT re-examined in the
   one-time run (parser was treating continue samples as unknown, not surface), so
   the positive/surface direction still needs a clean re-run to confirm.

   **The coherence-check PROMPT in `phase-5-implementation.md` was NOT changed** —
   the model judgment was correct; tuning the prompt would have been wrong.

   To close this risk: `export ANTHROPIC_API_KEY=sk-ant-... && python3 claude-flow/scripts/validate_coherence_judgment.py`. Update this entry with the actual pass rates and change status to `resolved` or `resolved-with-caveat` or `detection-weakness-found`.
   If surface-recall is low on the clean re-run: tune the coherence-check PROMPT in `phase-5-implementation.md` § "Mid-Plan Coherence Check" — do NOT adjust fixtures to manufacture a pass.

---

## GO / NO-GO / GO-WITH-SCOPE recommendation

**NO-GO on adopting "GOAP resume-from-state replanning" as described in ruflo.**

Ruflo's GOAP claim does not hold up to source audit. The A* planner is a pure function that requires LLM-manual failure detection and LLM-manual state reconstruction to trigger. The marketing phrase "re-runs A* from the current state instead of restarting" obscures that the "replanning" is the LLM noticing failure in text and calling the planner again with a hand-crafted WorldState. For claude_flow's build loop, the world-state modeling problem and the action-definition problem make a real A* implementation impractical — the state space is the full project context, and the "actions" are LLM-generated, task-specific plan steps.

**GO-WITH-SCOPE on the extractable idea: structured mid-plan coherence checks.**

The honest, useful kernel inside ruflo's planning checkpoints is: inject a compact mid-execution status check every 3-5 plan steps that asks the agent whether any discoveries have invalidated the remaining plan, and gates escalation to the user when they have. This is distinct from replanning (it does not recompute a plan) — it is an early-warning signal for plan-invalidating discoveries, so they surface before Phase 5 exhausts its retry budget on the wrong architecture.

Implementation scope: one new clause in Phase 5's step-execution protocol (a "plan coherence check" trigger after every N steps, returning `continue` or `surface-to-user`), plus a corresponding eval case. No new subagent, no world-state model, no A* implementation. Estimate: 1-2 hours authoring + eval case.

---

## How to revisit

If a future version of ruflo ships an actual closed-loop replanning implementation (automated failure detection, stateful plan tracking, event-driven A* reinvocation), this NO-GO should be reconsidered. The direction is correct; the implementation is not there yet.

If the GO-WITH-SCOPE (structured mid-plan coherence check) is approved, the plan goes in `docs/plans/2026-06-26-phase5-coherence-check.md` and is handed to `claude_flow` for Phase 0-6 execution.

---

## Evidence

- claude_flow phase files read: SKILL.md, phase-0 through phase-6, phase-5.5, phase-4c
- ruflo source files read: `v3/goal_ui/src/lib/goapPlanner.ts` (180 lines), `plugins/ruflo-goals/agents/goal-planner.md`, `plugins/ruflo-goals/skills/goal-plan/SKILL.md`, `v3/@claude-flow/cli/src/benchmarks/gaia-agent.ts`, `v3/@claude-flow/browser/src/application/goap-preflight.ts`, `README.md`
- Open/merged PRs on "claude-flow replanning": none found
- git log since 2026-01-01 on claude-flow/: no checkpoint/resume commits
