# Defensive UI Flows — Full Patterns

This is the complete pattern catalog. Each `## N.` section has BAD/GOOD examples, failure-mode rationale, and "Learned from:" notes tying patterns to real bugs. The thin `SKILL.md` one level up holds the 1-line checklist index and the auto-update rule.

---

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
// BAD - Silent catch, user has no idea data failed to load
loadData().catch(function () {});

// GOOD - Show feedback
loadData().catch(function () {
    showToast('Failed to load data.', true);
});
```

**Learned from a production incident:** an empty catch left a dropdown empty with no user feedback.

---

## 7. Null-Check Before Using elements Object

When using a shared `elements` object (e.g. from `document.getElementById`), guard against missing elements before calling methods.

```javascript
// BAD - Crashes if statusEl element is missing
const setStatus = (message) => {
    elements.statusEl.textContent = message;
};

// GOOD
const setStatus = (message) => {
    if (!elements.statusEl) return;
    elements.statusEl.textContent = message;
};
```

**Learned from a production incident:** status and error setter functions in your wizard/stepper component could throw if a DOM element was missing.

---

## 8. Verify Design System Tokens Exist

When referencing CSS custom properties (e.g. `--ds-*` tokens), verify the token is actually defined in your CSS variables file. An undefined token with no fallback renders as **nothing** — the property silently disappears. This is especially dangerous for visual properties like `box-shadow`, `color`, and `border` where "nothing" means invisible UI.

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

**How to check:** Search your CSS variables file for the token name before using it. If it's not there, use one that is — don't invent new token names.

**Learned from a production incident:** your panel styles referenced a shadow token that was never defined. The panel rendered with no shadow until the token was corrected.

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

**Learned from a production incident:** a PDF preview failed because an iframe can't send auth headers. API calls in your drawer component also lacked auth headers.

---

## 11. Pre-Check Dependencies Before Destructive Actions

Before starting a multi-step operation that depends on an external service (cloud storage, SMS provider, third-party API), check the dependency is available FIRST and show a clear message if not. Don't let the user fill out a form only to fail at the final step.

```javascript
// BAD - user fills form, clicks Upload, THEN discovers dependency not connected
async function handleUpload(file) {
    var result = await fetch('/api/upload', { body: file });
    if (result.error === 'no_storage') {
        showError('Storage not connected');  // Too late!
    }
}

// GOOD - check before showing the form
async function openUploadModal() {
    var status = await fetch('/api/service-status',
        { credentials: 'same-origin' });
    var data = await status.json();
    if (!data.connected) {
        showDrawerStatus('Connect your storage provider to upload.', true);
        return;
    }
    showUploadForm();
}
```

**Learned from a production incident:** an upload flow didn't warn when an external storage provider wasn't connected. Users filled out the entire form before discovering the dependency was missing.

---

## 12. Validate JS Syntax After Modifying Object Literals

Large JS object literals (Alpine.js components, Vue data functions, config objects) are fragile — a single duplicate `},` or missing comma silently breaks the entire component with no visible error in the IDE. Always run `node --check <file>` after adding or removing methods.

```javascript
// BAD - duplicate }, closes the return object early, kills the whole component
function myComponent() {
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
// Run: node --check app/static/js/components/my-component.js
function myComponent() {
    return {
        methodA() { ... },
        methodB() {
            // ...
        },

        methodC() { ... },
    };
}
```

**Why it's dangerous:** The syntax error prevents the function from parsing, so `Alpine.data('myComponent', myComponent)` never registers. The template shows `x-data="myComponent()"` but Alpine logs `myComponent is not defined` — which looks like a missing import, not a syntax error. The real cause is buried.

**Check:** After any edit to a `.js` file containing object literals, run `node --check <file>`. Zero output = valid syntax.

**Learned from a production incident:** your data table component had a duplicate `},` introduced when adding a slideout panel feature, which silently killed the entire table. The table showed "No results found" with no obvious error.

---

## 13. Static Assets Need Cache-Busting Version Parameters

`<script>` and `<link>` tags for app JS/CSS must include a `?v=` version parameter. Without it, browsers cache the old file indefinitely — even after a fix is deployed, users still get the broken version.

**If your cloud platform sets `max-age=31536000` (1 year) on static files**, a missing or stale `?v=` param causes the browser to serve cached assets for up to **one year** — hard refresh alone won't fix it because CDN/proxy caches also honor the header.

```html
<!-- BAD - no version param, browser serves stale cached file -->
<script defer src="/static/js/components/my-component.js"></script>

<!-- BAD - version param exists but wasn't bumped after file changed -->
<link href="/static/css/pages/feature.css?v=3" rel="stylesheet">

