# Phase 5 — Fidelity Gate

**Purpose:** Did the persona actually hold character? Filter out transcripts where the persona player refused, broke character, or was incoherent. Produce `$fidelity_report`.

**Cost:** 5 scores × ensemble size × transcript count. Default: 5 × 2 × 50 = 500 evaluator calls.

## Why this exists

Without a fidelity gate, persona-based testing reduces to whatever biases the role-play model happens to have. PersonaGym's 5-task rubric correlates ~0.75 Spearman with human judgment of persona fidelity (Samuel et al. 2025). We use the 5 tasks directly and gate on both mean and min.

## The 5 tasks (1–5 Likert each)

1. **Action Justification** — every persona action has a plausible rationale tied to the backstory.
2. **Expected Action** — a real user matching this persona would realistically take these actions.
3. **Linguistic Habits** — language matches `communication_style`.
4. **Persona Consistency** — character held across turns (no drift to generic assistant).
5. **Toxicity Control** — no harmful or inappropriate-for-persona content.

Full rubric anchors in `references/personagym-rubrics.md`.

## Ensemble evaluation

Use `$app_config.model_config.fidelity_evaluators` (minimum 2 models, prefer different families).

**Never self-evaluate.** If `persona_player = claude-sonnet-4-6`, remove Sonnet from that transcript's evaluator ensemble — or explicitly accept the self-eval bias and log it.

Per (transcript, task, evaluator) → one score. Mean across evaluators = task score. Mean across tasks = transcript score.

## Refusal detection

Independent check. Flag transcripts where the persona player:

- Output "I can't role-play as this persona" or similar.
- Broke meta-character ("as an AI, I...").
- Refused a benign persona request.

Regex pre-filter + 1 LLM-aided confirmation call per flagged transcript. Tracked per-persona as `refusal_rate_per_persona`. Rate >20% for a given persona → **Phase 2 fault** (persona prompt issue), not an app fault.

## Gate rule

Transcript passes if **all three** hold:

- Mean score across 5 tasks ≥ 3.5.
- No single task score < 2.0.
- No refusal detected.

Failed transcripts are **excluded from Phase 6 findings** but retained in `$fidelity_report` for audit.

## Run

```bash
python scripts/score_fidelity.py score \
  --transcripts <run-dir>/eval-transcripts.json \
  --pool <run-dir>/persona-pool.json \
  --evaluators "claude-sonnet-4-6,claude-opus-4-7" \
  --out <run-dir>/fidelity-report.json
```

## Output

Write `$fidelity_report` to `<run-dir>/fidelity-report.json`.

## Next

Proceed to Phase 6: `phases/phase-6-report.md`.
