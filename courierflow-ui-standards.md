---
name: courierflow-ui-standards
description: Use when creating or modifying UI files (templates, CSS) in CourierFlow. Use with "audit" argument for full codebase scan with visual inspection.
---

# CourierFlow UI Standards — "Quiet Elegance"

> **This is an ACTIVE skill.** It enforces standards, not just documents them.
>
> - **Pre-flight mode** (default): Automatically loads rules, scans touched files, auto-fixes violations before/after UI work.
> - **Audit mode** (`/courierflow-ui-standards audit`): Full codebase scan + visual inspection + auto-fix.

---

## Section 1: Rules Reference

### Design Philosophy

1. **Monochrome First** — Slate palette dominates. Color reserved for semantic meaning (success, warning, error) and interactive focus.
2. **Inter Only** — One font family. No Poppins, no secondary fonts.
3. **Content over Chrome** — Spacing, background tints, subtle shadows. Avoid heavy borders.
4. **Fail Visible** — Every state (loading, empty, error, success) has clear visual treatment.

### Tokens

All styling via `app/static/css/design-system/_variables.css`. Never hardcode colors, spacing, or shadows.

**Typography:**
```
Font:     var(--ds-font-family)           → Inter
Heading:  var(--ds-font-family-heading)   → var(--ds-font-family)

Sizes:    xs=11px  sm=13px  base=14px  md=16px  lg=18px  xl=24px  2xl=32px
Weights:  light=300  normal=400  medium=500  semibold=600  bold=700
```

| Tier | Size | Weight | Extras | Use For |
|------|------|--------|--------|---------|
| Card Title | `--ds-font-size-sm` (13px) | `--ds-font-weight-medium` (500) | — | Panel titles, card headings, stat labels |
| Section Label | `--ds-font-size-xs` (11px) | `--ds-font-weight-semibold` (600) | `text-transform: uppercase; letter-spacing: 0.05em; color: var(--ds-color-text-secondary)` | **ALL** within-page section headings: home panels, sidebar groups, card group labels, stat labels, document sections |

**Section Label is mandatory** for any class that serves as a section title within a page (`*-section-title`, `*-panel-title`, `*-section-header`, `*-section-label`). Sibling section titles on the same page MUST use identical styling. Never mix heading sizes for sibling sections.

**Color Palette:**
```
Canvas:    var(--ds-color-bg-primary)     → #F8FAFC
Secondary: var(--ds-color-bg-secondary)   → #F1F5F9
Tertiary:  var(--ds-color-bg-tertiary)    → #E2E8F0
Surface:   var(--ds-color-surface)        → #FFFFFF

Primary:   var(--ds-color-text-primary)   → #1E293B
Secondary: var(--ds-color-text-secondary) → #64748B
Tertiary:  var(--ds-color-text-tertiary)  → #94A3B8

Accent:    var(--ds-color-accent)         → #1E293B
Hover:     var(--ds-color-accent-hover)   → #0F172A

Success:   var(--ds-color-success)        → #047857
Warning:   var(--ds-color-warning)        → #B45309
Error:     var(--ds-color-error)          → #B91C1C
Info:      var(--ds-color-info)           → #334155
Spark:     var(--ds-color-spark)          → #6366F1
```

**Spacing:** `1=4px 2=8px 3=12px 4=16px 5=20px 6=24px 8=32px 10=40px 12=48px 16=64px` — use `var(--ds-space-N)`

**Border Radius:** `sm=4px md=8px lg=12px xl=16px 2xl=24px full=9999px`

**Shadows:** `xs`, `sm` (card default), `md` (card hover), `lg`, `card` — use `var(--ds-shadow-*)`

**Personality Variables (`--ds-p-*`):**
```css
--ds-p-radius-card: var(--ds-radius-2xl);   /* 24px */
--ds-p-radius-btn: var(--ds-radius-lg);    /* 12px */
--ds-p-radius-input: var(--ds-radius-lg);   /* 12px */
--ds-p-radius-modal: var(--ds-radius-2xl); /* 24px */
--ds-p-radius-badge: var(--ds-radius-full); /* pill */
--ds-p-shadow-card: var(--ds-shadow-sm);
--ds-p-shadow-hover: var(--ds-shadow-md);
--ds-p-hover-lift: -3px;
--ds-p-hover-scale: 1;
```

### Components

**Buttons:** Use `.btn` system. **Never use `wf-btn`** (legacy).

