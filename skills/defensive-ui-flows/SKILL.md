---
name: defensive-ui-flows
description: Use when building interactive UI with buttons that trigger async operations, multi-step wizards or drawers, overlay dialogs with validation, or any flow where a user clicks and waits for a result
---

# Defensive UI Flows

## Overview

Every user-triggered function must answer: **"What does the user see if this fails?"** If the answer is "nothing," you have a bug.

## The Checklist

Before finishing ANY interactive UI code, verify all six rules:

### 1. No Silent Guards

Every early `return` in a user-triggered function MUST show feedback.

```javascript
// ❌ BAD — user clicks, nothing happens
if (isSubmitting) return;

// ✅ GOOD — user knows why nothing happened
if (isSubmitting) {
    showFeedback('Already processing — please wait.');
    return;
}
```

### 2. State Flags Need Try-Catch

When a boolean flag guards re-entry, wrap ALL code between flag-set and promise-start in try-catch. An uncaught sync error leaves the flag stuck forever.

```javascript
// ❌ BAD — if getElementById returns null, flag stays true forever
_isBusy = true;
btn.disabled = true;
var el = document.getElementById('input');
el.value.trim();  // TypeError — .catch() never runs
api.save().then(...).catch(() => { _isBusy = false; });

// ✅ GOOD — sync errors caught, flag always cleaned up
_isBusy = true;
btn.disabled = true;
try {
    var el = document.getElementById('input');
    var val = el ? el.value.trim() : '';
} catch (err) {
    _isBusy = false;
    btn.disabled = false;
    showFeedback('Unexpected error.');
    return;
}
api.save().then(...).catch(() => { _isBusy = false; btn.disabled = false; });
```

### 3. Overlay UIs Need Inline Feedback

Modals, drawers, and slide-out panels MUST show errors **inside themselves**. External notification systems (toasts, snackbars) may be invisible behind the overlay due to z-index stacking contexts.

```javascript
// ❌ BAD — toast may be hidden behind drawer/modal
showToast('Name is required');

// ✅ GOOD — inline element inside the overlay, PLUS toast as backup
showInlineError('Name is required');  // always visible
showToast('Name is required');        // also fire toast for when overlay closes
```

This applies especially when ADDING validation to an EXISTING overlay that already uses an external notification system. Don't just reuse the existing `showToast()` — add inline feedback.

### 4. Navigation Resets ALL State

Step/panel navigation functions MUST reset every transient UI state:

```javascript
function showStep(n) {
    // Reset buttons
    nextBtn.disabled = false;
    nextBtn.textContent = n === lastStep ? 'Submit' : 'Next';

    // Clear errors from previous step
    clearInlineErrors();

    // Clear loading indicators
    hideSpinner();

    // THEN show the panel
    panels.forEach((p, i) => p.hidden = i !== n);
}
```

If Submit disables the button during async work, going Back → Forward must re-enable it.

### 5. Overlay Placement Needs Mode Gating

Clickable overlays that create objects (signature fields, annotations, markers) MUST have an explicit activation flag. Without it, every click creates a new object — making it impossible to drag or select existing ones.

```javascript
// ❌ BAD — overlay is always in "create" mode
overlay.addEventListener('click', function(e) {
    if (e.target !== overlay) return;
    createFieldAt(e.clientX, e.clientY);  // every click creates
});

// ✅ GOOD — explicit placement mode with entry/exit
overlay.addEventListener('click', function(e) {
    if (!_placementActive) return;        // gated
    if (e.target !== overlay) return;
    createFieldAt(e.clientX, e.clientY);
    if (!_stickyMode) _placementActive = false;  // auto-exit
});
// Field-type button enters placement mode
btn.addEventListener('click', () => { _placementActive = true; });
```

Also: draggable child elements inside the overlay MUST call `event.stopPropagation()` on `pointerdown` to prevent the parent click handler from firing during drag.

### 6. Checkbox Toggles Must Propagate to All Views

When a checkbox hides/excludes an item, ALL dependent views must re-render — not just the list the checkbox lives in.

```javascript
// ❌ BAD — signer hidden from list, but their fields still on PDF
checkbox.addEventListener('change', function() {
    signer._excluded = !checkbox.checked;
    renderSignerList();       // only updates signer panel
});

// ✅ GOOD — all dependent views updated
checkbox.addEventListener('change', function() {
    signer._excluded = !checkbox.checked;
    renderSignerList();       // signer panel
    renderOverlay();          // PDF fields
    updateThumbnails();       // page thumbnails
});
```

## Quick Reference

| Rule | Symptom When Violated | Check |
|------|----------------------|-------|
| No Silent Guards | "Button does nothing" | Every `return` has feedback? |
| State Flag Try-Catch | "Button stopped working permanently" | Sync code between flag-set and promise wrapped? |
| Inline Overlay Feedback | "Nothing happens" (error was shown but invisible) | Errors shown INSIDE the overlay element? |
| Navigation Reset | "Button disabled after going back" | `showStep()` resets disabled, text, errors? |
| Placement Mode Gating | "Clicking creates objects instead of selecting" | Overlay click gated by `_placementActive`? Children call `stopPropagation()`? |
| Checkbox Propagation | "Unchecked item still visible elsewhere" | All `_render*()` methods called on change? |

## Red Flags — STOP and Fix

If you catch yourself writing any of these, apply the checklist:

- `if (flag) return;` with no feedback call
- Setting `_isX = true` followed by DOM access without try-catch
- Calling `showToast()` or `showNotification()` from inside a modal/drawer without an inline fallback
- A `showStep()` / `setPanel()` function that only toggles panel visibility
- An overlay `click` handler that always creates objects with no mode gate
- A checkbox `change` handler that only updates one view when multiple views show the item

## When NOT to Use

- Pure server-rendered forms (no JS interaction)
- Simple single-action buttons with no async (a link click)
- Components using a framework's built-in state management (React state, Vue reactivity) that handles cleanup automatically
