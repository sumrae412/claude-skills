# CourierFlow Data Patterns

## Core Model Vocabulary

| UI term | Code term |
| --- | --- |
| Property | `Household` |
| Unit | `PropertyUnit` |
| Tenant | `HouseholdMember` / `Client` |
| Sequence | `WorkflowTemplate` |
| Sequence run | `WorkflowInstance` |
| Step | `WorkflowTemplateStep` / `WorkflowInstanceStep` |

Use UI language in templates and user messages. Use code vocabulary in model
and migration names unless the surrounding code already says otherwise.

## Relationship Shape

The important path is:

`User -> Household -> PropertyUnit -> HouseholdMember`

Calendar events connect through metadata:

`CalendarEvent -> CalendarEventMeta -> EventType + Household + HouseholdMember`

Workflow instances connect to confirmed calendar events and snapshot the
template/step state used at arming time.

## Migration Rules

- Use Alembic for every schema change.
- Never drop or null data before copying it.
- Keep migrations reversible when practical.
- For enums, check existing migration patterns before adding values.
- Add indexes for new scheduler, status, foreign-key, and user-scope filters.
- Verify generated migrations do not touch unrelated tables.

## Query Rules

- Default to `select()` with explicit filters.
- Use `selectinload` for one-to-many relationships shown in lists.
- Use `joinedload` for required many-to-one details shown with a single row.
- Avoid N+1 lookups in dashboard, sidebar, workflow, and event-resolution
  views.
- Do not use offset pagination in new list surfaces.

## Scheduler-Critical Data

Scheduler execution depends on:

- pending workflow steps
- `scheduled_for <= now()`
- advisory locks for single-worker execution
- idempotency keys for external actions
- retry timestamps for failed operations

Any change to these surfaces needs tests for duplicate prevention and retry
visibility.

## Timezone Rules

- Persist UTC.
- Normalize naive datetimes before arithmetic.
- Display user-facing timestamps in the landlord's timezone.
- Recalculate only pending steps after event date changes; executed steps stay
  immutable.