| Class | Resting | Hover |
|-------|---------|-------|
| `.btn-primary` | White bg, slate border, shadow-sm | Inverts to slate-800 bg, white text |
| `.btn-secondary` | White bg, slate-200 border | Border darkens |
| `.btn-dark` | Slate-800 bg, white text | Subtle brightness lift |
| `.btn-accent` | Accent gradient bg | Shadow lift + translateY(-3px) |
| `.btn-ghost` | Transparent | Tertiary bg on hover |
| `.btn-danger` | Red bg | Brightness lift |
| `.btn-success` | Green bg | Brightness lift |

Sizes: `.btn-xs` (px-2 py-1, 11px), `.btn-sm` (px-3 py-1.5, 13px), default (px-4 py-2, 14px), `.btn-lg` (px-6 py-3, 16px)

**Rules:** Never inline `style=` on buttons. Never use `wf-btn-*`. All buttons need `.btn` base. `btn-dark` is NOT for primary page actions — use `btn-primary`. Never duplicate `.btn` (e.g. `class="btn btn-success btn"`).

**Cards:**
```css
.card, .panel {
    background: var(--ds-color-surface);
    border: 1px solid var(--ds-border-color);
    border-radius: var(--ds-p-radius-card);
    box-shadow: var(--ds-p-shadow-card);
}
.card:hover { box-shadow: var(--ds-p-shadow-hover); transform: translateY(var(--ds-p-hover-lift)); }
```

**Page Layout:** Use `page-content-wrapper` + `page-header-standard` + `page-title-section` + `page-actions`. Or `{% from 'macros/ui_macros.html' import page_header %}`.

**Badges:** `page-status-badge` + `page-status-draft`, `page-status-active`, `page-status-paused`, `page-status-error`

**Stat Icons:** `.stat-icon` — `width/height: var(--ds-space-10)` (40px), `border-radius: var(--ds-radius-lg)`, `background: var(--ds-color-bg-secondary)`

**Template Cards:** Category-tinted icons (`template-icon.icon-lifecycle`, `.icon-recurring`, `.icon-safety`, `.icon-emergency`, `.icon-turnover`). Never inline gradients on template icons.

**Filter Bar:** Always use `_filter_bar.html` partial. Never create custom filter HTML with raw `<input>`/`<select>`.

**Alerts:** Use `var(--ds-color-success-bg)`, `var(--ds-color-warning-bg)`, `var(--ds-color-error-bg)` — never hardcoded colors.

### Template Rules

**Block names:** `page_title`, `content`, `extra_css`, `extra_scripts` — exact names from `base.html`.

**CSS Variable Rules:** No fallbacks. No hardcoded colors/spacing/shadows. No inline styles on buttons.

### CSS Layer Architecture

All CSS files must be wrapped in the appropriate `@layer`:
- `@layer bootstrap { ... }` — Bootstrap 5 (loaded via `@import layer()` in `base.html`)
- `@layer design-system { ... }` — tokens, typography, animations, accessibility, progressive enhancement
- `@layer components { ... }` — reusable component styles (loaded via `components/index.css`)
- `@layer pages { ... }` — page-specific overrides (loaded via `{% block extra_css %}`)
- **Unlayered** (wins by default) — `mobile.css` (responsive overrides), `dark.css` (theme overrides), `_page-header.css` (deliberately unlayered)

Layer order declared in `base.html`:
```html
<style>
  @layer bootstrap, design-system, components, pages;
  @import url('...bootstrap.min.css') layer(bootstrap);
</style>
```

Bootstrap is the **lowest-priority layer**. Design system, components, and pages all override it naturally. No `!important` needed.

New CSS files MUST be wrapped in the correct `@layer`. Only `mobile.css`, `dark.css`, and `_page-header.css` should be unlayered.

- **`workflows-modern.css`**: Loaded globally in `base.html` (async). Do NOT add per-template `<link>` tags for it — they cause double-loading and specificity conflicts.

### Exceptions

- **Workflow Builder** (`workflow-builder.css`): Own `--builder-primary` system.
- **Landing page** (`landing/`): Marketing styles, not bound to design system.
- **`--ds-gradient-*`**: Only `--ds-gradient-accent`, `--ds-gradient-subtle`, `--ds-gradient-dark`, and semantic alert gradients are valid.

### Quick Reference

| What | Token |
|------|-------|
| Card shadow | `var(--ds-p-shadow-card)` |
| Button radius | `var(--ds-p-radius-btn)` = 12px |
| Card radius | `var(--ds-p-radius-card)` = 24px |
| Primary button | White → dark on hover |
| Body font | `var(--ds-font-family)` = Inter |

