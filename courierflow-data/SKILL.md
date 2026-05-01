---
name: courierflow-data
description: CourierFlow data-layer guidance for SQLAlchemy 2.0 async models, Alembic migrations, PostgreSQL queries, Household/Property/tenant/event/workflow relationships, eager loading, scheduler indexes, and user-scoped persistence. Use when editing app/models, alembic, query helpers, migrations, or schema-driven tests.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow Data

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

## Verification

- Run migration generation/revision checks for schema changes.
- Run focused model/service tests.
- Inspect generated Alembic operations before accepting them.
- Verify scheduler-critical queries use indexed filters.
