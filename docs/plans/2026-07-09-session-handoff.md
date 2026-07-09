# 2026-07-09 Session Handoff

## Goal

Continue the persona-contract lint rollout for `claude-skills` without turning on
a noisy hard gate too early.

## Current State

- Shipped PR #207: `docs(skills): add role contracts to weak skills`.
  - Merge commit: `a44b66d407cbd49abf7fc07bab5a586d971f5ff6`.
  - Patched five true weak contracts: `github-search`, `measuring-pmf`,
    `founder-sales`, `fundraising`, `pricing-strategy`.
- In flight: PR #208, `feat(skills): add persona contract warning lint`.
  - Branch: `codex/persona-contract-lint-pr2`.
  - Head before this handoff doc: `abb6fddaebbd04a05503200f16887074142fd1d5`.
  - Adds `scripts/lint_persona_contracts.py`.
  - Adds `docs/decisions/2026-07-09-persona-contract-lint-exclusions.md`.
  - Local baseline: `127` skills, `16` weak, `16` excluded, `0` unexcluded.
  - GitHub reports no PR checks for this repo, so merge requires explicit
    Summer approval or a new CI workflow.
- Untouched: the 16 documented exclusions are not patched yet.

## Exact Next Task

Finish PR #208 first. Re-fetch, verify the PR is still clean, rerun the local
lint commands, update the PR body if this handoff commit changed the head, then
merge only if Summer has explicitly approved a no-CI merge.

Acceptance criteria:

- `gh pr view 208 --repo sumrae412/claude-skills --json state,isDraft,headRefOid,mergeStateStatus,statusCheckRollup`
  shows `state=OPEN`, `isDraft=false`, and `mergeStateStatus=CLEAN`.
- `python3 scripts/lint_persona_contracts.py --skill-root .` exits `0` and
  reports `weak=16 excluded=16 unexcluded=0`.
- `python3 scripts/lint_persona_contracts.py --skill-root . --strict --show-all-weak`
  exits `0`.
- `python3 -m py_compile scripts/lint_persona_contracts.py` exits `0`.
- `python3 claude-flow/scripts/test_skill_metadata.py` exits `0`.
- If merged, verify with both `gh pr view 208 --json state,mergedAt,mergeCommit`
  and `git log --first-parent origin/main --format='%H %s' -n 5`.

After PR #208 lands, start PR 3 by patching the easiest role-contract exclusions
in a small batch. Recommended first batch: `ai-writing`, `typography`,
`writing-voice`, `sme-voice`, and `session-handoff`. Keep the patch to explicit
role/scope/output wording only; do not refactor skill behavior.

## Template / Reference PRs

- #207: role-contract patch pattern for weak skills.
- #208: warning-only lint and documented exclusion pattern.

## Pre-flight Commands

```bash
cd /Users/summerrae/claude_code/claude-skills
git fetch origin --prune
gh pr list --state open --repo sumrae412/claude-skills
gh pr view 208 --repo sumrae412/claude-skills --json state,isDraft,headRefName,headRefOid,mergeStateStatus,statusCheckRollup,url
git worktree list
```

If continuing on the existing PR worktree:

```bash
cd /tmp/claude-skills-persona-lint-pr2
git fetch origin main
git status --short --branch
```

## Architectural Invariants To Preserve

- Henry AGENTS.md: verify premise before expensive work.
- Henry AGENTS.md: evidence on every completion claim.
- Henry AGENTS.md: no hard CI gate before manual review of score-2/3 skills.
- `docs/decisions/2026-07-09-persona-contract-lint-exclusions.md`: exclusions
  must stay explicit and burn-downable, not hidden in code.

## Gates

```bash
python3 scripts/lint_persona_contracts.py --skill-root .
python3 scripts/lint_persona_contracts.py --skill-root . --strict --show-all-weak
python3 -m py_compile scripts/lint_persona_contracts.py
python3 claude-flow/scripts/test_skill_metadata.py
git diff --check
```

## Ship Instructions

Ship via `/ship`. If still on PR #208, update the existing PR instead of opening
a new one. Do not auto-merge without CI unless Summer gives an explicit named
yes for PR #208. If PR #208 is already merged, start PR 3 from fresh
`origin/main` and update this handoff doc or a new dated handoff entry with the
new PR number before merging.

## PR 3 Update

- PR #208 is merged.
  - Merge commit: `73249a6e04b14a602f317a73466bf98e7bc13b6f`.
- PR #209 is open for the first exclusion burn-down batch.
  - Branch: `codex/persona-contract-pr3`.
  - Scope: `ai-writing`, `typography`, `writing-voice`, `sme-voice`, and
    `session-handoff`.
  - Local baseline after patch: `127` skills, `11` weak, `11` excluded,
    `0` unexcluded.
- This repo still reports no PR checks, so PR #209 should not be auto-merged
  unless Summer explicitly approves a no-CI merge or CI is added first.

## Mode Directive

Auto mode. Surface premise contradictions only.
