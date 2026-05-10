# CourierFlow Copilot Eval Implementation Notes

Use these notes when creating or modifying repo code for the eval runner.

## Suggested Repo Paths

Prefer these paths unless the repo already has a better convention:

- Eval cases: `evals/copilot/cases/*.yaml`
- Candidate queue: `evals/copilot/candidates/*.yaml`
- Runner: `scripts/eval_copilot.py`
- Report output: `artifacts/copilot-evals/<timestamp>.json`

## Runner Flow

1. Load eval case YAML.
2. Authenticate as the fixture user.
3. Record baseline DB state.
4. POST the prompt to `/api/copilot/agent/default/run`.
5. Parse SSE events into assistant text and tool activity.
6. Query DB for expected changes.
7. Query Phoenix traces for spans newer than the run start timestamp.
8. Score deterministic assertions.
9. Write a JSON report and exit nonzero on failure.

## Minimal Copilot Request Body

```json
{
  "threadId": "eval-thread-create-basic-workflow",
  "runId": "eval-run-create-basic-workflow",
  "messages": [
    {
      "id": "eval-message-1",
      "role": "user",
      "content": "Create a basic move-in workflow for a new tenant."
    }
  ],
  "actions": []
}
```

Send it to:

```text
POST http://127.0.0.1:8123/api/copilot/agent/default/run
Authorization: Bearer <token>
Accept: text/event-stream
Content-Type: application/json
```

## Candidate Capture

When adding capture middleware or an offline parser, store only sanitized prompt
content. Link to Phoenix trace IDs rather than copying full trace content into
candidate files.

Candidate novelty heuristics:

- Exact normalized prompt already exists: skip.
- Same intent and same expected tools: skip unless failure/safety issue.
- New tool sequence: add candidate.
- New entity type or fixture need: add candidate.
- Runtime error or no Phoenix trace: add candidate.

## Deterministic Scorers

Start with code-based checks:

- workflow count increased by expected amount,
- newest workflow name/category matches,
- minimum step count met,
- required tool span names are present,
- no raw traceback markers in response,
- no "sent", "started", or "completed" claims after preview-only tools.

Only add LLM-as-judge scoring after deterministic checks are stable.

## Phoenix Evals

Phoenix can run evaluators over datasets/experiments. Use it for subjective
dimensions such as correctness, relevance, and conciseness. Keep security and
business-rule checks deterministic in Python.

Useful docs:

- https://arize.com/docs/phoenix
- https://arize.com/docs/phoenix/datasets-and-experiments/how-to-experiments/run-experiments
- https://arize.com/docs/phoenix/api/evaluation-models
