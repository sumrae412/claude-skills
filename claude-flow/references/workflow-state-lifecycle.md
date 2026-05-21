# Workflow State Lifecycle

Load this reference only when:

- `.claude/workflow-state.json` already exists, or
- Phase 1 selected a path whose profile has `state_machine: true`

Fast, lite, bug, and explore paths do not initialize workflow state by
default.

Load `references/run-manifest.md` alongside this file when you need to persist
approvals, verification commands, or review-base metadata.

## State File

Path: `.claude/workflow-state.json`

Purpose:

- phase governance
- bounded retries
- cross-session resume for long workflows

## Initialization

Replace `SESSION_TIMESTAMP` with an ISO timestamp and `TASK_SUMMARY` with the
current user request.

```json
{
  "schema_version": 2,
  "workflow_id": "claude-flow",
  "session_id": "SESSION_TIMESTAMP",
  "status": "running",
  "started_at": "SESSION_TIMESTAMP",
  "review_base_sha": null,
  "run_manifest_path": ".claude/runs/SESSION_TIMESTAMP.json",
  "capability_matrix": {
    "test_command": null,
    "lint_command": null,
    "typecheck_command": null,
    "static_analysis_command": null,
    "analysis_roots": [],
    "dev_server_command": null,
    "ci_present": false,
    "diff_base_strategy": null
  },
  "approvals": {
    "requirements_sha256": null,
    "plan_sha256": null
  },
  "skill_selection_variant": "b",
  "current_phase": {
    "id": "phase-1",
    "name": "Discovery",
    "path": null,
    "status": "running",
    "started_at": "SESSION_TIMESTAMP",
    "step": 1,
    "step_label": "Choose workflow path",
    "agents_spawned": 0,
    "agents_completed": 0,
    "agents_failed": 0,
    "iteration": 1,
    "max_iterations": 1
  },
  "phase_history": [],
  "iterations": {
    "phase-1": 1
  },
  "task_summary": "TASK_SUMMARY",
  "artifacts": {
    "exploration_summary": null,
    "architecture_doc": null,
    "implementation_plan": null,
    "review_findings": null
  }
}
```

Initialize only after Phase 1 has picked a path that needs the state machine.

### `skill_selection_variant` field

Controls how Phase 5 subagent dispatches present available courierflow-* skills to the model:

| value | behavior |
|---|---|
| `"b"` (default) | Forced selection — subagent emits `SELECTED_SKILL: <name\|none>` line before any tool calls. Curated 5-skill menu (courierflow-{ui,api,data,integrations,security}). |
| `"a"` | Progressive disclosure — subagent sees "you may load X if useful" with no commit step. Reproduces the pre-2026-04-29 behavior; useful only for re-running the A/B experiment. |
| `"b150"`, `"c1"`, `"c3"` | Experimental scale variants. Do not use for production runs. See `docs/plans/2026-04-29-skill-selection-at-scale.md`. |

Default `"b"` shipped 2026-04-29 after a 60-trial A/B experiment. See [decisions/2026-04-29-ship-forced-selection-phase5.md](../../docs/decisions/2026-04-29-ship-forced-selection-phase5.md).

## Resume Rules

At the first state-aware checkpoint:

1. `status == "running"`:
   - if file age is more than 48h, ask whether to resume or start fresh
   - resume means jump to the recorded phase/step
   - fresh means archive to `.claude/workflow-state.archived.json`
2. `status == "completed"`:
   - archive and start a new state file only if the chosen profile needs one
3. file missing:
   - do nothing in Phase 0
   - initialize later only if the chosen profile enables state

If the branch changed or the stored `review_base_sha` is no longer an ancestor
of `HEAD`, recompute it before Phase 6 and update both the state file and run
manifest.

Resume summary format:

`Resuming workflow: "<task_summary>" / <phase.name> Step <step> (<step_label>) / Path: <path>`

## Transition Template

At each phase boundary, move the current phase to history and set the next
phase.

```bash
jq '
  .phase_history += [{
    id: .current_phase.id,
    name: .current_phase.name,
    status: "completed",
    started_at: .current_phase.started_at,
    completed_at: (now | todate),
    iteration: .current_phase.iteration,
    results: {}
  }] |
  .current_phase = {
    id: "NEXT_PHASE_ID",
    name: "NEXT_PHASE_NAME",
    path: .current_phase.path,
    status: "running",
    started_at: (now | todate),
    step: 1,
    step_label: "FIRST_STEP_LABEL",
    agents_spawned: 0,
    agents_completed: 0,
    agents_failed: 0,
    iteration: 1,
    max_iterations: MAX_ITERATIONS
  } |
  .iterations["NEXT_PHASE_ID"] = ((.iterations["NEXT_PHASE_ID"] // 0) + 1)
' .claude/workflow-state.json > .claude/workflow-state.tmp && mv .claude/workflow-state.tmp .claude/workflow-state.json
```

Step updates:

- `jq '.current_phase.step = N | .current_phase.step_label = "LABEL"'`
- approvals:
  - `jq '.approvals.requirements_sha256 = "HASH"'`
  - `jq '.approvals.plan_sha256 = "HASH"'`
- review base:
  - `jq '.review_base_sha = "SHA"'`
- workflow complete: `jq '.status = "completed"'`

## Experiment authoring

### End-task-pass rubric for retrieval/selection experiments

When the model never writes code (e.g., replays whose prompts say "do not write code"), `quick_ci.sh` cannot grade outcomes. Use the rubric: **pass = (loaded == gold) OR (baseline_skill_free_pass)**. The OR-clause prevents penalizing trials where the base model would have solved the task without any skill. Implementation: `claude-flow/scripts/grade_end_task_pass.py`. Decision-tree: ship if Δcorrect ≥ 15pp AND Δpass ≥ 5pp.

### A/B replay prompt isolation

When generating prompts for variant-A and variant-B replays, never describe both variants inside one prompt's task block — variant-A subjects will self-label as "Variant B" and emit the variant-B output token (e.g., `SELECTED_SKILL:`). Split into `VARIANT_A_TAIL` / `VARIANT_B_TAIL` constants with no cross-mention. Hit on `replay_skill_selection.py` first run; contaminated all 12 variant-A trials before the split.

## Iteration Limits

Mirror `../workflow-profiles.json`:

| Phase | Max |
|-------|-----|
| `phase-5` | 3 |
| `phase-6` | 2 |
| all others | 1 |
