# Phase 1 — App Config

**Purpose:** Elicit `$app_config` from the user. Validate against `contracts/app-config.schema.md`.

**Cost:** trivial (conversational, no LLM work).

## Entry check

Look for `docs/persona-eval/<app>/config.yaml`.

- If present, show a summary (name, segments, axes, flows) and ask:
  > "Found config from <date>. Reuse as-is, or re-elicit?"
- If reusing: load, skip to Phase 2.

## Elicitation order

Ask one question at a time. Push back on vague answers — this config seeds every downstream phase.

1. **App name + one-sentence description.**
2. **App kind + entry point.**
   - Map "web app" / "site" → `gui` with a URL.
   - "API" / "endpoint" → `api` with base URL.
   - "command-line tool" → `cli` with invocation string.
   - "chatbot" / "assistant" → `chatbot` with endpoint.
3. **Target user segments.**
   > "Who are the target users? Give me 1–3 rough segments in plain language."
   Translate to Nemotron-compatible tags (see `references/nemotron-filter.md`). Confirm the mapping with the user before writing.
4. **Diversity axes (2–4).**
   > "What would you want to vary across test users? What's the biggest source of variation that changes how someone would use this app?"
   For each axis, ask for low and high extremes with a concrete example. Reject >4 axes (coverage metrics get noisy).
5. **Flows (≥1).**
   > "What user journeys should I exercise? For each: (a) entry hint, (b) what 'done' looks like."
   If `app.repo_path` was provided, offer to scan and suggest flows.
   **Every flow needs `success_criteria` — no skipping.**

## Defaults (don't ask; user can override)

- `pool.nemotron = 15`, `pool.tail = 10`.
- `testing_styles_per_persona = 2`.
- `flows[].max_steps = 10`.
- `model_config.persona_player = "claude-sonnet-4-6"`.
- `model_config.fidelity_evaluators = ["claude-sonnet-4-6", "claude-opus-4-7"]`.
- `model_config.never_haiku = true`.

## Validation

Before writing:

- `diversity_axes.length` in `[2, 4]`.
- `segments.length >= 1`.
- `flows.length >= 1`, every `flow.success_criteria` non-empty.
- `pool.nemotron + pool.tail <= 50` (unless user explicitly overrides).

## Output

Generate `run_id` as `YYYY-MM-DD-<4-char-slug>`.

Write `$app_config` YAML to:

- `docs/persona-eval/<app>/config.yaml` (reusable cache).
- `docs/persona-eval/<app>/<run-id>/app-config.yaml` (immutable audit copy).

## Next

Proceed to Phase 2: `phases/phase-2-pool-build.md`.
