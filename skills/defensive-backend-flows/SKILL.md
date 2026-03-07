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

### 2. Catch What You Raise (and Enumerate What You Match)

When a function raises N exception types, every caller must handle all N — or explicitly let them propagate. A missing variant means an unhandled crash instead of graceful fallback.

This also applies to **error-code sets**: when you match against a set of known values (error codes, status strings), enumerate ALL variants up front. A missing variant means wrong behavior for that case.

```python
# ❌ BAD — check_quota() also raises QuotaExceededError
except (TokenNotFoundError, TokenExpiredError):
    return await self._send_via_smtp(...)

# ✅ GOOD — all three caught
except (TokenNotFoundError, TokenExpiredError, QuotaExceededError):
    return await self._send_via_smtp(...)

# ❌ BAD — only one permanent OAuth error listed
PERMANENT_ERRORS = {"invalid_grant"}
# invalid_client and unauthorized_client get retried forever

# ✅ GOOD — all permanent error codes enumerated
PERMANENT_ERRORS = {"invalid_grant", "invalid_client", "unauthorized_client"}
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

Constants, limits, column definitions, and **configuration sets** (scopes, feature flags, allowed values) must exist in exactly one place. Duplicates drift silently.

```python
# ❌ BAD — same limit defined differently in two files
# email.py:       'per_user_daily': 2000
# token_mgr.py:   daily_quota_limit = 500

# ✅ GOOD — single definition, others reference it
DAILY_QUOTA = 500  # defined once
```

This also applies to **configuration sets** like OAuth scopes, feature flags, or allowed values:

```python
# ❌ BAD — scopes hardcoded in calendar_service.py
flow = Flow.from_client_config(
    config,
    scopes=["calendar", "drive.file", "gmail.send"],  # drifts
)

# ✅ GOOD — import from the canonical source
from app.services.token_manager import REQUIRED_GOOGLE_SCOPES
flow = Flow.from_client_config(
    config,
    scopes=sorted(REQUIRED_GOOGLE_SCOPES),
)
```

**Learned from:** `calendar_service.py` — hardcoded Google OAuth scopes instead of importing `REQUIRED_GOOGLE_SCOPES` from `token_manager.py`. Adding `drive.file` scope to the source of truth didn't propagate to the calendar service.

This also applies to **template file paths**: a template's directory should match the route module that owns it. A template in the wrong directory is a naming lie that confuses debugging.

```python
# ❌ BAD — tenants route renders a template from properties/
# app/routes/tenants.py
return templates.TemplateResponse("properties/list.html", ...)
# Confusing: is this a properties page or a tenants page?

# ✅ GOOD — template path matches the route module
# app/routes/tenants.py
return templates.TemplateResponse("tenants/list.html", ...)
```

**Learned from:** `tenants.py` — route rendered `properties/list.html` which was 100% tenant content. When debugging "tenants disappeared," the wrong directory added confusion about which template was responsible.

This also applies to **CSS variant classes**: when a base class (`.stat-card`) defines visual properties, variant classes (`.stat-card-button`, `.stat-card-link`) must NOT redeclare those same properties. The variant should only add what the base doesn't cover (e.g., browser resets for `<button>` elements). Redundant declarations drift out of sync and cause subtle visual inconsistencies.

```css
/* ❌ BAD — variant redeclares base properties */
.stat-card { border: 1px solid gray; padding: 16px; }
.stat-card-button { border: 1px solid gray; padding: 16px; /* redundant */ }

/* ✅ GOOD — variant only adds what's unique (all 5 button resets) */
.stat-card { border: 1px solid gray; padding: 16px; }
.stat-card-button { display: block; appearance: none; font: inherit; color: inherit; cursor: pointer; }
```

**Learned from:** `home-dashboard.css` — `.home-stat-card-button` redeclared all properties from `.home-stat-card`, creating a visual mismatch with the `<a>`-based sibling cards.

### 5. Respect Encapsulation

Never call `_private` methods from outside the owning class/module. Create a public wrapper. Cross-module private calls cause double side-effects and break when internals change.

```python
# ❌ BAD — private call causes double record_error
await token_manager._refresh_token(db, connection)
connection.record_error(error)  # _refresh_token already did this

