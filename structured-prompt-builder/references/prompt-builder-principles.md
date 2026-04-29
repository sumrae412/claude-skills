# Prompt Builder Principles

## Reviewed Sources

- OpenAI Prompt guidance for GPT-5.5 / GPT-5.x models, verified 2026-04-29:
  https://developers.openai.com/api/docs/guides/prompt-guidance?model=gpt-5.5
- `prompt-optimization/SKILL.md`: metrics, trace analysis, challenger prompts.
- `prompt-governance/SKILL.md`: prompt ownership, evals, rollout, rollback.
- `context-engineering/SKILL.md`: context hierarchy, packing, ambiguity.
- `smart-exploration/SKILL.md`: task-classified subagent prompts.
- `token-economy/SKILL.md`: compact tool use and subagent reporting.
- `brevity/SKILL.md`: no-preamble and output minimalism.

## Synthesis

Strong prompts behave like contracts, not vibes. They define the goal,
available context, exact actions, ambiguity policy, tool rules, output format,
and completion criteria. The more autonomous or expensive the workflow, the
more the prompt needs explicit verification and eval hooks.

OpenAI's guidance for current GPT-5.x models emphasizes:

- structured output contracts for compact, predictable responses
- explicit autonomy and persistence rules for coding/tool agents
- sparse, high-signal user updates during long work
- reasoning effort tuned by task shape rather than raised by default
- Responses API reasoning persistence for multi-turn tool workflows
- explicit completion, verification, and tool-persistence contracts before
  increasing reasoning effort
- more structure for smaller models, including closed outputs and examples
- one-change-at-a-time prompt migration and eval-based iteration

Existing local skills add:

- prompts are code and need eval gates when production-facing
- optimize from observed failure buckets, not taste
- pack only useful context and provide one pattern example when style matters
- keep prompts and subagent reports compact enough to be followed
- route image prompts, production governance, and empirical variant promotion to
  their specialist skills

## Trigger Boundaries

Use `structured-prompt-builder` for creating or repairing the prompt itself.
Use `prompt-governance` when the question is about lifecycle infrastructure:
registry, owners, versioning, rollout, rollback, A/B tests, or CI evals.
Use `prompt-optimization` when there are traces, variants, scores, or a
promotion decision. Use `context-engineering` when the issue is what context an
agent should see rather than how the prompt should be written.

## Prompt Quality Checklist

1. Does the first paragraph say what the model must accomplish?
2. Are critical constraints before examples?
3. Are inputs and placeholders named?
4. Are steps ordered and dependency-aware?
5. Is tool use defined by when, how, and how to recover?
6. Is ambiguity behavior explicit?
7. Is output format enforceable?
8. Are edge cases included?
9. Is there a verification loop?
10. Is there an eval or rubric when quality matters?
11. Is the prompt shorter than the behavior requires?
12. Does it avoid requesting hidden chain-of-thought?

## Common Repairs

- Vague goal -> define success and non-goals.
- Chatty output -> add a concrete output contract.
- Model asks too many questions -> define when to ask vs proceed.
- Model stops early -> add completion contract and persistence.
- Tool misuse -> add dependency-aware tool rules and recovery.
- Flaky structured output -> add schema, field semantics, and one example.
- Shallow answer -> add verification loop and edge-case pass.
- Overlong prompt -> delete duplicated rules and move examples after rules.
- Regressions -> add golden cases before rewriting again.

## Reusable Prompt Skeleton

```text
<role_and_goal>
You are [role]. Your task is to [goal].
</role_and_goal>

<critical_rules>
- [Rule that would cause failure if missed.]
- [Constraint or non-goal.]
</critical_rules>

<inputs>
- [input_name]: [meaning]
</inputs>

<workflow>
1. [First action.]
2. [Second action.]
3. [Verification or synthesis action.]
</workflow>

<ambiguity_policy>
Ask one clarifying question only if [condition]. Otherwise proceed using
conservative assumptions and label them.
</ambiguity_policy>

<output_format>
[Exact sections, JSON schema, table, or prose shape.]
</output_format>
```
