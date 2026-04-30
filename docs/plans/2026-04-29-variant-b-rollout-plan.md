# Implementation Plan: Roll Out Variant B (Forced Skill Selection) as Phase 5 Default

**Date:** 2026-04-29
**Author:** Summer (via claude-flow `--plan-only`)
**Status:** Plan-only — awaiting user approval before Phase 5 implementation
**Path:** FULL workflow, stopped after Phase 4
**Dependencies:** [decision record](../decisions/2026-04-29-ship-forced-selection-phase5.md), [predecessor experiment](2026-04-29-skill-selection-vs-progressive-disclosure.md), [scale experiment](2026-04-29-skill-selection-at-scale.md)

---

## Phase 2 — `$exploration` (synthesized from prior experiment)

### Codebase artifacts already in place

| Path | Status | Role |
|---|---|---|
| [claude-flow/phases/phase-5-implementation.md](../../claude-flow/phases/phase-5-implementation.md) | Modified | Has the gated variant B prompt block under "Subagent Skill Loading"; gated on `skill_selection_variant` in workflow-state. Default is "a". |
| [claude-flow/scripts/log_skill_selection.py](../../claude-flow/scripts/log_skill_selection.py) | Created | Per-trial JSONL logger. Accepts variants `{a,b,b150,c1,c3}`. |
| [claude-flow/scripts/replay_skill_selection.py](../../claude-flow/scripts/replay_skill_selection.py) | Created | A/B replay harness. Produces `.claude/experiments/skill_selection_ab.jsonl`. |
| [claude-flow/scripts/analyze_skill_selection.py](../../claude-flow/scripts/analyze_skill_selection.py) | Created | Reads the JSONL log; computes 5 metrics; emits decision-tree recommendation. |
| [claude-flow/scripts/grade_end_task_pass.py](../../claude-flow/scripts/grade_end_task_pass.py) | Created | Applies pass-rubric to the JSONL log. |
| `.claude/experiments/skill_selection_ab.jsonl` | Populated | 60 trials across 5 variants. |
| Skill files at `~/.claude/skills/courierflow-{ui,api,data,integrations,security}/SKILL.md` | Unchanged | Skill descriptions in frontmatter still match the *old* 5-skill listing — the tightened versions live only in `.claude/experiments/skills_raw.txt`. |

### Workflow-state shape (current)

`workflow-state.json` is initialized by claude-flow at the top of each session for paths that have `state_machine: true`. Looking at `workflow-profiles.json`, paths `clone`, `lite`, `full`, `audit`, and `explore` all carry state. The variant B gate (`skill_selection_variant`) is a **new key** that doesn't yet appear in the canonical state schema.

Initialization happens in two places:
- Phase 1 (`phases/phase-1-discovery.md` §"After Choosing the Path") — initializes `review_base_sha`, `run_manifest_path`, capability snapshot.
- The state-lifecycle reference (`references/workflow-state-lifecycle.md`) documents the canonical fields.

There is no Python initializer that hard-codes defaults — claude-flow's state init is markdown-driven.

### Description-hygiene state

Tightened descriptions from `.claude/experiments/skills_raw.txt`:

```
courierflow-ui: Frontend code for courierflow — Jinja templates, CSS, Alpine.js, React components, workflow builder pages, dashboards, layouts, copilot UI surfaces.
courierflow-api: Backend route and service code for courierflow — FastAPI routes, service layer, business logic, request handlers, action executors, copilot agent runtime.
courierflow-data: Database layer for courierflow — SQLAlchemy ORM models, Alembic migrations, schema design, JSON and UUID column types, eager-loading, Household and HouseholdMember domain.
courierflow-integrations: External service integrations — Google Calendar scan and import, Twilio SMS, OpenAI, DocuSeal e-signature, Gmail contacts, onboarding wizard import flows.
courierflow-security: Authentication, authorization, registration, login, user accounts, secrets, permissions, session handling, landlord and tenant access boundaries for courierflow.
```

These need to land in the actual `~/.claude/skills/courierflow-*/SKILL.md` files' YAML frontmatter `description:` field. Per CLAUDE.md, `~/.claude/skills` is a symlink into `/Users/summerrae/claude_code/claude-skills/`, so edits land in the canonical repo and need to be committed/pushed from there.

### Scheduled-task infrastructure

The `mcp__scheduled-tasks__*` server is available (see system reminder — `create_scheduled_task`, `list_scheduled_tasks`, `update_scheduled_task`). The `/schedule` skill is also available. Either can fire a Claude Code session at a cron schedule. The hook needs to:

1. Run after 1 week of variant B being live.
2. Pull the live `.claude/experiments/skill_selection_ab.jsonl` (which the variant B gate writes to during real Phase 5 dispatches).
3. Run `analyze_skill_selection.py`.
4. Post results — either to a file under `docs/decisions/`, or as a comment on the original decision record.