# ✅ GOOD — public API handles internal state
success, error = await token_manager.refresh_connection(db, conn)
```

### 6. Verify Imports Match Signatures

Every type referenced in a function signature, return annotation, or type hint must be imported. A missing import causes `NameError` at runtime when the function is called — not at module load — so it passes `import` checks but crashes in production.

```python
# ❌ BAD — TenantPanelResponse used in return type but never imported
from app.schemas.tenant_panel import TenantPanelDocument, TenantPanelTenant

async def get_panel_data(...) -> Optional[TenantPanelResponse]:
    # NameError: name 'TenantPanelResponse' is not defined

# ✅ GOOD — all referenced types imported
from app.schemas.tenant_panel import (
    TenantPanelDocument,
    TenantPanelResponse,
    TenantPanelTenant,
)

async def get_panel_data(...) -> Optional[TenantPanelResponse]:
    ...
```

This also applies to **runtime references** inside function bodies — singletons, classes, or exceptions used before their import:

```python
# ❌ BAD — token_manager used before import inside function
async def _send_email_with_retry(self, ...):
    conn = await token_manager.get_connection(db, user_id)  # NameError
    from app.services.token_manager import token_manager  # too late

# ✅ GOOD — import before first use
async def _send_email_with_retry(self, ...):
    from app.services.token_manager import token_manager
    conn = await token_manager.get_connection(db, user_id)
```

This also applies to **string-quoted type annotations** — even though `"UUID | None"` is a string and won't cause a runtime `NameError`, linters (flake8 F821) flag the unquoted names as undefined. If a type appears in an annotation, it must be imported at module level:

```python
# ❌ BAD — UUID only imported inside function body, flake8 F821
def _parse_state(
    state: str | None,
) -> tuple["UUID | None", str | None]:
    from uuid import UUID  # too late for linter
    ...

# ✅ GOOD — module-level import satisfies both runtime and linter
from uuid import UUID

def _parse_state(
    state: str | None,
) -> tuple["UUID | None", str | None]:
    ...
```

**Check:** After writing any function, scan its signature and body for every type/object name and verify a matching import exists *above* first use. For string-quoted annotations, verify the type is imported at module level even though Python won't evaluate the string.

**Learned from:** `client.py` — `TenantPanelResponse` in return type without import. `email.py` — `token_manager` referenced before its late import. `calendar.py` — `AsyncSession` used in type hint before import. `auth.py` — `UUID` in string annotation `"UUID | None"` but only imported inside the function body.

### 7. Test Queries Against Real DB Semantics

SQLAlchemy queries that work on SQLite may fail on PostgreSQL. Common traps:

- **DISTINCT + JSON columns:** Postgres cannot compare JSON for equality, so `DISTINCT` on a table with JSON columns fails.
- **ORDER BY not in SELECT DISTINCT:** Postgres requires ORDER BY expressions to appear in the SELECT list when using DISTINCT.
- **Fix:** Use an ID subquery + `CASE` ordering instead of `DISTINCT` + `ORDER BY`.

```python
# ❌ BAD — DISTINCT on table with JSON columns + ORDER BY mismatch
query = (
    select(Document)
    .join(DocumentSigner)
    .distinct()
    .order_by(Document.created_at.desc())
    .limit(5)
)

# ✅ GOOD — subquery for IDs, then fetch full rows with CASE ordering
id_query = (
    select(Document.id, func.max(Document.created_at).label("ts"))
    .outerjoin(DocumentSigner)
    .where(...)
    .group_by(Document.id)
    .order_by(func.max(Document.created_at).desc())
    .limit(5)
)
ids_result = await db.execute(id_query)
doc_ids = [row[0] for row in ids_result.all()]

if doc_ids:
    order = case(
        {doc_id: idx for idx, doc_id in enumerate(doc_ids)},
        value=Document.id,
    )
    docs = await db.execute(
        select(Document).where(Document.id.in_(doc_ids)).order_by(order)
    )
```

**Learned from:** `client.py` — tenant panel document query used `DISTINCT` which broke on Postgres due to JSON column equality and ORDER BY mismatch.

### 8. Verify Model Attributes Before Access

When accessing model attributes — especially date/status fields for display — verify the attribute actually exists on the model. An `AttributeError` at runtime means you assumed a column that was never added or was named differently.

```python
# ❌ BAD — document.signed_at doesn't exist on Document model
status_date = document.signed_at or document.created_at
# AttributeError: 'Document' object has no attribute 'signed_at'

