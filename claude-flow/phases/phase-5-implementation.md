# Phase 5: Implementation (TDD + Defensive Patterns)

<!-- Loaded: after Phase 4d (or Phase 4 for lite) | Dropped: after tests+lint pass -->
<!-- Output: $diff contract -->
<!-- Implementation detail for mutation gate, visual verify, authoring-time lookups, and cross-model retry has moved to memory/ entries (mutation_gate_component, visual_verify_gate, authoring_time_lookups, cross_model_retry_ladder). This file orchestrates; it no longer documents internals. See memory/phase5_inline_to_references.md. -->

---

## Streaming watches (Monitor tool)

For long-running tests, dev-server tails, or worker logs during implementation, use `Monitor` instead of polling via Bash. Each stdout line streams as a notification while the executor keeps drafting. Filter must include failure signatures (`ERROR|Traceback|FAILED|Killed|OOM`), not just success markers — silence is not success. See `references/monitor-tool-patterns.md` §Phase 5 for recipes (test loops, dev-server tails, worker watches) and decision rules vs. `Bash run_in_background`.

---

## Context Management

Load `references/phase-5-context-management.md` only when:

- the loop is long enough to threaten context limits
- you are dispatching multiple implementer subagents
- compaction behavior itself becomes relevant

Phase 5 consumes:

- `$verified_plan` or `$plan`
- `$exploration`
- `$requirements`
- `$test_skeletons` on full path

Phase 5 produces:

- `$diff`

Never pass to subagents:

- advisor transcripts
- rejected architecture details
- Phase 0 loading decisions
- raw clarification Q&A

---

## Phase 5: Implementation

<HARD-GATE>
User must approve the plan before any implementation begins.
</HARD-GATE>

### Read the Sprint Contract first

Before any tool calls, read `.claude/sprint-contract.json` (emitted by Phase 4 Step 5c). The `exclusions` array is a **hard boundary** — items listed there are out of scope for this phase. Do not touch them even if they look related, broken, or trivially improvable. If the in-flight work surfaces a real reason to violate an exclusion, stop and surface it to the user as a scope-amendment request — do not silently expand.

The `verification_standards` map is the per-task definition-of-done. A task is not complete until its listed commands/artifacts produce the expected result; see WIP=1 + VCR below.