---

## Phase 3 — `$requirements`

### Goal

Ship variant B as the default Phase 5 subagent skill-loading pattern, lock in the description-hygiene improvements that drove BM25 recall@5 from 62.5% → 100%, and put a 1-week verification hook in place so the lab numbers can be re-confirmed against live runs.

### In scope

1. **Flip variant default to "b"** in claude-flow workflow-state initialization, including documenting the new `skill_selection_variant` field in the state-lifecycle reference.
2. **Land tightened descriptions** in the 5 courierflow-* SKILL.md frontmatter files.
3. **Schedule a 1-week re-analysis** that pulls `skill_selection_ab.jsonl`, runs the analyzer, and writes a follow-up decision-record entry.

### Out of scope

- **CopilotKit gap.** Authoring a `courierflow-copilot` skill is tracked as a separate workstream. PR #511 still failed under every variant in the experiment; that's a known limitation.
- **Description hygiene for non-courierflow skills.** The 7-edit experiment showed dramatic recall improvements but the same hygiene applied to all 205 session-loaded skills is a separate PR with its own review burden.
- **Variant C / scale variants.** The scale experiment closed with "don't ship" — none of B-150 / C1 / C3 beat shipped variant B.
- **Skill-selection telemetry beyond the JSONL.** No new metrics endpoints, dashboards, or alerts.

### Acceptance criteria

- New claude-flow sessions on `lite`/`full`/`clone` paths initialize with `skill_selection_variant = "b"` in workflow-state.
- The 5 courierflow-* SKILL.md files carry the tightened descriptions in their YAML frontmatter and pass `lint-memory` + skill-discovery validation.
- A scheduled task is registered to fire 7 days from rollout, run the analyzer, and write a follow-up note. Task is reproducible (defined in code, not a one-shot MCP call).
- All changes ship as a single PR with `quick_ci.sh` green.

### Non-functional requirements

- **No regression on variant A behavior.** Sessions that explicitly set `skill_selection_variant = "a"` (e.g., for reproducing the experiment) must still work.
- **Description edits don't change skill *names* or file paths.** Only the `description:` frontmatter field changes — preserves all existing skill-discovery references.
- **Token cost.** Variant B's prompt block adds ~200 tokens per qualifying Phase 5 dispatch vs. variant A. Already accounted for in the experiment.

### Open questions (resolved)

- **Q: Should the variant B gate apply to all paths or only `full` / `lite`?**
  Resolved: apply to any path that runs Phase 5 (`full`, `lite`, `clone`, `plan`). `fast` and `audit` skip Phase 5 entirely. `bug` routes to `/bug-fix` and is out of scope.
- **Q: Where should the live JSONL log land in real Phase 5 runs?**
  Resolved: same path as the experiment — `.claude/experiments/skill_selection_ab.jsonl` relative to the active project root. The logger script accepts a `--log` override.
- **Q: How do we handle the 1-week scheduled task if variant B is rolled back during the soak?**
  Resolved: the analyzer compares variant counts; if `n` is small or skewed toward variant A, it will print "INCOMPLETE" via the existing decision-tree branch. No new code needed.

---

## Phase 4 — Architecture

### Two architecture options considered

**Option 1 — Single PR with all 3 changes bundled.**
One commit that flips the default, edits 5 SKILL.md files, and adds the scheduled-task definition. Simple, atomic, easy to revert.

