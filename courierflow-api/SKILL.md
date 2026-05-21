---
name: courierflow-api
description: CourierFlow backend API guidance for FastAPI routes, async services, request handlers, domain exceptions, dashboard workflows, scheduler-adjacent service logic, and thin-route/thick-service boundaries. Use when editing app/routes, app/services, schemas, request validation, or landlord-facing API behavior.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow API

## Purpose

Keep CourierFlow backend changes aligned with the core product loop:
Google Calendar event -> landlord confirmation -> workflow instance -> visible
scheduled communication steps.

## Load Strategy

1. Read `references/api-patterns.md` before changing routes or services.
2. Pair with `defensive-backend-flows` for errors, state transitions, audit
   logs, and side effects.
3. Pair with `courierflow-security` for auth, permissions, user scoping, or
   webhooks.
4. Pair with `courierflow-data` for ORM models, query shape, or migrations.

## Non-Negotiables

- Routes validate input, call services, and map domain exceptions to HTTP.
- Services own business logic and do not call `db.commit()`.
- All database and I/O operations are async.
- Every user-owned query is scoped by `user_id`.
- Use `get_current_active_user` for protected routes.
- No automated action fires without explicit landlord confirmation.
- Failure states must become visible to the landlord.

## Verification

- Add or update tests for behavior changes.
- Run focused route/service tests.
- For state-machine changes, verify each exit transition sets an explicit
  status.
- For new external calls, fetch current API docs before implementation.
