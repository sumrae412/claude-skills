---
name: defensive-backend-flows
description: Use when writing or reviewing Python backend code that involves error handling, data migrations, service-layer functions, cross-module API calls, or constant definitions
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
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

### 7. Test Queries Against PostgreSQL Semantics

SQLAlchemy queries must respect PostgreSQL semantics. Common traps:

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

### 8a. SQLAlchemy Filters on Nonexistent Attributes Fail Silently

SQLAlchemy Python-side filter expressions (e.g., `m.is_primary` in a generator/list comprehension) do NOT raise `AttributeError` the way direct attribute access does. Instead, the expression evaluates against `None` or a descriptor and silently matches nothing. This is worse than a crash — it returns empty results with no error.

```python
# ❌ BAD — `is_primary` doesn't exist; silently returns None for every member
primary = next((m for m in members if m.is_primary), None)

# ✅ GOOD — use the actual column name
primary = next((m for m in members if m.is_primary_contact), None)
```

**Check:** When filtering model objects in Python (not SQL WHERE), verify the attribute name against the model class definition. Grep the model file for the column — do not assume names.

**Learned from:** `sync_service.py` — 4 occurrences of `is_primary` (wrong) instead of `is_primary_contact` silently matched nothing, causing primary contact detection to always fail.

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

### 14. Domain-Level Error Isolation

When an endpoint aggregates data from multiple independent sources, isolate each source with its own try/except. One failing domain must not take down the entire response.

```python
for domain in requested:
    try:
        results[domain] = await self._compute(db, user_id, domain)
    except SQLAlchemyError:
        logger.exception("domain=%s failed", domain)
        results[domain] = None  # graceful degradation
```

Combine with per-domain caching (independent TTLs) so a cache miss in one domain doesn't force recomputation of all. See `CountsService.get_counts()`.

**Check:** If an endpoint fetches 3+ independent data sources, ask: "Does a failure in source A prevent source B from returning?" If yes, wrap each independently.

**Learned from:** `counts_service.py` — unified counts endpoint serves 7 domains; each independently cached and independently error-isolated.

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

This also applies to **datetime arithmetic** — adding `timedelta` and then subtracting two datetimes. If one operand is timezone-naive (common for DB columns without `timezone=True`) and the other is aware, Python raises `TypeError`. Normalize before any arithmetic:

```python
# ❌ BAD — archived_at may be naive, now is aware -> TypeError
now = datetime.now(timezone.utc)
deletes_at = doc.archived_at + timedelta(days=30)
remaining = deletes_at - now  # TypeError if archived_at is naive

# ✅ GOOD — normalize to aware before arithmetic
now = datetime.now(timezone.utc)
archived_at = doc.archived_at if doc.archived_at.tzinfo else doc.archived_at.replace(tzinfo=timezone.utc)
deletes_at = archived_at + timedelta(days=30)
remaining = deletes_at - now
```

**Check:** Search for `.isoformat()` in comparisons or `>=`/`<=` with string timestamps. Every datetime comparison should use parsed `datetime` objects with explicit timezone. Any time a datetime from the database is used in arithmetic with `datetime.now(timezone.utc)`, verify the DB value has `tzinfo`.

**Learned from:** Home dashboard — upcoming events were filtered using string comparison of ISO timestamps, which dropped future events when timezone offsets varied. `documents.py` — `doc.archived_at` was naive while `now = datetime.now(timezone.utc)` was aware, causing `TypeError` on subtraction at line 486.

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

When modifying CSS or JS files, the commit must also bump the `?v=` version parameter in every template that loads the file.

### 20. Subprocess Commands Must Use List Arguments

Never use `shell=True` or string commands with subprocess. Always use list-based arguments with configurable timeouts. Add `# nosec` annotations with explanations for security scanners.

```python
# ❌ BAD — shell=True allows command injection
subprocess.run(f"git tag {tag_name}", shell=True)

# ✅ GOOD — list args, timeout, security annotation
# nosec B603,B607 - git is a trusted command with known arguments
result = subprocess.run(
    ["git", "tag", "-a", tag_name, "-m", message],
    capture_output=True,
    text=True,
    cwd=self.project_root,
    timeout=30,
)
```

**Learned from:** CI/CD scripts (release.py, rollback.py, canary_deploy.py) — all use list-based subprocess calls with timeouts and security annotations.

### 21. Lock File Acquisition Has TOCTOU Risk

When using file-based locks to prevent concurrent operations, there's a Time-Of-Check-To-Time-Of-Use race condition between checking if the lock exists and creating it. For critical operations, use atomic file creation or a proper locking library.

