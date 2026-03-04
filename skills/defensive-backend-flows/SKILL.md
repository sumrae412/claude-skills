---
name: defensive-backend-flows
description: Use when writing or reviewing Python backend code that involves error handling, data migrations, service-layer functions, cross-module API calls, or constant definitions
---

# Defensive Backend Flows

## Overview

Every backend function must answer: **"What happens to the data if this fails halfway?"** If the answer is "nothing visible," you have a bug.

## The Checklist

Before finishing ANY backend code, verify all five rules:

### 1. No Silent Swallows

Every `except` block must re-raise, log, or return an explicit error. Bare `except: pass` is always a bug.

```python
# ❌ BAD — failure disappears silently
except ScopeMismatchError:
    pass

# ✅ GOOD — failure is visible
except ScopeMismatchError as exc:
    logger.warning("Missing scopes for user %s: %s", user_id, exc)
    connection.status = "scope_error"
```

### 2. Catch What You Raise

When a function raises N exception types, every caller must handle all N — or explicitly let them propagate. A missing variant means an unhandled crash instead of graceful fallback.

```python
# ❌ BAD — check_quota() also raises QuotaExceededError
except (TokenNotFoundError, TokenExpiredError):
    return await self._send_via_smtp(...)

# ✅ GOOD — all three caught
except (TokenNotFoundError, TokenExpiredError, QuotaExceededError):
    return await self._send_via_smtp(...)
```

### 3. Copy Before Delete

Any operation that destroys data (NULL columns, DROP tables, DELETE rows) must copy to the destination first. Migrations need a reversible `downgrade()`.

```sql
-- ❌ BAD — NULLs tokens before they're copied
UPDATE users SET refresh_token = NULL;

-- ✅ GOOD — copy first, then NULL
INSERT INTO new_table (...) SELECT ... FROM users;
UPDATE users SET refresh_token = NULL;
```

### 4. One Source of Truth

Constants, limits, and column definitions must exist in exactly one place. Duplicates drift silently.

```python
# ❌ BAD — same limit defined differently in two files
# email.py:       'per_user_daily': 2000
# token_mgr.py:   daily_quota_limit = 500

# ✅ GOOD — single definition, others reference it
DAILY_QUOTA = 500  # defined once
```

### 5. Respect Encapsulation

Never call `_private` methods from outside the owning class/module. Create a public wrapper. Cross-module private calls cause double side-effects and break when internals change.

```python
# ❌ BAD — private call causes double record_error
await token_manager._refresh_token(db, connection)
connection.record_error(error)  # _refresh_token already did this

# ✅ GOOD — public API handles internal state
success, error = await token_manager.refresh_connection(db, conn)
```

## Quick Reference

| Rule | Symptom | Check |
|------|---------|-------|
| No Silent Swallows | Bug goes unnoticed for weeks | Every `except` logs or re-raises? |
| Catch What You Raise | Unhandled crash instead of fallback | Caller handles ALL exception types? |
| Copy Before Delete | Data loss on deploy | Data copied BEFORE source NULLed/dropped? |
| One Source of Truth | "Fixed it but still wrong" | Constant defined in exactly one place? |
| Respect Encapsulation | Double side-effects, brittle coupling | Only calling public API? |

## Red Flags — STOP and Fix

- `except SomeError: pass` with no logging
- A `try/except` that catches fewer types than the callee raises
- A migration that NULLs or DROPs before copying
- Same magic number in two files
- Calling `obj._method()` from outside `obj`'s module

## When NOT to Use

- Simple CRUD with no error handling complexity
- Read-only queries with no side effects
- Tests (mocking private methods in tests is acceptable)
