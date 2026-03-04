# Defensive Backend Flows — Evidence Log

> To add a new bug, copy the template below and fill it in.
> Then run the update-skill workflow to test and update the skill.

## Quick-Add Template

<!-- Copy everything between the dashes, paste at the end of the Bugs section, and fill in -->
<!--
---

## Bug N: SHORT_NAME (DATE)

**Symptom:** What was observed or what would happen in production.

**Root cause:** What actually went wrong in the code.

**Which rule violated:** [1: Silent Swallow | 2: Catch What You Raise | 3: Copy Before Delete | 4: One Source of Truth | 5: Respect Encapsulation | NEW]

**Code (bad):**
```python
# the broken pattern
```

**Code (fix):**
```python
# the corrected pattern
```

**Pressure scenario prompt:** A generic task prompt that would reproduce this bug.
-->

---

## Bug 1: Migration NULLs Before Copy (2026-03-03)

**Symptom:** Deploying the migration would permanently delete all user OAuth tokens with no way to recover.

**Root cause:** Alembic migration NULLed `users.google_calendar_refresh_token` without first INSERTing/UPDATEing into `integration_connections`. The `downgrade()` was a bare `pass`.

**Which rule violated:** 3: Copy Before Delete

**Code (bad):**
```python
def upgrade() -> None:
    op.execute(text("""
        UPDATE users SET
            google_calendar_token = NULL,
            google_calendar_refresh_token = NULL ...
    """))

def downgrade() -> None:
    pass
```

**Code (fix):**
```python
def upgrade() -> None:
    # Step 1: INSERT new integration_connections rows
    op.execute(text("""
        INSERT INTO integration_connections (...)
        SELECT ... FROM users WHERE refresh_token IS NOT NULL
    """))
    # Step 2: UPDATE existing rows with token data
    op.execute(text("""UPDATE integration_connections ic SET ... FROM users u ..."""))
    # Step 3: NOW safe to NULL
    op.execute(text("""UPDATE users SET google_calendar_token = NULL ..."""))

def downgrade() -> None:
    op.execute(text("""
        UPDATE users u SET refresh_token = ic.refresh_token_encrypted
        FROM integration_connections ic WHERE ...
    """))
```

**Pressure scenario prompt:** "Write an Alembic migration that moves user email preferences from a `users` column into a new `user_preferences` table, then removes the column from `users`."

---

## Bug 2: db.commit() in Services (2026-03-03)

**Symptom:** Partial commits when a multi-step service operation fails halfway. Route-level transaction boundary violated.

**Root cause:** `token_refresh_service.py` and `email.py` called `db.commit()` directly (5+ occurrences) instead of letting routes own transactions.

