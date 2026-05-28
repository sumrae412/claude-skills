# Phase 1 — Eval Design

Decide what to measure before building anything.

## Step 1: Name the failure mode

Forget "quality." Write the specific bad behavior in one sentence:

- "The assistant invents API endpoints that don't exist."
- "The summary drops the most important bullet from the source."
- "The router picks the wrong tool when the user mentions two domains."
- "The agent calls the same tool twice in a row instead of giving up."

If you can't name the failure mode yet, read traces or interview
the user until you can — naming is the eval.

## Step 2: Pick metric type per failure mode

Match the failure mode to the cheapest evaluator class that can catch
it.

| Failure mode shape                          | Metric class                |
| ------------------------------------------- | --------------------------- |
| Has ground truth (label, expected output)   | Code-based: exact match, set overlap, regex, JSON schema, numeric tolerance |
| Has reference but output is paraphrased     | Code-based + embedding similarity, or LLM-judge "semantic match" |
| Open-ended (helpfulness, tone, faithfulness)| LLM-as-judge with a single criterion per call |
| Behavior in a system (tool calls, retries)  | Trace-based assertion on span attributes |
| Subjective taste (humor, brand voice)       | Human review on a sampled subset |

Default order of preference: **code > embedding > LLM-judge > human**.
Each step up costs more, has more noise, and is harder to debug.

## Step 3: Define the success criterion

Without a target, an eval is a thermometer with no fever line.

For each metric write:

- **Direction** — higher is better, or lower
- **Threshold to ship** — e.g. "≥0.85 faithfulness on prod-sampled set"
- **Threshold to gate CI** — e.g. "no regression > 3 pts vs. baseline"
- **Sample size assumption** — e.g. "N=200 examples, 3 repetitions"

If you can't fill these in, the metric isn't ready.

## Step 4: Cost and latency budget

Estimate before building:

- examples × repetitions × evaluator-calls-per-example × judge-model-cost
- wall-clock per run (matters if this gates CI)

If a full eval costs more than $20 or takes more than 10 minutes, plan
a tiered setup: a small smoke set on every CI run, the full set on
nightly / pre-release.

## Step 5: Write the one-pager

Hand back to the user before any code:

- Failure modes (named, in their words)
- Metric per failure mode (type + name)
- Dataset size & source plan
- Evaluator(s) to build
- Success / gating thresholds
- Cost & latency estimate

Get sign-off here. Building the harness before alignment is the most
common waste in eval work.
