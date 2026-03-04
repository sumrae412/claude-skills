---
name: defensive-ui-flows
description: Defensive patterns for UI flows — guard clauses with feedback, state flags with try-catch, overlay inline feedback, multi-step state reset. Use when writing or reviewing JavaScript, modals, drawers, forms, or multi-step flows.
---

# Defensive UI Flows

Apply these patterns when writing or reviewing UI code to prevent silent failures and stuck states.

## Auto-Update Rule

**When a UI bug is found** (during development, testing, or code review), update this skill immediately:

1. **Add a new pattern** — If the bug reveals a new failure mode, add a numbered section with BAD/GOOD examples and the fix
2. **Extend an existing pattern** — If the bug fits an existing section, add the specific case to that section
3. **Update the checklist** — Add a new checklist item if the pattern is general enough
4. **Document the source** — Add a brief "Learned from:" note with the bug context (file, symptom) so future readers understand the origin

This skill is a living document. Each bug fixed should make the next similar bug less likely.

## 1. Guard Clauses Must Give Feedback

Never `return` silently from a user-triggered function. Every early exit must show visible feedback.

```javascript
// BAD - Silent return, user has no idea why nothing happened
function handleSubmit() {
  if (_isSending) return;
  if (!validateForm()) return;
  if (rateLimitExceeded()) return;
  // ...
}

// GOOD - Every guard shows feedback
function handleSubmit() {
  if (_isSending) {
    showToast('Please wait, request in progress');
    return;
  }
  if (!validateForm()) {
    setInlineError('#formStatus', 'Please fix the errors above');
    return;
  }
  if (rateLimitExceeded()) {
    showToast('Too many requests. Try again in a minute.');
    return;
  }
  // ...
}
```

**Feedback channels:** toast, inline message (`#drawerStatus`, `#formStatus`), or `console.warn` for dev-only guards.

---

## 2. State Flags Need Try-Catch

When a boolean flag guards against re-entry (e.g. `_isSending`), wrap ALL code between flag-set and flag-clear in try-catch. An uncaught error leaves the flag stuck and permanently disables the feature.

```javascript
// BAD - Error leaves _isSending stuck true forever
async function handleSubmit() {
  _isSending = true;
  disableButton();
  await api.submit(data);  // If this throws, _isSending stays true
  _isSending = false;
  enableButton();
}

// GOOD - Flag always cleared, even on error
async function handleSubmit() {
  _isSending = true;
  disableButton();
  try {
    await api.submit(data);
    showSuccess();
  } catch (err) {
    showError(err.message);
  } finally {
    _isSending = false;
    enableButton();
  }
}
```

---

## 3. Overlay UIs Need Inline Feedback

Drawers, modals, and overlays must show validation errors *inside themselves* — not via external toast systems that may be obscured when the overlay is open.

```javascript
// BAD - Toast may appear behind overlay or be missed
function validateAndSubmit() {
  if (!email) {
    showToast('Email required');  // User might not see it
    return;
  }
}

// GOOD - Inline status element inside the overlay
function validateAndSubmit() {
  const statusEl = document.getElementById('drawerStatus');
  if (!email) {
    if (statusEl) {
      statusEl.textContent = 'Email is required';
      statusEl.classList.add('text-danger');
    }
    return;
  }
  statusEl.textContent = '';
  statusEl.classList.remove('text-danger');
}
```

**Pattern:** Use `#drawerStatus`, `#formStatus`, or similar as the primary feedback channel for overlays.

---

## 4. Multi-Step UI State Reset

When navigating between steps/panels in a multi-step flow, reset ALL transient UI state: button disabled states, loading indicators, inline error messages.

```javascript
// BAD - Old step state leaks into new step
function setPanel(panelId) {
  showPanelContent(panelId);
  // Forgot to reset: loading spinner, disabled buttons, error text
}

// GOOD - Full reset on step change
function setPanel(panelId) {
  resetTransientState();  // Clear loading, errors, disabled buttons
  showPanelContent(panelId);
}

function resetTransientState() {
  document.querySelectorAll('.btn-loading').forEach(b => b.classList.remove('btn-loading'));
  document.querySelectorAll('[disabled]').forEach(el => el.removeAttribute('disabled'));
  document.querySelectorAll('.inline-error').forEach(el => { el.textContent = ''; });
}
```

