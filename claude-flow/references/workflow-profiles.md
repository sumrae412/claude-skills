# Workflow Profiles

Canonical source of truth for path behavior lives in
`../workflow-profiles.json`.

Load this file when:

- path selection is ambiguous
- you are editing `claude-flow` itself
- you need the exact transition or review ceiling for a path

Do not duplicate path metadata in multiple phase files. Update the JSON first,
then update any human-facing summaries that cite it.

## Path Summary

| Path | State Machine | Mutation | Main Phases | Review Ceiling |
|------|---------------|----------|-------------|----------------|
| `bug` | No | Yes | Route to `/bug-fix` | Owned by `/bug-fix` |
| `fast` | No | Yes | Inline from Phase 1 | Tests only |
| `plan` | Yes | Yes | 1 → 5 → 5.5 → 6 | Tier 1-3 plus specialists |
| `clone` | Yes | Yes | 1 → 5 → 5.5 → 6 | Tier 1-2 plus specialists |
| `lite` | No | Yes | 1 → 2 → 3 → 4 → 5 → 5.5 → 6 | Tier 1-3 |
| `audit` | Yes | No | 1 → 2 → 3 → 4 → 6 | Tier 1-3 file-list mode |
| `explore` | No | Yes | Route to sandbox from Phase 1 | No Phase 6 until graduation |
| `full` | Yes | Yes | 1 → 2 → 3 → 4 → 4c → 4d → 5 → 5.5 → 6 | Full cascade |

## Default Review Budgets

Each path profile also defines `review_budget_default` for Phase 6 selector
seeding:

- `low`: `fast`, `clone`, `lite`, `explore`
- `medium`: `bug`, `plan`, `audit`, `full`

## Operational Rules

1. Phase 0 does only a cheap existence check for workflow state.
2. Phase 1 chooses the path.
3. Initialize `.claude/workflow-state.json` only if the chosen profile has
   `state_machine: true`, unless an existing state file already forced a
   resume/archive decision in Phase 0.
4. Use the transition map from `workflow-profiles.json` instead of repeating the
   same table in multiple hot-path files.

## Why This Exists

This file keeps the router thin and prevents drift between:

- `SKILL.md`
- `phases/phase-0-context.md`
- `phases/phase-1-discovery.md`

The runtime phases should summarize only what they need for the current step.
The full path matrix stays here and in the JSON.