```python
# ❌ BAD — TOCTOU race between check and create
if os.path.exists(LOCK_FILE):
    raise RuntimeError("Already locked")
with open(LOCK_FILE, "w") as f:  # Another process could create it here
    f.write(str(os.getpid()))

# ✅ GOOD — atomic creation with exclusive flag
try:
    fd = os.open(LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.write(fd, str(os.getpid()).encode())
    os.close(fd)
except FileExistsError:
    raise RuntimeError("Lock already held")
```

**Note:** For simple scripts where race conditions are unlikely, the simpler pattern is acceptable with a comment acknowledging the limitation. The middleware sets `max-age=31536000` (1 year) on static files, so without a version bump, the deploy succeeds but browsers serve the old cached file — the change is invisible to users.

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

### 22. Never Use eval() — Use ast.parse() for Expression Evaluation

When evaluating composed expressions (boolean logic, arithmetic), never use the eval built-in. Even with "controlled" input, it is a code smell that security scanners (Bandit B307) flag. Use `ast.parse()` with a recursive evaluator that only handles expected node types.

```python
# BAD — security scanner flags this, potential code execution
expr = "True and False or not True"
return __builtins__["eval"](expr)  # Bandit B307

# GOOD — ast.parse with explicit node handling
import ast

def _safe_eval_bool(expr: str) -> bool:
    tree = ast.parse(expr.strip(), mode="eval")

    def _walk(node):
        if isinstance(node, ast.Expression):
            return _walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(_walk(v) for v in node.values)
            if isinstance(node.op, ast.Or):
                return any(_walk(v) for v in node.values)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return not _walk(node.operand)
        raise ValueError(f"Unsupported node: {ast.dump(node)}")

    return _walk(tree)
```

**Check:** Search for the eval built-in in the codebase. Every occurrence should be replaced with a purpose-built evaluator using `ast.parse()`.

**Learned from:** `automation_engine.py` — used the eval built-in to evaluate composed boolean expressions. Replaced with `_safe_eval_bool()` using `ast.parse(expr, mode="eval")`.

### 23. SQL Dynamic Table Names: Allowlist + Assert, Not F-Strings

When SQL queries need a dynamic table name (e.g., during table renaming migrations), never use f-strings inside `text()`. Instead: (1) assert the name is in an explicit allowlist, (2) use `.replace()` on a plain string, (3) wrap with `text()` after substitution.

```python
# BAD — f-string SQL injection vector, Bandit B608
query = text(f"""
    SELECT * FROM {table_name} WHERE user_id = :uid
""")

# GOOD — allowlist + replace + text()
assert table_name in ("households", "properties"), "Invalid table name"
sql = """
    SELECT * FROM {table_name} WHERE user_id = :uid
"""
query = text(sql.replace("{table_name}", table_name))
```

**Check:** Search for `text(f"` or `text(f'` in services. Every dynamic table/column name in SQL must use the allowlist pattern.

**Learned from:** `household_service.py` — three SQL queries used `text(f"...{households_table}...")`. Fixed with assert-allowlist + `.replace()`.

### 24. Retry Once on Transient DB OperationalError

For operations that call the database through dynamic dispatch (tool executors, plugin systems), wrap in a single-retry loop for `sqlalchemy.exc.OperationalError`. Transient connection resets happen on cloud platforms (Railway, Heroku) and a single retry usually succeeds.

```python
# BAD — transient connection reset crashes the operation
result = await self._execute_via_skill(tool_name, intent, input, ctx)

# GOOD — retry once on transient DB error
from sqlalchemy.exc import OperationalError

for attempt in range(2):
    try:
        result = await self._execute_via_skill(tool_name, intent, input, ctx)
        break
    except OperationalError:
        if attempt == 0:
            logger.warning(f"Transient DB error in {tool_name}, retrying")
            continue
        raise
```

**Check:** For any operation that calls the DB through a plugin/dispatch layer, ask: "Will a transient connection reset crash this?" If yes, add a single-retry loop.

**Learned from:** `tool_executor.py` — `_execute_via_skill()` occasionally hit transient DB connection resets. Added single-retry loop with `except OperationalError`.

### 25. Handle None vs Empty String for Nullable Text Fields

When a service updates a nullable text field, handle three cases: (1) non-None value → `.strip() or None`, (2) explicit `None` → set to `None` (clear the field), (3) not provided → don't touch. Missing the "explicit None" case means users can't clear a field once set.

