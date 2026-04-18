---
name: personas
description: Run simulated alpha or beta user testing on apps using diverse synthetic personas. Produces a diverse user population (Nemotron fat middle + generator tail), drives the app through multiple testing styles, checks persona fidelity, and reports bugs, UI snags, friction, usefulness ratings, and coverage. Use when: "alpha or beta test this app with simulated users", "assess usability before launch", "find UI snags", "see if personas would actually use this", "run persona-based eval", "test with diverse synthetic users", "find UX bugs before real users".
---

# Personas — Simulated Alpha & Beta User Testing

Generate a diverse synthetic user population, run it against an alpha- or beta-stage app, and produce an actionable report: bugs triggered, flows where personas got stuck, UI snags they flagged, usefulness ratings by user type, and which segments the app underserves.

**This pre-vets an app; it does not replace real user testing.** Use findings to prioritize fixes, sharpen the UI, and shape the real user-testing session that follows.

Three lenses per run:

- **Usability** — can each persona actually operate the app? (captured by `stuck` / `success` outcomes)
- **UI quality** — what snags do they hit even when they get through? (captured by per-step `ui_observations`)
- **Usefulness** — do they actually want this once they've used it? (captured by a per-cell in-character reflection)

## When to use

- App is at alpha or beta stage — enough to use, pre-launch or in early release.
- Want coverage across diverse user types, including edge cases real recruitment won't produce.
- Want to find crash/friction bugs that random testing misses because it has no user intent.
- Want to assess UI snags (confusing labels, unclear affordances, layout issues) and usefulness (would this persona actually use the app) before inviting real users.
- **Do not use** for production monitoring (too expensive, too slow) or as the sole signal for validating design decisions — real human feedback is still required.

## Related skills (don't confuse)

- `synthetic-persona` — models **one specific real person** from public data for pitch rehearsal / 1-on-1 feedback. Qualitative, N=1.
- `personas` (this skill) — synthetic **population** for quantitative coverage + bug discovery. N=25+.
- `website-tester` / `playwright-test` — drive a web app programmatically. This skill uses them as backends in Phase 4.

## Invocation contexts

- **Standalone** — run directly when a pre-launch app needs a synthetic beta pass. Primary entry point.
- **Post-merge follow-up from `/claude-flow`** — Phase 6 offers `/personas` as an optional pass for features that touched user-facing flows (see `claude-flow/phases/phase-6-quality.md` §Optional follow-up). Non-gating — surfaced as an offer, skipped if the user declines.

## Pipeline

Six phases; each reads a named contract from the prior and writes one to the next. See `contracts/` for schemas.

| Phase | Purpose | Reads | Writes |
|-------|---------|-------|--------|
| 1. App Config | Elicit app, segments, axes, flows | (user input) | `$app_config` |
| 2. Pool Build | Nemotron filter + two-stage tail generator | `$app_config` | `$persona_pool` |
| 3. Testing Matrix | Layer PersonaTester 3D for GUI apps | `$persona_pool`, `$app_config` | `$testing_matrix` |
| 4. Run Eval | Dispatch each cell to app-appropriate runner | `$testing_matrix` | `$eval_transcripts` |
| 5. Fidelity Gate | PersonaGym 5-task rubric; filter broken-character transcripts | `$eval_transcripts`, `$persona_pool` | `$fidelity_report` |
| 6. Report | Aggregate coverage + bugs + friction | `$fidelity_report`, `$eval_transcripts` | `$eval_report` → `docs/persona-eval/` |

Load phase files on demand: `phases/phase-N-<name>.md`.

## Entry flow

1. **Check saved config.** Look for `docs/persona-eval/<app>/config.yaml`. If present, offer to reuse or re-elicit.
2. **Phase 1.** Elicit or load `$app_config`. Validate against `contracts/app-config.schema.md`.
3. **Phases 2–6 run in order.** Each writes its contract output to `docs/persona-eval/<app>/<run-id>/` for audit.
4. **Save final report** to `docs/persona-eval/<app>/YYYY-MM-DD-<run-id>.md`.

Each phase file states its own cost profile so the user can skip or subsample.

## Model choice

**Persona role-play:** Sonnet 4.6 or Opus 4.7. **Never Haiku** — PersonaGym finding: Claude 3 Haiku refuses persona role-play 8.5× more than the next-highest model; the failure mode persists in later Haiku versions unless specifically tested.

**Fidelity evaluator:** ensemble of 2 models from different families when possible (e.g., Sonnet + Opus). Avoid self-evaluation (same model as persona player and evaluator).

**Deterministic work** (filtering, scoring, aggregation): scripts in `scripts/`, no LLM.

## Cost control

Full matrix (all personas × all testing styles × all flows) blows up fast. Defaults in `phase-3-testing-matrix.md`:
- 25 personas (15 Nemotron + 10 tail)
- 2 testing styles per persona (stratified sample from 9 combinations)
- All flows per cell, but each flow capped at 10 interaction steps
- → ~50 eval cells per run, ~500 LLM calls total

Scale up only after a first pass confirms the pipeline produces useful findings.

## Output

- **Primary:** `docs/persona-eval/<app>/YYYY-MM-DD-<run-id>.md` — human-readable report.
- **Audit trail:** `docs/persona-eval/<app>/<run-id>/` — all phase contracts, transcripts, scores.
- **Persona pool cache:** `docs/persona-eval/<app>/pool.json` — reuse across runs unless axes change.

## Next steps after a run

- High-friction personas → real-user recruitment profile.
- Crash/functional bugs → bug tracker.
- UI snag clusters → design review.
- Low usefulness ratings by persona cluster → revisit product-market fit for that segment (or refine onboarding to communicate value).
- Uncovered diversity axes → flag in report; consider expanding tail pool.
- Low fidelity scores → persona prompt refinement (Phase 2 issue, not an app issue).

## References

Grounded in three papers; load on demand:
- `references/two-stage-generator.md` — Paglieri et al. 2026, diverse synthetic persona generation via evolutionary search.
- `references/personagym-rubrics.md` — Samuel et al. NAACL 2025, 5-task decision-theory fidelity eval.
- `references/personatester-schema.md` — iGUITest, 3D testing-behavior schema for GUI apps.
- `references/nemotron-filter.md` — how to filter nvidia/Nemotron-Personas-USA by segment.
