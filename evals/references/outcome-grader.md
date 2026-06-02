# Outcome Grader

A separate-model invocation that judges an agent's final output
against explicit success criteria. The eval moves from "measurement"
to "gate" — the grader's verdict decides whether the task is done or
the agent retries.

Adapted from `verification-before-completion/references/outcome-grader.md`.
The canonical reference is the Anthropic Cookbook:

> Anthropic Claude Cookbook —
> `managed_agents/CMA_verify_with_outcome_grader.ipynb`
> https://github.com/anthropics/claude-cookbooks/blob/main/managed_agents/CMA_verify_with_outcome_grader.ipynb

The notebook walks through coordinating a primary agent with a
separate grader model, encoding success criteria as a grader prompt,
and using the verdict to gate completion or trigger a retry.

## Why a separate model

A primary agent rationalizing *"close enough"* is structurally
unable to grade itself reliably — the model that decided "done" is
the wrong evaluator for whether "done" matches the spec. A separate
invocation with different context (just the spec + the output, not
the trajectory) is the cleanest fix.

This is the production cousin of the LLM-as-judge pattern in
`phases/phase-3-evaluators.md`. Same machinery; the difference is
the verdict drives behavior, not just a dashboard.

## When to reach for this pattern

- **Managed-agent / background-agent runs** where no human reviews
  each step. The grader is the only check between agent output and
  downstream consumers.
- **Multi-step tool-using agents** where intermediate steps may
  succeed but the final outcome can still miss the requirement.
- **Production workflows that bill or notify users on completion** —
  false-positive completions have real cost.
- **Long-running tasks** where the model's own context is degraded
  by the time it claims done.

## When NOT to reach for it

- **Dev-loop work with a human in the session** — the human is the
  grader. The default Phase 3 measurement pattern is correct.
- **Cheap, fast tasks** — doubling inference on every completion is
  over-engineering. Reserve the gate for tasks where a false-positive
  completion costs more than an extra round-trip.
- **When acceptance criteria aren't writable as a prompt** — if you
  can't articulate success precisely enough for a separate model to
  check, the primary agent doesn't have a target either. Fix the
  criteria first.

## Design checklist

Before shipping an outcome grader:

- [ ] Success criteria are written, not implicit. The grader prompt
      can be read by someone who's never seen the system.
- [ ] Grader uses a *different* model than the primary agent (or at
      minimum a different prompt, different context, and ideally a
      stronger model).
- [ ] Grader returns a structured verdict (`pass | fail | retry`),
      not free-form prose.
- [ ] Retry budget is bounded **and the exhaustion behavior is
      defined**: when retries are spent, does the system return the
      best-of-N output, fail the task and surface the error,
      escalate to a human reviewer, or page the on-call team? Pick
      per failure mode — silent best-of-N on a billing or
      notification task is worse than a clean fail.
- [ ] Grader is calibrated against ≥30 human-labeled completions
      before it gates anything in production (see
      `references/judge-calibration.md`).
- [ ] Grader prompt and grader model are versioned alongside the
      agent. A grader change is a deploy.
- [ ] Cost and latency of the grader call are accounted for in the
      task's budget.

## Relationship to other eval phases

- **Phase 1 (design)** — success criteria for the grader are exactly
  the success criteria from the design one-pager. If the design
  step was skipped, build the grader from a written spec first.
- **Phase 3 (evaluators)** — the grader is an LLM-judge with one
  criterion: "does this output meet the spec?" All Phase 3 rules
  apply (one criterion, binary verdict, reason-then-label,
  calibrated).
- **Phase 4 (running)** — in offline mode, grader verdicts flow into
  the same aggregate metrics. In production, the verdict gates the
  task; log every verdict + reasoning so you can audit later.

The grader does not replace offline evals. It complements them:
offline evals tell you whether the grader itself is right; the
grader tells you whether each individual production task is done.

## Three-outcome parser contracts

A binary grader contract (`PASS` / `FAIL: <reason>`) looks complete
but hides a third real outcome: **format violation** — the model
returned a refusal, hedged prose, an unrecognized token, or a string
that doesn't match either branch of the contract. Silently coercing
those to `FAIL` contaminates the pass-rate signal and hides judge
regressions.

Define three outcomes in the parser, not two:

| Output shape                  | Action                                              |
|-------------------------------|-----------------------------------------------------|
| `PASS`                        | Record pass.                                        |
| `FAIL: <reason>`              | Record fail, capture reason.                        |
| Anything else                 | **Raise** (or surface in the result artifact as a distinct `format_violation` status). Never coerce to `FAIL`. |

Why it matters:

- Format-violations track **judge health**, not task health. A spike
  in format-violations means the judge is regressing (model
  deprecation, prompt drift, upstream API change) and needs
  attention — that signal disappears if violations are mapped to
  `FAIL`.
- Composes with the snapshot-pin rule (`references/judge-calibration.md`)
  — pin the judge model AND fail-loud on unexpected output shape.
- For production graders, route format-violations to the retry /
  escalation path defined in the design checklist above, not to the
  `fail` path.

Pattern from
[Shredmetal/llmtest](https://github.com/Shredmetal/llmtest/blob/main/docs/reliability_testing/behavioral_testing_reliability.md)
(strict PASS / FAIL:<reason> / RuntimeError contract).

## Alternative patterns

A separate LLM-grader is one approach. Equivalent or better choices
depending on the task shape:

- **Rule-based / deterministic finalizers** — when success is
  expressible as schema validation, regex, set-membership, or
  numeric tolerance, skip the LLM grader entirely. Cheaper, faster,
  fully deterministic, and not subject to judge drift.
- **Secondary classifier ensembles** — for safety / policy
  gating, a small fine-tuned classifier (or an ensemble of them)
  often beats an LLM judge on precision-at-fixed-recall and
  costs less per call.
- **Human-in-the-loop on a sampled subset** — for high-stakes or
  legally regulated tasks, accept that the highest-quality signal
  is a human review on a sampled fraction of completions; the LLM
  grader runs as a triage layer that selects which completions a
  human should see.

Reach for the LLM-grader pattern when the success criterion is
genuinely open-ended (free-text generation, multi-step plan
quality) and not reducible to one of the above.