---

## 5. Null-Check DOM Elements

Always null-check before using DOM elements. Crashes on missing elements are hard to debug.

```javascript
// BAD
document.getElementById('submitBtn').addEventListener('click', handler);

// GOOD
const btn = document.getElementById('submitBtn');
if (btn) btn.addEventListener('click', handler);

// GOOD - Optional chaining
document.getElementById('submitBtn')?.addEventListener('click', handler);
```

---

## 6. Async API Catch Must Give Feedback

Promise `.catch()` handlers that swallow errors leave the user with no explanation when something fails.

```javascript
// BAD - Silent catch, user has no idea properties failed to load
loadProperties().catch(function () {});

// GOOD - Show feedback
loadProperties().catch(function () {
    showToast('Failed to load properties.', true);
});
```

**Learned from:** signing-drawer.js `loadProperties` — empty catch left property dropdowns empty with no user feedback.

---

## 7. Null-Check Before Using elements Object

When using a shared `elements` object (e.g. from `document.getElementById`), guard against missing elements before calling methods.

```javascript
// BAD - Crashes if pdfStatus element is missing
const setPdfStatus = (message) => {
    elements.pdfStatus.textContent = message;
};

// GOOD
const setPdfStatus = (message) => {
    if (!elements.pdfStatus) return;
    elements.pdfStatus.textContent = message;
};
```

**Learned from:** document-templates/wizard.js — setPdfStatus and showPdfError could throw if pdfStatus element missing.

---

## 8. Verify Design System Tokens Exist

When referencing CSS custom properties (`--ds-*` tokens), verify the token is actually defined in `_variables.css`. An undefined token with no fallback renders as **nothing** — the property silently disappears. This is especially dangerous for visual properties like `box-shadow`, `color`, and `border` where "nothing" means invisible UI.

```css
/* BAD - --ds-shadow-elevated doesn't exist, renders no shadow */
.slideout-panel {
    box-shadow: var(--ds-shadow-elevated);
}

/* GOOD - use a token that actually exists */
.slideout-panel {
    box-shadow: var(--ds-shadow-modal);
}
```

**How to check:** Search `_variables.css` for the token name before using it. If it's not there, use one that is — don't invent new token names.

**Learned from:** `_slideout-panel.css` — referenced `--ds-shadow-elevated` which was never defined. Panel rendered with no shadow until changed to `--ds-shadow-modal`.

---

## 9. Form Accept Attributes Must Match API Validation

When a file upload `<input>` has an `accept` attribute, the accepted types, the help text shown to users, and the backend validation must all agree. A mismatch means the user selects a file the browser allows but the server rejects — or the help text promises formats the input doesn't accept.

```html
<!-- BAD - accept says PDF only, help text says "PDF, Word, images" -->
<input type="file" accept="application/pdf,.pdf">
<div class="form-text">Accepted formats: PDF, Word, images (max 10MB)</div>

<!-- GOOD - accept, help text, and backend all match -->
<input type="file" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png">
<div class="form-text">Accepted formats: PDF, Word, images (max 10MB)</div>
```

**Check:** When writing a file upload, verify three things match: (1) `accept` attribute, (2) visible help text, (3) backend validation. If different pages accept different formats, each page's accept+text+validation must be internally consistent.

**Learned from:** `documents.html` — PDF-only accept attribute but tenant upload page accepted Word/images. Help text on one page didn't match the accept attribute on another.

---

## 10. API Fetches in Overlays Must Send Auth Headers

When a modal, drawer, or overlay loads data or previews from the backend, the fetch must include auth credentials. Iframes cannot send auth headers at all — use `fetch()` with blob URL or a backend proxy instead.

