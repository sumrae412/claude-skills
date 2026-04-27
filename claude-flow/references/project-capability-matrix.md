# Project Capability Matrix

Load this reference in Phase 0 when you need a reproducible snapshot of how the
target project is supposed to be verified and run.

## Purpose

Later phases should not guess commands like `pytest`, `pyright`, or
`npm run dev` from vague repo signals. Record the project's own declared
capabilities once, then reuse them.

## Minimum Fields

Persist these fields to workflow state or the run manifest:

```json
{
  "test_command": null,
  "lint_command": null,
  "typecheck_command": null,
  "static_analysis_command": null,
  "analysis_roots": [],
  "dev_server_command": null,
  "ci_present": false,
  "diff_base_strategy": null
}
```

## Discovery Order

1. `CLAUDE.md` / `AGENTS.md` / project root instructions
2. package scripts, `pyproject.toml`, `Makefile`, `justfile`, `Taskfile.yml`
3. CI config (`.github/workflows`, Railway, etc.)
4. existing repo conventions visible from neighboring tests or docs

Only probe mechanically when those sources are silent.

## Rules

- Prefer explicit project commands over generic fallbacks.
- `analysis_roots` should list the directories static analysis should scan.
- `diff_base_strategy` should describe how Phase 6 chooses the review base:
  state file first, then merge-base against the branch upstream/default branch.
- If a field is unknown, store `null`; do not invent a command.