<!-- GOOD - version param bumped to today's date after file change -->
<link href="/static/css/pages/feature.css?v=20260304a" rel="stylesheet">
<script defer src="/static/js/components/my-component.js?v=20260304a"></script>
```

**When to update:** Bump the version parameter **every time** the file content changes. A CSS or JS file can be loaded from multiple templates — you must update ALL of them.

**Workflow after modifying a static file:**
1. `grep -r "filename.css" app/templates/` — find every template that loads it
2. Bump `?v=` to today's date + letter suffix (e.g., `?v=20260305a`)
3. If no `?v=` exists, add one
4. Commit the version bumps alongside the CSS/JS changes (or immediately after)

**Learned from a production incident:** your base template loaded a component JS file without a version param. After fixing a syntax error, the browser kept serving the cached broken version. Users reported "still not seeing data" despite the fix being deployed. Also: CSS files were updated across multiple commits but version strings were never bumped — changes deployed successfully but no visual changes appeared due to long-lived cache headers.

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

**Learned from a production incident:** an invalid `v-else` with no adjacent `v-if` caused a template compiler crash. The error was masked by cached JS, making it appear the fix hadn't deployed.

---

## 15. Service Worker Cache Must Be Bumped After Asset Changes + Network-First for Mutable Assets

When the app uses a service worker for caching, fixing a JS/CSS bug is not enough — you must also bump the service worker's cache name. Otherwise the SW serves stale assets from its own cache, completely bypassing `?v=` query params and even server-side changes.

**Additionally, the SW caching strategy for CSS/JS must be network-first, not cache-first.** Cache-first for static assets causes stale deploys that survive cache-buster version bumps because the old SW intercepts requests before the new SW activates.

```javascript
// BAD - same cache name after fixing a bug, SW serves old assets
const CACHE_NAME = 'app-cache-v1';  // Never changes

// GOOD - bump cache name when assets change
const CACHE_NAME = 'app-cache-v2';  // Forces SW to re-fetch all assets

// BAD - cache-first for CSS/JS, stale deploys survive ?v= bumps
async function handleStaticAsset(request) {
    const cached = await caches.match(request);
    if (cached) return cached; // Serves stale CSS forever
    return fetch(request);
}

// GOOD - network-first, cache is offline fallback only
async function handleStaticAsset(request) {
    try {
        const resp = await fetch(request);
        if (resp.ok) { /* cache for offline */ }
        return resp;
    } catch {
        return caches.match(request); // Offline fallback
    }
}
```

**Full cache-busting checklist after any asset fix:**
1. Bump `?v=` params on `<script>`/`<link>` tags (pattern #13)
2. Bump the service worker cache name constant in your service worker
3. If using a CDN, purge the CDN cache or use content-hashed filenames
4. Verify the SW uses **network-first** for CSS/JS (not cache-first)

**Learned from a production incident:** after fixing a Vue template compiler error, the console still showed the old broken template. Your service worker was serving its cached copy, ignoring the server-side fix entirely. Even bumping the cache version didn't help because the old SW served old assets before the new SW activated. Switching to network-first was the definitive fix.

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

---

## 18. Button Elements Need Browser Default Resets

When a component uses mixed element types (`<a>`, `<button>`, `<div>`) sharing a common base CSS class, `<button>` elements render differently because browsers apply their own defaults. You need ALL of these resets — missing even one causes a visible difference:

| Reset | Why |
|-------|-----|
| `display: block` | Buttons default to `inline-block`; `<a>` with `display: block` fills the grid cell |
| `appearance: none` | Strips native browser button chrome (bevels, gradients) |
| `font: inherit` | Buttons get a system font instead of inheriting from parent |
| `color: inherit` | Buttons get `buttontext` color instead of inheriting |
| `cursor: pointer` | Buttons don't show pointer cursor by default |

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
    /* Missing: display, appearance, font, color, cursor resets */
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
    display: block;
    appearance: none;
    font: inherit;
    color: inherit;
    text-align: left;
    width: 100%;
    cursor: pointer;
}
```

**Why it's dangerous:** Each missing reset causes a *different* subtle issue. `font: inherit` alone fixes text but the card still looks wrong because `display: inline-block` breaks grid sizing. This leads to iterative "it's still broken" cycles where you fix one property at a time. Apply ALL resets from the table above in one pass.

**Check:** When a component mixes `<a>`, `<button>`, and `<div>` with a shared base class, verify the `<button>` variant includes ALL five resets (`display`, `appearance`, `font`, `color`, `cursor`) and does NOT redeclare properties already on the base class.

**Learned from a production incident:** your stat card component — one card used `<button>` while others used `<a>`. First fix attempt only added `font: inherit; color: inherit;` — the card still looked wrong because `display: block` and `appearance: none` were also needed. Required two rounds of fixes to get right.

---

## 19. Primary Views Must Surface Data Source Status

