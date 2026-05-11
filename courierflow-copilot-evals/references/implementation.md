# CourierFlow Copilot Eval Implementation Notes

Use these notes when creating or modifying repo code for the eval runner.

## Suggested Repo Paths

Prefer these paths unless the repo already has a better convention:

- Eval cases: `evals/copilot/cases/*.yaml`
- Candidate queue: `evals/copilot/candidates/*.yaml`
- Runner: `scripts/eval_copilot.py`
- Report output: `artifacts/copilot-evals/<timestamp>.json`

## Self-Improvement Iteration Contract

When the eval runner is used for Arise/Phoenix failure-mode work, it must make
baseline-vs-change comparison easy:

- Accept or record a fixed trace set ID from Alyx's Email #2 grouping.
- Include trace IDs in every per-case result.
- Write immutable baseline and candidate reports under separate artifact paths.
- Compare reports from the same trace set only.
- Print score delta, newly passing trace IDs, newly failing trace IDs, and
  unchanged failures.
- Exit nonzero if required safety or business-rule checks regress, even when the
  aggregate score improves.

Do not let the runner silently refresh, expand, dedupe, or replace the trace set
between baseline and candidate runs. That turns iteration into scoreboard
gardening, which is not engineering.

## Production Eval Operations

For production monitoring, the runner or scheduled job should:

- Sample real Copilot traffic after sanitization.
- Attach Phoenix trace IDs and deployment/version metadata to every scored run.
- Compare production scores against the shipped baseline for each fixed failure
  mode.
- Emit regression events when a previously fixed case fails again.
- Group unknown failures for later Alyx review instead of auto-promoting them.
- Publish CI/CD and dashboard-friendly JSON fields: pass rate, regression count,
  safety failures, latency, trace set ID, app version, and failure cluster.

Use CI/CD for the critical fixed eval set. Use dashboards for production drift
and new failure discovery.

## Runner Flow

1. Load eval case YAML.
2. Authenticate as the fixture user.
3. Record baseline DB state.
4. POST the prompt to `/api/copilot/agent/default/run`.
5. Parse SSE events into assistant text and tool activity.
6. Query DB for expected changes.
7. Query Phoenix traces for spans newer than the run start timestamp.
8. Score deterministic assertions.
9. Write a JSON report with case IDs, trace IDs, score, and artifact metadata.
10. If given a baseline report, compare against it and exit nonzero on
    regression.

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
