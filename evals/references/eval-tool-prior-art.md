# Eval-Tool Prior Art

When standing up a new eval surface, two OSS projects ship variants of the patterns this skill teaches. Read these before you write a fourth bespoke harness — but with the caveat that neither matches every requirement, and both impose architectural shape you may not want.

## Shredmetal/llmtest — behavioral testing for LLM apps

[GitHub](https://github.com/Shredmetal/llmtest) · Python, MIT, ~17 stars (small, active)

**Form factor:** `behavioral_assert.assert_behavioral_match(actual_output, expected_behavior)` — an `assert(str, str)` that fails the test if an LLM judge says the output doesn't match the natural-language expectation. Drops into pytest / CI exactly like any other assertion.

**Philosophy worth borrowing:** treat LLM apps as closed-source third-party libraries. Test the *interface boundary* and application-level behavior — not the model's internal metrics. Behavioral tests as a fast, cheap first line of defense before expensive benchmarking. Validated by the authors across 30,000 test executions with explicit non-determinism mitigations.

**When this maps to your problem:**

- You're writing graders that compare a Charlie reply against a natural-language expectation (semantic-consistency, state-default-phrasing, refuse-and-refer wording checks). The `assert(actual, expected_behavior)` shape is exactly what those graders already do under the hood — `llmtest` packages it.
- You want behavioral test coverage in CI without standing up a dataset / experiment platform.

**When it doesn't fit:**

- You need structured fixtures, pre/post state diffing, or tool-call trace verification (outcome-validator class). `llmtest` is single-call assert; the outcome validator pattern needs more architecture.
- You need calibration sets, paired analyses, or regression-gate semantics. `llmtest` is per-assertion, not per-experiment.
- You're already on a runner with cost meters, judge-sample retries, and result artifacts (courierflow_beta `tools/phoenix/run_evals.py`). The behavioral-assert call shape is borrowable; the framework is redundant.

## google/litmus — GCP-native LLM testing platform

[GitHub](https://github.com/google/litmus) · Python, GCP-first, not an official Google product

**Form factor:** Full-stack eval platform — Proxy → API → Worker → UI — running on Cloud Run + Firestore + BigQuery + Vertex AI. Supports "Test Run" (single-turn) and "Test Mission" (multi-turn). Three evaluator backends:

- **Custom LLM Evaluation** — tailored prompts comparing actual vs expected reply
- **Ragas** — RAG metrics: relevancy, recall, precision, harmfulness
- **DeepEval** — LLM-based metrics: faithfulness, hallucination, bias, toxicity

**Worth borrowing — vocabulary:**

- "Test Mission" as the multi-turn unit of evaluation (vs. single-shot "Test Run") — useful naming when explaining graders to non-eval-natives.
- Proxy-as-monitoring-substrate — every LLM call passes through a recorded boundary, used for both evaluation and production drift detection.
- The Ragas / DeepEval metric names are widely recognized across the field; using their vocabulary (`faithfulness`, `hallucination`, `precision@K`) saves explanation cost in any cross-team conversation.

**When it doesn't fit:**

- You're not on GCP. The Firestore + Cloud Run + BigQuery + Vertex AI stack is structural, not optional.
- You want a single-runner Python file you can read end-to-end. Litmus is a full platform with multiple services and a UI; the cost of operating it exceeds its value for a small surface.
- Your dominant failure mode is operational hygiene (judge-error rate caps, multi-sample agreement, cost meters). Litmus's evaluator backends are general-purpose; the operational gates this skill cares about are layered on top.

## How to apply

When designing a new eval surface, run a five-minute "is one of these a better starting point than my hand-roll?" check:

1. **Pure behavioral-assert use case** (one input → one Charlie reply → does it match an English spec?) → consider `llmtest` directly, or borrow the `assert(actual, expected_behavior)` shape into your existing runner.
2. **Multi-turn, RAG-heavy, GCP-native** → consider `litmus`, or at minimum borrow Ragas / DeepEval as your evaluator backend.
3. **Anything else** (custom fixtures, state-diff outcome validation, tool-call trace verification, regression-gate semantics, cost meters, multi-sample agreement) → stay on your own runner, but cite the vocabulary and architectures from both projects in your design docs so reviewers know you considered the alternatives.

## Composes with

- This skill's "One judge, one criterion" rule — `llmtest`'s `assert_behavioral_match` violates this if you write a kitchen-sink expectation string. Constrain each expectation to one axis.
- This skill's calibration-set sizing — both tools punt on calibration; you still own the N≥30 (or domain-tier larger) gate.
- `/llm-cost-optimizer` — both tools call judges in the test path; the cost-gate triad (combined meter, repetition cap, paths-negation) still applies.

## Public agent benchmark landscape

When calibrating your eval surface or validating discriminative power,
these benchmarks are the established reference points as of mid-2026:

| Benchmark | Domain | Notes |
| --- | --- | --- |
| **SWE-bench Verified** | Code / software engineering | Human-verified subset of SWE-bench; standard bar for coding agents |
| **τ-bench / τ2-bench** | Tool use / agentic tasks | Tool-interaction tasks across domains; τ2 adds multi-hop tool chains |
| **GAIA** | General assistant / multi-step | "General AI Assistants" — multi-step web + tool tasks; hard for current models |
| **WebArena / OSWorld** | Web / desktop computer use | Real browser and OS interaction; high fidelity, slow to run |
| **AgentRewardBench** | Reward model / judge quality | Meta-benchmark for grading how well judge models rank agent outputs |

**Saturation and validity concern:** public benchmarks saturate as
models overfit to their format and training corpora. Watch for:
- "Do-nothing" baselines passing tests designed around specific action
  sequences.
- Rigid step-sequence grading penalizing valid alternative solutions
  (same failure mode as the "grade outcome, not trajectory" rule in
  `phases/phase-3-evaluators.md`).
- Contamination of training data with benchmark items.

Use public benchmarks as a **calibration check** on your own eval
surface (does our eval discriminate the same way SWE-bench does?),
not as a replacement for domain-specific evals on your actual
production failure modes.

## Sources

- Shredmetal/llmtest — [github.com/Shredmetal/llmtest](https://github.com/Shredmetal/llmtest) (MIT, 2025–2026).
- google/litmus — [github.com/google/litmus](https://github.com/google/litmus) (not official Google project; Apache 2.0).