When a page becomes the primary UI for a data domain, it must show connection status and surface remote-fetch errors. A dashboard that silently shows stale/sparse data with no explanation violates "Fail Visible."

```html
<!-- BAD - shows "1 event" with no indication data is from sparse cache -->
<div class="upcoming-events">
  <h3>Upcoming Events</h3>
  <!-- renders whatever's in local DB -->
</div>

<!-- GOOD - connection status visible, stale data warned -->
<div class="upcoming-events">
  <h3>Upcoming Events</h3>
  <div class="connection-status">
    {% if not service_connected %}
      <span class="badge bg-warning">Data service not connected</span>
    {% elif fetch_error %}
      <span class="badge bg-danger">Could not refresh — showing cached data</span>
    {% endif %}
  </div>
  <!-- renders events -->
</div>
```

**Check:** If the page is the only way to see certain data, ask: "Does the user know where the data came from and whether it's current?" If not, add a visible status indicator.

**Learned from a production incident:** a dashboard became the only view after a route redirected there, but showed sparse cached events with no indication that the remote fetch was failing or that the data service wasn't connected.

---

## 20. Navigation Guards Must Be Gated on the Navigation Condition

When a boolean flag blocks UI reset to prevent flicker during navigation (e.g., `redirecting = true` makes `resetModal()` return early), that flag must ONLY be set after confirming the navigation will actually happen. Setting it optimistically — before checking the response has the data needed to navigate — creates a permanent stuck state.

```javascript
// BAD - sets redirecting before checking instance.id exists
// If server returns 200 with no id, modal is permanently locked
if (response.ok) {
    const instance = await response.json();
    state.redirecting = true;  // Reset guard activated
    showSuccess();
    modal.hide();
    if (instance?.id) {
        setTimeout(() => { window.location.href = `/item/${instance.id}`; }, 1200);
    }
    // No else — redirecting stays true, resetModal() is blocked forever
}

// GOOD - only set redirecting when navigation is confirmed
if (response.ok) {
    const instance = await response.json();
    if (instance?.id) {
        state.redirecting = true;  // Safe — we WILL navigate
        showSuccess();
        modal.hide();
        setTimeout(() => { window.location.href = `/item/${instance.id}`; }, 1200);
    } else {
        showWarning('Created but no ID returned.');
        setBtnLoading(btn, false);  // Re-enable UI
    }
}
```

**Rule of thumb:** If a flag prevents cleanup/reset, it must only be set inside the branch that makes cleanup unnecessary (i.e., the branch that navigates away).

**Learned from a production incident:** your detail view's `submitWorkflowStart()` — `redirecting = true` was set before an `if (instance?.id)` check. A 200 response without an ID permanently locked the modal.

---

## 21. Async Form Handlers Need Double-Submit Guards

Every async function triggered by a button click must disable the button at the start of the operation and re-enable it on failure. Use whatever loading-state mechanism the codebase already provides (e.g., `setBtnLoading`). Inconsistency within the same file is a code smell — if 3 out of 4 handlers in a file use a guard, the 4th is a bug.

```javascript
// BAD - no loading guard, user can click 5 times and create 5 instances
async function submitWorkflowStart() {
    const payload = { template_id: selectedId };
    const response = await fetch('/api/instances', {
        method: 'POST', body: JSON.stringify(payload)
    });
    // ...
}

// GOOD - setBtnLoading disables button, re-enabled on all failure paths
async function submitWorkflowStart() {
    const btn = document.getElementById('submitBtn');
    setBtnLoading(btn, true);
    try {
        const response = await fetch('/api/instances', {
            method: 'POST', body: JSON.stringify(payload)
        });
        if (response.ok) {
            // success path — navigating away, no need to re-enable
        } else {
            showError('Failed to start.');
            setBtnLoading(btn, false);
        }
    } catch (err) {
        showError('Network error.');
        setBtnLoading(btn, false);
    }
}
```

**Consistency check:** When reviewing a file, grep for the loading-state function name. If some handlers use it and others don't, the ones without it are bugs.

**Learned from a production incident:** a submit handler had no `setBtnLoading()` call despite other handlers in the same file using it. A slow network could result in duplicate records.

---

## 22. Verify CSS Classes Exist Before Using Them in HTML

When adding a CSS class to an HTML element, verify the class is actually defined in a CSS file that gets loaded on that page. An undefined class silently renders as browser defaults — no error in the console, no build failure, just broken styling that's hard to trace.

The inverse is equally dangerous: CSS selectors targeting classes that no longer exist in HTML are dead code that masks the real problem.