# ✅ GOOD — use attributes that exist, chain fallbacks
status_date = (
    document.completed_at
    or document.sent_at
    or document.viewed_at
    or document.created_at
)
```

**Check:** Before accessing `model.attribute`, confirm the attribute exists in the model class definition. Don't assume column names — check the schema.

**Learned from:** `client.py` — status date calculation referenced `document.signed_at` which doesn't exist on the `Document` model. Fixed by using `viewed_at` as fallback.

### 9. Auxiliary Side-Effects Must Not Abort Primary Flow

When a primary operation (disconnect, deploy, cleanup) has auxiliary side-effects (send notification, log analytics, update cache), wrap each auxiliary call in its own try-catch. A notification failure must never abort the core operation.

```python
# ❌ BAD — SMS failure aborts the entire disconnect
async def disconnect_google(self, db, user_id):
    conn.status = "disconnected"
    await db.flush()
    await self._send_disconnect_sms(db, user_id)  # raises → rollback
    await self._create_alert(db, user_id)

# ✅ GOOD — SMS is best-effort, disconnect completes regardless
async def disconnect_google(self, db, user_id):
    conn.status = "disconnected"
    await db.flush()
    await self._create_alert(db, user_id)  # critical — keep unwrapped
    try:
        await self._send_disconnect_sms(db, user_id)
    except Exception as exc:
        logger.warning("Disconnect SMS failed for %s: %s", user_id, exc)
```

**Check:** For each side-effect in a multi-step operation, ask: "If this fails, should the whole operation fail?" If no, wrap it in try-catch with logging.

**Learned from:** `token_manager.py` — SMS notification failure during `disconnect()` aborted the entire disconnect flow, leaving the user in a broken state.

### 10. User-Facing Actions Must Create Audit Trails

When a service performs an action visible to the user (send document, update preferences, trigger workflow), it must create an `ActionLog` entry. Missing audit trails mean the action disappears from the dashboard — the user has no proof it happened.

```python
# ❌ BAD — document sent but no ActionLog, invisible in Recent Activity
async def send_document(self, db, document, tenant):
    await self._deliver(document, tenant)
    document.status = "sent"
    await db.flush()
    # No ActionLog — landlord sees nothing on dashboard

# ✅ GOOD — ActionLog makes the action visible
async def send_document(self, db, document, tenant):
    await self._deliver(document, tenant)
    document.status = "sent"
    db.add(ActionLog(
        user_id=document.user_id,
        action_type=ActionLogType.DOCUMENT_SENT,
        title=f"Sent document to {tenant.full_name}",
        level=ActionLogLevel.INFO,
    ))
    await db.flush()
```

**Check:** After adding any state-changing endpoint, ask: "Will the landlord see this in Recent Activity?" If no, add an `ActionLog`.

**Learned from:** `documents.py` — document sends had no ActionLog, so they never appeared in the home feed. `tenant_action_service.py` — tenant contact preference updates were invisible to the landlord.

### 11. Error-Level Logs Must Surface to Users

When querying activity feeds or dashboards, never filter out ERROR-level logs by default. Errors are the most important thing a user needs to see. A default filter that hides errors violates "Fail Visible."

```python
# ❌ BAD — errors excluded by default, landlord misses failures
async def get_recent_activity(db, user_id, include_errors=False):
    conditions = [ActionLog.user_id == user_id]
    if not include_errors:
        conditions.append(ActionLog.level != ActionLogLevel.ERROR)

# dashboard calls without override → errors hidden
activity = await get_recent_activity(db, user_id)

# ✅ GOOD — errors included by default for dashboard feeds
activity = await get_recent_activity(
    db, user_id, include_errors=True,
)
```

**Check:** If a query function has an `include_errors` or `min_level` parameter, verify the caller passes the right value. Dashboard feeds should always include errors.

**Learned from:** `logging_service.py` — `get_recent_activity()` defaulted `include_errors=False`, so ERROR-level workflow failures never showed on the home feed.

### 12. Never Depend on Ephemeral Local Storage

Cloud platforms (Railway, Heroku, Render) destroy the local filesystem on every deploy. File uploads, temp files, and caches written to local disk vanish silently. Always use persistent storage (Google Drive, S3, database BLOBs).

```python
# ❌ BAD — file disappears after next deploy
file_path = f"uploads/{user_id}/{filename}"
async with aiofiles.open(file_path, "wb") as f:
    await f.write(content)
