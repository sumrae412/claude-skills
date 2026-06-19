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

### Single-turn, multi-turn, or agent?

Classify the surface before picking metrics — it changes everything
downstream:

- **Single-turn** — prompt → response → grade. The default this skill
  assumes elsewhere.
- **Multi-turn / agent** — the system calls tools and mutates state
  across turns. Mistakes **propagate and compound**: a wrong tool call
  on turn 2 poisons every later turn, so a single end-of-run score
  hides *where* it broke. Grade the **end-state/outcome**, and add
  trace assertions for the steps that are load-bearing (see
  `phase-3` "Span / trace evaluators").
- **Conversational agent** — to exercise multiple turns you usually
  need a **second LLM to simulate the user**, driven by a persona +
  goal spec. The simulator is itself a prompt — pin and version it,
  or your eval moves when the simulator moves.

Pick the **evaluation level** to match — these map to what your tracing
captures:

- **Run-level** — one decision/step (did it pick the right tool, with
  valid params?). Unit-test-like.
- **Trace-level** — one full turn (right tools called, output correct,
  correct end-state/artifacts?). **Start here** — it's the level that
  catches the most with the least harness.
- **Thread-level** — a multi-turn conversation (does context accumulate
  correctly across turns?). Use conditional logic to check after each
  turn and **fail early** when it goes off track.

Don't start at run-level — step-by-step asserts are brittle and miss
whole-task failures. Add run-level checks only for the few steps that
are load-bearing.

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

For **agents**, don't measure only task success — report a metric
*per dimension*: task success, tool selection, parameter correctness,
**efficiency** (steps taken, tool calls, latency, tokens), and
safety/compliance. A run that succeeds in 12 steps when 4 would do is a
real regression a pass/fail score hides. See
`references/agent-type-graders.md` for the dimension table.

## Step 3: Define the success criterion

Without a target, an eval is a thermometer with no fever line.

For each metric write:

- **Direction** — higher is better, or lower
- **Threshold to ship** — e.g. "≥0.85 faithfulness on prod-sampled set"
- **Threshold to gate CI** — e.g. "no regression > 3 pts vs. baseline"
- **Sample size assumption** — e.g. "N=200 examples, 3 repetitions"

If you can't fill these in, the metric isn't ready.

### Capability eval or regression eval? (opposite targets)

Tag every eval set as one of two kinds — they want *opposite*
pass-rates:

- **Capability eval** — "what can this agent do well?" Should **start
  at a low pass rate**; the headroom is the point. A capability set
  sitting at 100% is **saturated** — it no longer guides improvement.
  Retire it, or harden it with cases the agent currently fails.
- **Regression eval** — "does the agent still handle what it used to?"
  Target **~100%**; any drop is a real regression and gates CI.

The same pass-rate number means opposite things depending on the tag.
"Saturation is not success" — a capability eval pinned at 100% is a
dead thermometer, not a win.

**Validity gate — does it discriminate?** A good capability eval
*separates* strong models from weak ones. If every model scores the
same — all at chance (too hard / measuring something none can do) or
all bunched near the top in the noise band (saturated) — the eval isn't
measuring capability, it's measuring nothing. Before trusting an eval,
confirm a known-strong model beats a known-weak one on it by more than
the noise floor. Where you can, prefer an **unbounded outcome metric**
(dollars earned, items handled, steps-to-goal) over a bounded
percentage: an open-ended metric has headroom and never saturates,
where a % pins at 100 and goes dark.

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
