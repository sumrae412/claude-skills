---
name: verification-before-completion
description: Use before any "applied", "shipped", "fixed", "merged", "deployed", "done", "complete", or "ready" claim — verify behavior at runtime, not just code state. Check the actual output (endpoint response, UI render, deployed PR state), cite concrete evidence (file_path:line link, git diff --stat, gh pr view, fenced command output), and surface gaps. Required when the claim involves runtime behavior; especially after Edit/Write tool successes (which do not render in the user transcript and are not evidence by themselves).
---

# Verification Before Completion

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


## Overview

Claiming work is complete without verification is dishonesty, not efficiency.

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of this rule.**

## The Iron Law

```
NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE
```

If you haven't run the verification command in this message, you cannot claim it passes.

## The Gate Function

```
BEFORE claiming any status or expressing satisfaction:

1. IDENTIFY: What command proves this claim?
2. RUN: Execute the FULL command (fresh, complete)
3. READ: Full output, check exit code, count failures
4. VERIFY: Does output confirm the claim?
   - If NO: State actual status with evidence
   - If YES: State claim WITH evidence
5. SURFACE RISKS: Name what was NOT verified — skipped suites, untested
   environments, runtime paths not exercised — and what could still break.
   Nothing unverified? Say so explicitly.
6. ONLY THEN: Make the claim

Skip any step = lying, not verifying
```

## Common Failures

| Claim | Requires | Not Sufficient |
|-------|----------|----------------|
| Tests pass | Test command output: 0 failures | Previous run, "should pass" |
| Linter clean | Linter output: 0 errors | Partial check, extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing, logs look good |
| Bug fixed | Test original symptom: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified | Test passes once |
| Agent completed | VCS diff shows changes | Agent reports "success" |
| Requirements met | Line-by-line checklist | Tests passing |
| Count / quantity claim | Enumerate full result set | API `resultSizeEstimate` / `total` / `count` heuristic field |
| LLM-judge grader "works" | Hand-labeled calibration set (≥6 neg + ≥4 amb) passes the gate THIS run | Spot-check of 3 positives, eyeballed evidence strings, "looks reasonable" |
| Async UI action verified via logs | Settle/poll window before the verification query runs, AND confirmed record/card identity matches the one acted on | Log timestamps read immediately after the action, first matching row assumed correct |
| Background job/sweep "ran clean, did nothing" | Direct state read confirming the negative (e.g. a count query returns 0) | Absence of a conditionally-gated log line, e.g. `if (count > 0) logger.warn(...)` |

