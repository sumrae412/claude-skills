# Phase 3 — Testing Matrix

**Purpose:** Build the cross-product of personas × testing styles × flows, pruned to budget. Produce `$testing_matrix`.

**Cost:** trivial (deterministic computation, no LLM).

## Cell construction

### GUI apps

Layer the PersonaTester 3D schema (see `references/personatester-schema.md`):

- **mindset:** `sequential` | `divergent`
- **strategy:** `click` | `core_function` | `input_oriented`
- **habit:** `valid_short` | `invalid`

Full Cartesian product = 2 × 3 × 2 = 12 styles per persona.

Stratified subsample to `testing_styles_per_persona` (default 2) with these rules:

- Each persona's 2 styles differ on **≥2 of 3** dimensions (avoid redundant coverage).
- Globally, each axis-value is hit by ~equal numbers of personas (e.g., ~half get `sequential`, ~half get `divergent`).
- Seeded PRNG; seed recorded in `matrix_metadata.seed`.

Cells: `personas × testing_styles_per_persona × flows`.

### API / CLI / chatbot apps

No PersonaTester layer. `testing_style = null`. Cells: `personas × flows`.

## Budget guard

Compute `|cells|` and show the user:

```
Full matrix: <N_personas> × <styles_per_persona> × <N_flows> = <cells> cells
Estimated LLM calls: cells × 10 (max_steps) = <calls>
```

If `|cells| > 100`, warn and offer:

- Proceed as-is.
- Cap at 100 via random subsample.
- Reduce `testing_styles_per_persona` to 1 (re-run stratification).

## Output

Write `$testing_matrix` to `docs/persona-eval/<app>/<run-id>/testing-matrix.json`.

## Next

Proceed to Phase 4: `phases/phase-4-run-eval.md`.