doc.file_path = file_path  # DB points to a ghost file

# ❌ BAD — silent fallback to local when Drive fails
if not drive_result.success:
    local_path = save_to_disk(content, filename)
    doc.file_path = local_path  # Works today, gone tomorrow

# ✅ GOOD — persistent storage required, fail if unavailable
result = await drive_service.upload(token, content, filename)
if not result.success:
    raise ExternalServiceError(
        "Upload failed. Please connect Google Drive."
    )
doc.file_url = result.file_url  # Persistent URL
```

**Check:** If code writes to the filesystem, ask: "Will this file exist after a deploy?" If no, use persistent storage or fail visibly. Never silently fall back to local disk.

**Learned from:** `document_upload_service.py` — local fallback saved files to `uploads/` which vanished on Railway redeploy. Also: `documents.py` — attachment sends, bulk sends, and file-availability checks all assumed local files existed.

### 13. Never Leak Internal Errors to Users

Exception messages, tracebacks, file paths, and stack traces must never appear in HTTP responses, redirect URLs, or user-visible error messages. Log the full error server-side; show the user a generic message.

```python
# ❌ BAD — raw exception leaks internals
except Exception as e:
    error_msg = quote_plus(str(e)[:200])
    return RedirectResponse(url=f"/page?error={error_msg}")

# ❌ BAD — traceback in response
except Exception as e:
    raise HTTPException(
        status_code=500,
        detail=f"Failed: {str(e)}",  # May contain file paths
    )

# ✅ GOOD — log internally, show generic message
except Exception:
    logger.error("Operation failed", exc_info=True)
    error_msg = quote_plus("Something went wrong. Please try again.")
    return RedirectResponse(url=f"/page?error={error_msg}")
```

**Also applies to:** `print()` debug statements in production code. Remove all `print(f"DEBUG: ...")` before merging.

**Check:** After writing any error handler, ask: "Does the HTTP response or redirect URL contain `str(e)`, `traceback`, or `exc_info`?" If yes, replace with a generic message.

**Learned from:** `auth.py` — OAuth callback leaked raw exception strings (including file paths and tracebacks) in redirect URL query params. Also contained `print()` debug statements.

### 14. Never Compare Datetimes as Strings

String comparison of ISO timestamps breaks with timezone offsets, variable-length fractional seconds, and `Z` vs `+00:00` differences. Always parse to `datetime` objects and compare with timezone-aware values.

```python
# ❌ BAD — string comparison, "2026-03-04T10:00:00+00:00" > "2026-03-04T09:00:00-05:00" is WRONG
upcoming = [
    e for e in events
    if e["start"] >= datetime.utcnow().isoformat()
]

# ❌ BAD — naive datetime compared to offset-aware string
now = datetime.utcnow()  # naive, no tzinfo
upcoming = [e for e in events if parse(e["start"]) >= now]  # TypeError

# ✅ GOOD — parse both sides, timezone-aware comparison
from datetime import datetime, timezone
from dateutil.parser import parse

now = datetime.now(timezone.utc)
upcoming = [
    e for e in events
    if parse(e["start"]) >= now
]
```

**Check:** Search for `.isoformat()` in comparisons or `>=`/`<=` with string timestamps. Every datetime comparison should use parsed `datetime` objects with explicit timezone.

**Learned from:** Home dashboard — upcoming events were filtered using string comparison of ISO timestamps, which dropped future events when timezone offsets varied.

### 15. Use the Canonical Service for Connection State

When checking if an external service (Google, Twilio, Stripe) is connected, use the service/manager that owns the connection state — not a shortcut column on the user model. Shortcut columns go stale when the real connection changes.

```python
# ❌ BAD — checks deprecated user column, stale after token refresh
if not user.google_calendar_token:
    return {"google_connected": False}