---

## Section 2: Pre-flight Workflow (Automatic)

**Trigger:** Any task that creates or modifies files in `app/templates/` or `app/static/css/`.

This is NOT manually invoked. It runs automatically when the skill is loaded for UI work.

### Before Writing Code

1. **Rules are now in context** — follow Section 1 exactly.
2. **If editing existing files**, scan each file for violations using the detection patterns below and auto-fix before writing new code.

### Detection Patterns (Source-Level)

Run these checks on files being touched. Auto-fix violations found.

**Auto-fixable violations:**

| # | Category | Grep Pattern | Fix |
|---|----------|-------------|-----|
| 1 | Hardcoded hex colors | `#[0-9a-fA-F]{3,8}` in templates/CSS (not `_variables.css`) | Replace with matching `var(--ds-*)` token |
| 2 | Hardcoded spacing | `padding:\|margin:\|gap:` with px/rem values | Replace with `var(--ds-space-*)` |
| 3 | Hardcoded shadows | `box-shadow:` with raw rgba (not `var(--ds-shadow-*)`) | Replace with closest `var(--ds-shadow-*)` |
| 4 | Legacy classes | `wf-btn\|wf-page-header\|wf-page-title\|wf-btn-ghost` | Replace: `wf-btn`→`btn`, etc. |
| 5 | Inline button styles | `style=` on `<button>` or `.btn` elements | Remove inline, apply `.btn-*` class |
| 6 | Wrong font families | `font-family:` not using `var(--ds-font-family)`, or `Poppins` | Replace with `var(--ds-font-family)` |
| 7 | CSS variable fallbacks | `var(--ds-.*,` (comma = fallback) | Remove fallback value |
| 8 | Hardcoded border-radius | `border-radius:` with px/rem (not `var(--ds-radius-*\|--ds-p-radius-*)`) | Replace with closest token |
| 9 | Hardcoded font-size | `font-size:` with px/rem (not `var(--ds-font-size-*)`) | Replace with closest token |
| 10 | Hardcoded font-weight | `font-weight:` with numeric (not `var(--ds-font-weight-*)`) | Replace with closest token |
| 11 | Duplicate btn class | `class="btn.*btn"` with trailing duplicate | Remove duplicate |
| 12 | Duplicate global CSS link | `workflows-modern.css` in `{% block extra_css %}` | Remove — already loaded globally in `base.html` |

**Flag for manual review:**

| # | Category | Detection |
|---|----------|-----------|
| 13 | Missing page structure | Template missing `page-content-wrapper` or `page-header-standard` |
| 14 | Custom filter bars | Raw `<input>`/`<select>` that should use `_filter_bar.html` |
| 15 | Wrong template blocks | Block names not in: `page_title`, `content`, `extra_css`, `extra_scripts` |
| 16 | Inconsistent section titles | Section title classes (`*-section-title`, `*-panel-title`, `*-section-header`) with `font-size` not `var(--ds-font-size-xs)` or missing `text-transform: uppercase` |

### After Finishing UI Changes

Re-scan only the modified files using the same detection patterns. Auto-fix any violations introduced during the session. Report what was fixed.

---

## Section 3: Audit Procedure (Manual)

**Trigger:** Invoked explicitly with `/courierflow-ui-standards audit`.

**Dead CSS/Template Archiving:**
When the audit identifies entire CSS files or templates with no live references:
1. Move dead files to `_archived/css/` or `_archived/templates/` (preserving subdirectory structure)
2. Remove corresponding `<link>` tags from `base.html` and any templates
3. For partially-dead files, remove dead sections in-place and add an audit header comment noting what was removed and when
4. Bump service worker `CACHE_NAME` and all `?v=` cache-busters after removal

### Phase 1: Source-Level Scan

**Scope:** All files in `app/templates/**/*.html` and `app/static/css/**/*.css`.

**Exclude:**
- `app/static/css/design-system/_variables.css`
- `app/static/css/workflow-builder.css`
- `app/templates/landing/`
- `_archived/`

Run ALL detection patterns from Section 2 across the full scope. Auto-fix categories 1–12. Flag categories 13–16 for manual review.

For each file with violations, report:
- File path and line number
- What was found vs. what it was replaced with

### Phase 2: Visual Inspection

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
   Use a unique email with timestamp (e.g., `ui-audit-1709827200@courierflow-test.com`) to avoid conflicts. Do NOT use `.local` TLD — it is rejected by the email validator. The response returns an `access_token`.

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

### Phase 3: Audit Report

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
