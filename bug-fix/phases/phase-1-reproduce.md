# Phase 1: Reproduce

## Goal

Capture the bug in a failing test or equivalent reproducible signal.

## Rules

- A bug without reproduction is a guess.
- Write the failing test before investigating.
- If the bug is UI-specific, exercise the deepest reliable testable
  surface.

## Reproduction-loop ladder

Work through this list in order. Stop at the first method that yields a
command or test you can run and watch fail on demand. That artifact is
your red-capable command.

1. **Failing unit test** — write the smallest test that asserts the
   broken invariant and watch it fail.
2. **curl / HTTP script** — for API or network bugs, a single `curl`
   invocation that returns the wrong status or body.
3. **CLI invocation** — a one-liner that triggers the broken path
   directly (e.g. `node ./scripts/foo.js --bad-flag`).
4. **Headless browser** — for UI bugs, a Playwright/Puppeteer snippet
   that clicks to the failure and asserts the wrong state.
5. **Replay trace / log** — feed a captured request log back into the
   system and observe the failure deterministically.
6. **Throwaway harness** — a standalone script that wires just enough
   of the system together to trigger the symptom.
7. **Property-fuzz** — generate random inputs and assert the invariant;
   let the fuzzer find the minimal failing case.
8. **Bisection harness** — `git bisect run <script>` to locate the
   commit that introduced the regression.
9. **Differential loop** — run the old version and the new version
   side-by-side on the same input and diff the outputs.
10. **Human-in-the-loop bash** — as a last resort, give the user a
    precise sequence of shell commands and ask them to paste the output.

## Hard gate

**No red-capable command, no Phase 2.**

Phase 2 (diagnosis) is blocked until Phase 1 produces an artifact — a
command, test, or script — that can be shown failing on demand. A
symptom description or a theory does not satisfy the gate. If none of
the ten methods above yield a runnable artifact, document why each was
tried and blocked, then escalate to human-in-the-loop before
proceeding.

## Process

- understand the symptom
- pick the lowest-numbered ladder method that applies and attempt it
- run it and confirm it fails
- if local reproduction is impossible, inspect logs and environment
  signals
- if only the user can reproduce, add throwaway instrumentation and use
  their runtime output to localize the failure
- confirm the red-capable command before advancing to Phase 2

## Output

Bug report with symptom, expected behavior, reproduction path, and
affected area.
