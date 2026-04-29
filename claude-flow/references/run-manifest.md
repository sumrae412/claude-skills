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

## Optional Trajectory Export

Use `scripts/export_run_timeline.py` when you need to inspect or visualize a
run as an ordered event stream instead of a nested manifest.

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

## Rules

- Append new approval records; do not overwrite earlier ones.
- Treat the manifest as workflow metadata, not product code.
- If the workflow resumes in a later session, continue updating the same
  manifest unless the user explicitly starts a fresh run.