**Option 2 — Three sequenced PRs.**
PR-A: SKILL.md description edits (lowest risk, lands first).
PR-B: variant default flip (depends on PR-A's improved descriptions).
PR-C: scheduled re-analysis hook (depends on PR-B being live for the soak window).

**Trade-off:**

| | Option 1 (bundled) | Option 2 (sequenced) |
|---|---|---|
| Review burden | 1 PR, ~80 LoC | 3 PRs, ~30 LoC each |
| Rollback granularity | All-or-nothing | Per-change |
| Soak signal cleanliness | Mixed (descriptions + variant flip change at same instant) | Clean (description hygiene effect isolated from variant flip) |
| Time-to-live | Same day | 3 days minimum (PR-B waits for PR-A merge; PR-C deferred 1 week) |

**Choice: Option 1 (bundled).** The changes are tightly coupled — the variant B gate already references the curated 5-skill menu; landing tightened descriptions in the same PR makes the menu coherent on day 1. Per CLAUDE.md feedback memory `feedback_summer_bundled_pr_for_coupled_changes.md` (if it exists; if not, this is the first such instance), bundling is the right call when the changes don't make sense in isolation. PR-B alone (variant flip without tightened descriptions) would ship a mismatch between the Phase 5 prompt block and the actual SKILL.md content.

The clean-soak-signal concern is real but addressable: the scheduled re-analysis script can compare the live `correct_skill_rate` against the experiment's 75.0% baseline. If live numbers tank, that's a signal regardless of which sub-change caused it.

### Risk register

| Risk | Mitigation |
|---|---|
| Symlink edit lands in wrong tree | Per CLAUDE.md "Plugin Cache / Skills Management": edit `~/.claude/skills/courierflow-*/SKILL.md` directly (it's the symlinked canonical path), then `cd /Users/summerrae/claude_code/claude-skills && git status` to confirm uncommitted changes show up there. |
| Variant flip breaks existing live sessions mid-flight | New gate field defaults to "b" only on **fresh** workflow-state init. Existing in-progress sessions keep their current state. |
| Scheduled task fires when no live data exists | Analyzer prints "INCOMPLETE" cleanly; no error, no new code. |
| Description edits trip skill-discovery indexing | Run `/lint-memory` and `/skill-discovery` as part of the PR's `quick_ci.sh` gate. |
| `~/.claude/skills` symlink resolution differs across worktree vs. main repo | Worktree-aware: per CLAUDE.md memory `worktree_symlink_edit_lands_in_main_repo.md`, edits via `~/.claude/skills/` from a worktree session resolve to the main repo. Use absolute paths and `cd /Users/summerrae/claude_code/claude-skills && git add -A` for the commit. |

### `$plan` contract

```yaml
steps:
  - id: 1
    description: |
      Add `skill_selection_variant` to the canonical workflow-state schema.
      Document it in the state-lifecycle reference as a new field with valid
      values {a, b, b150, c1, c3} and default "b". Update the file's
      "Initialization must include" list in phase-1-discovery.md to mention
      the field.
    files:
      - claude-flow/references/workflow-state-lifecycle.md
      - claude-flow/phases/phase-1-discovery.md
    type: shared_prerequisite
    depends_on: []
    test_requirements: |
      Verify markdown links resolve. No code execution; this is documentation.
    status: pending

  - id: 2
    description: |
      Edit the 5 courierflow-* SKILL.md frontmatter `description:` fields to
      use the tightened wording from .claude/experiments/skills_raw.txt. Edit
      via the absolute path under ~/.claude/skills/ — the symlink resolves to
      the canonical /Users/summerrae/claude_code/claude-skills/ tree.
    files:
      - ~/.claude/skills/courierflow-ui/SKILL.md
      - ~/.claude/skills/courierflow-api/SKILL.md
      - ~/.claude/skills/courierflow-data/SKILL.md
      - ~/.claude/skills/courierflow-integrations/SKILL.md
      - ~/.claude/skills/courierflow-security/SKILL.md
    type: value_unit
    depends_on: []
    test_requirements: |
      - Run `/lint-memory` to confirm no broken cross-references.
      - Run `/skill-discovery` smoke: verify the 5 skills still appear in the
        index with new descriptions.
      - cd to canonical repo and verify `git status` shows 5 modified SKILL.md
        files (not the worktree).
    status: pending

  - id: 3
    description: |
      Update the variant B gate documentation in phase-5-implementation.md
      to clarify that variant B is now the default. Specifically:
      - Reverse the `Variant A (control, default)` / `Variant B (forced
        selection)` labels — B becomes default, A becomes opt-out.
      - Remove the experiment-active language ("This block runs only while
        the experiment is active").
      - Add a one-line footnote pointing to the decision record.
    files:
      - claude-flow/phases/phase-5-implementation.md
    type: value_unit
    depends_on:
      - step: 1
        type: knowledge
    test_requirements: |
      Manual diff inspection — text-only change. The Bash gate-test from the
      worksheet (`workflow-state.json` key `skill_selection_variant`) should
      resolve to "b" by default after step 4.
    status: pending

  - id: 4
    description: |
      Land the default flip. Search the codebase for all places that
      initialize workflow-state and ensure the new field defaults to "b".
      Concretely: scripts/run_manifest.py, scripts/orchestrate.py, any
      Phase 0/1 markdown that lists initialization fields, and the
      workflow-profiles.json schema. Add a Python-level default in any
      init helper.
    files:
      - claude-flow/scripts/run_manifest.py
      - claude-flow/workflow-profiles.json
      - claude-flow/references/workflow-state-lifecycle.md
    type: value_unit
    depends_on:
      - step: 1
        type: build
    test_requirements: |
      - Add a unit test asserting `init_workflow_state()` includes
        `skill_selection_variant: "b"` by default.
      - Add a test for the override path (`skill_selection_variant: "a"`
        should be preserved if explicitly set).
    status: pending

  - id: 5
    description: |
      Add a CRON-scheduled task that fires 7 days from rollout. The task
      pulls .claude/experiments/skill_selection_ab.jsonl (from the live
      courierflow project root, not the experiment directory), runs
      `analyze_skill_selection.py`, and writes a follow-up note at
      docs/decisions/2026-05-06-variant-b-soak-results.md (or similar
      timestamp). Use the /schedule skill or mcp__scheduled-tasks__create_scheduled_task.
      Define the task in code (not a one-shot MCP call) so it can be
      re-created if the schedule is lost.
    files:
      - claude-flow/scripts/schedule_variant_b_soak_check.py
      - docs/decisions/2026-04-29-ship-forced-selection-phase5.md  # update follow-ups section
    type: value_unit
    depends_on:
      - step: 4
        type: data
    test_requirements: |
      - Dry-run the scheduling script with a 60-second future timestamp;
        verify it registers the task via list_scheduled_tasks.
      - Verify the task's command runs analyze_skill_selection.py with the
        correct --log path.
      - Cancel the dry-run task before committing.
    status: pending

  - id: 6
    description: |
      End-to-end smoke: run claude-flow on a trivial lite-path task in the
      courierflow repo. Verify that:
      1. workflow-state.json contains `skill_selection_variant: "b"`.
      2. Phase 5 subagent dispatch (if it occurs) follows the variant B
         prompt — emits SELECTED_SKILL: line.
      3. log_skill_selection.py records the trial in the live JSONL log.
    files: []
    type: value_unit
    depends_on:
      - step: 5
        type: data
    test_requirements: |
      Manual smoke run; capture output as evidence in the PR description.
    status: pending

  - id: 7
    description: |
      Ship the bundle. Run `quick_ci.sh`, open PR with body that summarizes
      experiment results + links the decision record + plan. Get review
      sign-off, merge.
    files: []
    type: value_unit
    depends_on:
      - step: 6
        type: data
    test_requirements: |
      `./scripts/quick_ci.sh` green. PR review approved. Post-merge:
      verify the scheduled task is registered and will fire on
      2026-05-06.
    status: pending
```

### Phase 4 advisor (Opus) review — synthesized

**Strengths:**
- Step ordering (docs → SKILL.md → phase-5 doc → default flip → scheduled task → smoke → ship) puts the lowest-risk changes first and gates the schema change before the runtime default.
- Step 4 has a unit test for the override path — guards against silent regression of variant A reproducibility.
- The Phase 5 doc reversal (step 3) is decoupled from the runtime flip (step 4), so a doc-only revert is possible without touching workflow-state code.

**Open critiques:**
- **Step 5's task definition is vendor-locked to scheduled-tasks MCP.** If that server isn't connected at fire time, the task silently no-ops. Consider a fallback: a markdown reminder file at `docs/decisions/REMINDERS.md` that any session can pick up via the `next` skill.
- **No regression test for the gate ON/OFF transition.** If a session has `skill_selection_variant: "b"` and the user flips it mid-session to "a", the prompt block in phase-5-implementation.md should respect the live value. Step 6's smoke covers fresh sessions but not in-flight flips.
- **Step 2's symlink-edit guidance assumes the human reads the worktree caveat.** Add a pre-commit assertion: a Bash one-liner that fails if the working dir is a worktree and the SKILL.md edits don't show up in `git -C /Users/summerrae/claude_code/claude-skills/ status`.

**Stress-test of the architectural decision:**
- *What if BM25 recall regresses post-launch?* The scheduled re-analysis (step 5) catches this — the 1-week soak is the safety net. If `correct_skill_rate` drops below 70% (5pp below experiment baseline), the follow-up note flags it.
- *What if variant B's over-load reduction (−25pp) doesn't replicate live?* Same — the scheduled re-analysis is the verification. No code change needed; only a decision-record update.
- *What if the 5 SKILL.md edits introduce typos that break skill-discovery?* Step 2's `/lint-memory` + `/skill-discovery` smoke catches this before merge. Guard is in place.

### Recommendation

Proceed with Option 1 (bundled PR). Address the three critiques as in-PR refinements:
1. Add Step 2's pre-commit symlink assertion to the test_requirements.
2. Add a fallback markdown reminder alongside the scheduled task in Step 5.
3. Extend Step 6's smoke to include a mid-session variant flip.

These don't change the structure — just tighten the test_requirements field for steps 2, 5, and 6.

---

## What user approval gates

Before Phase 5 implementation begins:

1. Confirm Option 1 (bundled PR) over Option 2 (sequenced).
2. Confirm out-of-scope items: CopilotKit skill is deferred, full description hygiene is deferred.
3. Confirm the scheduled-task fire date (7 days from merge, so ~2026-05-06).
4. Confirm the three Phase-4 critique addenda land in the test_requirements rather than as new steps.

Once approved, run `/claude-flow` again **without `--plan-only`** to execute Phase 5 against this plan, or invoke Phase 4c verification first to mechanically check file paths and references.