```python
# BAD — only handles non-None, can't clear the field
if value is not None:
    profile.field = value.strip() or None
# Passing None does nothing — field stays set forever

# GOOD — three-way handling
if value is not None:
    profile.field = value.strip() or None
else:
    profile.field = None  # explicit clear
```

**Check:** For every nullable text field update, ask: "Can the user clear this field by passing None/null?" If the service only has an `if value is not None` branch, it can't.

**Learned from:** `user_profile_service.py` — `update_tenant_opt_in_clause()` only handled non-None values. Passing `None` was silently ignored, so users couldn't clear the clause.

### 26. DB Fallback Paths: Narrow Catch and Preserve Filters

When a service uses a primary query, then a fallback query, then a "bare" query (e.g. no eager loading), (1) catch only `SQLAlchemyError` (not a generic exception type) so non-DB errors propagate; (2) in the bare fallback, apply the same filters (e.g. status, search) as in the primary path — do not skip filters or the bare path returns different data than the primary. For unknown filter values (e.g. status_filter not in allowlist), log a warning and treat as no filter; do not silently ignore.

**Check:** In layered DB fallbacks, does the bare path call the same filter helper as the primary? Does the `except` block catch only `SQLAlchemyError`?

**Learned from:** `client.py` — `search_clients_grouped` fallback skipped status filter in bare path; CodeRabbit review.

### 27. Never Use BaseHTTPMiddleware with Async SQLAlchemy

Starlette's `BaseHTTPMiddleware.call_next()` wraps the response body in an internal task group, which breaks `AsyncSession` lifecycle in FastAPI dependency-injected routes. Symptoms: random "Session is closed" / "greenlet_spawn has not been called" errors on endpoints that work fine without the middleware. **Always** use the pure ASGI pattern (`__init__(self, app)` / `async def __call__(self, scope, receive, send)`) instead.

**Check:** `grep -r "BaseHTTPMiddleware" app/` returns zero hits? Any new middleware uses the `scope/receive/send` signature?

**Learned from:** `app/main.py`, `app/middleware/audit.py`, `app/middleware/google_connection.py` — Four middleware classes using `BaseHTTPMiddleware` broke async SQLAlchemy sessions on `/api/copilot` and AI Insights endpoints. PR #223 fixed one; PR #226 fixed the remaining three only after a second bug report.

### 28. Audit ALL Instances When Fixing a Class of Bug

When a bug is caused by a **pattern** (e.g., using a deprecated base class, a wrong import style, a misconfigured decorator), do not fix only the instance the user reported. `grep` the entire codebase for ALL instances of the same pattern and fix them all in one PR. A partial fix leads to a second bug report and a second PR for the same root cause.

**Check:** Before shipping a pattern-class fix, run a codebase-wide grep for the offending pattern. Are there zero remaining instances?

**Learned from:** PR #223 fixed `CopilotAuthMiddleware` but missed `PerformanceMiddleware`, `AuditMiddleware`, and `GoogleConnectionMiddleware` — all using the same broken `BaseHTTPMiddleware` base class. PR #226 was needed to finish the job.

### 29. Expose Public Wrappers for Cross-Service Data Sync

When a private service method needs to be called by other services (e.g., `_sync_client_for_member()` needed by integration services), expose a public wrapper rather than making the private method public or calling it directly. This preserves encapsulation (rule 5) while enabling defensive sync from multiple code paths.

```python
# ❌ BAD — integration service reaches into private internals
await household_service._sync_client_for_member(db, user_id, ...)

# ✅ GOOD — public wrapper with simpler interface
await household_service.ensure_client_for_member(
    db, user_id=user_id, household_id=hid,
    first_name="Jane", last_name="Doe", email="jane@example.com",
)
```

**Learned from:** `sync_service.py` and `contact_import_service.py` — both needed to call `_sync_client_for_member()` to enforce the HouseholdMember → Client invariant. Added `ensure_client_for_member()` as a public wrapper.

**Tiered lookup for cross-property sync:** When syncing records that may exist under a specific parent (e.g., Client per Property), first query with the exact parent match (`household_id`), then fall back to an unlinked record (`household_id IS NULL`). This avoids both duplicate creation and incorrect cross-property matching.

**Inline creation variant:** When creating a Client directly (not via `ensure_client_for_member`), always: (1) flush the parent `HouseholdMember` first so `member.id` is available, (2) check for existing Client by email before insert (duplicate guard), (3) call `client.normalize_contact_info()` before adding.

### 30. Dedup Must Cover All Contact Identifiers

