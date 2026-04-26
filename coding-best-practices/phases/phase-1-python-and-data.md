# Phase 1: Python and Data

Load `../docs/python-patterns.md` before running this phase. Load
`../docs/performance.md` when query shape or caching matters.

## Goal

Apply Python, SQLAlchemy, async, and data-layer standards.

## Always Check

- type hints on params and returns
- async/await for I/O
- service-layer ownership of business logic
- migrations for schema changes
- indexes on high-frequency queries
- correct relationship configuration for multiple foreign keys

## Repo-Specific Gotchas

- Multiple independent counts on one page: combine them into a single
  query with `scalar_subquery()`.
- Retry-prone aggregators must stamp and dedup output records.
- Shared libraries used by multiple consumers should use a generic schema:
  stable `workflow` id plus open metadata, not consumer-specific fields.
- Never parse Alembic files manually to find heads; use `alembic heads`.

## Output

Targeted Python/data review guidance or implementation checklist for the
current change.
