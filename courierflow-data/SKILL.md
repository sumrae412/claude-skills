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
- Backfill migrations that INSERT records MUST include duplicate protection (e.g., a `seen_keys` set in Python or `ON CONFLICT DO NOTHING` in SQL). Members sharing the same `(user_id, email)` can exist across households — without dedup, the migration crashes on unique constraints or creates duplicates.

### Alembic Version Desync

The `alembic_version` table can reference a revision that does not exist as a migration file (e.g., after manual stamping or failed operations). When this happens, `alembic upgrade head` fails because Alembic cannot traverse the migration chain from the current revision.

**Diagnosis:**
```sql
SELECT version_num FROM alembic_version;  -- Check current stamp
```
Then verify the returned revision exists in `alembic/versions/`. If it does not, the chain is broken.

**Recovery:**
1. Identify the actual latest revision file: `ls -t alembic/versions/ | head -5`
2. Stamp to a known-good revision: `alembic stamp <existing_revision>`
3. Then run `alembic upgrade head`

**Prevention:** Never manually stamp `alembic_version` to a revision ID that does not correspond to an actual migration file. When creating manual "alignment" migrations, always generate a real migration file with `alembic revision`.

### Backfill: Nullable Derived Columns

When backfilling a nullable column derived from multiple source columns (e.g. `preferred_contact_method` from `email` and `phone`), use a `CASE` with an explicit `ELSE NULL` when all sources are NULL. Without it, the column may get a wrong default or violate NOT NULL in edge cases.

```sql
-- BAD — when both email and phone are NULL, ELSE defaults to 'phone'
CASE WHEN hm.email IS NOT NULL THEN 'email' ELSE 'phone' END

-- GOOD — explicit ELSE NULL
CASE
  WHEN hm.email IS NOT NULL THEN 'email'
  WHEN hm.phone IS NOT NULL THEN 'phone'
  ELSE NULL
END
```

**Learned from:** `scripts/run_migration_manual.py` backfill for `preferred_contact_method`; CodeRabbit review.

### Multiple Heads from Parallel PRs

When two feature branches both set `down_revision` to the same migration (a common race condition during parallel development), merging both creates two Alembic heads. Alembic will refuse to run `upgrade head` when multiple heads exist.

**Diagnosis:**
```bash
alembic heads  # Shows 2+ head revisions
```

**Fix:**
```bash
alembic merge <head1_rev> <head2_rev> -m "merge <branch1> with <branch2>"
# Generates a new migration file with both revisions as down_revision tuple
```

**Guard:** Add `# pragma: allowlist secret` to the merge migration's revision lines if hex IDs trigger detect-secrets.

**Pattern:** In a cleanup session merging 3+ PRs that share the same base migration, you may need to run `alembic merge` multiple times — once per competing pair of heads. Always run `alembic heads` after each merge migration is added.

### Backfill: Iterative Fix for Broken Sync

When a sync bug left orphaned records (e.g., HouseholdMembers without Clients), and a previous backfill already ran but was incomplete due to the same bug, write a targeted backfill that:
1. Uses `NOT EXISTS` to find only still-orphaned records
2. Matches by the **parent relationship** (`household_id`) not just the contact field (`email`)
3. Handles both email and name-based matching for records without email
4. Guards against empty-string normalized fields — use `NULLIF` or Python guard (`value if value else None`) to store `NULL` instead of `''` for normalized fields derived from optional source columns

## JSON Column Mutation

SQLAlchemy doesn't track in-place mutation of `Column(JSON)` / `Column(JSONB)` fields. `.append()`, `.update()`, and nested dict assignment are silent no-ops at flush time. Two safe options:

```python
# Option 1: reassign wholesale (works on any model)
conversation.messages = list(conversation.messages or []) + [entry]

# Option 2: opt into mutation tracking on the column
from sqlalchemy.ext.mutable import MutableList
messages: Mapped[list] = mapped_column(MutableList.as_mutable(JSON), default=list)
```

Audit: `rg -n '\.\w+\.append\(' app/services/` — every hit on a JSON-typed column needs reassignment. See MEMORY `gotcha_sqlalchemy_json_column_in_place_mutation.md`.

## Enum Naming Discipline

Postgres enum types share a single namespace. Multiple `ConversationStatus` enums silently shadow each other in migrations. Pre-flight grep before naming a new enum:

```bash
rg -n "class \w+Status\(.*Enum" app/models/
```

If the unprefixed name already exists, prefix the new one with the feature/domain (`Concierge*`, `Workflow*`, `Document*`). PR #342 hit this — plan said `ConversationStatus`, `app/models/chat.py` already had it; renamed to `ConciergeConversationStatus`.

## Performance Patterns

1. **Cursor-based pagination** — No offset pagination in new code
2. **Index query filters** — Especially `ix_steps_scheduled_pending`
3. **No N+1 queries** — Use `selectinload`/`joinedload`
4. **Batch external API calls** where possible
5. **Cache read-heavy config** via `CacheManager` with stampede prevention

## Postgres-First Scaling

- **PostgreSQL only** — No SQLite support. `app/database/__init__.py` has no dialect branching; `app/config.py` defaults to `postgresql+asyncpg://`. Do not add SQLite fallbacks, `_is_postgresql()` checks, or `aiosqlite` imports.

No Redis, no external queue. Maximize PostgreSQL:

- **Job queue** — `pending_operations` table with `SKIP LOCKED` dequeue
- **Retry** — Exponential backoff via `next_retry_at`
- **Idempotency** — `idempotency_key` column
- **Advisory locks** — Prevent duplicate scheduler execution
