---
name: courierflow-skill-sync
description: Synchronize CourierFlow skills with the live CourierFlow codebase and project instructions using git diffs, source scans, and targeted reference updates. Use after significant changes to routes, services, models, migrations, templates, integrations, security rules, CLAUDE.md/AGENTS.md, or claude-flow skill routing.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow Skill Sync

## Purpose

Keep `courierflow-*` skills in sync with the CourierFlow application and
`claude-flow` routing docs. This adapts the Base44 sync pattern to a Python
FastAPI/Jinja/PostgreSQL product.

## Workflow

1. Read `references/sync-workflow.md`.
2. Identify the CourierFlow app repo path and the comparison base.
3. Use `git diff --name-only <base>...HEAD` to classify changed files.
4. Route changed files to the owning CourierFlow skill.
5. Update only the affected `SKILL.md` description or reference files.
6. Run `courierflow-skill-reviewer` checks on changed skills.
7. Run `claude-flow` workflow lint/tests if routing docs changed.

## Rules

- Do not bulk rewrite skills.
- Do not copy source code into skills when a pattern summary is enough.
- Prefer reference updates over bloating `SKILL.md`.
- Preserve project-specific vocabulary and locked architecture decisions.
- Flag uncertain source behavior for manual review instead of guessing.

## Output

Return changed source areas, affected skills, files updated, and any manual
review items.
