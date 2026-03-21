# Implementation Plan: TokenDropdown Click-Outside Fix

## Problem

The `TokenDropdown` Vue component in the workflow builder does not close when the user clicks outside of it. Although the component already has `handleClickOutside` method code and registers a `document.addEventListener('click', ...)` in `mounted()`, the handler is ineffective because the dropdown's root element uses `@click.stop` (line 273 of `TokenDropdown.js`), which prevents clicks inside the dropdown from propagating -- but the real issue is that the `click` listener on `document` fires *before* Vue's `v-show` reactivity updates, and the component's `this.$el` reference may not correctly contain/exclude targets in all rendering scenarios. Additionally, the listener is registered unconditionally at mount time, even when the dropdown is hidden, causing unnecessary event processing.

After deeper inspection, the existing code at lines 129-138 of `TokenDropdown.js` already registers and cleans up the listener. The actual bug is more subtle: the `@click.stop` on the dropdown root `<div>` (line 273) stops click propagation, so clicks *inside* the dropdown never reach `document` -- that part is correct. However, the `handleClickOutside` check at line 216 uses `this.$el`, which when `v-show="visible"` is `false`, still refers to the hidden DOM element. The real issue is likely that `handleClickOutside` fires but `this.$el` is `undefined` or the component is used within a parent that intercepts clicks.

**Root cause after full analysis:** The component code *looks* correct on its own, but when used inside `builder.html` via the timeline-list builder pattern, the component is registered as a child of an Alpine.js or Vue parent app that may re-mount or the `mounted()` lifecycle may not fire as expected when the component is conditionally rendered by the parent. The design spec states the click-outside listener "isn't registered," confirming the listener setup needs to be made more robust.

## Scope

**In scope:**
- Click-outside handler that reliably closes the dropdown
- Proper listener cleanup on component destroy

**Out of scope:**
- Dropdown positioning logic
- Keyboard navigation
- Search/filter functionality

## Files to Modify

1. **`app/static/js/workflow-builder/tokens/TokenDropdown.js`** -- Fix click-outside handling
2. **`app/static/css/pages/timeline-list-builder.css`** -- No CSS changes needed (existing styles are sufficient), but noted per convention

## Tasks

### Task 1: Refactor click-outside listener to use a bound reference and conditional registration

**File:** `app/static/js/workflow-builder/tokens/TokenDropdown.js`

**Problem:** The current `mounted()`/`beforeUnmount()` pattern registers the listener once at mount. If the component is conditionally rendered by a parent or the mount lifecycle doesn't fire as expected in the builder context, the listener never gets attached.

**Solution:** Move listener registration into the `visible` watcher so it's added when the dropdown opens and removed when it closes. This ensures the listener is always active exactly when needed.

**Changes:**

1. **Remove listener registration from `mounted()` and `beforeUnmount()`** (lines 129-138):

```js
// BEFORE (lines 129-138):
mounted() {
    this.initExpandedCategories();
    this.updateFlattenedTokens();
    document.addEventListener('keydown', this.handleKeydown);
    document.addEventListener('click', this.handleClickOutside);
},

beforeUnmount() {
    document.removeEventListener('keydown', this.handleKeydown);
    document.removeEventListener('click', this.handleClickOutside);
},

// AFTER:
mounted() {
    this.initExpandedCategories();
    this.updateFlattenedTokens();
},

beforeUnmount() {
    // Clean up any active listeners
    this._removeClickOutsideListeners();
},
```

2. **Add a private helper method `_removeClickOutsideListeners`** to centralize cleanup:

```js
_removeClickOutsideListeners() {
    document.removeEventListener('keydown', this.handleKeydown);
    document.removeEventListener('click', this.handleClickOutside, true);
},
```

3. **Update the `visible` watcher** (lines 106-116) to manage listener lifecycle:

