---
name: courierflow-data
description: "LEGACY (Python repo only) — CourierFlow data-layer guidance for SQLAlchemy 2.0 async models, Alembic migrations, PostgreSQL queries, Household/Property/tenant/event/workflow relationships, eager loading, scheduler indexes, and user-scoped persistence. Use ONLY when editing the frozen Python repo at ~/claude_code/courierflow/ (app/models, alembic, query helpers). Do NOT use for the active TypeScript beta at ~/claude_code/courierflow_beta/, which uses Drizzle ORM + PostgreSQL with a different schema layout."
license: MIT
metadata:
  author: summerela
  version: "1.1.0"
---

# CourierFlow Data

> **Legacy scope (2026-05-21):** This skill applies to the **legacy Python repo** at `~/claude_code/courierflow/` only. Active development has moved to **`courierflow_beta`** — TypeScript with **Drizzle ORM** schemas in `lib/db/src/schema/` and `pnpm --filter @workspace/db run push` for dev migrations. SQLAlchemy / Alembic / Household-vs-Property terminology does NOT apply to beta. The old repo is in **frozen reference** mode: readable for historical context, no new work. Do not auto-trigger this skill when cwd is inside `courierflow_beta`.

## Purpose

Protect CourierFlow's landlord-centric data model and scheduler reliability.
Use this skill for models, migrations, relationship loading, persistence rules,
and query performance.

## Load Strategy

1. Read `references/data-patterns.md` before changing models, migrations, or
   query-heavy services.
2. Pair with `new-migration` when schema changes are required.
3. Pair with `defensive-backend-flows` for migrations and state transitions.

## Non-Negotiables

- Landlord data flows through Property -> Tenant -> Event -> Workflow.
- Internal names may use `Household`, `HouseholdMember`, and `Client`; UI labels
  stay landlord-friendly.
- Every user-owned table/query must be scoped by `user_id` or by a parent row
  already scoped by `user_id`.
- Store datetimes in UTC and display in the user's timezone.
- New schema changes require Alembic migrations.
- PostgreSQL is the queue/locking/cache coordination substrate; do not add
  Redis or a new queue.
- During the SQLAlchemy → SQLModel migration (slices 1.3a–1.3d), import
  `SQLModel` from `app.database`, NOT from `sqlmodel` directly. The
  shared-registry wiring in `app/database/__init__.py` depends on import
  order — a direct `from sqlmodel import SQLModel` before `app.database`
  runs caches SQLModel's own metadata on the class before reassignment.
  See `references/data-patterns.md` → SQLModel Coexistence + Gotchas.

## Verification

- Run migration generation/revision checks for schema changes.
- Run focused model/service tests.
- Inspect generated Alembic operations before accepting them.
- Verify scheduler-critical queries use indexed filters.