When syncing or creating records that deduplicate by contact info, the lookup must check **all** identifier types — not just one. If dedup only checks email, phone-only records create duplicates silently.

```python
# ❌ BAD — only email dedup, phone-only members always create duplicates
if member_data.email:
    existing = await find_by_email(db, user_id, member_data.email)
# No phone fallback — phone-only member always inserts

# ✅ GOOD — email first, then phone fallback
if member_data.email:
    existing = await find_by_email(db, user_id, member_data.email)
elif member_data.phone:
    phone_digits = re.sub(r"[^0-9]", "", member_data.phone)
    existing = await find_by_phone_normalized(db, user_id, phone_digits)
```

**Learned from:** `_sync_client_for_member()` — only checked email for dedup. CRM contacts with phone but no email created duplicate Clients on every sync.

### 31. Use `scalars().first()` for Non-Unique Column Lookups

`scalar_one_or_none()` raises `MultipleResultsFound` when the query matches more than one row. This is correct for primary-key or unique-column lookups, but crashes on non-unique columns (email, phone, name) as soon as duplicates appear in production.

```python
# ❌ BAD — works until two clients share an email, then crashes
result = await db.execute(
    select(Client).where(Client.email == email, Client.user_id == user_id)
)
existing = result.scalar_one_or_none()  # MultipleResultsFound!

# ✅ GOOD — returns first match, safe with duplicates
result = await db.execute(
    select(Client).where(Client.email == email, Client.user_id == user_id)
)
existing = result.scalars().first()
```

**Decision tree:**
- Querying by **primary key or unique constraint** → `scalar_one_or_none()` is correct
- Querying by **non-unique column** (email, phone, name) → `scalars().first()`
- Need to **assert uniqueness** as a business rule → use `scalar_one_or_none()` but handle `MultipleResultsFound` explicitly

### 32. Post-Merge: Verify No Duplicate Side-Effect Calls

After resolving merge conflicts in service files, scan the resolved file for consecutive duplicate calls. When both branches add a call to the same utility function, the merged file can end up calling it twice in the same code path.

```python
# ❌ BAD — merge conflict left two back-to-back calls
await ensure_client_for_member(db, user_id, household_id, ...)
await ensure_client_for_member(db, user_id, household_id, ...)  # duplicate

# ✅ GOOD — single call
await ensure_client_for_member(db, user_id, household_id, ...)
```

**Check:** After resolving any conflict in a service file, grep for repeated adjacent calls:
```bash
grep -n 'ensure_client_for_member\|_sync_client' FILE | head -20
```
If the same call appears on consecutive lines with no intervening logic, remove the duplicate.

**Learned from:** PR #240 merge — both the PR branch and main had added `ensure_client_for_member()` calls; conflict resolution left both in `contact_import_service.py` and `sync_service.py`.

### 33. Dialect Portability for Shared SQL

Production runs Postgres; tests run SQLite. Any `sqlalchemy.func.X` call where X is Postgres-specific crashes the test path while passing in prod, producing CI red that prod doesn't see.

Postgres-only (partial list): `pg_*advisory_lock*`, `date_trunc`, `to_tsvector`, `plainto_tsquery`, `array_agg`/`string_agg` with ORDER BY, `jsonb_*`, `generate_series`, `distinct on`.

```python
# ❌ BAD — crashes SQLite tests with `no such function: date_trunc`
daily_stmt = select(
    func.date_trunc("day", ActionLog.created_at).label("day"),
    func.count().label("cnt"),
).where(...)

# ✅ GOOD — branch on dialect; SQLite uses strftime
if db.bind.dialect.name == "postgresql":
    day_expr = func.date_trunc("day", ActionLog.created_at)
else:
    day_expr = func.strftime("%Y-%m-%d", ActionLog.created_at)
daily_stmt = select(day_expr.label("day"), func.count().label("cnt")).where(...)
```

For advisory locks specifically, SQLite tests can skip the call entirely — single-connection per test means no cross-session race exists:

```python
if db.bind.dialect.name == "postgresql":
    lock_result = await db.execute(text("SELECT pg_try_advisory_xact_lock(:id)"), {"id": lock_id})
    if not lock_result.scalar():
        return
# else: SQLite path falls through, no lock
```

**Check:** Before committing any new `func.X` call, verify X exists in SQLite's function set. If Postgres-only, add the dialect branch.

**Learned from:** Two CI-red sites in commit `66cf9b0e` (event_meta_service.py advisory lock + routes/logs.py date_trunc) — both shipped without crashing prod, both blocked the test suite for days. Hit in two separate sessions.

