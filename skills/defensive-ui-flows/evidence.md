# Defensive UI Flows — Evidence Log

> To add a new bug, copy the template below and fill it in.
> Then run `/update-defensive-ui` to test and update the skill.

## Quick-Add Template

<!-- Copy everything between the dashes, paste at the end of the Bugs section, and fill in -->
<!--
---

## Bug N: SHORT_NAME (DATE)

**Symptom:** What the user reported.

**Root cause:** What actually went wrong in the code.

**Which rule violated:** [1: Silent Guard | 2: Stuck Flag | 3: Overlay Feedback | 4: Navigation Reset | NEW]

**Code (bad):**
```javascript
// the broken pattern
```

**Code (fix):**
```javascript
// the corrected pattern
```

**Pressure scenario prompt:** A generic task prompt that would reproduce this bug.
-->

---

## Bug 1: Silent Guard Clause (2026-03-03)

**Symptom:** "Send for Signatures" button does nothing on click.

**Root cause:** `_isSending` boolean guard returned silently:
```javascript
// BAD — user sees nothing
function sendForSignatures() {
    if (_isSending) return;
    // ...
}
```

**What agent did wrong:** Wrote a guard clause that silently exits with no user feedback. The user clicked repeatedly, assumed the feature was broken.

**Fix pattern:**
```javascript
// GOOD — user sees feedback
function sendForSignatures() {
    if (_isSending) {
        showToast('Already sending — please wait.', true);
        return;
    }
    // ...
}
```

**Pressure scenario:** "Add a rate-limit guard to prevent double-submit on a payment button."

---

## Bug 2: Stuck State Flag (2026-03-03)

**Symptom:** After one failed send attempt, the Send button permanently stops working — even on retry.

**Root cause:** `_isSending = true` was set before synchronous code that could throw. The throw skipped the cleanup in the `.catch()` handler because it happened before the promise chain started.

```javascript
// BAD — sync throw leaves flag stuck
_isSending = true;
setSendButtonBusy(true);

// This line can throw if element doesn't exist
var codeEl = document.getElementById('drawerAccessCode' + index);
codeEl.value.trim();  // TypeError if codeEl is null

// Promise chain never starts, .catch() never runs
core.saveSigners().then(...)
    .catch(function() { _isSending = false; });
```

**Fix pattern:**
```javascript
// GOOD — wrap sync code in try-catch
_isSending = true;
setSendButtonBusy(true);
try {
    // sync code that might throw
    var codeEl = document.getElementById('drawerAccessCode' + index);
    var codeVal = codeEl && codeEl.value ? codeEl.value.trim() : '';
} catch (syncErr) {
    console.error('sync error:', syncErr);
    _isSending = false;
    setSendButtonBusy(false);
    showToast('Unexpected error.', true);
    return;
}
// NOW start promise chain
core.saveSigners().then(...)
```

**Pressure scenario:** "Add a loading spinner to an async form submit that calls an API."

---

## Bug 3: Toast Hidden Behind Overlay (2026-03-03)

**Symptom:** Validation fires correctly, toast notification fires correctly, but user reports "nothing happens" — error message is invisible.

**Root cause:** Toast container at `z-index: 1200` should render above the drawer at `z-index: 1050`, but in practice the toast was not visible to the user. Possible causes: stacking context isolation, toast positioned outside viewport, or drawer backdrop intercepting focus.

**What agent did wrong:** Relied solely on an external notification system (toasts) for feedback inside an overlay UI (drawer). Never verified that the toast was actually visible when the drawer was open.

**Fix pattern:** Add inline feedback element directly inside the overlay:
```html
<div class="drawer-status" id="drawerStatus"
     role="alert" aria-live="polite"
     style="display:none;"></div>
```
```javascript
function showDrawerStatus(message, isError) {
    var el = document.getElementById('drawerStatus');
    if (!el) return;
    el.textContent = message;
    el.className = 'drawer-status ' +
        (isError ? 'is-error' : 'is-success');
    el.style.display = '';
}
```

**Pressure scenario:** "Add form validation to a modal dialog. Show errors when required fields are missing."

---

## Bug 4: Button Disabled State Not Reset (2026-03-03)

**Symptom:** After navigating back from Review step to Signers step, the "Continue to Review" button is permanently disabled.

**Root cause:** `_nextBtn.disabled = true` was set during the send flow, but `setPanel()` — the function that handles step navigation — never reset it.

**Fix pattern:** Reset ALL transient state in navigation functions:
```javascript
function setPanel(stepIndex) {
    // Reset button states
    if (_nextBtn) {
        _nextBtn.disabled = false;
        _nextBtn.textContent = '';
        // ... set correct text for this step
    }
    // Reset inline errors
    clearDrawerStatus();
    // Show/hide panels
    _panels.forEach(function(panel, i) {
        panel.classList.toggle('is-active', i === stepIndex + 1);
    });
}
```

