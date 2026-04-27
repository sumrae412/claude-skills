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

## Rules

- Append new approval records; do not overwrite earlier ones.
- Treat the manifest as workflow metadata, not product code.
- If the workflow resumes in a later session, continue updating the same
  manifest unless the user explicitly starts a fresh run.
