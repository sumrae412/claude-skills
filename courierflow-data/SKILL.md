---
name: courierflow-data
description: Data model, migrations, queries, performance. Load when working on app/models/*, alembic/*, or schema changes.
---

# CourierFlow Data Patterns

## Data Model

```
User (landlord)
  └── Household (1:many) — "Property"
        └── PropertyUnit (1:many)
              └── HouseholdMember (1:many) — "Tenant"

CalendarEvent
  └── CalendarEventMeta (1:1)
        ├── EventType
        ├── Household (matched property)
        └── HouseholdMember (matched tenant)

WorkflowTemplate
  └── WorkflowTemplateStep (ordered)
        ├── timing: event-relative (e.g., -7 days)
        ├── recipient: TENANT, LANDLORD, BOTH
        └── action: EMAIL, SMS, TASK, NOTIFICATION, SEND_DOCUMENT, START_WORKFLOW
```

## Event Type Taxonomy

`LandlordEventType` values:
- MOVE_IN, MOVE_OUT, LEASE_RENEWAL, INSPECTION
- MAINTENANCE, RENT_DUE, LEASE_END, CUSTOM

## Locked Architectural Decisions (Do Not Revisit)

1. **Eager Time Calculation** — Compute all `scheduled_for` timestamps on workflow instance creation
2. **Recipient Routing** — Template-level `recipient_type` with optional instance-level `recipient_override`
3. **Event Date Changes** — Recalculate all pending step timestamps; executed steps unaffected
4. **Event Deletion** — Pause (don't cancel) linked workflow instances
5. **Recurring Events** — Each occurrence creates separate WorkflowInstance
6. **Workflow Chaining** — `START_WORKFLOW` passes only `trigger_outcome` and `parent_instance_id`
7. **Scheduler** — APScheduler polls `scheduled_for <= now() AND status = 'pending'`
8. **Template Snapshots** — Instance creation snapshots template state

## Migration Rules

**Before changing schema, run `/new-migration`**

- Data migrations that NULL or DROP columns MUST copy data first
- Always implement reversible `downgrade()`
- Test both upgrade and downgrade

## Performance Patterns

1. **Cursor-based pagination** — No offset pagination in new code
2. **Index query filters** — Especially `ix_steps_scheduled_pending`
3. **No N+1 queries** — Use `selectinload`/`joinedload`
4. **Batch external API calls** where possible
5. **Cache read-heavy config** via `CacheManager` with stampede prevention

## Postgres-First Scaling

No Redis, no external queue. Maximize PostgreSQL:

- **Job queue** — `pending_operations` table with `SKIP LOCKED` dequeue
- **Retry** — Exponential backoff via `next_retry_at`
- **Idempotency** — `idempotency_key` column
- **Advisory locks** — Prevent duplicate scheduler execution