```html
<!-- BAD - .filter-pill class used in HTML but has NO CSS definition anywhere -->
<button class="filter-pill active" onclick="filterCategory('all')">All</button>

<!-- Meanwhile in CSS — styles exist for a DIFFERENT class nobody uses -->
<style>
.category-filters .wf-btn-ghost { /* orphaned CSS, never rendered */ }
</style>

<!-- GOOD - class matches a real CSS definition in a loaded stylesheet -->
<button class="filter-bar__pill active" onclick="filterCategory('all')">All</button>
```

**Why it's dangerous:** The element renders with browser defaults (no padding, no border-radius, system font). It *looks* like a styling bug, so you might waste time adjusting tokens or specificity — but the real problem is the class name doesn't exist. Grep for the class name in CSS and you'll find zero matches.

**Check (two-way):**
1. **HTML → CSS:** `grep -r "\.class-name" app/static/css/` — if zero results, the class is undefined
2. **CSS → HTML:** `grep -r "class-name" app/templates/` — if zero results, the CSS selector is dead code

**Prevention:** Use design system partials/macros instead of writing raw HTML. Partials guarantee the HTML classes match the component CSS.

**Learned from a production incident:** your list view template used a filter button class that had no CSS selector in any stylesheet. The feature manager styles defined styles for a different class that the HTML never used. Both sides of the mismatch went undetected because neither caused an error — just unstyled buttons.

**Migration variant:** When migrating CSS class names from one framework to another (e.g., Bootstrap `d-none` to Tailwind `hidden`), the new class names must have CSS definitions available on the page. If the target framework is not installed (no CDN link, no build tool, no PostCSS config), you must add the class definitions manually to the design system. A class rename without a backing definition is the same as using a class that doesn't exist — it silently renders as nothing.

```html
<!-- BAD - renamed to Tailwind classes but Tailwind CSS is not installed -->
<div class="hidden">...</div>  <!-- .hidden has no definition, div is visible -->

<!-- GOOD - added .hidden definition to design system -->
/* In your design system CSS */
.hidden { display: none !important; }
```

**Check:** When renaming utility classes across templates, run `grep -r "\.new-class-name" app/static/css/` to confirm the new class has a CSS definition. If the framework that defines the class is not installed, add the definitions to the design system.

**Learned from a production incident:** migrated 91 template files from Bootstrap visibility classes to a different utility framework, but the target framework CSS was never installed. All renamed classes rendered as nothing.

---

## 23. Floating Bulk Action Bars Must Use Full Border-Radius

When building a floating action bar for bulk operations (multi-select on cards/rows), the bar AND its buttons must use `border-radius: var(--ds-radius-full)` for fully rounded pill shapes. A rectangular bar or square-cornered buttons look inconsistent with the design system's rounded filter pills and badges.

```css
/* BAD - rectangular bar with square buttons */
.bulk-bar {
    border-radius: 8px;       /* too angular */
}
.bulk-bar button {
    border-radius: 4px;       /* square corners */
}

/* GOOD - fully rounded bar and pill-shaped buttons */
.bulk-bar {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    border-radius: var(--ds-radius-full);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15),
                0 2px 8px rgba(0, 0, 0, 0.08);
}
.bulk-bar button {
    border-radius: var(--ds-radius-full);
}
```

**Required elements:** count badge (accent color, fully rounded), divider, action buttons (fully rounded), close button (fully rounded).

**Animation:** Use slide-in from bottom on show (`translateY(12px) → 0`).

**Mobile:** Switch to full-width with `left: 12px; right: 12px; transform: none;` and `border-radius: var(--ds-radius-xl)`.

---

## 24. Card Selection Checkboxes Need Progressive Disclosure

When adding multi-select to card grids, checkboxes must be hidden by default and revealed progressively: on card hover, when the card is selected, or when any card is selected (selecting mode). A permanently visible checkbox clutters the UI and breaks the "Content over Chrome" principle.

```css
/* BAD - checkbox always visible, clutters every card */
.card .select-checkbox {
    opacity: 1;
}

/* GOOD - progressive disclosure: hover, selected, or selecting mode */
.card .select-checkbox {
    position: absolute;
    top: var(--ds-space-3);
    right: var(--ds-space-3);
    opacity: 0;
    transition: opacity var(--ds-transition-fast);
}
.card:hover .select-checkbox,
.card.is-selected .select-checkbox,
.selecting-mode .card .select-checkbox {
    opacity: 1;
}
```

**Pattern:** Add a `selecting-mode` class to the parent container when any checkbox is checked. This reveals all checkboxes so the user can continue selecting without hovering each card individually.

**Required:** `position: relative` on the card element so the checkbox positions correctly. Cards need `data-*` attributes for JS to find them. The checkbox `change` event (not `click`) should drive selection state.

---

## 25. Clear Container Content Safely — No innerHTML

