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

## SQLModel Coexistence (slices 1.3a–1.3d)

CourierFlow is mid-migration from `class Foo(Base)` to
`class Foo(SQLModel, table=True)`. Both styles coexist via shared `metadata`
and SQLAlchemy `_sa_registry` in `app/database/__init__.py`.

- **Always** import via `from app.database import GUID, SQLModel`. Never
  `from sqlmodel import SQLModel` directly — order-of-import would cache
  SQLModel's own metadata before the foundation reassignment runs.
- **The authoritative conversion reference is
  `docs/decisions/2026-05-12-slice-1.3a-conversion-pattern.md`** in the
  CourierFlow repo. It documents the two `Field(...)` kwarg shapes
  (`sa_type=` for simple cases, `sa_column=Column(...)` for SA-only
  kwargs), the full conversion table, and an 8-entry quirks log. Follow
  it mechanically when converting new models.
- **JSON columns:** use `default_factory=list` / `default_factory=dict`,
  NOT `default=list` / `default=dict`. Per-instance isolation depends on
  the factory call. Verified by slice 1.3a Probe B.
- **`@property` clusters and mutator methods are safe** on SQLModel
  table classes — Pydantic v2 does not intercept `@property`, and
  `self.attr = value` works without `validate_assignment` issues.
  Verified by slice 1.3a Probe C against OAuthToken's 7 properties + 9
  mutators.
- **Cross-style relationships resolve** — old-style `class Foo(Base)`
  with `relationship(back_populates=...)` resolves against new-style
  `class Bar(SQLModel, table=True)` after `configure_mappers()`.
  Verified for OAuthToken ↔ legacy User.
- **Baseline metadata count:** 120 tables, 53 model files, 126 class
  declarations (6 abstract/non-table classes). `Base.metadata.tables` is
  empty unless `app.models` is imported first; class registration fires
  at class-definition time, not at `app.database` import time.

## SQLModel-specific Gotchas

- **No mypy plugin.** `class Foo(SQLModel, table=True):` triggers
  `error: Unexpected keyword argument "table" for "__init_subclass__"
  of "object" [call-arg]`. Scope-disable `call-arg` in `mypy.ini` under
  `[mypy-app.models.*]` — per-class `# type: ignore` would be 125+
  lines once 1.3b/1.3c land.
- **`SQLModel.registry` raises AttributeError** because Pydantic v2's
  metaclass intercepts public attribute reads. Use the private
  `SQLModel._sa_registry` — that's the SQLAlchemy-side canonical name
  and is fully readable + writable.
- **`Base.metadata.tables` is empty without `import app.models`** —
  class registration only fires when modules are imported. Any
  introspection-time assertion (e.g.
  `verify_sqlmodel_registry_consolidated` in
  `app/database/__init__.py`) must `import app.models` first.
