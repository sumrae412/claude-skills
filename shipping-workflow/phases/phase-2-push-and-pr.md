# Phase 2: Push and PR

## Goal

Push the shipping branch and open the PR with the right scope and
metadata.

## Process

- create or confirm feature branch if needed
- push with upstream
- create PR with concise summary and test plan
- capture PR number for later phases
- **handoff-doc fast path check**: after PR creation, if the diff matches ALL conditions in the Handoff-doc fast path section of SKILL.md (single additive `docs/plans/*handoff*.md` file, doc-prefixed branch, base = main), auto-merge with `env -u GH_TOKEN gh pr merge <N> --squash --delete-branch` and skip directly to Phase 4. Do NOT run Phase 3 — handoff docs ship without the review/CI gate. When any condition fails, fall through to Phase 3 as normal.

## Optional

- start background CI monitoring if useful

## Output

Pushed branch plus PR link/number — OR confirmed merge (handoff-doc fast path).
