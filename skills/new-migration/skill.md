---
name: new-migration
description: Create and validate Alembic database migrations with safety checks
user-invocable: true
---

# Create New Migration

Standardized workflow for creating safe, reversible Alembic migrations.

## Usage

```
/new-migration <description>
```

Example: `/new-migration add_phone_verified_column_to_users`

## Workflow

### Step 1: Generate Migration

```bash
cd ~/claude_code/courierflow
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
python -c "from app.models import *; print('Models OK')"
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

## Pre-Commit Checklist

- [ ] Migration has descriptive name
- [ ] Upgrade and downgrade are symmetric
- [ ] No blocking operations on large tables
- [ ] Foreign keys are indexed
- [ ] Tests pass after migration
- [ ] Reviewed by migration-reviewer agent
