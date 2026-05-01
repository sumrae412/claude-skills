---
name: courierflow-skill-reviewer
description: Review CourierFlow skills and claude-flow routing for trigger accuracy, scope, progressive disclosure, stale project rules, missing references, and Phase 5 skill-selection quality. Use when editing courierflow-* skills, CLAUDE.md/AGENTS.md, claude-flow skill menus, or diagnosing wrong skill selection.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow Skill Reviewer

## Purpose

Keep the CourierFlow skill library accurate, compact, and useful to subagents.
This is a maintenance skill for reviewing `courierflow-*` skills and the
`claude-flow` trigger/selection docs that route to them.

## Workflow

1. Read `references/review-checklist.md`.
2. Identify the skill or routing file under review.
3. Validate structure and frontmatter.
4. Check trigger description quality.
5. Check whether detailed rules belong in `references/` instead of `SKILL.md`.
6. Compare the skill against current CourierFlow project rules.
7. Report concrete edits, ordered by risk.

## Review Targets

- `courierflow-*/SKILL.md`
- `courierflow-*/references/*.md`
- `claude-flow/references/skill-triggers.md`
- `claude-flow/phases/phase-5-implementation.md`
- project `CLAUDE.md` / `AGENTS.md` routing instructions

## Output

Lead with findings. Include file paths, trigger gaps, stale rules, missing
references, and proposed exact edits.