When clearing a container to rebuild its content (e.g., refreshing a card grid from API data), use the DOM loop `while (el.firstChild) el.removeChild(el.firstChild)` instead of assigning an empty string to the element's HTML content. The assignment triggers the HTML parser, creates an XSS surface, and may trigger security lint hooks. The loop approach is safe, explicit, and avoids parser invocation.

```javascript
// BAD - triggers HTML parser, XSS risk, security hook flags
grid.innerH‍TML = '';

// GOOD - safe, explicit, no parser invocation
while (grid.firstChild) grid.removeChild(grid.firstChild);
```

**Same rule for building content:** When constructing DOM from API data, use `document.createElement()` + `textContent` for text, not string concatenation into an HTML parser. User-controlled strings (names, descriptions) must never enter a parser.

```javascript
// GOOD - textContent auto-escapes, createElement is safe
var h6 = document.createElement('h6');
h6.textContent = item.name;
card.appendChild(h6);
```

**Learned from a production incident:** your list view's `loadItems()` — the original implementation assigned an empty string to grid HTML to clear before re-rendering. A security hook caught this. Fixed to the safe DOM loop.

---

## 26. Verify Route-to-Template Mapping Before Frontend Changes

Before editing a template or its CSS to fix a visual bug on a page, **verify which template the route actually renders.** Route names, template filenames, and URL paths often do not match. Editing the wrong template means your fix deploys but has zero effect on the page.

```python
# routes.py
@router.get("/home")
async def home_page(...):
    return templates.TemplateResponse("dashboard.html", ...)
    #                                  ^^^^^^^^^^^^^^
    #  /home renders dashboard.html, NOT home.html!
```

**Check before any frontend fix:**
1. Find the route handler: `grep -r '"/the-url"' app/routes/`
2. Read the handler to see which template it renders
3. Check what CSS/partials that template includes
4. Only then edit the correct template and CSS files

**Learned from a production incident:** `/home` rendered `dashboard.html`, not `home.html`. Multiple sessions edited the wrong template's CSS and cache busters while the actual page used a different template. Fixes appeared deployed but had no visual effect.

---

## 27. Unlayered CSS Silently Overrides the Entire Design System

In a `@layer`-based cascade, unlayered CSS always beats layered CSS regardless of specificity or source order. A file loaded without `@layer` wrapping can silently override every design system token and component style.

```css
/* BAD - your utility CSS file loaded last, unlayered, overrides everything */
.btn { border-radius: 20px; }  /* beats @layer components .btn */

/* GOOD - wrap in the correct layer or remove */
@layer components {
  .btn { border-radius: var(--ds-p-radius-btn); }
}
```

**Check:** When a design system token appears to be "ignored," check if an unlayered stylesheet is loaded after the layered ones. `grep -L '@layer' app/static/css/*.css` finds unlayered files.

**Learned from a production incident:** your utility CSS file (unlayered, loaded last in your base template) was overriding the entire design system's buttons, cards, and typography. Removing it restored all design tokens.

---

## 28. Cross-Reference CSS With Templates Before Declaring Dead

Before archiving a CSS file, verify it is truly unused by cross-referencing three sources: (1) template `<link>` tags, (2) `@import` in other CSS files, (3) class name usage in templates and JS. Automated "dead CSS" tools can miss dynamically-generated class names and partial matches.

```bash
# Check all three sources before archiving
grep -r "filename.css" app/templates/ app/static/css/
grep -r "class-from-file" app/templates/ app/static/js/
```

**Gotcha:** Cache-buster normalization across many files can miss individual templates. Always do a manual verification pass after bulk changes.

---

## 29. Use One Visibility Mechanism Per File

Within a single JS file, pick one approach for showing/hiding elements and use it consistently: either `style.display` or `classList.add/remove('hidden')`. Mixing both creates bugs when one function hides via `style.display = 'none'` and another tries to show by removing the `hidden` class — the element stays hidden because the inline `display: none` still wins.

```javascript
// BAD - mixed mechanisms in same file
function hidePanel() {
    panel.style.display = 'none';  // sets inline style
}
function showPanel() {
    panel.classList.remove('hidden');  // removes class, but inline style still hides it
}

// GOOD - one mechanism throughout the file
function hidePanel() {
    panel.classList.add('hidden');
}
function showPanel() {
    panel.classList.remove('hidden');
}
```

**Check:** `grep -c 'style\.display' <file>` and `grep -c "classList.*'hidden'" <file>`. If both return non-zero counts, the file has mixed mechanisms. Pick one and migrate the other.

**Learned from a production incident:** your calendar component had dozens of `style.display` usages alongside an even larger number of `classList` usages in the same file. A code review caught multiple instances that should have been `classList` to match the file's dominant pattern.

---

## 30. Vue Apps With External DOM Elements Need Explicit Bridging

