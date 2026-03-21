---
name: courierflow-ui-audit
description: "Full codebase UI audit — source-level scan + visual inspection + auto-fix. Use with: /courierflow-ui-audit"
---

# CourierFlow UI Audit Procedure

> **Trigger:** Invoked explicitly with `/courierflow-ui-audit`.
> **Prerequisite:** Load `/courierflow-ui-standards` first — it contains all rules, tokens, and detection patterns referenced below.

**Dead CSS/Template Archiving:**
When the audit identifies entire CSS files or templates with no live references:
1. Move dead files to `_archived/css/` or `_archived/templates/` (preserving subdirectory structure)
2. Remove corresponding `<link>` tags from `base.html` and any templates
3. For partially-dead files, remove dead sections in-place and add an audit header comment noting what was removed and when
4. Bump service worker `CACHE_NAME` and all `?v=` cache-busters after removal

## Phase 1: Source-Level Scan

**Scope:** All files in `app/templates/**/*.html` and `app/static/css/**/*.css`.

**Exclude:**
- `app/static/css/design-system/_variables.css`
- `app/static/css/workflow-builder.css`
- `app/templates/landing/`
- `_archived/`

Run ALL detection patterns from `/courierflow-ui-standards` Section 2 across the full scope. Auto-fix categories 1–12. Flag categories 13–16 for manual review.

For each file with violations, report:
- File path and line number
- What was found vs. what it was replaced with

## Phase 2: Visual Inspection

After source-level fixes, start the dev server and inspect computed styles.

**Step 1: Start dev server**

Use `preview_start` to launch the dev server. If the server fails to start, STOP the audit and ask the user to help troubleshoot. Do NOT skip visual inspection.

**Step 1b: Create test user and login (AUTOMATIC)**

Dashboard, Properties, Tenants, Workflows, Settings, and Calendar require login. Always create a disposable test user and authenticate automatically — never ask the user for credentials.

**Procedure:**

1. **Register a test user** via the API:
   ```bash
   curl -s -X POST "http://localhost:<PORT>/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "email": "ui-audit-<TIMESTAMP>@courierflow-test.com",
       "password": "AuditTest123!",  # pragma: allowlist secret
       "full_name": "UI Audit Bot"
     }'
   ```
   Use a unique email with timestamp to avoid conflicts. Do NOT use `.local` TLD — rejected by email validator. The response returns an `access_token`.

2. **Login via the browser** using Playwright/preview tools:
   - Navigate to `/auth/login`
   - Fill the email field with the test email
   - Fill the password field with `AuditTest123!`
   - Click the Login button
   - Wait for redirect to `/home` (dashboard)

3. **Verify login succeeded** — confirm the page URL changed from `/auth/login`. Note: `/home` (dashboard) and `/tenants/` may return 500 for a fresh test user with no data (no Google Calendar connected, no properties). This is expected — skip those pages and inspect the ones that render: Properties, Workflows, Settings, Documents, Email Templates.

If registration fails (e.g., database not configured, server error), report: "Visual inspection of protected pages skipped — could not create test user: [error details]." Do NOT ask the user for credentials; just skip and document the failure.

**Step 2: Crawl key pages**

Navigate to each page and run `preview_inspect` on key elements. The browser session is already authenticated from Step 1b.

**Pages:** Dashboard, Properties, Tenants, Workflows, Settings, Calendar

**Checks per page:**

| Check | Selector(s) | Expected Value |
|-------|-------------|----------------|
| Button radius | `.btn` | `border-radius: 12px` (from `--ds-p-radius-btn: var(--ds-radius-lg)`) |
| Card radius | `.card, .panel` | `border-radius: 24px` |
| Font family | `body` | `font-family` contains "Inter" |
| No Poppins | all text elements | No element computes to Poppins |
| Button centering | `.btn` | `display: flex; align-items: center; justify-content: center` |
| Page header exists | `.page-header-standard` | Element exists on page |
| Stat icon size | `.stat-icon` | `width: 40px; height: 40px` |
| Badge radius | `.page-status-badge` | `border-radius: 9999px` |
| Card shadow | `.card` | `box-shadow` matches shadow-sm pattern |
| Text colors | `h1, h2, h3, p` | Uses slate palette values only |

**Step 3: Report visual issues**

For each visual violation, report:
- Page URL
- Element selector
- Expected vs. actual computed value
- Whether it's likely a CSS specificity override

## Phase 3: Audit Report

Output a structured report:

```
## UI Standards Audit — [date]

### Source-Level Fixes Applied
- [file]: [N] violations fixed
  - Line NN: Replaced X → Y

### Visual Inspection Results
- ✅ Page — all checks passed
- ⚠️ Page — N issues
  - selector: expected X, got Y

### Manual Review Required
- [file:line]: description of issue

### Summary
Files scanned: N | Fixed: N | Visual issues: N | Manual review: N
```