# ✅ GOOD — token manager owns Google connection state
connection = await token_manager.get_active_connection(
    db, user_id, "google"
)
google_connected = connection is not None and connection.is_valid
```

**Check:** When you see `user.some_token` or `user.is_connected_to_x` in a route, verify it's not a stale shortcut. The service that manages tokens/connections is the source of truth.

**Learned from:** Home dashboard — used `user.google_calendar_token` to decide if Google was connected, but the real connection lived in `IntegrationConnection` via the token manager. Home skipped remote calendar fetches even when Google was connected.

### 16. Primary View Must Use the Live Data Source

When a page becomes the primary UI for a data domain (e.g., Home becomes the only calendar view after `/calendar` redirects there), it must fetch from the live source — not rely on a sparse local cache that was adequate when it was a secondary view.

```python
# ❌ BAD — Home shows cached events only, but /calendar redirects here
events = await get_cached_events(db, user_id)  # sparse, stale
# User sees "1 event" when they have 15 on Google Calendar

# ✅ GOOD — try live source first, fall back to cache with warning
try:
    events = await fetch_remote_events(db, user_id)
except ExternalServiceError:
    events = await get_cached_events(db, user_id)
    show_warning = True  # Surface that data may be stale
```

**Also:** When a page becomes the primary view, it should surface connection status and remote-fetch errors visibly. Silent "only one event" with no explanation violates Fail Visible.

**Check:** If route A redirects to route B, verify route B fetches from the same data source route A used. A redirect that silently downgrades data quality is a bug.

**Learned from:** Home dashboard — relied on sparse DB cache while `/calendar` redirected to Home. Users saw far fewer events than expected with no explanation.

### 17. After Conflict Resolution, Re-Run Targeted Tests

When a cherry-pick or merge has conflicts, the resolved code may subtly differ from the original. Always re-run the tests that cover the changed code before pushing — don't assume the resolution preserved behavior.

```bash
# ❌ BAD — resolve conflict, push immediately
git cherry-pick abc123
# ... resolve conflicts ...
git add . && git cherry-pick --continue && git push

# ✅ GOOD — resolve, test, then push
git cherry-pick abc123
# ... resolve conflicts ...
git add . && git cherry-pick --continue
pytest tests/test_home_dashboard.py -v  # verify resolved behavior
git push
```

**Learned from:** Cherry-pick of datetime filter fix conflicted on main. The first resolution silently dropped the datetime-based filter, requiring a second fix.

### 18. Variables Don't Follow When Functions Split

When refactoring a large function into smaller ones (or copying logic from one function to another), variables defined in the original function don't carry over. Each function has its own scope — a variable computed in `function_a()` is not available in `function_b()` even if they're in the same module.

```python
# ❌ BAD — google_connected defined in get_chat_context(),
#          used in get_home_data() where it doesn't exist
async def get_chat_context(db, user):
    status = await token_manager.get_connection_status(db, user.id)
    google_connected = status.is_connected  # defined here
    ...

async def get_home_data(db, user):
    ...
    if google_connected:  # NameError — not defined in this scope
        events = await fetch_remote_events(db, user.id)

# ✅ GOOD — each function computes what it needs
async def get_home_data(db, user):
    status = await token_manager.get_connection_status(db, user.id)
    google_connected = status.is_connected
    if google_connected:
        events = await fetch_remote_events(db, user.id)
```

**Check:** After splitting a function or copying a code block that references local variables, verify every variable used in the new function is either (a) a parameter, (b) defined locally, or (c) imported. Search for names used before assignment.

**Learned from:** `chat.py` — `google_connected` was defined in `get_chat_context()` but referenced in `get_home_data()` where it was never defined. Caused `NameError` at runtime.

### 19. Static Asset Changes Must Include Cache-Busting Bumps

When modifying CSS or JS files, the commit must also bump the `?v=` version parameter in every template that loads the file. The middleware sets `max-age=31536000` (1 year) on static files, so without a version bump, the deploy succeeds but browsers serve the old cached file — the change is invisible to users.

```python
# ❌ BAD — CSS file updated, templates untouched
# git diff shows: app/static/css/pages/calendar.css changed
# But calendar.html still has: <link href="...calendar.css?v=3">
# Deploy succeeds, no visual change on site

