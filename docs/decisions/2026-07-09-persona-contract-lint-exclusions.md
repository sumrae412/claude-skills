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

- `ai-writing` - strong writing-quality gate, but no explicit role contract.
- `codebase-design` - useful design vocabulary, but output contract is implicit.
- `courierflow-api` - legacy reference skill, but output contract is implicit.
- `courierflow-data` - legacy reference skill, but output contract is implicit.
- `courierflow-security` - legacy reference skill, but output contract is implicit.
- `courierflow-skill-reviewer` - reviewer scope is clear, but boundary contract is implicit.
- `courierflow-ui` - legacy reference skill, but output contract is implicit.
- `inbox-triage` - workflow boundaries exist, but no explicit role/scope section.
- `new-migration` - migration guardrails exist, but no explicit role/scope section.
- `session-handoff` - artifact rules exist, but no explicit role/scope section.
- `sme-voice` - voice-preservation rules exist, but no explicit role/scope section.
- `typography` - correction rules exist, but no explicit role/scope section.
- `user-stories` - workflow and output are clear, but no explicit role/scope section.
- `verify-premise-before-asserting` - verification rule exists, but no explicit role/scope section.
- `web-scraping-efficient` - execution/output contract exists, but no explicit role/scope section.
- `writing-voice` - voice rules exist, but no explicit role/scope section.

## Gate Plan

1. Keep PR 2 warning-only.
2. Patch or re-score the exclusions in small follow-up PRs.
3. Switch CI to `--strict` only after the exclusion list is empty or intentionally
   narrowed to permanent exceptions.
