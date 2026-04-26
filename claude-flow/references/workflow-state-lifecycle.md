# Workflow State Lifecycle

Load this reference only when:

- `.claude/workflow-state.json` already exists, or
- Phase 1 selected a path whose profile has `state_machine: true`

Fast, lite, bug, and explore paths do not initialize workflow state by
default.

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
  "schema_version": 1,
  "workflow_id": "claude-flow",
  "session_id": "SESSION_TIMESTAMP",
  "status": "running",
  "started_at": "SESSION_TIMESTAMP",
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
- workflow complete: `jq '.status = "completed"'`

## Iteration Limits

Mirror `../workflow-profiles.json`:

| Phase | Max |
|-------|-----|
| `phase-5` | 3 |
| `phase-6` | 2 |
| all others | 1 |