# ✅ GOOD — CSS change + version bump in same commit (or immediately after)
# git diff shows:
#   app/static/css/pages/calendar.css  (style changes)
#   app/templates/calendar.html        (?v=3 → ?v=20260304a)
#   app/templates/dashboard.html       (?v=3 → ?v=20260304a)
```

**Workflow after modifying any static file:**
1. `grep -r "filename.css" app/templates/` — find ALL templates that load it
2. Bump every `?v=` to today's date + letter suffix
3. If no `?v=` exists, add one
4. Commit the version bumps alongside the asset changes

**Check:** After any commit that touches `.css` or `.js` files, verify the same commit (or a follow-up) also bumps the `?v=` parameters in all templates that reference those files. A CSS-only commit with no template changes is a red flag.

**Learned from:** Four CSS commits (`09ee4b29` through `3d4b22a1`) were pushed and deployed but no visual changes appeared on the site. The CSS files were updated on disk, but `calendar.html`, `dashboard.html`, `home.html`, `tasks/list_modern.html`, and `properties/list_modern.html` all still had stale `?v=` parameters. Required a follow-up commit to bump all version strings.

## Quick Reference

| Rule | Symptom | Check |
|------|---------|-------|
| No Silent Swallows | Bug goes unnoticed for weeks | Every `except` logs or re-raises? |
| Catch What You Raise | Unhandled crash instead of fallback | Caller handles ALL exception types? Error-code sets complete? |
| Copy Before Delete | Data loss on deploy | Data copied BEFORE source NULLed/dropped? |
| One Source of Truth | "Fixed it but still wrong" | Constant/scope/config defined in exactly one place? |
| Respect Encapsulation | Double side-effects, brittle coupling | Only calling public API? |
| Verify Imports | `NameError` on first call | Every type/object imported before use? |
| Real DB Semantics | Query works locally, crashes in prod | DISTINCT/JSON/ORDER BY safe for Postgres? |
| Verify Model Attrs | `AttributeError` at runtime | Attribute exists on the model class? |
| Auxiliary Side-Effects | Notification failure aborts core op | Each side-effect wrapped independently? |
| Audit Trail | Action invisible in dashboard | State-changing endpoint creates ActionLog? |
| Error Visibility | Errors hidden from user | Dashboard feed includes ERROR-level logs? |
| Ephemeral Storage | Files vanish after deploy | All file I/O uses persistent storage? |
| Error Leaking | Internal details in HTTP response | Error messages generic, no `str(e)`? |
| String Datetime Compare | Future items filtered out | All datetime comparisons use parsed tz-aware objects? |
| Stale Connection Check | Feature disabled despite connection | Connection state read from owning service, not user column? |
| Cache-Only Primary View | "Only 1 event" when 15 exist | Primary view fetches live source, not just local cache? |
| Post-Conflict Testing | Resolved code breaks behavior | Tests re-run after conflict resolution before push? |
| Split Function Scope | `NameError` on variable from sibling function | Every variable in new function defined locally, as param, or imported? |
| Static Asset Cache-Busting | "Deployed but no visual change" | CSS/JS commit also bumps `?v=` in all loading templates? |

## Red Flags — STOP and Fix

- `except SomeError: pass` with no logging
- A `try/except` that catches fewer types than the callee raises
- An error-code set that doesn't enumerate all permanent/known codes
- A migration that NULLs or DROPs before copying
- Same magic number in two files
- Same scope/config list hardcoded in multiple files
- Calling `obj._method()` from outside `obj`'s module
- A type in a function signature that has no matching `import`
- An object referenced before its late import in a function body
- `DISTINCT` on a table with JSON columns
- `ORDER BY` column not in `SELECT DISTINCT` list
- Accessing `model.attribute` without checking the model definition
- An unwrapped notification/SMS/email call inside a critical operation
- A state-changing endpoint with no `ActionLog` entry
- A dashboard query that filters out ERROR-level logs by default
- Writing files to local disk on a cloud platform (Railway, Heroku)
- Silent fallback to local storage when external storage fails
- `str(e)` or `traceback.format_exc()` in an HTTP response or redirect URL
- `print()` debug statements in production code
- Template file in a directory that doesn't match the route module using it
- CSS variant class that redeclares properties already on the base class
- Datetime comparison using string `>=`/`<=` instead of parsed objects
- Connection check using `user.some_token` instead of the token manager
- Primary view reading from local cache when it's the only UI for that data
- Cherry-pick/merge pushed without re-running affected tests
- Variable used in a function that was defined in a different function (split/copy artifact)
- String-quoted type annotation (`"UUID | None"`) without module-level import of the type
- A commit that changes `.css`/`.js` files but doesn't bump `?v=` params in loading templates

## When NOT to Use

- Simple CRUD with no error handling complexity
- Read-only queries with no side effects
- Tests (mocking private methods in tests is acceptable)