### 34. Normalize DB-Readback Datetimes Before Arithmetic with Aware `now()`

SQLite strips tzinfo on datetime-column read; Postgres TIMESTAMPTZ preserves it. Code that subtracts a DB-stored datetime from `datetime.now(timezone.utc)` works in prod but raises `TypeError: can't subtract offset-naive and offset-aware datetimes` in tests.

```python
# ❌ BAD — assumes paused_at is always aware
pause_duration = datetime.now(timezone.utc) - instance.paused_at

# ✅ GOOD — normalize the naive side
paused_at = instance.paused_at
if paused_at and paused_at.tzinfo is None:
    paused_at = paused_at.replace(tzinfo=timezone.utc)
pause_duration = datetime.now(timezone.utc) - paused_at
```

Same pattern applies on test assertions that compare a DB-readback datetime to an aware `expected`:

```python
# ❌ BAD — paused.resume_date is naive on SQLite
assert paused.resume_date == resume_date  # TypeError or wrong tz

# ✅ GOOD — normalize before compare
actual = paused.resume_date
if actual.tzinfo is None:
    actual = actual.replace(tzinfo=timezone.utc)
assert actual == resume_date
```

**Check:** Any `datetime.now(timezone.utc) - <something_from_db>` or comparison thereof needs the naive guard on the DB side.

**Learned from:** 5 service sites in commit `66cf9b0e` (workflow.py, workflow_service.py, workflow_scheduler.py, calendar_sync_service.py × 2). Production was unaffected (Postgres TIMESTAMPTZ); tests were red until normalized.

### 35. Get-or-Create Services Must Verify Parent Scope Before Insert

If a service follows `SELECT ... on (parent_id, user_id); INSERT on miss`, **always look up the parent first** in a separate scoped query. Otherwise a route whose 404 path depends on `None` will 200 for any UUID — the service materializes a row for any identifier.

```python
# BAD: auto-creates TemplateMetrics for any template_id, masking 404
metrics = get_or_create_metrics(template_id, user_id)

# GOOD: verify the parent belongs to the user before materializing anything
template = (
    await db.execute(
        select(WorkflowTemplate).where(
            WorkflowTemplate.id == template_id,
            WorkflowTemplate.user_id == user_id,
        )
    )
).scalar_one_or_none()
if template is None:
    return None
metrics = get_or_create_metrics(template_id, user_id)
```

Scope the parent lookup by `user_id` so the check doubles as authorization — don't leak cross-user existence through differing status codes.

**Audit:** `rg -n 'def (get_or_create|refresh_|ensure_)' app/services/`.

**Learned from:** `template_analytics_service.refresh_template_metrics` (`7066a568`) — `GET /api/analytics/templates/<bogus>/metrics` returned 200 (with empty stats) instead of 404, because the service happily created a metrics row for any UUID and the route's `if not metrics: 404` branch never fired.

### 36. Consuming LLM-Generated JSON

Any function that processes LLM output sits at the highest-variance input boundary in your stack. The LLM may omit fields, emit strings where numbers were expected, or shift nesting. Code written against the "happy-path schema" crashes at runtime on malformed output — and the aggregator/reviewer that was supposed to catch production bugs becomes the bug.

**Rule:** every field from LLM output is optional and type-guarded.

- `.get(key)` / `.get(key, default)` — never `dict[key]`
- Type-check numerics: `isinstance(v, (int, float))` before comparison; coerce with `try: int(v) except (TypeError, ValueError): continue`
- Check container types: `isinstance(scores, list)` before iterating; skip-with-warning if the shape is wrong
- WARNING-log on skip with the raw offending value + reviewer/source id; never silent `None`
- One malformed item must not kill the aggregate — continue past bad entries

```python
# BAD: crashes Phase 6 when the LLM omits 'break_case' or emits score="unknown"
for score_entry in reviewer_output["scores"]:
    if score_entry["score"] < threshold:
        findings.append({"message": f"{score_entry['criterion']}: {score_entry['break_case']}"})

# GOOD: malformed entries are skipped with a log, valid ones still produce findings
for i, score_entry in enumerate(reviewer_output.get("scores", []) or []):
    if not isinstance(score_entry, dict):
        log.warning("%s scores[%d] not a dict; skipping", reviewer_id, i); continue
    criterion = score_entry.get("criterion")
    break_case = score_entry.get("break_case", "<no break_case provided>")
    try:
        score = int(score_entry.get("score"))
    except (TypeError, ValueError):
        log.warning("%s scores[%d] score=%r not int; skipping", reviewer_id, i, score_entry.get("score")); continue
    if criterion is None or score >= threshold:
        continue
    findings.append({"message": f"{criterion}: {break_case}"})
```

