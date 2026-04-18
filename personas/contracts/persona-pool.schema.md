# Contract: `$persona_pool`

Output of Phase 2. The generated synthetic population for this app.

## Schema (JSON)

```json
{
  "run_id": "2026-04-17-a1b2",
  "app_name": "CourierFlow",
  "generated_at": "ISO-8601 timestamp",
  "axes_covered": [
    { "name": "portfolio_size", "low": "1_unit", "high": "10_units", "type": "ordinal" }
  ],
  "personas": [
    {
      "id": "p01",
      "source": "nemotron | tail",
      "axis_positions": { "portfolio_size": 0.2, "tech_savviness": 0.8, "trust_in_automation": 0.5 },
      "descriptor": "string — one-line summary, e.g. 'first-time landlord, tech-native, cautiously delegates'",
      "backstory": "string — ~150 words in first or third person; includes JTBD-style reasoning",
      "demographics": {
        "age": "integer | null",
        "location": "string | null",
        "occupation": "string | null",
        "...": "any Nemotron-native fields preserved when source=nemotron"
      },
      "goals_in_app": "string — why this persona is using the app being tested",
      "frustrations": ["string", "..."],
      "communication_style": "string — for Phase 4 linguistic fidelity and Phase 5 Linguistic Habits scoring"
    }
  ],
  "coverage_estimate": {
    "method": "monte_carlo_k_radius",
    "estimated_support_coverage": 0.0,
    "convex_hull_volume": 0.0,
    "min_pairwise_distance": 0.0,
    "average_pairwise_distance": 0.0
  },
  "generator_metadata": {
    "nemotron_filter_spec": { "segments": ["..."], "fields_matched": ["..."] },
    "nemotron_sampled_ids": ["..."],
    "tail_generator_seed": 12345,
    "tail_generator_prompt_hash": "sha256..."
  }
}
```

## Axis positions

- Normalized to `[0.0, 1.0]` regardless of `type`.
- **Ordinal axes:** continuous Sobol quasi-random samples; 0=low, 1=high.
- **Categorical axes:** still 0.0/1.0 (treated as binary); mixed ordinal+categorical is fine.

## Source field

- `nemotron`: sampled from filtered NVIDIA Nemotron-Personas-USA. Demographics populated from source dataset. Position on axes is **inferred** post-hoc (see `references/nemotron-filter.md`). These are the "fat middle" — realistic density but may cluster.
- `tail`: produced by the two-stage generator (see `references/two-stage-generator.md`). Position on axes is **prescribed** (quasi-random Sobol sample), then stage 2 expands to full persona. These are the "long tail" — explicitly targeting underrepresented combinations.

## Coverage estimate

Computed by `scripts/score_fidelity.py` (despite the name, it also handles pool coverage metrics). Used in Phase 6 report to answer: "Did we actually span the axes we said we'd span?"

- `estimated_support_coverage`: fraction of the axis space within k-radius of any persona, Monte Carlo over 10k reference points; k calibrated against a Sobol reference distribution (target: 99% coverage at N personas).
- Low coverage (<60%) → Phase 6 flags the run as "under-covered" and suggests increasing `pool.tail`.

## Persistence

Written to `docs/persona-eval/<app>/<run-id>/persona-pool.json`. The pool is cached at `docs/persona-eval/<app>/pool.json` and reused for subsequent runs **unless** `diversity_axes` or `segments` change (cache invalidates).
