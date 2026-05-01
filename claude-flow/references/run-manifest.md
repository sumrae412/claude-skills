# Run Manifest

Use a per-run manifest to make the workflow replayable and auditable.

The preferred writer is `scripts/run_manifest.py`. Use it instead of ad hoc
`jq` edits so approval hashes, verification runs, review runs, and command
records stay consistent.

## Path

`.claude/runs/<session-id>.json`

Store the path in workflow state as `run_manifest_path`.

## Required Fields

```json
{
  "workflow_version": "2",
  "workflow_path": null,
  "task_summary": null,
  "review_base_sha": null,
  "event_log_path": null,
  "capability_matrix": {},
  "requirements_approvals": [],
  "plan_approvals": [],
  "verification_runs": [],
  "review_runs": [],
  "commands_run": []
}
```

## What To Record

- chosen workflow path and any later path escalation
- `review_base_sha` and how it was resolved
- capability matrix captured in Phase 0
- SHA256 hashes of approved `$requirements` and `$plan`
- plan-verification results from Phase 4c / 4c-lite
- tests, lint, typecheck, and static-analysis commands with exit codes
- reviewer selection, budget, skipped reviewers, and redaction count
- any empirical tool-behavior checks that overruled reviewer claims

## Append-Only Event Log

Each run may have a sibling JSONL event log:

`.claude/runs/<session-id>.events.jsonl`

Use it for session-continuity facts that are too granular for the manifest but
important after compaction or resume:

- files read, created, edited, or intentionally left untouched
- user decisions and rejected alternatives
- blockers and unblockers
- subagent launch/completion summaries
- failing assertions and later resolutions
- command outcomes that should be searchable as exact facts
- tool and subagent errors with the class names from
  `references/failure-taxonomy.md`

Preferred writer:

```bash
python3 <claude-flow-root>/scripts/run_manifest.py record-event \
  --manifest .claude/runs/<session-id>.json \
  --event-type decision \
  --category decision \
  --source user \
  --payload '{"summary":"Use append-only continuity events"}'
```

`record-command` automatically mirrors command outcomes into the event log. The
manifest stores `event_log_path` so later tools can discover the event stream.

### Tool and Subagent Error Events

Record failed tool calls and subagent dispatches as explicit events instead of
leaving the failure only in chat history. This keeps later compaction, resume,
and retrospective analysis grounded in exact facts.

Use `event_type` values:

- `tool_error` for a local tool, MCP tool, CLI helper, or external API call
- `subagent_error` for a spawned agent, reviewer, implementer, or advisor

Allowed `error_class` values are `unknown-tool-error`, `invalid-arguments`,
`unexpected-environment`, `provider-error`, `timeout`, and `user-aborted`.

The payload must include:

```json
{
  "tool_name": "grep",
  "subagent_role": null,
  "phase": "phase-2",
  "error_class": "timeout",
  "expected": true,
  "failure_tag": "tool-selection",
  "summary": "Repository-wide grep timed out on an unbounded pattern",
  "recovery": "Reran with a narrower rg query under app/services"
}
```

For `subagent_error`, set `tool_name` to `null` and fill `subagent_role`.
`error_class` must be one of the classes in
`references/failure-taxonomy.md`. Use `unknown-tool-error` only when no
existing class fits; those events should be investigated rather than accepted
as normal workflow noise.

## Optional Trajectory Export

Use `scripts/export_run_timeline.py` when you need to inspect or visualize a
run as an ordered event stream instead of a nested manifest. If the event log
exists, the exporter includes those JSONL records as `session_event` entries.

```bash
python3 <claude-flow-root>/scripts/export_run_timeline.py \
  --manifest .claude/runs/<session-id>.json \
  --output .claude/runs/<session-id>.timeline.jsonl
```

If `--output` is omitted, the script writes JSONL to stdout. The export is
read-only and must not mutate the manifest or workflow state.

Each line is a JSON object with:

- `sequence`: monotonic event number in export order
- `type`: `metadata`, `approval`, `verification_run`, `review_run`, or
  `command`
- `timestamp`: best available event timestamp, or `null`
- `payload`: the original manifest fields relevant to that event

Export order is deterministic: metadata first, then timestamped events in
chronological order, with untimestamped events kept after timestamped events in
their manifest order. This format is intentionally close to trajectory logs in
recursive inference runtimes: a thin append-style stream that can feed a local
viewer without teaching the viewer the full manifest schema.

## Reliability Scan

Use `scripts/analyze_run_reliability.py` to summarize tool and subagent errors
across event logs:

```bash
python3 <claude-flow-root>/scripts/analyze_run_reliability.py \
  --runs-dir .claude/runs \
  --json
```

The scanner reports unknown error counts, totals by error class, phase, tool,
and subagent role, repeated failures, and simple latest-run spikes. Treat any
`unknown-tool-error` count above zero as investigation-worthy: either classify
the failure into an expected error class or fix the workflow/tool surface that
produced it.

## Rules

- Append new approval records; do not overwrite earlier ones.
- Treat the manifest as workflow metadata, not product code.
- If the workflow resumes in a later session, continue updating the same
  manifest unless the user explicitly starts a fresh run.
