---
name: new-migration
description: Create and validate Alembic database migrations with built-in safety checks — autogenerates revision, validates schema against models, runs upgrade then downgrade roundtrip, and flags destructive operations (DROP, NOT NULL on existing rows, type narrowing). Use when user says "create a migration", "new alembic migration", "/new-migration", "add a column to X table", or after editing SQLAlchemy models. Triggers also include "schema change", "DB migration", "alembic revision". NOT for raw SQL migrations (use `migration-architect` for zero-downtime planning) or non-Alembic frameworks (Django, Prisma, Drizzle have their own tooling).
user-invocable: true
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# Create New Migration

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Standardized workflow for creating safe, reversible Alembic migrations.

## Usage

```
/new-migration <description>
```

Example: `/new-migration add_phone_verified_column_to_users`

## Workflow

### Step 1: Generate Migration

```bash
cd <project-root>
alembic revision --autogenerate -m "<description>"
```

### Step 2: Review Generated Migration

Open the new migration file in `alembic/versions/` and check:

#### Upgrade Function
- [ ] All intended changes are captured
- [ ] No unintended changes (check for stale model imports)
- [ ] Correct column types and constraints
- [ ] Foreign keys have `ondelete` behavior specified
- [ ] Indexes added for foreign keys and frequently queried columns

#### Downgrade Function
- [ ] Mirrors upgrade exactly (in reverse)
- [ ] No `pass` statements for destructive operations
- [ ] Data can be restored if needed

#### Safety Checks
- [ ] No `DROP` without backup strategy
- [ ] `NOT NULL` columns have server_default or data migration
- [ ] Large table operations consider batching

### Step 3: Test Migration Cycle

```bash
# Test full cycle
alembic upgrade head
alembic downgrade -1
alembic upgrade head

# Verify schema matches models
python -c "from your_app.models import *; print('Models OK')"
```

### Step 4: Run Migration Reviewer

Invoke the migration-reviewer subagent:

```
Review this migration file: alembic/versions/<revision>_<description>.py
```

## Common Patterns

### Adding a Column

```python
def upgrade():
    op.add_column('users', sa.Column(
        'phone_verified',
        sa.Boolean(),
        nullable=False,
        server_default=sa.false()
    ))

def downgrade():
    op.drop_column('users', 'phone_verified')
```

### Adding a Foreign Key

```python
def upgrade():
    op.add_column('events', sa.Column(
        'property_id',
        sa.Integer(),
        sa.ForeignKey('properties.id', ondelete='CASCADE'),
        nullable=True
    ))
    op.create_index('ix_events_property_id', 'events', ['property_id'])

def downgrade():
    op.drop_index('ix_events_property_id', 'events')
    op.drop_column('events', 'property_id')
```

### Renaming a Column (Data-Safe)

```python
def upgrade():
    op.alter_column('users', 'old_name', new_column_name='new_name')

def downgrade():
    op.alter_column('users', 'new_name', new_column_name='old_name')
```

### Removing a Column (With Backup)

```python
def upgrade():
    # Backup data first
    op.execute("""
        CREATE TABLE _backup_users_legacy_field AS
        SELECT id, legacy_field FROM users WHERE legacy_field IS NOT NULL
    """)
    op.drop_column('users', 'legacy_field')

def downgrade():
    op.add_column('users', sa.Column('legacy_field', sa.String()))
    op.execute("""
        UPDATE users SET legacy_field = b.legacy_field
        FROM _backup_users_legacy_field b WHERE users.id = b.id
    """)
    op.execute("DROP TABLE _backup_users_legacy_field")
```

### Python-side Backfill (alternative to SQL `CASE`)

For large or complex mapping tables (e.g. taxonomy unification with 15+ legacy labels), read rows with `op.get_bind().execute()`, map in Python, then UPDATE per-row. Pairs with `op.batch_alter_table` for SQLite compatibility.

```python
from app.models.foo import NAME_MAPPING, LEGACY_FALLBACK

def upgrade():
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, name, old_col FROM t")).fetchall()
    for row_id, name, legacy in rows:
        new_val = NAME_MAPPING.get(name) or LEGACY_FALLBACK.get(legacy, "default")
        conn.execute(
            sa.text("UPDATE t SET old_col = :v WHERE id = :id"),
            {"v": new_val, "id": str(row_id)},
        )
    with op.batch_alter_table("t") as batch_op:
        batch_op.alter_column("old_col", nullable=False, server_default="default")
```

**Prefer over SQL `CASE`** when: mapping logic is non-trivial (name-primary + legacy-fallback composition), shared with a route handler (colocate constants with the enum, import from both sites), or exceeds ~10 branches.

Reference: `alembic/versions/20260424_014459_unify_workflow_template_category.py` (courierflow). Related memory: `pattern_shared_mapping_constants_next_to_enum.md`.

## Pre-Commit Checklist

- [ ] Migration has descriptive name
- [ ] Upgrade and downgrade are symmetric
- [ ] No blocking operations on large tables
- [ ] Foreign keys are indexed
- [ ] Tests pass after migration
- [ ] Reviewed by migration-reviewer agent

## Guardrails

- Always create a backup or test on a branch database before running destructive migrations
- Never add NOT NULL columns without a server_default on tables with existing data
- Test migrations both up and down before committing

## Out of Scope

This skill does NOT:
- Plan zero-downtime expand-contract or blue-green migration strategies—use `migration-architect`.
- Handle Django, Prisma, Drizzle, or non-Alembic migration frameworks—use the framework's own tooling.
- Decide whether legacy schema/code should be deprecated or maintained—use `deprecation-and-migration`.
- Ship the migration through commit/PR/merge—use `shipping-workflow`.
- Run pre-ship safety review (production-readiness, security)—use `production-readiness-check`.