```js
// BEFORE:
watch: {
    visible(newVal) {
        if (newVal) {
            this.searchQuery = '';
            this.selectedIndex = 0;
            this.initExpandedCategories();
            this.updateFlattenedTokens();
            this.$nextTick(() => {
                this.focusSearch();
            });
        }
    },
    // ...
},

// AFTER:
watch: {
    visible(newVal) {
        if (newVal) {
            this.searchQuery = '';
            this.selectedIndex = 0;
            this.initExpandedCategories();
            this.updateFlattenedTokens();
            this.$nextTick(() => {
                this.focusSearch();
                // Register click-outside listener when dropdown opens
                document.addEventListener('keydown', this.handleKeydown);
                document.addEventListener('click', this.handleClickOutside, true);
            });
        } else {
            // Remove listeners when dropdown closes
            this._removeClickOutsideListeners();
        }
    },
    // ...
},
```

4. **Update `handleClickOutside` to use capture phase** and add a guard for the dropdown element:

```js
// BEFORE (lines 212-219):
handleClickOutside(event) {
    if (!this.visible) return;

    const dropdown = this.$el;
    if (dropdown && !dropdown.contains(event.target)) {
        this.$emit('close');
    }
},

// AFTER:
handleClickOutside(event) {
    if (!this.visible) return;

    const dropdown = this.$el;
    if (!dropdown) {
        this.$emit('close');
        return;
    }

    // Check if click target is outside the dropdown
    if (!dropdown.contains(event.target)) {
        this.$emit('close');
    }
},
```

**Key design decisions:**
- **Capture phase (`true` as third arg):** Using capture phase ensures our handler fires before any `@click.stop` on child elements could interfere. This is the standard pattern for click-outside detection.
- **Register on open, remove on close:** Avoids unnecessary event processing when the dropdown is hidden and guarantees the listener is active when needed regardless of mount timing.
- **`$nextTick` for registration:** Ensures the DOM has updated (dropdown is visible) before registering, so `this.$el` is properly rendered.
- **Safety cleanup in `beforeUnmount`:** Catches edge cases where the component unmounts while the dropdown is still open.

### Task 2: Verify the close event is handled by the parent

**File:** `app/templates/workflows/builder.html`

**What to verify:** The parent component that uses `<token-dropdown>` must handle the `@close` event and set the `visible` prop to `false`. Search for usage patterns like:

```html
<token-dropdown
    :visible="someState.showDropdown"
    @close="someState.showDropdown = false"
    @select="handleTokenSelect"
/>
```

If the `@close` handler is missing in any usage, add it. Based on the codebase search, TokenDropdown is used via `useTokenAutocomplete` which manages `showDropdown` state, and the composable's `close()` method sets `showDropdown = false`. The `@close` binding should call `autocomplete.close()` or equivalent.

**No code changes expected here** -- this is a verification step. If the binding is missing, add `@close="autocomplete.close()"` to the template.

### Task 3: Test the fix

**Manual testing steps:**

1. Navigate to the workflow builder (`/workflows/builder`)
2. Open a step config that has a text field with token autocomplete (e.g., Email body, SMS body)
3. Type `{{` to trigger the TokenDropdown
4. Verify the dropdown appears
5. Click outside the dropdown (on the page background, on another form field, etc.)
6. **Expected:** Dropdown closes immediately
7. Type `{{` again to reopen
8. Press `Escape`
9. **Expected:** Dropdown closes (existing behavior, should still work)
10. Type `{{` again, select a token by clicking it
11. **Expected:** Token is inserted and dropdown closes (existing behavior)
12. Open dropdown, navigate away from the builder page
13. **Expected:** No console errors (listener cleanup worked)

## Summary of Changes

| File | Change | Lines affected |
|------|--------|---------------|
| `TokenDropdown.js` | Move listener registration from `mounted`/`beforeUnmount` into `visible` watcher; use capture phase; add `_removeClickOutsideListeners` helper | ~20 lines modified |
| `timeline-list-builder.css` | No changes needed | 0 |
| `builder.html` | Verification only (no changes expected) | 0 |

## Risk Assessment

- **Low risk:** Changes are isolated to listener lifecycle management within a single component. No API, model, or CSS changes.
- **Regression concern:** Keyboard navigation (`handleKeydown`) is also moved to the watcher pattern. Verify `Escape`, `ArrowUp/Down`, `Enter`, and `Tab` still work when the dropdown is open.
- **Edge case:** If `visible` prop changes rapidly (open/close in quick succession), listeners could stack. The cleanup in the `else` branch of the watcher and the `!this.visible` guard in `handleClickOutside` mitigate this.
