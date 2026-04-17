---
name: defensive-ui-flows
description: Defensive patterns for UI flows — guard clauses with feedback, state flags with try-catch, overlay inline feedback, multi-step state reset. Use when writing or reviewing JavaScript, modals, drawers, forms, or multi-step flows.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# Defensive UI Flows

Apply these patterns when writing or reviewing UI code to prevent silent failures and stuck states.

## How to Use

1. Scan the **Checklist** below before committing any UI change — it's the 1-line index of every pattern.
2. For BAD/GOOD examples, failure-mode rationale, and code, load **references/patterns.md**.
3. Apply the **Auto-Update Rule** when a new UI bug surfaces.

## Auto-Update Rule

**When a UI bug is found** (during development, testing, or code review), update this skill immediately:

1. **Add a new pattern** to `references/patterns.md` — If the bug reveals a new failure mode, add a numbered section with BAD/GOOD examples and the fix
2. **Extend an existing pattern** — If the bug fits an existing section, add the specific case to that section
3. **Update the checklist** below — Add a new checklist item if the pattern is general enough
4. **Document the source** — Add a brief "Learned from:" note with the bug context (file, symptom) so future readers understand the origin

This skill is a living document. Each bug fixed should make the next similar bug less likely.

## Checklist for New UI Code

- [ ] Every guard clause shows feedback (toast, inline, or console)
- [ ] State flags wrapped in try-catch-finally
- [ ] Overlays use inline status elements for errors
- [ ] Multi-step flows reset transient state on panel change
- [ ] DOM elements null-checked before use
- [ ] Async catch handlers show user feedback (no empty catch)
- [ ] elements object members null-checked before use
- [ ] CSS design system tokens verified to exist in your CSS variables file before use
- [ ] File upload `accept` attr matches help text and backend validation
- [ ] API fetches in overlays include auth credentials
- [ ] Dependency availability checked before multi-step operations
- [ ] JS files validated with `node --check` after editing object literals
- [ ] Static asset `<script>`/`<link>` tags include `?v=` cache-busting param (grep ALL templates for the filename — one file may be loaded from multiple templates)
- [ ] Vue `v-else`/`v-else-if` has an immediately adjacent `v-if` sibling
- [ ] Service worker cache name bumped after asset changes (in your service worker)
- [ ] Framework CDN uses production build (`.prod.js` or `.min.js`)
- [ ] "Unexpected token" errors checked via Network tab before debugging JS
- [ ] `<button>` variants include ALL 5 resets (`display:block`, `appearance:none`, `font:inherit`, `color:inherit`, `cursor:pointer`)
- [ ] Cache-busting updated in BOTH `?v=` param AND service worker cache name (doing one without the other doesn't work)
- [ ] Primary data views show connection status and surface fetch errors visibly
- [ ] Navigation-guard flags (e.g., `redirecting`) only set INSIDE the branch that actually navigates
- [ ] Every async button handler has a double-submit guard (`setBtnLoading` or `disabled`); grep the file for consistency
- [ ] CSS classes used in HTML verified to exist in loaded stylesheets (`grep -r "\.class-name" app/static/css/`); prefer design system partials over raw HTML
- [ ] Floating bulk action bars use `border-radius: var(--ds-radius-full)` on BOTH the bar AND its buttons; include count badge, divider, action buttons, close button, and slide-in animation
- [ ] Card selection checkboxes use progressive disclosure (`opacity: 0` default, shown on hover/selected/selecting-mode); parent container gets a `selecting-mode` class when any card is selected
- [ ] Container clearing uses `while (el.firstChild) el.removeChild(el.firstChild)` — never assign empty HTML strings; DOM construction uses `createElement` + `textContent`, not string concatenation into HTML parser
- [ ] Service worker uses **network-first** strategy for CSS/JS (never cache-first for mutable assets)
- [ ] Before any frontend fix, verified which template the route actually renders (`grep -r '"/url"' app/routes/` and read the handler)
- [ ] New CSS files wrapped in the correct `@layer` (e.g., `design-system`, `components`, or `pages`); only reset/base stylesheets should be unlayered
- [ ] When migrating CSS class names between frameworks, confirmed the new classes have CSS definitions (framework installed OR definitions added to design system)
- [ ] Visibility toggling uses ONE mechanism per file (`style.display` OR `classList.add/remove('hidden')`, not both); `grep -c` both patterns to verify
- [ ] Vue apps with header/toolbar elements outside the mount point have explicit DOM bridging (`getElementById` + `$watch` in `mounted()`)
- [ ] Store setters that accept external data normalize legacy field formats to the current schema
- [ ] Modules with multiple `addEventListener` calls use an `AbortController` + `{ signal }` option for bulk cleanup on teardown/reinit; call `controller.abort()` before re-attaching
- [ ] Inline `<script>` blocks in templates that do NOT reference template variables are extracted to external `.js` files with `defer` for browser caching
- [ ] Dark mode overrides include explicit `color` for ALL text elements — never rely on light-mode inherited colors (invisible text on dark backgrounds)
- [ ] Shadow DOM UIs attach `stopPropagation` on the HOST element (not inside shadow root) to isolate composed keyboard/mouse events from the host page
- [ ] Keyboard event interceptors check for open autocomplete/mention dropdowns before suppressing keystrokes (scope dropdown selectors to the correct platform)
- [ ] Platform-specific DOM selectors are guarded by a platform check (don't query one platform's selectors inside another)
- [ ] Animations are functional (150-300ms, transforms/opacity only), not decorative; wrapped in `prefers-reduced-motion` media query; no `animation: infinite` on non-loading elements
- [ ] Cross-frame / cross-process actions use id-tagged request → `:ack` response with `{ok, error?}` — never paint success after a fire-and-forget `postMessage` or `chrome.runtime.sendMessage`
- [ ] Every failure return from a stateful callback clears the same module-level state the success return clears (grep `return { ok: false` or equivalent, audit each)

---

## Guardrails

- These patterns apply to any JavaScript UI with async operations, modals, or multi-step flows
- When reviewing, flag violations but preserve existing functionality
- Guard clauses and state flags are defensive — do not remove them to "simplify" code
