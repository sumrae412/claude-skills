---
name: coding-best-practices
description: Comprehensive coding standards for Python, JavaScript, APIs, testing, and performance. Apply when writing code, reviewing PRs, debugging, or designing systems. Covers SQLAlchemy relationships, async patterns, DOM safety, REST design, and optimization techniques.
license: MIT
metadata:
  author: summerela
  version: "1.1.0"
user-invocable: false
---

# Coding Best Practices

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant
  patterns inline instead of loading extra material.

## Overview

Cross-project coding standards router for implementation, review,
debugging, and design work. This file should stay resident; detailed
language and domain guidance should be loaded on demand.

## Always-On Rules

- Write tests for behavior changes.
- Use async for I/O-bound Python work.
- Put business logic in services, not routes.
- Add type hints on function signatures.
- Create migrations for schema changes.
- Fetch external API docs before integrating.

## Risk Gate

- High risk: DB schema/types, auth, event loops, async boundaries, test
  fixtures, external integrations
- Medium risk: API changes, service layer changes, caching, rate limiting
- Low risk: templates, CSS, docs, config

For high-risk work, load the relevant phase file before making changes.

## Load Strategy

1. Identify the dominant surface area.
2. Load only the matching phase file from `phases/`.
3. Pull the linked doc or reference only when the phase calls for it.
4. Apply repo-specific gotchas only when they match the current change.

## Phase Map

1. `phases/phase-1-python-and-data.md`
2. `phases/phase-2-javascript-and-api.md`
3. `phases/phase-3-testing-and-release.md`
4. `phases/phase-4-repo-gotchas.md`

## Reference Map

- Python:
  `docs/python-patterns.md`
- JavaScript:
  `docs/javascript-safety.md`
- API design:
  `docs/api-design.md`
- Testing:
  `docs/testing.md`
- Performance:
  `docs/performance.md`
- Security:
  `docs/security.md`

## Quick Checks

- Renaming a symbol: grep Python, templates, and JS.
- Multiple independent count queries: prefer one aggregated SELECT.
- Shared-library schemas: keep them workflow-agnostic.
- Any retry-prone aggregator: make it idempotent.
- Any path from untrusted input: resolve and verify containment.

## Guardrails

- Prefer simple, readable code over abstraction by default.
- Avoid manual Alembic head parsing; use `alembic heads`.
- Design cleanup for shell side effects before the side effect exists.
- Prefer deterministic scripts and checks over prose-only assurance.
