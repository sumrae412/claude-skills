# Phase 4 — Run Eval

**Purpose:** Drive the app through each cell. Produce `$eval_transcripts`.

**Cost:** dominant phase. ~5–15 LLM calls per cell (persona utterance + response interpretation + next-action decision). Default 50 cells → ~500 calls.

## Runner dispatch

Read `$app_config.app.kind` and `runner_config`:

| Kind | Backend | Notes |
|------|---------|-------|
| `gui` | `website-tester` or `playwright-test` (per `runner_config.gui.backend`) | Headless per config. One browser per worker (default 2). |
| `api` | Native HTTP client | Respect `runner_config.api.rate_limit_per_sec`. Include `auth_header` if set. |
| `cli` | Bash | Sandbox per `runner_config.cli.sandbox` (default `true` for alpha apps). |
| `chatbot` | LLM-to-LLM loop | Persona on one side, app endpoint on the other. |

**Never use Haiku as the persona player.** See `references/personagym-rubrics.md` §Haiku warning.

## Per-cell loop

For each cell in `$testing_matrix`:

### 1. Initialize persona context

Prompt includes:

- Persona card: `descriptor`, `backstory`, `communication_style`, `goals_in_app`, `frustrations`.
- Flow goal: `flow.success_criteria`.
- Entry hint: `flow.entry_hint`.
- Testing style directive (GUI only): see `references/personatester-schema.md` §Prompting.

### 2. Step loop (until terminal outcome)

Repeat up to `flow.max_steps`:

1. **Persona generates an action** in character (click label, endpoint to hit, command to run, message to send).
2. **Runner executes** against the app.
3. **Runner captures response:** DOM snapshot / HTTP body / stdout+stderr / chat reply / exception.
4. **Persona interprets** response and decides next action. If something about the interface gave them pause but didn't stop them — a confusing label, a button that doesn't look clickable, a cramped layout, a vague error message — they log it in `ui_observations[]` for this step and keep going.
5. **Check `flow.success_criteria`.** If met → `outcome = success`.
6. **Classify errors.** Unhandled exceptions, HTTP 5xx, hangs → `outcome = crash`. Wrong but structured responses → log to `app_errors[]` with `type=functional`.
7. **Stall detection.** No progress (no state change, same DOM, persona repeats itself) for 2 steps → `outcome = stuck`.

UI observations are distinct from bugs and friction: they're noticed-but-kept-going signals. A persona who completes a flow but comments *"I had no idea the 'Reconcile' button would do what I needed"* has produced a UI snag, not a bug. Capture them even on `outcome = success` transcripts.

### 3. Usefulness reflection

Once the cell terminates (any outcome), one additional LLM call — in-character. The persona reflects on whether they'd actually use this app, not just whether they could operate it.

Prompt (full template in `references/usefulness-interview.md`):

> "Stepping back: imagine a friend asked you about this app. In your own voice, would you actually use it? Rate 1–5. What was the biggest draw, and what would keep you from using it? Rate the app itself, not the test run."

Return `usefulness_reflection` with `rating`, `would_use`, `quote`, `biggest_draw`, `biggest_blocker`. Write into the transcript.

**Why this matters:** a persona can complete a flow (`outcome = success`), hit no bugs, file no UI snags, and still say *"I'd never bother using this."* That's the beta-testing signal this call catches — often a product-market-fit tell, not a fixable UX issue.

**Bias note:** explicitly instruct the persona to "rate the app, not the test run" — mitigates the `invalid` testing-style pushing ratings down. Phase 6 averages across a persona's multiple styles for the same flow before clustering, which helps further.

### 4. Persist transcript

Write to `<run-dir>/transcripts/<cell_id>.json`.

## Session memory

- **Reset between cells** — each cell starts fresh (kills question-order / carryover bias).
- **Maintain within a cell** — persona must remember what they already tried in this flow.

## Concurrency

Cells are independent. Parallelize within limits:

- GUI: memory-bound; default 2 browser workers.
- API: respect `rate_limit_per_sec`.
- CLI: one sandbox per worker.
- Chatbot: LLM rate-limit-bound.

## Output

- Roll-up: `<run-dir>/eval-transcripts.json` (indexed by `cell_id`).
- Per-cell: `<run-dir>/transcripts/<cell_id>.json`.

## Next

Proceed to Phase 5: `phases/phase-5-fidelity-gate.md`.