Source: [Learn Harness Engineering, lecture 11](https://walkinglabs.github.io/learn-harness-engineering/en/) — exclusions as the structural defense against scope creep.

### WIP=1 + Verified Completion Rate (VCR) invariant

**WIP=1:** Exactly one task in `$plan.steps` may have status `in_progress` at any time. Mark the next task `in_progress` only after the previous task is `verified_complete` (not just `complete`).

**Verified Completion Rate:** `VCR = verified_complete / total_attempted` reported at every task boundary.

- A task is `verified_complete` only when its `verification_standards` from the Sprint Contract have been run and produced the expected result (command exited 0, artifact exists with expected content, test passed). Reading the diff and concluding "looks right" does NOT count.
- A task that was marked `complete` but failed verification is `attempted_not_verified` and contributes to the denominator but not the numerator.
- The existing Phantom-Completion Audit (HARD GATE before Phase 5.5) is the canonical VCR computation — its output (`X [X] tasks audited, Y verified, Z downgraded to [~]`) IS the VCR signal. Wire the audit's numerator/denominator into the phase-exit summary as `vcr: 0.XX`.

**Block new task activation when `vcr < 1.0`.** If any prior task is `attempted_not_verified`, do not mark the next task `in_progress`. Either finish the verification (run the standards command, fix the gap) or amend the plan with an explicit `[~]` and justification. This converts the silent-skip failure mode (mark complete → move on → audit catches it at phase exit) into a per-task gate.

Source: [Learn Harness Engineering, lecture 07](https://walkinglabs.github.io/learn-harness-engineering/en/) — WIP=1 and Verified Completion Rate as the two invariants that keep agentic execution honest at task granularity, not just phase granularity.

### Goal-mode entry (when `--goal` is set)

After the plan approval gate clears and BEFORE invoking the External API Contract gate, check `state.flags.goal === true` and inject the Phase 5 goal:

```text
/goal $plan.steps all have status=complete; uv run pytest <touched-dirs> exits 0;
uv run ruff check <touched-dirs> exits 0; static analysis (semgrep --severity ERROR,
ast-grep scan) reports 0 ERROR-level findings; phantom-completion audit (per
executing-plans § "Step 4.5") shows 0 MUST-FIX; no new pytest.skip/xfail/skipif
markers added in $diff; no test files deleted in $diff without replacement;
$diff.context_facts captured for any task that surfaced new domain knowledge;
or stop after <workflow-profiles.goal_turn_budgets[<path>][phase-5]> turns
```

Before injection: run `/goal` with no arg. If a user-set goal is active, surface its condition and ask whether to replace. If `--no-goal` is set or `state.flags.goal === false`, skip injection entirely.

After injection, record the event:

```bash
python3 <claude-flow-root>/scripts/run_manifest.py record-goal \
  --manifest .claude/runs/<session-id>.json \
  --state-file .claude/workflow-state.json \
  --phase phase-5 --action set --goal-flag \
  --path-name "<workflow_path>" \
  --turn-budget "<goal_turn_budgets[<path>][phase-5]>" \
  --condition-file /tmp/goal-condition.txt
```

At Phase 5 exit (transition to Phase 5.5): run `/goal clear` so the reflection step runs without an active goal driving the loop, and record the clear:

```bash
python3 <claude-flow-root>/scripts/run_manifest.py record-goal \
  --manifest .claude/runs/<session-id>.json \
  --state-file .claude/workflow-state.json \
  --phase phase-5 --action achieved --no-goal-flag
```

Use `--action budget_exhausted` instead when the turn budget tripped before the condition was met.

### Pre-Implementation: Verify External API Contract

<HARD-GATE>
If ANY plan step involves calling an external API (GitHub, Google Calendar, Twilio, OpenAI, DocuSeal, Stripe, Supabase, Railway, Sentry, Slack, etc.), verify the current API contract BEFORE writing code. Do NOT code against external APIs from memory — endpoints, request formats, and auth patterns change between versions. This gate applies even if you loaded the integrations skill in Phase 0.
</HARD-GATE>

Load `references/phase-5-external-api-gate.md` only when the current step
touches an external API.

### Create TodoWrite Items

Break the plan into individual TodoWrite items. Mark each complete as you finish it.

### Execute Each Step

For each plan step:

```
1. Write test FIRST (see `claude-flow/references/test-driven-development.md`)
   - Test the expected behavior, not the implementation
   - Include edge cases identified in Phase 3

2. Implement to make the test pass
   - Follow patterns discovered in Phase 2
   - Apply defensive patterns throughout:
     UI → guard clauses, feedback states, loading/error/success
     Backend → input validation, error handling, no silent swallows

3. Run test → verify green
   - If test fails and the error is NOT self-explanatory:
     invoke /investigator with the failure as input.
     Review the evidence matrix BEFORE attempting a fix.
     (Prevents fix-retry loops on complex failures.)

   3a'. **Implementer pushback protocol:** When a code-quality or spec-review reviewer makes claims about external-tool behavior (CLI flag semantics, config discovery order, exit-code meanings), implementers MUST verify empirically before applying the fix. Record that verification in the run manifest or review notes, not in product code comments. Reviewer authority does not override tool output. See `reviewer_claims_need_verification.md`.

   3a. If one fix attempt already failed, load
       `references/phase-5-retry-and-facts.md` and apply the
       explain-before-fix gate before iter-2.

   3b. After the target test passes, load
       `references/phase-5-retry-and-facts.md` and run the scoped
       regression guard before proceeding.

   3e. After tests and guard pass, load
       `references/phase-5-retry-and-facts.md` and extract reusable
       context facts into `$diff.context_facts` when the task discovered
       new domain knowledge.

4. Run static analysis on changed files (catch issues early):
   semgrep --config=.semgrep.yml <changed-files>
   ast-grep scan <changed-directory>

   Fix any ERROR-level issues before proceeding.

5. Mark TodoWrite item complete

6. Inter-task verification gate (proactive, not just reactive):
   Run full test suite + lint + build check BEFORE starting next task.
   Catches cross-TASK regressions (step 3b catches within-FIX ones).
   See `claude-flow/references/subagent-driven-development.md` for full gate protocol.
   Skip full suite for Task 1 or trivial tasks.
   If gate fails → fix regression → re-verify → then proceed.
```

### Mid-Plan Coherence Check (every 3-5 steps)

After every N completed plan steps (default: every 3 steps; for plans with ≥8 steps,
every 5 steps), run a compact structured self-check BEFORE starting the next step.
This is a prompt-level gate — no new subagent, no world-state model, no A*.

**Trigger condition:** step index mod N == 0 AND at least one more plan step remains.

**Coherence check prompt (inject inline, ~150 tokens):**

```
PLAN COHERENCE CHECK — pause before step [N+1] of [total].

Answer three questions based only on what has been built and discovered so far:

1. COMPLETED: Which steps are done with passing tests?
   (List step numbers only.)

2. INVALIDATED: Has anything discovered or built since the plan was written
   changed the preconditions or approach for any REMAINING step?
   (If yes, name the step and what changed. If no, say "none".)

3. VERDICT:
   - "continue" — remaining steps are still valid as written; proceed.
   - "surface" — a discovery invalidates at least one remaining step;
     describe it and stop for user input before proceeding.
```

**Routing on verdict:**
- `continue` — proceed immediately to the next plan step; log the check result in the
  run manifest.
- `surface` — DO NOT proceed to the next step. Surface the invalidating discovery
  to the user with: (a) which step is affected, (b) what changed, (c) a proposed
  amendment or a request for direction. Wait for user input before resuming.
  Log the escalation in the run manifest.

**Scope guard:** the coherence check is bounded to three questions and returns one of
two verdicts. It does not re-derive the plan, re-run Phase 4 analysis, or spawn
additional agents. A "surface" verdict is not a restart — it is a targeted flag.
Local fixes (a test fails on a type error) stay local and do not trigger "surface."
Only plan-invalidating discoveries (the architecture doesn't fit, a discovered
constraint blocks a remaining step) warrant "surface."

**Skipped when:** plan has ≤2 remaining steps after the check trigger, or the task
is Lite-mode with <3 total steps (the inter-task gate already covers those).

---

### Long Loops and Fresh Context

If the plan has 5+ steps or context pressure is noticeable, load
`references/phase-5-context-management.md` and compact the working set.

When dispatching the next task's subagent, include prior
`$diff.context_facts` as a short "Known context from earlier tasks" preamble.

### Advisor: Mid-Implementation (optional)

Only at genuinely ambiguous decision points. Not routine steps.
Dispatch Sonnet with: specific decision context from current `$plan` step.
Question: focused on the specific ambiguity.

Downgraded from Opus to Sonnet 2026-04-24 after a 15-trial dual-judge eval showed the two models tied on mid-implementation reasoning (both 0.989 judge score). See `decisions/2026-04-24-sonnet-vs-opus-phase-downgrade.md` in the claude_flow repo.

**When to call:** non-obvious integration patterns, conflicting precedents, step diverging from plan in ways affecting later steps.
**When NOT to call:** routine implementation, standard TDD cycles with clear requirements, unambiguous plan steps.

### Subagent Skill Loading

When a Phase 5 subagent dispatch could plausibly use ≥2 domain skills (UI / API / data / integrations / security), check `skill_selection_variant` in workflow-state. Default is `"b"` (shipped 2026-04-29 — see [decision record](../docs/decisions/2026-04-29-ship-forced-selection-phase5.md)).

For UI-affecting tasks, carry `$design_context` into implementation dispatches.
Implementers must preserve centralized design-system patterns and satisfy the
task design brief's required states before polishing visuals.

- **Variant B (forced selection — DEFAULT):** Prepend the following block to the subagent prompt. The `Available skills` list below is the **default CourierFlow menu** — replace it with your project's menu (see `../references/project-skill-menu.md` for authoring rules).

  ```
  Before any tool calls, output exactly one line:
  SELECTED_SKILL: <name|none>

  Available skills (pick one):
  - courierflow-ui — Frontend code: Jinja templates, CSS, Vue workflow builder pages, dashboards, calendar/sidebar layouts; preserve design-system alignment, task-specific design brief, complete UI states, and centralized patterns over one-off styles
  - courierflow-api — Backend route and service code: FastAPI routes, service layer, business logic, request handlers
  - courierflow-data — Database layer: SQLAlchemy ORM models, Alembic migrations, schema design, eager-loading, Household/HouseholdMember domain
  - courierflow-integrations — External services: Google Calendar, Twilio SMS, OpenAI, DocuSeal, Gmail, onboarding wizard
  - courierflow-security — Auth, registration, login, secrets, permissions, session handling, landlord/tenant access

  Pick "none" only if the task is fully solvable with built-in tools.
  After your SELECTED_SKILL line, the orchestrator will inject that skill's
  full content (or none). One commit per dispatch — no mid-task switching.
  ```

  After the subagent emits `SELECTED_SKILL:`, the orchestrator parses the line, injects the chosen SKILL.md, and the subagent resumes. Log the selection + ground-truth gold via `scripts/log_skill_selection.py`.

- **Variant A (opt-out / progressive disclosure):** Pre-2026-04-29 behavior — list available skills as "you may invoke if useful." Use only for re-running the A/B experiment (set `skill_selection_variant: "a"` in workflow-state). Do not use for production work.

Variant B's curated 5-skill menu is hand-selected to be domain-coherent. Per the [scale experiment](../docs/plans/2026-04-29-skill-selection-at-scale.md), retrieving from a broader corpus (BM25 / rerank) under-performed this curated menu. Do not replace the menu with retrieval without re-running the experiment.

Keep `courierflow-troubleshooter`, `courierflow-skill-sync`, and
`courierflow-skill-reviewer` out of the implementation forced-selection menu.
Use them in Phase 0 or maintenance/diagnosis tasks; Phase 5 implementers should
select one code-surface skill above.

### Parallel Subagent Dispatch (For Independent Steps)

When the plan has 3+ steps with no dependencies between them:

```
Follow `claude-flow/references/subagent-driven-development.md`:
  → Dispatch parallel implementation agents with model: "sonnet"
  → Each follows the same TDD + defensive pattern
  → Merge results when all complete
```

> **Explicit parallel fan-out (Opus 4.7):** When dispatching N independent reviewers / researchers / implementers across M items, emit a single message with N tool-use blocks. Do **not** issue them sequentially — 4.7's default bias is under-parallelization.

<!-- Task taxonomy (types + dependency types) defined in writing-plans/SKILL.md. Keep in sync. -->
**Dependency-aware dispatch:**
- `data` or `build` dependencies → strictly sequential (predecessor must complete first)
- `knowledge` dependencies → parallelizable (dispatch concurrently, record assumptions in each subagent's context)
- Tasks with no dependencies → parallelizable
- `shared_prerequisite` tasks → always execute before dependent `value_unit` tasks

### Conditional Specialist Reviews (During Implementation)

When a plan step produces code matching a specialist's domain, dispatch the specialist immediately (**sonnet**, background) before proceeding to the next step:

| Trigger | Agent | Action on CRITICAL |
|---------|-------|--------------------|
| Alembic migration file created/modified | `migration-reviewer` | Fix before next step |
| Google Calendar/Drive/Gmail API code | `google-api-reviewer` | Fix before next step |
| `async def` with I/O operations | `async-reviewer` | Fix before next step |

MEDIUM/LOW findings defer to Phase 6 review. Agents that ran in Phase 5 are **skipped** in Phase 6 (no double review).

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

### Phantom-Completion Audit (HARD GATE before Phase 5.5)

After the final task in the plan is marked complete and tests+lint pass, run the phantom-completion audit from `executing-plans/SKILL.md` § "Step 4.5: Phantom-Completion Audit" before transitioning to Phase 5.5.

For each `[X]` task in the plan, verify the promised artifacts (files, symbols, migration revisions) actually exist on disk and the diff against `origin/main` is non-empty. Downgrade unverified `[X]` to `[~]` and either complete the work or amend the plan with justification — never silently ship a hollow checkmark.

**Skip:** Lite-mode plans with <3 tasks where the per-task inter-task verification gate already inspected each diff.

**State transition:** If tests+lint pass AND phantom-completion audit is clean, transition to phase-5.5. If failed
and iteration < 3, load `references/phase-5-retry-and-facts.md` and follow the
retry ladder. If iteration limit is reached, set status to "failed" and surface
it to the user.

---

## Agent-Oriented Error Messages (what + why + fix)

Error and diagnostic output produced during Phase 5 — hook output, lint rules, finding payloads, test failures emitted by project-local helpers, structured logs — must follow a three-element format so the consuming agent has enough signal to act without re-deriving context:

```
ERROR: <what failed, as observable fact>
WHY:   <root cause or most-likely cause, named concretely>
FIX:   <the next concrete action — command, edit, or decision>
```

Example (good):

```
ERROR: pytest tests/test_workflows.py::test_create exited 1 with AssertionError on line 42.
WHY:   The fixture `workflow_factory` returns a Workflow with status=draft, but the assertion expects status=active. The fixture default changed in commit a1b2c3d.
FIX:   Either update the assertion to expect `draft`, or pass `status="active"` to the factory call on line 38.
```

Example (bad — what's wrong, no signal on why or fix):

```
AssertionError: expected 'active', got 'draft'
```

**Where to apply:** any hook that emits to stdout/stderr during Phase 5, custom lint rules and detectors, finding payloads from in-repo reviewers (`pr-reviewer/triage.ts` in the claude_flow repo is the canonical implementation site — output finding JSON should include `what`/`why`/`fix` keys, not just `message`), test-helper assertion messages, and structured-log statements that another agent or human will read.

**Where NOT to apply:** raw tool output from third-party CLIs (pytest, ruff, semgrep) — wrapping their output would lose grep-ability. The rule covers messages this codebase emits, not messages it merely passes through.

Source: [Learn Harness Engineering, lecture 10](https://walkinglabs.github.io/learn-harness-engineering/en/) — Agent-Oriented Error Messages as the diagnostic contract that lets downstream agents recover without round-tripping for context.

---

## Multi-surface features — phased commits

For features spanning multiple surfaces (backend + client + infra, >500 LoC), Phase 5 MAY land as N logical phase commits on one branch rather than a single commit. Each phase must leave full test suites green. See `executing-plans` § "Multi-Surface Features: Phased Commits with Green Between" for the DAG-documentation convention, labeling (A–F), and skip criteria.

---

## Turn-closing summary discipline

When closing a turn that includes Edit/Write tool calls, cite evidence in the summary: `path/to/file.md:L12-18` refs, `git diff --stat` output, or `gh pr view --json mergedAt`. The Edit tool's "updated successfully" response doesn't render prominently in the user transcript, so bare claims ("edits applied", "fixed", "shipped") read as unverifiable and trip approval-challenge hooks. Autocommit/stop hooks can also land work between your edits and the summary — cite the commit SHA or PR URL when that happens. Same bar for Phase 6 quality-gate summaries. Project-level analog: courierflow CLAUDE.md boundary #8.