```javascript
// BAD - iframe src can't send auth, preview fails for protected files
previewFrame.src = '/api/documents/' + id + '/preview';

// BAD - fetch without credentials, 401 for authenticated endpoints
var resp = await fetch('/api/documents/' + id + '/content');

// GOOD - auth-aware fetch, render via blob URL
var resp = await fetch('/api/documents/' + id + '/preview', {
    credentials: 'same-origin',
    headers: { 'X-CSRFToken': csrfToken },
});
var blob = await resp.blob();
previewFrame.src = URL.createObjectURL(blob);
```

**Pattern:** Use an auth-aware fetch helper for all API calls in overlay components. Never assume iframes or plain `fetch()` will have the right auth context.

**Learned from:** `documents.html` — PDF preview failed because iframe can't send auth headers. Also: `signing-setup-core.js` — API calls in signing setup lacked auth headers.

---

## 11. Pre-Check Dependencies Before Destructive Actions

Before starting a multi-step operation that depends on an external service (Drive, Twilio, API), check the dependency is available FIRST and show a clear message if not. Don't let the user fill out a form only to fail at the final step.

```javascript
// BAD - user fills form, clicks Upload, THEN discovers Drive not connected
async function handleUpload(file) {
    var result = await fetch('/api/documents/upload', { body: file });
    if (result.error === 'no_drive') {
        showError('Google Drive not connected');  // Too late!
    }
}

// GOOD - check before showing the form
async function openUploadModal() {
    var status = await fetch('/api/drive-status',
        { credentials: 'same-origin' });
    var data = await status.json();
    if (!data.connected) {
        showDrawerStatus('Connect Google Drive to upload.', true);
        return;
    }
    showUploadForm();
}
```

**Learned from:** `documents.html` — upload flow didn't warn when Drive wasn't connected. Users filled out the entire form before discovering the dependency was missing.

---

## 12. Validate JS Syntax After Modifying Object Literals

Large JS object literals (Alpine.js components, Vue data functions, config objects) are fragile — a single duplicate `},` or missing comma silently breaks the entire component with no visible error in the IDE. Always run `node --check <file>` after adding or removing methods.

```javascript
// BAD - duplicate }, closes the return object early, kills the whole component
function tenantTable() {
    return {
        methodA() { ... },
        methodB() {
            // ...
        },
        },  // <-- DUPLICATE — SyntaxError, entire component dead

        methodC() { ... },
    };
}

// GOOD - verify syntax after every edit to object literals
// Run: node --check app/static/js/components/tenant-table.js
function tenantTable() {
    return {
        methodA() { ... },
        methodB() {
            // ...
        },

        methodC() { ... },
    };
}
```

**Why it's dangerous:** The syntax error prevents the function from parsing, so `Alpine.data('tenantTable', tenantTable)` never registers. The template shows `x-data="tenantTable()"` but Alpine logs `tenantTable is not defined` — which looks like a missing import, not a syntax error. The real cause is buried.

**Check:** After any edit to a `.js` file containing object literals, run `node --check <file>`. Zero output = valid syntax.

**Learned from:** `tenant-table.js` — a duplicate `},` introduced when adding a slideout panel feature silently killed the entire tenant list. The table showed "No tenants found" with no obvious error.

---

## 13. Static Assets Need Cache-Busting Version Parameters

`<script>` and `<link>` tags for app JS/CSS must include a `?v=` version parameter. Without it, browsers cache the old file indefinitely — even after a fix is deployed, users still get the broken version.

```html
<!-- BAD - no version param, browser serves stale cached file -->
<script defer src="/static/js/components/tenant-table.js"></script>

<!-- GOOD - version param forces cache refresh on deploy -->
<script defer src="/static/js/components/tenant-table.js?v=20260304"></script>
```

**When to update:** Bump the version parameter any time the file content changes. Ideally, automate this with a build step or content hash.

**Learned from:** `base.html` — loaded `tenant-table.js` without a version param. After fixing a syntax error, the browser kept serving the cached broken version. User reported "still not seeing tenants" despite the fix being deployed.

---

## 14. Vue Runtime Template Directives Must Be Structurally Adjacent

