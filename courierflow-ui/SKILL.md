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

**Page headers in hybrid pages (Vue/Alpine + Jinja):**
When the page uses a JS framework that mounts in a sub-container, the `.page-header-standard` must be placed OUTSIDE the framework mount point so it renders immediately (no FOUC). The JS app then bridges to header elements via `getElementById`. See `builder.html` for the canonical example.

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

**Verification after deploy:** If CSS changes do not appear on the live site after deploy, first check that the `?v=` param was bumped, then check Railway build status (builds may be failing silently). Use `WebFetch` against the live URL to compare deployed CSS with the repo version.

## Logo & Favicon Asset Pipeline

Source: `app/static/images/courier_transparent.png` (RGBA).

Refresh procedure documented in MEMORY: `pattern_logo_and_favicon_asset_pipeline.md`. Key points:
- Generate variants `courier{,_transparent}{,-medium,-thumbnail}.{png,webp,jpeg}` so legacy filenames update together.
- macOS `sips` cannot output WebP — use `.venv/bin/python3` + Pillow.
- Bump `?v=YYYYMMDD[letter]` on every nav-logo `<img>` and favicon `<link>` in `base.html`. Landing pages reference assets without `?v=` and pick up new files automatically.
- Logo size lives in `app/static/css/components/_navigation.css` (`.cf-nav-logo`). Anchor percentage bumps to the original baseline, not the current size.

## Required favicon `<link>` tags in base.html

`base.html` MUST include the four favicon link tags (`favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`) immediately after `<link rel="manifest">`. `errors/404.html` previously had them while `base.html` did not — this was a latent SEO/UX bug fixed in PR #309. Verify presence on any new layout file that doesn't extend `base.html`.

## Service Worker

- **Network-first for CSS/JS** — Cache is offline fallback only
- Cache-first causes stale deploys that survive `?v=` bumps

## Landing Pages Exception

`landing/index.html`, `landing/features.html`, `landing/pricing.html`:
- Extend `landing_base.html`, NOT `base.html`
- Load their own CSS independently
- Design-system layers do not apply

## CSS Grid Patterns

- **Equal-width columns:** Always use `repeat(N, minmax(0, 1fr))` instead of `repeat(N, 1fr)`. Plain `1fr` allows content (long text, images) to inflate individual columns beyond their fair share. `minmax(0, 1fr)` constrains the minimum to 0, forcing truly equal widths.
- **Equal-height rows:** For grids that need uniform row heights (calendars, dashboards), set `grid-auto-rows: minmax(<min>, 1fr)` so rows do not size to content. Without this, rows with more content appear taller than empty rows.

## CopilotKit generative UI + page_context readables

Two conventions established in PRs #384 / #385 (2026-04-18):

1. **Generative UI cards** live in `app/static/src/components/generative-ui/` and are registered via `useGenerativeActions` hook. Adding a new card: build the component following the existing `TenantCard` / `ConfirmationCard` shape, export from `generative-ui/index.ts`, register a `useCopilotAction` handler in `useGenerativeActions.ts` (use `render` for display-only, `renderAndWaitForResponse` for human-in-the-loop).

2. **Page context readables** — to expose per-page state to the AI, override `{% block page_context %}` in your page template with a JSON object. Publish IDs and UX state (tab, filters, counts) — **never PII**. Backend actions fetch the actual data. See MEMORY `pattern_copilotkit_page_context_readables.md`.

## Before Creating New CSS

Check if existing component/page file already covers the need.

Dead CSS → `_archived/css/`
Dead templates → `_archived/templates/`
