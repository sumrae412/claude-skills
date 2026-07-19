# Persona-Contract Lint Exclusions

Status: temporary soft-warning baseline.

PR 2 introduces `scripts/lint_persona_contracts.py` as a warning-only check for
skill role contracts. The linter scores five signals:

- metadata frontmatter
- explicit role/persona contract
- scope or trigger
- boundary or guardrail
- output or deliverable

Skills scoring below 4/5 stay excluded from strict failure until they are
manually patched or the heuristic is revised. These exclusions are deliberately
documented in one file so a future CI gate has a small burn-down list instead of
a hidden hardcoded allowlist.

## Temporary Exclusions

None. The warning baseline has been burned down; new weak contracts should fail
strict mode unless this document is deliberately reopened with a named exception.

## Gate Plan

1. Keep PR 2 warning-only.
2. Patch or re-score the exclusions in small follow-up PRs.
3. Switch CI to `--strict` only after the exclusion list is empty or intentionally
   narrowed to permanent exceptions.
