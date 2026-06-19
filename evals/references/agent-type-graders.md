# Agent-type grader playbook

Different agent types want different grader *stacks*. Pick the mix by
type, then drop to `phase-3` for how to build each grader. The unifying
rule across all types: **grade the outcome/end-state, not a prescribed
step sequence** (see `phases/phase-3-evaluators.md` "Grade the outcome,
not the trajectory").

Source: Anthropic, ["Demystifying evals for AI agents"](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

| Agent type | Primary graders | Add | Notes |
| --- | --- | --- | --- |
| **Coding** | Deterministic: unit tests pass *and* existing tests still pass | Static analysis (ruff, mypy, bandit); code-quality rubric (LLM-judge); tool-call verification | Lean hard on code-based graders — ground truth exists. Verify the change doesn't break the rest of the suite, not just that the new test goes green. |
| **Conversational** | Verifiable end-state outcome (task done) + interaction-quality rubric | **Second LLM to simulate the user** (persona + goal spec, pinned/versioned) | Score completion *and* interaction quality separately — a one-criterion-per-judge split. |
| **Research** | Groundedness (every claim traceable to a source) | Coverage (key facts present); source-quality check | Use LLM graders here, but calibrate frequently against expert human judgment — open-ended outputs drift. |
| **Computer use** | Backend/state verification | URL + page-state checks; run in a real or sandboxed environment | Assert on the world the agent changed, not the pixels it clicked. |

## Metric dimensions (report per-dimension, not one pass/fail)

An agent run can succeed on the outcome while failing on cost or safety.
Score each dimension separately so a single number doesn't hide a
regression:

| Dimension | Example |
| --- | --- |
| **Task success** | Refund processed correctly in the target system |
| **Tool selection** | Called `search_db` instead of `delete_record` |
| **Parameter correctness** | Passed `instance_id`, not `region_name` |
| **Efficiency** | Completed in 4 steps, not 12; token + latency budget held |
| **Safety / compliance** | No unauthorized data access or policy violation |

Efficiency is the one most often dropped — a correct-but-12-step run is
a real regression. Track steps, tool calls, latency, and tokens beside
the quality score (source: Braintrust, "Agent evaluation").

## Conditional (branching) scorers

Route the grader by what the agent did, not a fixed checklist. If the
agent made a tool call, score tool selection + parameter correctness;
if it answered directly instead, score the response for hallucination.
One fixed scorer applied to both branches mis-grades half the cases.

## Fault injection (resilience)

Deliberately break tools and external systems — time out an API, return
a malformed payload, 500 a downstream call — and grade how the agent
responds under stress (does it retry sanely, degrade gracefully, surface
the error, or silently corrupt state?). Outcome-only evals on a happy
path never exercise this (source: Braintrust, "Agent evaluation").

## Long-horizon agents: test near the context limit

For agents that run for thousands of turns / hundreds of millions of
tokens (autonomous operators, long-running assistants), **context-window
degradation is itself a failure mode to test** — not just an
implementation detail. As the window fills, models drift into repetition
loops, existential spirals, and incoherence; failures concentrate near
the limit, not uniformly across the run. Don't only eval short happy-path
traces: include long runs that actually approach the context ceiling, and
score for late-run coherence and on-task persistence. How the agent
manages its own context (summarization, sliding window, scratchpad files)
becomes part of what you're grading.

## Cross-cutting harness rule: isolate trials

Every trial starts from a **clean environment**. Agents mutate
state — shared state across trials means trial N's leftovers corrupt
trial N+1, and a "failure" may just be contamination from a prior run.
Isolate (fresh sandbox / reset fixture per trial) so a failure is
attributable to the trial, not the harness.

## See also

- `phases/phase-3-evaluators.md` — how to build each grader class.
- `phases/phase-1-design.md` — single-turn vs multi-turn vs agent
  framing; capability vs regression tagging.
- `references/outcome-grader.md` — separate-model outcome grading for
  managed-agent / production runs.
