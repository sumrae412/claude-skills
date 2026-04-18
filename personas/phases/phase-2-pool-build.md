# Phase 2 — Pool Build

**Purpose:** Produce `$persona_pool` — Nemotron fat middle + two-stage generator tail.

**Cost:** moderate.

- Nemotron filter: zero LLM calls (deterministic).
- Axis-position inference for Nemotron personas: 1 call per persona (default 15).
- Two-stage tail: 1 call per tail persona (default 10).
- Total ~25 LLM calls for a 25-persona pool.

## Cache check

Before generating, check `docs/persona-eval/<app>/pool.json`.

Reuse if all three hold:

- File exists.
- `axes_covered` matches `$app_config.diversity_axes` exactly (name + low + high).
- `generator_metadata.segments` matches `$app_config.segments`.

Any mismatch → invalidate and regenerate.

## Step 1 — Nemotron filter (fat middle)

```bash
python scripts/filter_nemotron.py \
  --segments "<seg1>,<seg2>" \
  --count <pool.nemotron> \
  --seed <run_id_hash> \
  --out <run-dir>/nemotron-raw.json
```

Pulls `nvidia/Nemotron-Personas-USA`, applies segment filter, stratified-samples by age × location type × education. See `references/nemotron-filter.md` for segment→field mapping.

## Step 2 — Infer axis positions for Nemotron personas

Nemotron personas don't carry our app-specific axes. For each, one LLM call:

> "Given this persona: `<backstory + demographics>`, rate them on these axes (0.0–1.0):
> - `<axis_name>`: 0=`<low>`, 1=`<high>`
> - ..."

Batch across personas. Use `model_config.persona_player`. Write inferred positions into each record's `axis_positions`.

## Step 3 — Two-stage tail generator

```bash
python scripts/generate_tail.py \
  --config <run-dir>/app-config.yaml \
  --count <pool.tail> \
  --nemotron-coverage <run-dir>/nemotron-raw.json \
  --seed <run_id_hash> \
  --out <run-dir>/tail-raw.json
```

- **Stage 1 (autoregressive):** quasi-random Sobol samples in axis space, biased toward regions far from the Nemotron cloud (farthest-first).
- **Stage 2 (parallel):** one LLM call per prescribed position expands it into a full persona.

See `references/two-stage-generator.md` for the full technique.

## Step 4 — Merge and compute coverage

Concatenate Nemotron + tail. Assign IDs `p01`...`pN`.

```bash
python scripts/score_fidelity.py coverage \
  --pool <run-dir>/persona-pool.json \
  --axes <run-dir>/app-config.yaml
```

Produces the `coverage_estimate` block: Monte Carlo k-radius support coverage, convex-hull volume proxy, pairwise distance statistics.

## Step 5 — Write `$persona_pool`

- Audit: `docs/persona-eval/<app>/<run-id>/persona-pool.json`.
- Cache: `docs/persona-eval/<app>/pool.json`.

## Quality check

If `coverage_estimate.estimated_support_coverage < 0.6`:

- Flag in Phase 6 report as "under-covered".
- Suggest `pool.tail += 5` for next run.

## Next

Proceed to Phase 3: `phases/phase-3-testing-matrix.md`.