**Pressure scenario:** "Build a wizard with Back/Next buttons and a final Submit step."

---

## Common Thread

All four bugs share one root cause: **the agent optimized for the happy path and didn't think about what the user sees when something goes wrong.**

The agent:
1. Assumed guard clauses don't need feedback (Bug 1)
2. Assumed promise `.catch()` covers all errors (Bug 2)
3. Assumed external notification systems always work (Bug 3)
4. Assumed UI state only needs to be set, not reset (Bug 4)

Each is a failure to ask: **"What does the user see if this fails?"**

---

## Baseline Test Results (RED Phase — 2026-03-03)

### Scenario 1: Double-Submit Guard → **Bug 1 CONFIRMED**

Agent (haiku, no skill) wrote:
```javascript
if (paymentInProgress) {
    return;  // ← SILENT. No feedback.
}
```
- Guard clause returns silently — user sees nothing ✅ BUG REPRODUCED
- No try-catch around pre-async sync code (Bug 2 partial)
- Did use `.finally()` for cleanup — good practice naturally applied
- Did NOT show feedback when guard blocks

### Scenario 3: Checkout Modal → **Bug 3 NOT triggered, Bug 4 PARTIAL**

Agent (haiku, no skill) wrote inline errors inside the modal:
```javascript
showError(message) {
    const errorEl = this.modal.querySelector('[data-error-message]');
    // ...
}
```
- Used inline error element inside the modal ✅ GOOD (Bug 3 not triggered)
- `updateUI()` clears errors on navigation ✅ GOOD
- BUT `updateUI()` does NOT reset `nextBtn.disabled` ⚠️ Bug 4 partial
- `handleConfirm()` doesn't disable button during async work ⚠️ Bug 2 partial

**Key insight on Bug 3:** When building a modal FROM SCRATCH, agents naturally
use inline errors. Bug 3 manifests when ADDING validation to an EXISTING overlay
that already has an external notification system (like toasts). The agent reuses
the existing pattern instead of questioning whether it's visible.

**Refined scenario needed:** "An existing app uses `window.showToast()` for all
notifications. Add required-field validation to an existing modal dialog.
Show errors when fields are empty."

---

## GREEN Phase Results (WITH Skill — 2026-03-03)

### Scenario 1 (Double-Submit Guard): **PASSED ✅**

Agent (haiku, WITH skill injected) wrote:
```javascript
if (btn.disabled) {
    showNotification('Payment is already processing. Please wait.', 'error');
    return;
}
```
- Guard clause shows feedback ✅ (was silent without skill)
- Added try-catch around pre-promise validation ✅
- Resets button state in both .then() and .catch() ✅
- Saves originalText to restore button text ✅

**Comparison:**
| Behavior | WITHOUT Skill | WITH Skill |
|----------|--------------|------------|
| Guard clause | Silent `return` | Shows notification + `return` |
| Pre-async try-catch | None | Yes, wraps validation |
| Button state cleanup | `.finally()` only | Both `.then()` and `.catch()` |

**Verdict:** Skill directly fixed the confirmed Bug 1 anti-pattern.

---

## Known Loopholes for Future REFACTOR Iterations

### Loophole 1: Bug 3 (Overlay Feedback) not triggered by "build from scratch" prompts
- When building a modal from scratch, agents naturally use inline errors
- Bug 3 only manifests when ADDING validation to an EXISTING overlay that uses toasts
- **Next test:** Provide existing code with `showToast()` and ask agent to add validation to a modal
- Status: **UNTESTED** — needs a more realistic scenario

### Loophole 2: Bug 4 (Navigation Reset) only partially triggered
- Agent's `updateUI()` DID clear errors but did NOT reset `nextBtn.disabled`
- Skill may need stronger emphasis on "reset ALL transient state including disabled"
- Status: **PARTIAL** — skill addresses it but hasn't been retested

### Loophole 3: Combined scenario (Bug 5) not tested
- The Scenario 5 (full signing drawer) hasn't been run yet
- This is the most realistic test — all four bugs in one flow
- Status: **UNTESTED** — save for next session

### Loophole 4: Word count (608 words) exceeds guideline
- Writing-skills guide says < 500 words for non-frequently-loaded skills
- Current skill is 608 words — could trim examples
- Status: **LOW PRIORITY** — skill is effective, trim later if needed

### Future evidence to collect
- Any new bugs found in future sessions that fit these patterns
- Edge cases: what about `async/await` vs Promise chains?
- Framework-specific: does this apply to React/Vue or only vanilla JS?