Applies to every scored reviewer, aggregator, fixture loader, and JSON-consuming endpoint. See MEMORY `defensive_llm_output_consumers.md`.

**Audit:** `rg -n 'reviewer_output\[' -g '*.py'` and `rg -n 'response\["' -g '*.py' services/ | grep -i llm`.

## Stopgap In-Memory Rate Limiter

Before Redis, an async-safe in-memory rate limiter needs BOTH pieces — partial fixes regress to the race.

1. **Per-key `asyncio.Lock`** to serialize the `len(store) < MAX` check and the `append`. Without it, two coroutines at the boundary both pass the check, then both append — the window overflows by the concurrency factor.
2. **Explicit per-process caveat** in the module docstring and the function docstring: multi-worker deploys (`uvicorn --workers N`) multiply the effective ceiling by N. Document it so callers don't treat it as a global guarantee.

```python
_store: Dict[str, List[float]] = defaultdict(list)
_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

async def check_rate_limit(key: str) -> bool:
    async with _locks[key]:
        now = datetime.now(timezone.utc).timestamp()
        _store[key] = [ts for ts in _store[key] if ts > now - WINDOW]
        if len(_store[key]) >= MAX:
            return False
        _store[key].append(now)
        return True
```

See MEMORY `pattern_asyncio_lock_per_key_rate_limit.md`.

### 37. Test Constraints, Not Just Return Shapes

When a unit test mocks `db.execute`, the mock returns the same object regardless of WHERE clause. A query with the wrong column or missing scope passes its test silently. Three independent bugs in the concierge feature (wrong `Client.phone` instead of `phone_normalized`, missing landlord scoping, missing INSERT path) all passed unit tests because mocks short-circuited the WHERE clause.

**Defenses:**
- After `mock_db.execute.assert_awaited_once()`, inspect the bound `Select` statement and assert key columns/scopes appear in the compiled SQL
- OR write at least one integration test per query exercising real DB matching

**Audit:** Search test files for `mock_db.execute.return_value` with no companion assertion on call args.

**Learned from:** PR #342 — `identify_tenant`, `process_inbound_sms` landlord scoping, `ConciergeConversation` insert path. See MEMORY `policy_test_query_constraints.md`.

### 38. JSON Column Updates Must Reassign, Not Mutate In Place

SQLAlchemy doesn't track in-place mutation of `Column(JSON)` / `Column(JSONB)` fields. `model.field.append(x)` is a no-op at flush time. Either reassign wholesale or opt into mutation tracking.

```python
# BAD: silent no-op at flush
conversation.messages.append(entry)

# GOOD option 1: reassign
conversation.messages = list(conversation.messages or []) + [entry]

# GOOD option 2: opt into mutation tracking on the column
from sqlalchemy.ext.mutable import MutableList
messages: Mapped[list] = mapped_column(MutableList.as_mutable(JSON), default=list)
```

**Audit:** `rg -n '\.\w+\.append\(|\.metadata\[.*\] =' app/services/` — every hit on a JSON column needs reassignment.

**Learned from:** PR #342, `concierge_service._append_message`. See MEMORY `gotcha_sqlalchemy_json_column_in_place_mutation.md`.

### 39. Phone Lookups Use `phone_normalized`, Not `phone`

`Client.phone` is freeform; `Client.phone_normalized` is digits-only and indexed at `ix_clients_phone_normalized`. External systems (Twilio E.164, CSV imports) deliver canonical formats that never equal the freeform value. Always also scope by `user_id` — same phone can appear under different landlords.

```python
import re
digits = re.sub(r"\D", "", from_number)
stmt = select(Client).where(
    Client.phone_normalized == digits,
    Client.user_id == landlord_id,
)
```

**Audit:** `rg -n 'Client\.phone\s*==' app/`.

**Learned from:** PR #342 — `identify_tenant` queried `Client.phone` against E.164. Tests passed; real tenants matched zero rows.

### 40. State-Machine Transitions on Every Exit Path

When a model has a status enum, every action that exits a state must explicitly transition `status`. Clearing only the trigger field (e.g. `pending_action = None`) leaves the state machine permanently stuck.

```python
# BAD — status stays PENDING_APPROVAL forever
conversation.pending_action = None

# GOOD — explicit transition on exit
conversation.pending_action = None
conversation.status = ConciergeConversationStatus.ACTIVE
```

