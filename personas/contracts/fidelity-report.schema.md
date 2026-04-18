# Contract: `$fidelity_report`

Output of Phase 5. PersonaGym 5-task scores per transcript, plus a pass/fail gate.

## Schema (JSON)

```json
{
  "run_id": "...",
  "scored_transcripts": [
    {
      "cell_id": "c001",
      "persona_id": "p01",
      "scores": {
        "action_justification": 4.2,
        "expected_action": 3.8,
        "linguistic_habits": 4.0,
        "persona_consistency": 4.5,
        "toxicity_control": 5.0
      },
      "mean_score": 4.3,
      "evaluator_ensemble": ["claude-sonnet-4-6", "claude-opus-4-7"],
      "passed_gate": true,
      "refusal_detected": false,
      "notes": "optional free-form"
    }
  ],
  "aggregate": {
    "pass_rate": 0.85,
    "by_task_mean": {
      "action_justification": 4.1,
      "expected_action": 3.9,
      "linguistic_habits": 4.0,
      "persona_consistency": 4.4,
      "toxicity_control": 4.9
    },
    "refusal_rate_per_persona": { "p01": 0.0, "p02": 0.5 }
  }
}
```

## Gate rule

A transcript passes if **all three** hold:

- Mean score across 5 tasks ≥ 3.5 (1–5 Likert).
- No single task score < 2.0.
- No refusal detected.

Failed transcripts are excluded from Phase 6 findings but retained for audit.

## Refusal detection

Independent of the 5-task score. Flags transcripts where the persona player broke meta-character ("as an AI, I...") or refused to role-play. Phase 6 uses `refusal_rate_per_persona > 0.2` as a signal to revisit Phase 2 (persona prompt issue, not an app issue).

## Persistence

Written to `docs/persona-eval/<app>/<run-id>/fidelity-report.json`.