**Which rule violated:** Project-specific (CourierFlow Boundaries #7). Not in generic skill.

**Pressure scenario prompt:** N/A — project-specific, covered by CLAUDE.md.

---

## Bug 3: Private Method Called Externally (2026-03-03)

**Symptom:** Double `record_error` on permanent token failure — the error count incremented twice per failure.

**Root cause:** `token_refresh_service` called `token_manager._refresh_token()` directly instead of a public API. `_refresh_token` internally calls `record_error`, and the caller also called it, doubling the side effect.

**Which rule violated:** 5: Respect Encapsulation

**Code (bad):**
```python
# token_refresh_service.py
await token_manager._refresh_token(db, connection)
connection.record_success()
connection.status = IntegrationConnectionStatus.CONNECTED
```

**Code (fix):**
```python
# token_manager.py — new public method
async def refresh_connection(self, db, connection):
    try:
        await self._refresh_token(db, connection)
        return True, None
    except TokenExpiredError as exc:
        return False, str(exc)

# token_refresh_service.py — uses public API
success, error = await token_manager.refresh_connection(db, connection)
```

**Pressure scenario prompt:** "Write a service function `refresh_user_session()` that refreshes an OAuth token using an existing `TokenStore` class. The `TokenStore` has a `_do_refresh(conn)` method that handles the HTTP call and updates internal state."

---

## Bug 4: Duplicate Column Definitions (2026-03-03)

**Symptom:** SQLAlchemy model had 3 columns defined twice. Confusing for readers, risk of inconsistent defaults.

**Root cause:** Copy-paste error in `IntegrationConnection` model — `daily_quota_used`, `daily_quota_limit`, `quota_reset_at` appeared in two separate blocks.

**Which rule violated:** 4: One Source of Truth

**Pressure scenario prompt:** N/A — copy-paste error, not reproducible by prompt.

---

## Bug 5: Cache Eviction in Wrong Function (2026-03-03)

**Symptom:** Cache eviction (a write-side concern) ran on every status check (a read-side operation), adding unnecessary overhead and mixing concerns.

**Root cause:** Cache eviction logic was placed in `_google_connected()` (read-only check) instead of `_set_cached_events()` (write operation).

**Which rule violated:** Project-specific (misplaced side effect). Not in generic skill.

---

## Bug 6: QuotaExceededError Not Caught (2026-03-03)

**Symptom:** When Gmail quota was exceeded, `send_email()` raised an unhandled `QuotaExceededError` instead of falling back to SMTP.

**Root cause:** `send_simple_email()` caught `TokenNotFoundError` and `TokenExpiredError` for SMTP fallback but missed `QuotaExceededError`, which `check_gmail_quota()` also raises.

**Which rule violated:** 2: Catch What You Raise

**Code (bad):**
```python
try:
    await token_manager.check_gmail_quota(db, user.id)
except (TokenNotFoundError, TokenExpiredError):
    return await self._send_via_smtp(...)
# QuotaExceededError crashes here
```

**Code (fix):**
```python
try:
    await token_manager.check_gmail_quota(db, user.id)
except (TokenNotFoundError, TokenExpiredError, QuotaExceededError):
    return await self._send_via_smtp(...)
```

**Pressure scenario prompt:** "Write a `send_notification()` function that tries to send via a premium API first. If the API raises `RateLimitError`, `AuthError`, or `QuotaError`, fall back to a basic SMTP sender."

---

## Bug 7: Double record_error (2026-03-03)

**Symptom:** Connection error counter incremented twice per failure, triggering circuit breaker prematurely.

**Root cause:** `_refresh_token` internally calls `record_error` on failure. The caller (`token_refresh_service`) also called `connection.record_error()` in its own `except` block.

**Which rule violated:** 5: Respect Encapsulation (same root cause as Bug 3)

---

## Bug 8: ScopeMismatchError Silently Swallowed (2026-03-03)

**Symptom:** Users logged in without required Drive scopes. No log entry, no status update, no way to diagnose.

**Root cause:** `except ScopeMismatchError: pass` in the Google OAuth callback route.

**Which rule violated:** 1: No Silent Swallows

**Code (bad):**
```python
except ScopeMismatchError:
    pass
```

**Code (fix):**
```python
except ScopeMismatchError as scope_err:
    logger.warning(
        "Google login missing scopes for user %s: %s",
        user.id, scope_err,
    )
    user.gmail_auth_status = "scope_error"
    await db.commit()
```

**Pressure scenario prompt:** "Write an OAuth callback handler that stores the access token and checks if the granted scopes include 'drive.file'. Handle the case where scopes are missing."

---

## Bug 9: Missing Public API (2026-03-03)

**Symptom:** External service had to call `_private` method because no public alternative existed.

**Root cause:** `TokenManager` only had `_refresh_token()` (private). `token_refresh_service` needed to refresh tokens but had no public entry point.

**Which rule violated:** 5: Respect Encapsulation (same family as Bug 3 and 7)

---

## Bug 10: Conflicting Quota Limits (2026-03-03)

**Symptom:** Email service allowed 2000 emails/day while token manager enforced 500. Inconsistent behavior depending on which check ran first.

**Root cause:** `email.py` defined `'per_user_daily': 2000` while `token_manager.py` defined `daily_quota_limit = 500`.

**Which rule violated:** 4: One Source of Truth

**Code (bad):**
```python
# email.py
GMAIL_RATE_LIMITS = {'per_user_daily': 2000}
# token_manager.py
daily_quota_limit = Column(Integer, default=500)
```

**Code (fix):**
```python
# email.py — defer to token_manager as source of truth
GMAIL_RATE_LIMITS = {'per_user_daily': 500}  # token_manager is source of truth
```

**Pressure scenario prompt:** "Write two service modules that both enforce a rate limit. Module A sends messages, Module B tracks quotas. Both need to know the daily limit."

---

## Common Thread

All ten bugs share one root cause: **the code optimized for the happy path and didn't consider what happens when things go wrong or when the same concept exists in multiple places.**

The agent:
1. Assumed exceptions could be silently ignored (Bugs 1, 8)
2. Assumed callers would catch all exception types (Bug 6)
3. Assumed data operations are atomic (Bug 1)
4. Assumed duplicate definitions would stay in sync (Bugs 4, 10)
5. Assumed private methods could be safely called externally (Bugs 3, 7, 9)

Each is a failure to ask: **"What happens to the data if this fails halfway?"**

---

## RED/GREEN Test Results (2026-03-03)

### Scenario 1: Silent Exception Handling (Rule 1)

**RED (without skill):** ⚠️ PARTIAL REPRODUCTION — Agent added `?error=scope_mismatch` to the redirect URL but wrote NO actual `logger` call. A code comment said "Log scope mismatch" but no logging was implemented. The exception was effectively swallowed — no log entry, no status update. This confirms the skill catches a real anti-pattern: agents write *comments about logging* but don't actually log.

**GREEN (with skill):** ✅ FIXED — Every `except` block included `logger.warning()` or `logger.error()` with structured context (user_id, error message). The agent explicitly cited Rule 1 as the reason for adding logging.

**Verdict:** Skill directly fixed the anti-pattern. Scenario is effective.

---

### Scenario 2: Incomplete Exception Handling (Rule 2)

**RED (without skill):** ❌ NOT REPRODUCED — Agent caught all 3 exception types (`RateLimitError`, `AuthenticationError`, `QuotaExceededError`) naturally. The prompt explicitly listed all 3 types, making it too easy to catch them all.

**GREEN (with skill):** ✅ IMPROVED — Agent additionally re-raised unexpected errors as `NotificationError` instead of silently returning, and added more structured error context.

**Verdict:** Scenario needs refinement. The prompt lists all exception types explicitly, removing the ambiguity that causes the real bug. Future version should mention some types only in docstrings or have the callee raise types not mentioned in the prompt.

---

### Scenario 4: Encapsulation Violation (Rule 5)

**RED (without skill):** ❌ NOT REPRODUCED — Agent used public `get_valid_token()` instead of calling `_do_refresh()` directly. **Caveat:** the general-purpose subagent had file access and read the project's actual `token_manager.py`, which biased it toward the correct pattern.

**GREEN (with skill):** ✅ IMPROVED — Agent provided more specific error handling and explicitly cited Rule 5 ("Respect Encapsulation") in comments explaining why `get_valid_token()` was used instead of `_do_refresh()`.

**Verdict:** Scenario needs refinement. The prompt shows both public and private methods with clear naming conventions (`_do_refresh` vs `get_valid_token`). A subtler test would only show the private method and see if the agent creates a public wrapper. Also, subagent file access should be restricted for fairer testing.

---

### Summary

| Scenario | Rule | RED Result | GREEN Result | Effective? |
|----------|------|-----------|-------------|------------|
| 1: Silent Exception | 1 | ⚠️ Partial bug | ✅ Fixed | **Yes** |
| 2: Incomplete Catch | 2 | ❌ Not reproduced | ✅ Improved | Needs refinement |
| 4: Encapsulation | 5 | ❌ Not reproduced | ✅ Improved | Needs refinement |

**Key finding:** Scenario 1 is the strongest validation — it caught a real anti-pattern where the agent acknowledged the need for logging but didn't implement it. Scenarios 2 and 4 need more subtle prompts that don't telegraph the correct answer.