**Check:** For each status value, list every exit action. Verify each sets `status` explicitly.

**Learned from:** PR #342 — `approve_action`/`reject_action` cleared `pending_action` but never transitioned `status`.

### 41. Webhook Signature Validators Must Fail Closed in Production

A webhook validator that returns `True` when the auth token is unset is convenient for dev but turns the endpoint into an unauthenticated public POST in prod. Branch on `settings.is_production` (or `settings.environment == "production"`) and hard-fail.

```python
def _validate_signature(request, body):
    if not settings.twilio_auth_token:
        if settings.is_production:
            return False
        return True  # dev convenience only
    return RequestValidator(settings.twilio_auth_token).validate(...)
```

**Audit:** `rg -n 'auth_token|webhook.*validate|signature' app/routes/` — every webhook validator's no-token branch must hard-fail in prod.

**Learned from:** PR #342 — `_validate_twilio_signature` failed open. `app/routes/sms.py` has the same pattern (sweep candidate).

### 42. Escape User/AI Content in String-Templated Markup

TwiML, RSS, SOAP, sitemaps — any string-templated XML — never f-string AI-generated or user-derived content into the response body. Wrap with `xml.sax.saxutils.escape`. Same family as HTML escaping for `innerHTML`.

```python
from xml.sax.saxutils import escape as xml_escape
twiml = f'<Response><Message>{xml_escape(reply)}</Message></Response>'
```

A reply text of `</Message><Redirect>https://attacker.example.com/twiml</Redirect><Message>` would otherwise hijack the entire Twilio conversation.

**Learned from:** PR #342 — `app/routes/twilio_inbound.py` line 167.

### 43. Sanitizers That Modify Parseable Text Must Track Context

A global regex that mutates control chars, quotes, or whitespace in JSON/SQL/HTML/markdown will corrupt valid input by hitting structural positions as well as in-literal positions. The output looks plausible — one character off — but the downstream parser rejects it.

```python
# BAD — global regex escapes all control chars, including structural whitespace
# between { and the first property name. Pretty-printed JSON breaks at position 1.
sanitized = re.sub(r'[\x00-\x1F\x7F]', lambda m: {
    '\n': r'\n', '\r': r'\r', '\t': r'\t'
}.get(m.group(), ''), raw_json)
return json.loads(sanitized)  # fails: "{\n  \"flagged\"" after sanitize → parse error

# GOOD — state-machine walk. Only escape control chars inside "..." literals.
def escape_control_chars_in_strings(s: str) -> str:
    out, in_string, escaped = [], False, False
    for ch in s:
        if escaped:
            out.append(ch); escaped = False; continue
        if ch == '\\' and in_string:
            out.append(ch); escaped = True; continue
        if ch == '"':
            in_string = not in_string; out.append(ch); continue
        if in_string and ord(ch) < 0x20:
            out.append({'\n': r'\n', '\r': r'\r', '\t': r'\t'}.get(
                ch, f'\\u{ord(ch):04x}'))
        else:
            out.append(ch)
    return ''.join(out)

# Canonical parse pattern: fast-path → sanitizer fallback → surface error
def parse_model_json(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(escape_control_chars_in_strings(raw))
    except json.JSONDecodeError:
        return None  # caller MUST handle — no silent destructive fallback
```

**Paired anti-pattern:** silent `try/except` around the primary parse that falls through to a destructive default (send, publish, commit). Parse failures must surface to the user, not trigger irreversible actions under the guise of "fail open."