When using runtime-compiled Vue templates (CDN build, not SFC), `v-if`/`v-else-if`/`v-else` must be on immediately adjacent sibling elements with no intervening elements or whitespace nodes. A stray `v-else` with no adjacent `v-if` causes a template compilation crash — `Codegen node is missing for element/if/for node` — that kills the entire component.

```html
<!-- BAD - v-else has no adjacent v-if (there's a wrapper div between them) -->
<template>
  <div v-if="items.length > 0">
    <item-card v-for="item in items" :key="item.id" />
  </div>
  <div class="spacer"></div>  <!-- breaks the v-if/v-else chain -->
  <div v-else class="empty-state">No items</div>
</template>

<!-- GOOD - v-if and v-else are immediately adjacent siblings -->
<template>
  <div v-if="items.length > 0">
    <item-card v-for="item in items" :key="item.id" />
  </div>
  <div v-else class="empty-state">No items</div>
</template>
```

**Why it's dangerous:** The error message (`Codegen node is missing`) is cryptic and doesn't point to the offending `v-else`. The entire Vue app fails to mount, so all components on the page break — not just the one with the bad directive.

**Check:** After editing any runtime-compiled Vue template, verify every `v-else` / `v-else-if` has an immediately preceding sibling with `v-if` or `v-else-if`. Search for `v-else` and trace upward.

**Learned from:** VerticalTimeline component — an invalid `v-else` with no adjacent `v-if` caused a template compiler crash. The error was masked by cached JS, making it appear the fix hadn't deployed.

---

## 15. Service Worker Cache Must Be Bumped After Asset Changes

When the app uses a service worker for caching, fixing a JS/CSS bug is not enough — you must also bump the service worker's cache name. Otherwise the SW serves stale assets from its own cache, completely bypassing `?v=` query params and even server-side changes.

```javascript
// BAD - same cache name after fixing a bug, SW serves old assets
const CACHE_NAME = 'app-cache-v1';  // Never changes

// GOOD - bump cache name when assets change
const CACHE_NAME = 'app-cache-v2';  // Forces SW to re-fetch all assets
```

