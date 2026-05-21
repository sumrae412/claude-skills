# Discovery Question Bank

Pick 3-5 questions per session. Don't ask all of them. Don't ask anything you can answer yourself by reading the codebase, README, or existing docs.

Use lettered options so the user can reply `1A, 2C, 3B`.

**Order of preference when picking:**

1. Risk-class questions (auth / privacy / money / data_loss / external / public_api) — wrong answer here forces full workflow
2. Scope-out questions — what to explicitly exclude
3. Success-metric questions — what does "done" look like
4. Persona questions — who specifically uses this
5. Edge-case questions — only if exploration didn't surface them

---

## Problem & Audience

**P-1. Who specifically experiences this problem?**

A. New users only
B. Existing users only
C. All users
D. Admin / internal users
E. Other: <specify>

**P-2. How often does the problem occur?**

A. Constantly (every session)
B. Frequently (every few days)
C. Occasionally (weekly-ish)
D. Rarely but with high impact when it does
E. Don't know yet — need to validate

**P-3. What's the cost of not solving it?**

A. User churn / dissatisfaction
B. Revenue loss
C. Support burden
D. Competitive disadvantage
E. Internal team productivity
F. Compliance / legal exposure

---

## Scope

**S-1. What's the appropriate v1 scope?**

A. Minimal viable — just the core happy path
B. Core + obvious adjacent capabilities
C. Full feature parity with <competitor / existing system>
D. Backend / API only (UI later)
E. UI only (backend already exists)

**S-2. What should this feature explicitly NOT do (v1)?**

<Free response — list 2+ adjacent capabilities to defer>

**S-3. If we cut this in half to ship faster, what comes out?**

<Free response — forces priority ranking>

---

## Success Metrics

**M-1. How will we know it worked?**

A. Adoption rate (% of eligible users who try it)
B. Activation rate (% who complete the core action)
C. Time to complete the workflow
D. Error / drop-off rate reduction
E. Revenue / conversion impact
F. Qualitative user satisfaction (NPS, surveys)

**M-2. What's the target threshold?**

<Concrete number + measurement window. "50% adoption within 30 days" not "high adoption">

**M-3. What would indicate failure?**

<Free response — explicit failure mode is healthier than only defining success>

---

## Risk Class

**R-1. Does this feature touch authentication or session management?**

A. Yes — new auth flow / session change
B. Yes — extends existing auth
C. No — but reads user identity
D. No — anonymous

**R-2. Does this handle private user data, PII, or PHI?**

A. Yes — new private data
B. Yes — uses existing private data in a new way
C. No — only public / non-sensitive data

**R-3. Does this move money, charge users, or change billing?**

A. Yes — new payment flow
B. Yes — modifies existing billing
C. No — but references prices
D. No — no money involved

**R-4. Could this delete or corrupt user data?**

A. Yes — destructive operation (delete, overwrite, migrate)
B. Could in failure modes
C. No — read-only or additive only

**R-5. Does this trigger external side-effects (emails, SMS, third-party APIs, webhooks)?**

A. Yes — new external integration
B. Yes — extends existing integration
C. No

**R-6. Does this change a public API contract or shipped behavior?**

A. Yes — breaking change
B. Yes — additive change to public surface
C. No — internal only

---

## User Stories

**U-1. What's the primary action the user takes?**

<Free response — describe the verb. "Sets per-channel notification preferences" not "manages settings">

**U-2. What does the user see right after completing the action?**

A. Confirmation message
B. Updated state in the same view
C. Redirect to a different page
D. Email / notification confirmation
E. Nothing visible — silent success

**U-3. What's the current workaround users do?**

<Free response — names the pain concretely>

---

## Edge Cases

**E-1. What happens on network / service failure?**

A. Show retry button, keep user input
B. Show error, clear input
C. Queue and retry in background
D. Block the user until they retry
E. Hasn't been considered yet

**E-2. What happens when the input is empty / malformed / duplicated?**

<Free response per case>

**E-3. What happens at scale boundaries (1 vs 1k vs 1M)?**

A. No explicit limits — best effort
B. Hard cap at <number>
C. Pagination / lazy load
D. Not expecting volume

**E-4. What happens when two users race on the same resource?**

A. Last write wins
B. First write wins, second errors
C. Merge / append
D. Lock / serialize
E. Not applicable

---

## Non-Functional

**N-1. Performance expectations?**

A. p95 < 200ms (interactive feel)
B. p95 < 1s (acceptable for typed input)
C. p95 < 5s (acceptable for batch / heavy ops)
D. Best effort — performance not a primary concern

**N-2. Backward compatibility?**

A. Must not break existing API / UX
B. May break with explicit migration path
C. Greenfield — no compat concerns

**N-3. Accessibility?**

A. WCAG 2.1 AA required (public-facing UI)
B. Internal tool — basic keyboard / screen-reader support
C. Not applicable (no UI)

---

## When to stop asking

If after one round of questions you can fill the template without `<TBD>` markers in any non-optional field, write the PRD. Anything left ambiguous goes to **Open Questions** — not to another round of asking. Open Questions belong in the document; clarification rounds don't scale.
