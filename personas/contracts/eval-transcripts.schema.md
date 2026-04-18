# Contract: `$eval_transcripts`

Output of Phase 4. One transcript per cell from `$testing_matrix`.

## Schema (JSON)

```json
{
  "run_id": "...",
  "transcripts": [
    {
      "cell_id": "c001",
      "persona_id": "p01",
      "flow_name": "...",
      "testing_style": { "mindset": "...", "strategy": "...", "habit": "..." },
      "runner_backend": "website-tester | playwright-test | http | bash | llm-to-llm",
      "started_at": "ISO-8601",
      "ended_at": "ISO-8601",
      "steps": [
        {
          "step_index": 0,
          "persona_utterance": "string — what the persona 'said' or decided, in character",
          "action": "click | type | navigate | api_call | command | message",
          "action_detail": { "selector": "...", "value": "..." },
          "app_response": "raw response (HTML snippet, HTTP body, stdout, chat reply, or stack trace)",
          "observation": "persona's interpretation of what they saw",
          "ui_observations": ["short in-character notes about UI issues the persona noticed but kept going past"]
        }
      ],
      "outcome": "success | stuck | crash | error | max_steps",
      "outcome_detail": "one-line explanation",
      "app_errors": [
        { "type": "crash | functional | warning", "message": "...", "step_index": 3 }
      ],
      "usefulness_reflection": {
        "rating": "integer 1-5",
        "would_use": "yes | no | maybe",
        "quote": "2-3 sentences in persona voice: how they'd describe the app to a friend",
        "biggest_draw": "what worked for them, or null",
        "biggest_blocker": "what would keep them from using it, or null"
      }
    }
  ]
}
```

## Outcomes

- `success` — persona hit the flow's `success_criteria`.
- `stuck` — persona stopped progressing with no app error (couldn't figure out what to do next).
- `crash` — unrecoverable app error: unhandled exception, HTTP 500, hang, segfault.
- `error` — app returned an expected-shape response that was wrong (persona-reported).
- `max_steps` — persona hit `flow.max_steps` without reaching success.

## UI observations vs bugs vs friction

Three distinct signals, separate fields:

- **`app_errors[]`** — app misbehaved (crash, wrong response).
- **`ui_observations[]` per step** — persona noticed-but-kept-going UI concerns (confusing label, unclear button, cramped layout, vague error copy). Preserved even when `outcome == success`.
- **`outcome in {stuck, max_steps}`** — persona gave up. Drives Friction Findings in Phase 6.

## Usefulness reflection

Written at cell termination (any outcome). In-character rating + quote captured by an extra LLM call — see `references/usefulness-interview.md` for the prompt and rating anchors. Drives the Usefulness Assessment section of the Phase 6 report.

## Persistence

- Full roll-up: `docs/persona-eval/<app>/<run-id>/eval-transcripts.json`
- Per-cell files: `docs/persona-eval/<app>/<run-id>/transcripts/<cell_id>.json`
