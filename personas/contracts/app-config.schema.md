# Contract: `$app_config`

The per-app input to the personas pipeline. Produced by Phase 1, consumed by Phases 2–6.

## Schema (YAML)

```yaml
app:
  name: string                     # short identifier, used for file paths
  description: string              # 1–3 sentences; what the app does, who it's for
  entry: string                    # URL, CLI command, API base URL, or chat endpoint
  kind: gui | api | cli | chatbot  # dispatches Phase 4 runner
  repo_path: string | null         # local path to codebase, if available (enables Phase 2 context extraction)

segments:                          # used to filter Nemotron; free-form tags, matched against Nemotron persona fields
  - string                         # e.g., "small_landlord_us", "renter_us_urban"

diversity_axes:                    # 2–4 axes; fewer is better, extremes must be distinguishable
  - name: string
    low: string                    # short description of the low extreme
    high: string                   # short description of the high extreme
    type: ordinal | categorical    # defaults to ordinal

flows:                             # distinct user journeys to exercise
  - name: string                   # e.g., "send_document_for_signature"
    entry_hint: string             # how a persona should start this flow (URL path, button label, API endpoint)
    success_criteria: string       # what "done" looks like for the persona
    max_steps: integer             # cap per run, default 10

pool:
  nemotron: integer                # fat-middle size, default 15
  tail: integer                    # edge-case size from two-stage generator, default 10

testing_styles_per_persona: integer  # default 2; stratified subsample of PersonaTester 3D combinations (only applies if kind=gui)

runner_config:                     # Phase 4 backend options
  gui:
    backend: website-tester | playwright-test | custom
    headless: boolean
    base_url: string
  api:
    auth_header: string | null
    rate_limit_per_sec: integer
  cli:
    sandbox: boolean               # recommended true for alpha apps
  chatbot:
    endpoint: string
    auth: string | null

model_config:
  persona_player: string           # default "claude-sonnet-4-6"
  fidelity_evaluators:             # ensemble; minimum 2, prefer different families
    - string                       # e.g. "claude-sonnet-4-6"
    - string                       # e.g. "claude-opus-4-7"
  never_haiku: true                # guard flag; Phase 2 and 4 reject Haiku for persona role-play

run_id: string                     # auto-generated timestamp-slug, e.g. "2026-04-17-a1b2"
```

## Required fields

- `app.name`, `app.description`, `app.entry`, `app.kind`
- `segments` (≥1)
- `diversity_axes` (≥2)
- `flows` (≥1)

All others have defaults.

## Elicitation order (Phase 1 prompts user in this order)

1. App name + 1-sentence description.
2. App kind + entry point.
3. Who are the target users? (free-form → segment tags)
4. What 2–3 things would you want to vary across test users? (→ diversity axes; Phase 1 refines with examples of low/high extremes)
5. What flows do you want exercised? (Phase 1 offers to auto-suggest from repo scan if `repo_path` given)

## Validation

Phase 2 validates before proceeding:
- Reject runs with >4 axes (pipeline will still work but coverage metrics get noisy).
- Reject `pool.nemotron + pool.tail > 50` without explicit override (cost guard).
- Reject `flows` with no `success_criteria` — without it, Phase 4 can't tell when a persona is done.

## Persistence

Written to `docs/persona-eval/<app>/config.yaml` at end of Phase 1. Reused across runs unless user requests re-elicitation.