**Learned from:** ToneGuard PR #20 — the service-worker's global-regex sanitizer escaped `\n` → `\\n` in structural positions once Claude Haiku 4.5 began pretty-printing JSON. `JSON.parse` rejected at "position 1 column 2"; the catch block fell through to `releaseSend()` and the user's unreviewed message was sent.

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
| Naive/Aware Datetime Arithmetic | `TypeError: can't subtract offset-naive and offset-aware` | DB datetime normalized to aware before arithmetic with `datetime.now(tz.utc)`? |
| Stale Connection Check | Feature disabled despite connection | Connection state read from owning service, not user column? |
| Cache-Only Primary View | "Only 1 event" when 15 exist | Primary view fetches live source, not just local cache? |
| Post-Conflict Testing | Resolved code breaks behavior | Tests re-run after conflict resolution before push? |
| Split Function Scope | `NameError` on variable from sibling function | Every variable in new function defined locally, as param, or imported? |
| Static Asset Cache-Busting | "Deployed but no visual change" | CSS/JS commit also bumps `?v=` in all loading templates? |
| Subprocess Shell Injection | Command injection vulnerability | Using list args with `shell=False` and timeout? |
| Lock File TOCTOU | Race condition in concurrent ops | Using atomic `O_CREAT | O_EXCL` or proper lock library? |
| Flag Evaluation N+1 | Slow feature flag checks | Batch-loading flags before loop evaluation? |
| Eval Built-in Usage | Security scanner flags, code injection risk | Using `ast.parse()` with explicit node handler? |
| SQL F-String Table Names | SQL injection via dynamic table name | Using allowlist assert + `.replace()` pattern? |
| Transient DB Crash | Operation fails on connection reset | Single-retry loop for `OperationalError`? |
| Can't Clear Nullable Field | User can set but never clear a text field | Explicit `None` → set to `None` branch exists? |
| DB fallback filters | Bare path returns different set than primary | Fallback path applies same filters as primary? Catch only SQLAlchemyError? |
| No BaseHTTPMiddleware | "Session is closed" / greenlet errors | `grep -r "BaseHTTPMiddleware" app/` returns zero? |
| Audit ALL Pattern Instances | Same bug reported twice, different file | Codebase-wide grep for pattern before shipping fix? |
| `scalar_one_or_none` on non-unique col | `MultipleResultsFound` crash months later | WHERE clause backed by unique DB constraint? If no, use `scalars().first()` |
| Test Constraints, Not Shapes | "Tests passed but feature is broken" | Mocked `db.execute` test asserts the bound `Select`? OR has companion integration test? |
| JSON Column Reassignment | `model.field.append(x)` doesn't persist | JSON-column writes reassign (`field = list(field) + [x]`) or use `MutableList`? |
| Phone Lookup Normalization | Twilio E.164 never matches stored phone | Lookup uses `Client.phone_normalized` AND `Client.user_id` scope? |
| State-Machine Exit Transitions | Status stuck in `PENDING_*` forever | Every exit action sets `status` explicitly, not just clears trigger field? |
| Fail-Closed Webhook Validators | Public unauthenticated POST in prod | No-token branch hard-fails when `settings.is_production`? |
| Escape XML/TwiML Substitutions | TwiML hijack via tag injection | AI/user content wrapped in `xml_escape()` before f-string? |
| Context-Aware Sanitizers | "JSON.parse fails at position 1 after sanitize" | Sanitizer is a state-machine walk (tracks in-string vs structural), not a global regex? Fallback path doesn't silently release destructive action on parse failure? |

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
- Datetime arithmetic between a DB column value and `datetime.now(timezone.utc)` without normalizing timezone awareness
- Connection check using `user.some_token` instead of the token manager
- Primary view reading from local cache when it's the only UI for that data
- Cherry-pick/merge pushed without re-running affected tests
- Variable used in a function that was defined in a different function (split/copy artifact)
- String-quoted type annotation (`"UUID | None"`) without module-level import of the type
- A commit that changes `.css`/`.js` files but doesn't bump `?v=` params in loading templates
- Any use of the eval built-in — replace with `ast.parse()` + purpose-built evaluator
- `text(f"...{variable}...")` in SQL — use allowlist assert + `.replace()` instead
- DB call through dynamic dispatch with no retry for `OperationalError`
- Nullable text field update with only `if value is not None` branch (can't clear)
- A layered DB fallback whose bare path skips filters (status, search) applied in primary path
- `except Exception` in a DB fallback — use `except SQLAlchemyError` so non-DB errors propagate
- `from starlette.middleware.base import BaseHTTPMiddleware` — use pure ASGI middleware instead
- A pattern-class bug fix that only fixes the reported instance without grepping for all occurrences
- `scalar_one_or_none()` on a query filtering by a non-unique column (email, phone, name) — use `scalars().first()` instead
- Mocked `db.execute.return_value` in a test with no companion assertion on the bound `Select` — WHERE clause is invisible
- `.append()` / nested-dict mutation on a `Column(JSON)` value — silent no-op without reassignment or `MutableList`
- `Client.phone == ...` lookup against external (E.164) input — use `Client.phone_normalized` and scope by `user_id`
- Status-enum-driven model where an exit action only clears a trigger field and never reassigns `status`
- Webhook signature validator with a no-token branch that returns `True` unconditionally — must hard-fail in production
- F-string interpolation of AI/user content into XML/TwiML/RSS without `xml.sax.saxutils.escape`

## When NOT to Use

- Simple CRUD with no error handling complexity
- Read-only queries with no side effects
- Tests (mocking private methods in tests is acceptable)