**Full cache-busting checklist after any asset fix:**
1. Bump `?v=` params on `<script>`/`<link>` tags (pattern #13)
2. Bump the service worker cache name constant
3. If using a CDN, purge the CDN cache or use content-hashed filenames

**Learned from:** After fixing a Vue template compiler error, the console still showed the old broken template. The service worker was serving its cached copy, ignoring the server-side fix entirely.

---

## 16. Use Production Builds of Frameworks in Production

Development builds of Vue, React, and other frameworks include extra warnings, runtime checks, and verbose error messages that add noise to the console and reduce performance. Always use production/minified CDN builds in production.

```html
<!-- BAD - development build, noisy console warnings in prod -->
<script src="https://unpkg.com/vue@3/dist/vue.global.js"></script>

<!-- GOOD - production build, smaller + no dev warnings -->
<script src="https://unpkg.com/vue@3/dist/vue.global.prod.js"></script>
```

**Check:** Search for framework CDN `<script>` tags. If the URL doesn't contain `.prod.` or `.min.`, it's a dev build.

**Learned from:** Vue "You are running a development build" warning in production — not fatal but noisy and can mask real errors in the console.

---

## 17. "Unexpected token" Usually Means Wrong Response Type

When the browser shows `Uncaught SyntaxError: Unexpected token '<'` or `Unexpected token '{'` for a `.js` file, the server is likely returning HTML (an error page) or JSON instead of JavaScript. Don't search for syntax errors in the JS file — check the server response first.

```javascript
// The error looks like a JS bug:
// Uncaught SyntaxError: Unexpected token '{' (at app.js:1:1)

// But the real problem is the server response:
// Request:  GET /static/js/app.js
// Response: {"error": "not found"}  ← JSON, not JS
// Or:       <!DOCTYPE html><html>... ← HTML error page
```

**Debugging steps:**
1. Open browser DevTools → Network tab
2. Find the failing `.js` request
3. Check the Response tab — is it actually JavaScript?
4. If it's HTML/JSON, fix the server route or static file path

**Learned from:** `Unexpected token '{'` error that appeared to be a JS syntax issue but was actually a server returning the wrong content type for a static asset request.

---

## 18. Button Elements Need Browser Default Resets

When a component uses mixed element types (`<a>`, `<button>`, `<div>`) sharing a common base CSS class, `<button>` elements render differently because browsers apply their own `font`, `color`, and `cursor` defaults to buttons — unlike `<a>` and `<div>` which inherit from parents. The fix is to add `font: inherit; color: inherit; cursor: pointer;` on the button variant class.

Also: **never redeclare base class properties in variant classes.** If `.base-card` already defines `border`, `padding`, `background`, `box-shadow`, don't repeat them in `.base-card-button`. The redundant declarations drift out of sync and create subtle visual differences.

```css
/* BAD - redeclares base class props, missing browser resets */
.stat-card { /* base */
    border: 1px solid var(--ds-border-color);
    border-radius: var(--ds-radius-xl);
    padding: var(--ds-space-5);
    background: var(--ds-color-surface);
    box-shadow: var(--ds-p-shadow-card);
}
.stat-card-button { /* variant for <button> */
    border: 1px solid var(--ds-border-color);   /* redundant */
    border-radius: var(--ds-radius-xl);          /* redundant */
    padding: var(--ds-space-5);                  /* redundant */
    background: var(--ds-color-surface);         /* redundant */
    box-shadow: var(--ds-p-shadow-card);         /* redundant */
    text-align: left;
    width: 100%;
    /* Missing: font: inherit; color: inherit; cursor: pointer; */
}

/* GOOD - variant only resets button-specific browser defaults */
.stat-card { /* base — all visual styles here */
    border: 1px solid var(--ds-border-color);
    border-radius: var(--ds-radius-xl);
    padding: var(--ds-space-5);
    background: var(--ds-color-surface);
    box-shadow: var(--ds-p-shadow-card);
}
.stat-card-button { /* variant — only button resets */
    font: inherit;
    color: inherit;
    text-align: left;
    width: 100%;
    cursor: pointer;
}
```

**Why it's dangerous:** The visual difference is subtle — slightly different font, color, or line-height — so it passes a quick glance but looks "off" to users. The redundant property declarations also mean any future change to the base class must be duplicated in the variant, or they drift apart.

**Check:** When a component mixes `<a>`, `<button>`, and `<div>` with a shared base class, verify the `<button>` variant includes `font: inherit; color: inherit;` and does NOT redeclare properties already on the base class.

**Learned from:** `home-dashboard.css` / `_stats.html` — Alerts stat card used `<button>` while the other three used `<a>`. The `.home-stat-card-button` class redeclared all base class properties but omitted `font: inherit` and `color: inherit`, causing the Alerts card to render with different text styling.

---

## Checklist for New UI Code

- [ ] Every guard clause shows feedback (toast, inline, or console)
- [ ] State flags wrapped in try-catch-finally
- [ ] Overlays use inline status elements for errors
- [ ] Multi-step flows reset transient state on panel change
- [ ] DOM elements null-checked before use
- [ ] Async catch handlers show user feedback (no empty catch)
- [ ] elements object members null-checked before use
- [ ] CSS `--ds-*` tokens verified to exist in `_variables.css`
- [ ] File upload `accept` attr matches help text and backend validation
- [ ] API fetches in overlays include auth credentials
- [ ] Dependency availability checked before multi-step operations
- [ ] JS files validated with `node --check` after editing object literals
- [ ] Static asset `<script>`/`<link>` tags include `?v=` cache-busting param
- [ ] Vue `v-else`/`v-else-if` has an immediately adjacent `v-if` sibling
- [ ] Service worker cache name bumped after asset changes
- [ ] Framework CDN uses production build (`.prod.js` or `.min.js`)
- [ ] "Unexpected token" errors checked via Network tab before debugging JS
- [ ] `<button>` variants include `font: inherit; color: inherit;` and don't redeclare base class props
