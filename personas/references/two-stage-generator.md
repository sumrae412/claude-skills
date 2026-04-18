# Two-Stage Persona Generator

Adapted from Paglieri et al. 2026, "Persona Generators: Generating Diverse Synthetic Personas at Scale" (Google DeepMind).

## Why two stages

Autoregressive generation alone can't span a diversity space — it mode-collapses and reproduces training-set density artifacts. Fully-parallel generation can't coordinate for diversity either, because independent calls don't see where prior samples landed.

The two-stage split resolves this:

1. **Stage 1 (autoregressive, coordinated):** decides *where* each persona sits on the diversity axes. Sequential; sees prior placements; enforces spread.
2. **Stage 2 (parallel, independent):** given a fixed axis position, expands into a full persona. Each call is independent — cheap and high-throughput.

## Stage 1 — Axis placement

Goal: pick N points in `[0,1]^K` (K = `len(diversity_axes)`) that maximize support coverage, biased toward regions under-sampled by the Nemotron pool.

### Algorithm (implemented in `scripts/generate_tail.py`)

1. Compute the Nemotron pool's positions in axis space (from Phase 2 Step 2 inference).
2. Generate `5N` Sobol quasi-random samples in `[0,1]^K`.
3. For each sample, compute Euclidean distance to the nearest Nemotron point.
4. Keep the top N by distance (farthest-first traversal).

Output: `tail_axis_positions: List[Dict[axis_name, float]]`.

### Why Sobol, not uniform random

Sobol sequences have low discrepancy — they fill space more evenly than pseudo-random samples at the same count. This matters at small N (~10 tail personas); at N→∞ the distinction disappears.

## Stage 2 — Persona expansion

For each prescribed position, one LLM call produces a full persona.

### Prompt template

```
You are generating a synthetic user persona for testing <app_name>.

The persona sits at these positions on the diversity axes:
- <axis_1>: <position> (0=<low>, 1=<high>)
- <axis_2>: <position>
...

The app is for these segments: <segments>.

Write a persona that:
- naturally sits at those axis positions,
- is plausibly a member of one of the target segments,
- has a real reason to use this app.

Return strict JSON with fields: descriptor, backstory (~150 words),
demographics (age, location, occupation), goals_in_app, frustrations (2-4),
communication_style.

Do NOT caricature the axis positions — make them believable and specific.
```

### Model choice

Use `$app_config.model_config.persona_player` (Sonnet or Opus). Never Haiku — see `references/personagym-rubrics.md` §Haiku warning.

## Evolutionary search (not yet wired)

Paglieri et al. also use AlphaEvolve-style evolutionary search to refine the Stage 2 prompt over time. We don't wire this in v1 — the one-shot two-stage approach is usually enough for 10-persona tails.

**Consider adding** if: Phase 5 fidelity scores for tail personas consistently come in <3.5 across multiple runs, indicating the expansion prompt is systematically producing weak personas.

## Determinism

- Sobol seed from `tail_generator_seed`.
- Prompt hash (`tail_generator_prompt_hash`) recorded in `generator_metadata` so reruns are reproducible even if the prompt template shifts.