**Async-settle + identity-confirmation failure mode.** After an async UI action (approve/send/submit), a verification query fired before the effect lands reads stale state and looks like failure — and in a multi-card/multi-record UI, the first or top match may not be the record the user actually acted on. Both errors compound: a premature query plus a wrong-card read produces a confident, wrong root cause. Validated 2026-07-19 on courierflow_beta: an "approve→send is broken, GoDaddy redirect returns fake-success HTML" root-cause claim was wrong — a full-log-window re-check found two clean successful sends; the original verdict was a verification race (query ran before the tap's effect landed) compounded by reading the wrong card. Demoted from trust-critical incident to routine cosmetic issue on re-verification.

**Log-silence-is-ambiguous failure mode.** A log line gated behind a conditional (`if (newItems > 0) logger.warn(...)`) proves nothing on its own when absent — "ran clean, 0 items" and "never ran at all" produce identical silence. Treat that silence as inconclusive until an orthogonal direct-state check (a DB count, an API response, a file diff) confirms which case it is. Validated 2026-07-19 on courierflow_beta: a production reconcile sweep's absent warning log was consistent with both "it ran and found nothing" and "the flag never took effect" — only a direct `SELECT count(*) ... WHERE processed_at IS NULL` (0, down from 16) closed the gap.

## Red Flags - STOP

- Using "should", "probably", "seems to"
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!", etc.)
- About to commit/push/PR without verification
- Trusting agent success reports
- Relying on partial verification
- Thinking "just this once"
- Tired and wanting work over
- **ANY wording implying success without having run verification**

## Rationalization Prevention

| Excuse | Reality |
|--------|---------|
| "Should work now" | RUN the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "Agent said success" | Verify independently |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words so rule doesn't apply" | Spirit over letter |

## Key Patterns

**Tests:**
```
✅ [Run test command] [See: 34/34 pass] "All tests pass"
❌ "Should pass now" / "Looks correct"
```

**Regression tests (TDD Red-Green):**
```
✅ Write → Run (pass) → Revert fix → Run (MUST FAIL) → Restore → Run (pass)
❌ "I've written a regression test" (without red-green verification)
```

**Build:**
```
✅ [Run build] [See: exit 0] "Build passes"
❌ "Linter passed" (linter doesn't check compilation)
```

**Requirements:**
```
✅ Re-read plan → Create checklist → Verify each → Report gaps or completion
❌ "Tests pass, phase complete"
```

**Agent delegation:**
```
✅ Agent reports success → Check VCS diff → Verify changes → Report actual state
❌ Trust agent report
```

**LLM-judge grader (calibration gate):**
```
✅ Run calibration set (negatives + ambiguous) → ≥5/6 neg + ≥3/4 amb + ≥8/10 total → cite cost + agreement → "judge calibrated"
❌ "10 positive examples all passed" (proves the judge approves; proves nothing about what it rejects)
```

**Browser/UI state ("looking at the screen now"):**
```
✅ browser_snapshot → Check URL bar matches expected route → Read the snapshot tree → Then answer
❌ "I can see the form" / "you're set up looking at the screen" (without snapshot — tab may be about:blank, a stale route, or wrong port)
```

Playwright (or any browser-control) tab content is unverified until you snapshot. Lesson from 2026-05-22 onboarding debug: assistant answered as if it saw the form, but the active tab was actually `about:blank`. Cross-check the URL bar against the route you think you're on; if the route uses a non-standard port (e.g. `localhost:22333`), discover the actual port via `lsof` or the dev-server banner rather than assuming a default.

## Regression tests for silent service-signature changes (red-green-revert)

When hot-fixing a regression caused by a service returning a new shape (e.g. `T` → `Optional[T]`), write the test and verify it with full red-green-revert:

1. Write the test. Run — MUST pass (green) with your fix in place.
2. Revert the fix. Run — MUST fail with the EXACT production signature (e.g. `pydantic_core._pydantic_core.ValidationError` with the specific field path, not just any `AssertionError`).
3. Restore the fix. Run — green again.

Document the production signature in the test docstring. A regression test that fails for some reason other than the regression is not a regression test; it's an aspirational test.

Concrete example: PR #344 (analytics 404 hot-fix). The test asserts the exact `Pydantic ValidationError` that a bogus `template_id` triggered before the 404 guard was added.

See: `memory/pattern_orphan_edit_redirect.md`.

## Features that only verify under live traffic

Some features cannot be confirmed by unit tests — the instrumentation fires only against a real external service. Examples: prompt-cache hits (`usage.cache_read > 0`), webhook signature validation against a real provider, rate-limit headers, response-shape fields populated only by a specific model version.

**Pattern:** unit tests prove the wiring compiles and parses; one live canary call proves it works. Before marking such a step "done":

1. Run one real API call.
2. Assert the specific field your change produces (`cache_read`, `cache_creation`, signature header, etc.) is non-zero / present.
3. If the field is zero, the feature is no-op'd silently — NOT done. Investigate before marking complete.

Shape-only test passes ("no schema error") are necessary but not sufficient for features whose entire value is a runtime side-effect.

Concrete example: 2026-04-24 advisor-tool eval wired Anthropic `cache_control` breakpoints. Unit tests confirmed request shape; pilot showed `cache_read_input_tokens=0` on every live call because prompts sat below Anthropic's 1024-token minimum. The feature shipped green on unit tests but did nothing in production.

## Parallel-bundle delta probe (pre-fix vs post-fix isolation)

When a fix landed on `main` but a feature branch was forked BEFORE the fix, you can verify the fix's runtime effect by running two dev servers from two checkouts against a single shared backend. They differ only in the client bundle — same DB, same api-server, same session cookie.

1. Start the api-server once. Open two checkouts (main + feature branch) and run two web dev servers on different ports (e.g. Vite: `PORT=22333 BASE_PATH=/ ./node_modules/.bin/vite ...` and `PORT=22433 BASE_PATH=/ ./node_modules/.bin/vite ...`).
2. Seed test state once via a non-prod auth route (e.g. `POST /api/auth/test-login`) plus direct DB-shape curls — skip the LLM-driven UI path to cut 5–15 min per run.
3. Drive each port via Playwright; compare URL stability / viewport screenshots side-by-side.

Validated 2026-05-22 on courierflow_beta PR #17 (cache-sync hook): post-fix bundle stayed on `/dashboard`; pre-fix bundle bounced back to `/onboarding` because `AppShell` guard re-read stale TanStack cache. Same DB row, different React behavior = clean isolation of the React-layer fix.

**Pre-flight check before any runtime verification on a feature branch:** run `git log --oneline origin/main..HEAD` and `git merge-base HEAD origin/main` to know which fixes the bundle DOES NOT include. A branch forked before a fix lands ships the buggy bundle even when `main` is green.

## False-Confidence Audit (test effectiveness, not just presence)

A passing test suite is only evidence if the tests would actually *fail* when the behavior breaks. A test that passes whether or not the code works proves nothing — it is false confidence, and a green run built on it is a lie dressed as verification.

Before claiming green on a test-backed change, audit test **effectiveness**:

1. **Break the behavior on purpose** — revert the fix, comment out the guard, or corrupt the value the test depends on.
2. **Run the suite — it MUST fail**, and fail for the *right reason* (the assertion that targets your change, not an unrelated error).
3. **Restore and re-run — green again.**

A test that stays green through step 2 asserts nothing about your change; fix the test before trusting the score. This is the general form of the TDD red-green cycle and the red-green-revert pattern above — applied as a gate on *any* "tests pass" claim, not just newly-written regression tests.

Source: Jamon Holmgren's agentic verification setup (from the 2026-07-14 /articles triage).

## Why This Matters

From 24 failure memories:
- your human partner said "I don't believe you" - trust broken
- Undefined functions shipped - would crash
- Missing requirements shipped - incomplete features
- Time wasted on false completion → redirect → rework
- Violates: "Honesty is a core value. If you lie, you'll be replaced."

## When To Apply

**ALWAYS before:**
- ANY variation of success/completion claims
- ANY expression of satisfaction
- ANY positive statement about work state
- Committing, PR creation, task completion
- Moving to next task
- Delegating to agents

**Rule applies to:**
- Exact phrases
- Paraphrases and synonyms
- Implications of success
- ANY communication suggesting completion/correctness

## The Bottom Line

**No shortcuts for verification.**

Run the command. Read the output. THEN claim the result.

This is non-negotiable.

---

## Next Steps

- **All checks pass?** Use `/ship` to commit, push, create PR, run review, and merge to main.
- **Tests failing?** Use `/investigator` to collect evidence before diagnosing.
- **Lint or type errors?** Fix them inline — re-run `/verification-before-completion` after fixes.
