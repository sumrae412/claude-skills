---
name: courierflow-ui
description: CSS architecture, design system, templates, UI standards. Load when working on app/templates/*, *.css, *.html, or UI features.
---

# CourierFlow UI Standards

## CSS Architecture

**Layer cascade (declared in `base.html`):**

```css
@layer design-system, components, pages;
```

- `design-system` — tokens, base typography, animations, accessibility
- `components` — reusable component styles (via `components/index.css`)
- `pages` — page-specific overrides (via `{% block extra_css %}`)
- Unlayered (wins by default) — Bootstrap, `mobile.css`

## Component Rules

- Component selectors (`.btn`, `.form-control`, `.modal-content`, `.card`, `.badge`, `.empty-state`) defined **once** in `components/`
- Page files scope overrides with page-specific parent: `.workflow-editor .form-control { ... }`
- Scrollbar (`::-webkit-scrollbar`) defined once in `design-system/index.css`
- `workflows-modern.css` loaded globally — do NOT add per-template `<link>` tags

## Design System Tokens

**Always use `var(--ds-*)` variables:**

| Element | Use | NEVER Use |
|---------|-----|-----------|
| Page wrapper | `.page-content-wrapper` | Inline `style="background:..."` |
| Page headers | `.page-header-standard` | Custom header divs |
| Buttons | `.btn .btn-primary` | `wf-btn`, inline styles |
| Colors | `var(--ds-*)` tokens | Hardcoded hex values |
| Spacing | `var(--ds-space-*)` | Hardcoded px/rem |
| Shadows | `var(--ds-shadow-*)` | Hardcoded box-shadow |

Variables file: `app/static/css/design-system/_variables.css`

## "Quiet Elegance" Principles

- **Monochrome First** — Slate palette dominates; color for sparing semantic emphasis
- **Inter Only** — One font family (`--ds-font-family`). No Poppins.
- **White + Shadow Buttons** — Primary = `bg-white border shadow-sm`, not `bg-slate-900`
- **Subtle Semantic Badges** — Desaturated emerald/amber/red, not pure monochrome
- **Content over Chrome** — Spacing and background tints separate sections, not borders

## Template Blocks

Use exact names from `base.html`:
- `extra_css` — Additional stylesheets
- `extra_scripts` — Additional JavaScript
- `page_title` — Page title
- `content` — Main content

## Cache Busting

Format: `?v=YYYYMMDD[letter]` (e.g., `?v=20260306b`)

When changing CSS/JS:
1. Bump `?v=` param on all `<link>`/`<script>` tags referencing the file
2. Bump `CACHE_NAME` in `app/static/sw.js`

## Service Worker

- **Network-first for CSS/JS** — Cache is offline fallback only
- Cache-first causes stale deploys that survive `?v=` bumps

## Landing Pages Exception

`landing/index.html`, `landing/features.html`, `landing/pricing.html`:
- Extend `landing_base.html`, NOT `base.html`
- Load their own CSS independently
- Design-system layers do not apply

## Workflow Builder: CSS Target Stylesheet

**`builder.html` loads `timeline-list-builder.css` — NOT `workflow-builder.css`.** Any CSS for the workflow builder page (TokenDropdown, config panels, timeline steps) must go in `app/static/css/pages/timeline-list-builder.css`. This is a recurring mistake across sessions.

## Workflow Builder: Script & Component Registration

Every config component JS file referenced by `TimelineListBuilder.js` must have:
1. A `<script>` tag in `builder.html` (in the config scripts block)
2. A registration entry in the `configComponents` array inside `initializeBuilderApp()`

**Load order matters:** `ConditionBuilder.js` must load BEFORE `ConditionConfig.js` because `ConditionConfig` references `window.ConditionBuilder` at definition time.

## Workflow Builder: TokenDropdown Integration Pattern

All config components (SMSConfig, TaskConfig, NoticeConfig, StatusUpdateConfig, SendDocumentConfig) use a shared `TokenDropdown` component instead of inline token menus. The integration follows this exact pattern:

**Data (3 fields):** `showTokenDropdown: false`, `activeTokenField: null`, `tokenDropdownPos: { x: 0, y: 0 }`

**Methods (3 methods):** `openTokenDropdown(field, event)`, `closeTokenDropdown()`, `handleTokenSelect(payload)`

**Template:** Single `<TokenDropdown :visible="showTokenDropdown" :position="tokenDropdownPos" @select="handleTokenSelect" @close="closeTokenDropdown" />` at the end of the template.

**Multi-field token insertion:** Use a `refMap` object to map `activeTokenField` string to `$refs` name, then use `this.config[configKey]` for the current value and dynamic key in `updateConfig`.

**updateConfig signature varies by component:** SMSConfig/TaskConfig/NoticeConfig/StatusUpdateConfig use `updateConfig({ key: value })` (1-arg object). SendDocumentConfig uses `updateConfig(key, value)` (2-arg). Always match the existing component convention.

**payload.token is pre-formatted:** `handleTokenSelect(payload)` receives `payload.token` already formatted as `{{category.key}}` — do NOT wrap in additional `{{ }}`.

## SVG Progress Rings

Always include a `<text>` element inside SVG progress rings with class `.pd-ring-text` showing the ratio (e.g. "2/2"). A ring without a label is ambiguous — especially at 0% or 100% where the visual is indistinguishable from empty/full circles. Use `text-anchor="middle" dominant-baseline="central"` for centering, and apply `transform: rotate(90deg); transform-origin: center;` to counter the ring's -90deg rotation.

## Avatar Stacks with Limits

When displaying avatar stacks capped at N visible items (e.g. 2), always render a `+M` overflow badge (class `.pd-avatar-overflow`) when the actual count exceeds N. The badge uses the same `.pd-avatar-stack-item` base class plus the overflow modifier. Never silently truncate a list without indicating hidden items.

## Clickable Row Indicators

On fully clickable cards/rows (e.g., unit cards on property detail), use `.pd-tenant-arrow-btn` with `fa-chevron-right` as the navigation indicator. Do not use action-specific icons (phone, email) as decorative elements on clickable containers — they create false affordance via event bubbling. The old `.pd-tenant-phone-btn` class has been removed.

## Activity Timeline Pattern

The property detail page includes a full activity timeline (`properties/detail.html` + `properties-detail.css`). Key conventions:

- **Filter pills** use `.pd-timeline-filter` buttons with `data-filter` attributes; JS toggles `.active` on the pill and `.pd-timeline-hidden` on non-matching items
- **Channel badges** use `.pd-timeline-badge--{channel}` (email, sms, task, system)
- **Cursor-based pagination**: API returns `{ items, next_cursor, has_more }`; JS appends new items on "Load More"
- **Static anchor**: "Property Created" event is rendered server-side at the bottom, not from API data
- **DOM safety**: All dynamic content uses `createElement` + `textContent` (no innerHTML); each item wrapped in try/catch

## Before Creating New CSS

Check if existing component/page file already covers the need.

Dead CSS → `_archived/css/`
Dead templates → `_archived/templates/`