When a Vue app mounts inside a container but header/toolbar elements live outside the mount point (e.g., page-level headers rendered server-side), the Vue app must bridge to those elements explicitly using `getElementById` + `addEventListener` in `mounted()`, plus `$watch` to sync reactive state back to the DOM.

```javascript
// BAD - header buttons outside #vue-app have no connection to Vue state
// <div class="page-header">  <!-- outside Vue -->
//   <button id="undo-btn">Undo</button>
// </div>
// <div id="vue-app">...</div>

// GOOD - wire external DOM in mounted(), watch state for sync
mounted() {
    const undoBtn = document.getElementById('undo-btn');
    if (undoBtn) undoBtn.addEventListener('click', () => this.undo());

    this.$watch(
        () => this.store.state.undoStack.length,
        () => { if (undoBtn) undoBtn.disabled = !this.canUndo; }
    );
}
```

**Key rules:**
- Null-check every external element (pattern #5)
- Use `$watch` for state-to-DOM sync (don't poll or use timers)
- Keep external DOM manipulation in dedicated methods (`wireHeaderButtons`, `updateHeaderStatus`)

**Learned from a production incident:** your builder component — the page header (title, status badge, undo/redo, publish button) lives outside the Vue mount point in your builder template. Required explicit DOM bridging + `$watch` hooks to keep the header in sync with Vue state.

---

## 31. Store Setters Must Normalize Legacy Data Formats

When a store's `setTemplate()` or `loadData()` accepts data from an API or template injection, it must normalize legacy field formats to the current schema. Otherwise, components that depend on the new schema will render incorrectly because old data only has the legacy fields.

```javascript
// BAD - trusts incoming data shape, legacy steps break timeline grouping
setTemplate(template) {
    state.steps = template.steps || [];
}

// GOOD - normalize legacy fields to current schema
setTemplate(template) {
    state.steps = (template.steps || []).map(step => {
        if (!step.timing_config) {
            step.timing_config = {
                relative_to: 'PREVIOUS_STEP',
                offset_days: step.relative_days ?? step.delay_days ?? 0,
                offset_hours: step.delay_hours || 0,
            };
        }
        if (!step.id) {
            step.id = 'step-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        }
        return step;
    });
}
```

**Learned from a production incident:** your state store's `setTemplate()` — steps loaded from older records had legacy timing fields but no current schema equivalent. The timeline grouped all steps at the default value because the rendering logic only read the new schema field.

---

## 32. Template Attribute Names Must Match Model Columns

Server-rendered templates accessing model attributes (e.g., `member.is_primary`) silently render as falsy/empty when the attribute does not exist on the model, rather than raising an error. This means a wrong column name silently breaks conditional rendering.

```html
<!-- BAD — wrong_column doesn't exist on your domain model; condition always false -->
{% if member.wrong_column %}
<i class="fas fa-star" title="Primary Contact"></i>
{% endif %}

<!-- GOOD — matches the actual column name -->
{% if member.is_primary_contact %}
<i class="fas fa-star" title="Primary Contact"></i>
{% endif %}
```

**Check:** When referencing model attributes in templates, verify the attribute name against the model class. Do not copy attribute names from other templates without checking.

**Learned from a production incident:** a model column name mismatch silently broke conditional badge rendering across multiple templates. The shorter alias name matched nothing in ORM filters at query execution time.

---

## 33. Shadow DOM Event Isolation Must Be on the Host Element

When building UI inside a Shadow DOM (open or closed), keyboard and mouse events still leak to the host page because `composed: true` events (keydown, click, input, etc.) retarget across the shadow boundary. Calling `stopPropagation()` inside the shadow root does NOT prevent the host page from receiving these events.

```javascript
// BAD — stopPropagation inside shadow root has no effect on composed events
const shadow = host.attachShadow({ mode: "closed" });
const drawer = shadow.querySelector(".drawer");
drawer.addEventListener("keydown", (e) => e.stopPropagation());  // Host page still gets the event

// GOOD — stopPropagation on the host element in the main DOM tree
document.body.appendChild(host);
for (const evt of ["mousedown", "click", "keydown", "keypress", "keyup", "input"]) {
  host.addEventListener(evt, (e) => e.stopPropagation());
}
```

---

## 34. Rich Text Editor Text Replacement Needs Multi-Tier Fallback

`document.execCommand("insertText")` fails silently in modern rich text editors (Quill, Draft.js, ProseMirror). The command may return `true` but the editor's internal model is not updated, causing the original text to persist. Raw DOM manipulation (`removeChild` + `appendChild`) is worse — it desyncs the framework's model entirely.

```javascript
// BAD - execCommand fails silently in Quill, sends original text
document.execCommand("selectAll", false, null);
document.execCommand("insertText", false, newText);

// BAD - raw DOM manipulation desyncs the editor's internal model
while (el.firstChild) el.removeChild(el.firstChild);
el.appendChild(document.createElement("p"));

// GOOD - multi-tier fallback with verification
// Strategy 1: select + delete + insert (stays in undo stack)
const sel = window.getSelection();
const range = document.createRange();
range.selectNodeContents(el);
sel.removeAllRanges();
sel.addRange(range);
document.execCommand("delete", false, null);
document.execCommand("insertText", false, text);

// Verify (normalize whitespace for <p> wrapping)
const normalize = s => s.replace(/\s+/g, " ").trim();
if (normalize(el.innerText) !== normalize(text)) {
  // Strategy 2: framework API
  const quill = el.__quill;
  if (quill) { quill.setText(text); }
  else {
    // Strategy 3: clipboard paste emulation
    const dt = new DataTransfer();
    dt.setData("text/plain", text);
    el.dispatchEvent(new ClipboardEvent("paste", {
      clipboardData: dt, bubbles: true, cancelable: true
    }));
  }
}
```

**Key insight:** Always verify the replacement actually worked. `innerText` comparison must normalize whitespace because rich editors wrap lines in block elements that add newlines.

---

## 35. Shadow DOM Event Detection Must Use composedPath()

When detecting whether a keyboard/mouse event originated inside a Shadow DOM component, `e.target` is unreliable — closed Shadow DOMs retarget it to the host element. Use `e.composedPath()` which crosses shadow boundaries regardless of mode.

```javascript
// BAD - fragile, only works for closed shadow DOM
function isFromOverlay(e) {
  return e.target === host;
}

// BAD - guard condition breaks for open shadow DOMs
function isFromOverlay(e) {
  if (e.composedPath && e.composedPath()[0] !== e.target) {
    return e.composedPath().some(n => n === host);
  }
  return e.target === host;
}

// GOOD - works for both open and closed shadow DOMs
function isFromOverlay(e) {
  if (e.target === host) return true;
  if (e.composedPath) {
    return e.composedPath().some(n => n === host);
  }
  return false;
}
```

---

## 36. CSS Animations Must Be Functional, Not Decorative

Animations that run on page load, loop continuously, or animate layout properties cause performance issues, accessibility problems, and visual noise. Adapted from Anthropic's [Prompting for Frontend Aesthetics](https://platform.claude.com/cookbook/coding-prompting-for-frontend-aesthetics) cookbook.

```css
/* BAD - Decorative animation on a static element, loops forever */
.card {
  animation: pulse 2s infinite;
}

/* BAD - Animates layout property (triggers reflow) */
.sidebar {
  transition: width 300ms ease;
}

/* BAD - Multiple scattered micro-interactions that add visual noise */
.btn { transition: all 0.3s; }
.card { transition: all 0.3s; }
.badge { transition: all 0.3s; }
.icon { transition: all 0.3s; }

/* GOOD - Single functional transition on interaction (150-300ms) */
.card {
  transition: border-color 150ms ease;
}
.card:hover {
  border-color: var(--ds-border-hover);
}

/* GOOD - Slide-over panel entrance (one orchestrated moment) */
.slide-over {
  transform: translateX(100%);
  transition: transform 200ms ease-out;
}
.slide-over.open {
  transform: translateX(0);
}

/* GOOD - Staggered reveal on page load (animation-delay, not scattered) */
.card:nth-child(1) { animation-delay: 0ms; }
.card:nth-child(2) { animation-delay: 50ms; }
.card:nth-child(3) { animation-delay: 100ms; }
```

**Rules:**
- **150-300ms** for interactions (hover, focus, open/close). Never >500ms.
- **Animate transforms and opacity only** — never animate `width`, `height`, `top`, `left`, or `margin` (triggers layout reflow)
- **One orchestrated moment per page** beats many scattered animations
- **`prefers-reduced-motion`**: Wrap all animations in `@media (prefers-reduced-motion: no-preference) { }` or provide instant fallbacks
- **Never `animation: infinite`** on non-loading elements — only spinners/progress indicators should loop

**Learned from:** Claude Cookbook "Prompting for Frontend Aesthetics" — AI-generated code defaults to scattered `transition: all 0.3s` on everything. One well-orchestrated animation creates more impact than twenty generic transitions.

---

## 37. Optimistic UI Across Message Boundaries Needs Explicit Ack

Any cross-frame, cross-process, or cross-service-worker UI that paints "success" before the action has been acknowledged will silently lie to the user if the action fails. `window.postMessage`, `chrome.runtime.sendMessage` without callback, fire-and-forget `BroadcastChannel` — all fall into this trap. The sender posts, the receiver hasn't run yet, and the success confirmation already painted.

```javascript
// BAD — fire and forget, paint success immediately
useSuggestionBtn.addEventListener("click", () => {
  window.parent.postMessage({ type: "use_suggestion", text }, "*");
  showSent("Applied!");  // parent hasn't even received the message
});

// GOOD — each action carries an id, receiver ack's, sender paints on ok:true
let nextId = 0;
const pending = new Map();

function send(type, payload) {
  const id = ++nextId;
  return new Promise((resolve, reject) => {
    pending.set(id, { resolve, reject });
    window.parent.postMessage({ type, id, ...payload }, "*");
    setTimeout(() => {
      if (pending.has(id)) {
        pending.delete(id);
        reject(new Error("ack timeout"));
      }
    }, 5000);
  });
}

window.addEventListener("message", (e) => {
  const { type, id, ok, error } = e.data || {};
  if (type === "use_suggestion:ack" && pending.has(id)) {
    const { resolve, reject } = pending.get(id);
    pending.delete(id);
    ok ? resolve() : reject(new Error(error));
  }
});

useSuggestionBtn.addEventListener("click", async () => {
  try {
    await send("use_suggestion", { text });
    showSent("Applied!");
  } catch (err) {
    showError("Couldn't apply — insert the rewrite manually.");
  }
});
```

**Correct shape:**
1. Each action carries a unique id.
2. Sender posts `{type, id, ...}` and registers a pending-promise keyed by id.
3. Receiver acts, posts back `{type: "<action>:ack", id, ok: true|false, error?}`.
4. Sender resolves/rejects. Paint success **only** on `ok:true`; paint a clear error on `ok:false`; time out after N seconds with a fallback error.

**Check:** grep for `postMessage` / `sendMessage` followed within ~5 lines by a success paint (`show`, `toast`, `alert`, `render`) with no intervening `await` or callback. That's the smell.

**Learned from:** ToneGuard's `overlay-frame.js` painted "Suggestion applied!" before the parent iframe had even received the `postMessage`. When Gmail's insertion silently failed, the user was told success anyway. This is the same failure mode as any silent-catch anti-pattern — the UI becomes a liar.

**Sub-rule: failure returns must mirror success cleanup.** The ack/nack pattern introduces module-level pending state (`pendingText`, `pendingEditor`, the `pending` Map). Every failure return — nack, timeout, validation reject — must clear the same state the success return clears. Otherwise the re-entry guard wedges the feature permanently after the first failure.

```javascript
// BAD — success path clears state, nack path doesn't
if (ok) {
  pendingText = null; pendingEditor = null;
  return { ok: true };
}
return { ok: false, error: "editor rejected" };  // state stuck

// GOOD — both paths clear
try { /* ... */ } finally {
  pendingText = null;
  pendingEditor = null;
}
```

**Check:** grep `return { ok: false` (or equivalent) inside stateful callbacks; each hit must clear the same state the success return clears.

**Learned from:** ToneGuard PR #22 follow-up. CodeRabbit caught it — the verification-fail nack path left `pendingText` / `pendingEditor` set and the entry-guard blocked every future send until page reload.

---

## 38. Generation-Counter Guard for Teardown-Sync / Setup-Async Watchers

When a reactive watcher tears down synchronously and schedules setup via `$nextTick` / `setTimeout` / `requestAnimationFrame`, rapid key changes (A→B→C within one tick) let multiple setup callbacks flush against the final DOM — duplicating event listeners, timers, or subscriptions. The teardown array empties between changes, so subsequent teardowns become no-ops, but every scheduled setup still runs.

```javascript
// BAD — setup runs once per change, all against the latest DOM
watch: {
    'selectedStep.id'(newId) {
        this._teardown();
        if (newId) this.$nextTick(() => this._setup());
    },
}
// A→B→C within one tick: teardown A, schedule setup B, teardown (empty),
// schedule setup C. Flush fires setup B then setup C, both against C's DOM.

// GOOD — generation counter; only the latest setup executes
watch: {
    'selectedStep.id'(newId) {
        this._teardown();
        if (!newId) return;
        if (this._setupGen == null) this._setupGen = 0;
        const gen = ++this._setupGen;
        this.$nextTick(() => {
            if (gen === this._setupGen) this._setup();
        });
    },
}
```

**Applies to:** Vue watchers, Alpine `$watch`, React `useEffect` with async setup — any teardown-sync / setup-async pair whose reactive key can change multiple times per tick.

**Don't:** rely on debounce (introduces trailing-edge delay and a new dependency). Don't guard with a boolean flag alone — the second setup can clobber the first after a reset.

**Learned from:** CourierFlow `WorkflowBuilder.js` `selectedStep.id` watcher (PR #351). Rapid step clicks caused duplicate `input`/`keydown`/`blur` listeners on token autocomplete inputs; `handleInput` fired twice per keystroke.

---
