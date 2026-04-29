---
name: structured-prompt-builder
description: "Create, rewrite, or critique prompts for LLMs, agents, system instructions, developer instructions, user prompts, tool-use workflows, evaluation prompts, or reusable prompt templates. Auto-trigger when the user asks for a prompt, prompt creator, prompt rewrite, meta-prompt, agent prompt, system prompt, instruction hierarchy, output format, few-shot examples, JSON/schema prompt, tool-use prompt, or to make an AI assistant behave more reliably. NOT for image-generation prompts (use image-generation), production prompt registries/A-B tests/eval pipelines (use prompt-governance), empirical prompt variant promotion (use prompt-optimization), or broad context-loading strategy (use context-engineering)."
---

# Structured Prompt Builder

## Purpose

Build prompts that are explicit, testable, and hard to misread. Use this
skill to turn vague intent into a production-quality prompt or to repair a
prompt that is too broad, brittle, chatty, underspecified, or hard to
evaluate.

This skill combines:

- OpenAI prompt guidance for GPT-5.5 / GPT-5.x style models.
- `context-engineering` context-packing rules.
- `prompt-governance` eval and rollback discipline.
- `prompt-optimization` failure-bucket and challenger drafting discipline.
- `token-economy` compactness and subagent prompt hygiene.
- `brevity` response-shape control.

## When to Use

Use when the user asks to:

- write, improve, or debug an LLM prompt
- create a prompt template, system prompt, agent prompt, or meta-prompt
- define assistant behavior, tool-use rules, output structure, or examples
- make a prompt more reliable, concise, robust, autonomous, or eval-ready
- convert messy instructions into a reusable prompt artifact

Route elsewhere when the task is really:

- image prompt writing -> `image-generation`
- prompt versioning, rollout, A/B tests, CI evals -> `prompt-governance`
- selecting/promoting prompt variants from trace data -> `prompt-optimization`
- deciding what project context to load -> `context-engineering`
- reducing production LLM spend -> `llm-cost-optimizer`

## Core Workflow

1. Identify the prompt job.
   - `new`: create from user intent.
   - `rewrite`: improve an existing prompt.
   - `diagnose`: explain failure modes before rewriting.
   - `template`: create a reusable prompt with placeholders.
   - `eval`: create scoring criteria or test cases.
2. Extract the prompt contract.
   - Goal: what success looks like.
   - Audience/model: who or what will run it.
   - Inputs: required variables, optional context, tools, files, constraints.
   - Actions: exact steps the model should take.
   - Ambiguity behavior: ask, assume, abstain, or proceed with stated assumptions.
   - Output: format, length, sections, schema, examples, and forbidden extras.
   - Verification: checks before final answer.
3. Ask only if a missing detail would change the prompt materially. Otherwise,
   make conservative assumptions and label them.
4. Draft the prompt in the smallest structure that controls the behavior.
5. Add an evaluation block when quality matters.
6. Deliver the prompt first, then brief notes on assumptions or usage.

## Prompt Architecture

Prefer this order unless the user's target platform requires another format:

1. Role and goal
2. Critical rules
3. Inputs and available context
4. Step-by-step workflow
5. Tool-use rules, if any
6. Ambiguity and refusal behavior
7. Verification loop
8. Output format
9. Examples, only when they reduce ambiguity

Use XML-style blocks for long or fragile sections because they create clear
boundaries:

```text
<role_and_goal>
...
</role_and_goal>

<critical_rules>
- ...
</critical_rules>

<workflow>
1. ...
</workflow>

<output_format>
...
</output_format>
```

## Reliability Rules

- Put critical rules first. Do not bury constraints after examples.
- Be specific about what counts as done.
- Separate "do the work" from "report the work."
- Define when to ask a clarifying question. Do not let the model ask by reflex.
- Prefer positive instructions over only prohibitions.
- For smaller or cheaper models, use more structure: numbered steps, closed
  outputs, explicit edge cases, and one correct example.
- For agentic/tool workflows, include persistence, tool discipline, and
  dependency ordering.
- For research tasks, include source quality, citation format, empty-result
  recovery, and verification rules.
- For structured outputs, include a schema plus semantic rules for each field.
- Avoid "output nothing else" unless scoped to a final artifact; it can suppress
  useful recovery behavior.

## Agentic Prompt Blocks

Use these blocks when the prompt controls an agent that can use tools.

```text
<autonomy_and_persistence>
Persist until the task is fully handled end-to-end within the current turn
whenever feasible. Do not stop at analysis or partial work. Carry the work
through execution, verification, and a concise outcome report unless the user
explicitly pauses or redirects you.
</autonomy_and_persistence>
```

```text
<tool_persistence_rules>
- Use tools when the answer depends on files, current data, external state, or
  verification.
- Batch independent reads/searches when possible.
- Do not re-read unchanged files.
- After tool use, continue from the evidence instead of restarting analysis.
- If a tool fails, recover once with a narrower query or alternate source before
  asking the user.
</tool_persistence_rules>
```

```text
<verification_loop>
Before finalizing, check the output against the goal, constraints, edge cases,
and requested format. If a requirement is unmet, fix it before answering.
</verification_loop>
```

```text
<completion_contract>
The task is complete only when:
- the requested artifact is produced or updated,
- assumptions are labeled,
- verification has been performed or the gap is disclosed,
- the final answer states what changed and any remaining risk.
</completion_contract>
```

## Output Contracts

Choose one:

- `artifact_only`: final prompt or template only.
- `prompt_plus_notes`: prompt first, then assumptions and usage notes.
- `diagnosis_then_rewrite`: failure modes, rewrite, eval checks.
- `template_with_variables`: reusable prompt plus variable definitions.
- `eval_pack`: prompt, golden cases, scoring rubric, pass threshold.

When the user did not specify, default to `prompt_plus_notes`.

## Eval Add-On

For important prompts, include:

- 3-5 golden test inputs, including at least one edge case.
- Expected behavior, not just expected wording.
- Failure modes the prompt is designed to prevent.
- A simple pass/fail or 1-5 rubric.
- One-change-at-a-time iteration advice if the prompt is still failing.

## Review Checklist

Before delivering, verify:

- The goal is concrete.
- Required inputs are named.
- Steps are ordered.
- Ambiguity behavior is explicit.
- Output format is enforceable.
- Tool rules exist when tools matter.
- Verification criteria exist when accuracy matters.
- The prompt does not ask for hidden reasoning or chain-of-thought disclosure.
- The prompt is no longer than needed.

## Reference

Read `references/prompt-builder-principles.md` only when you need the reviewed
source synthesis, trigger boundaries, or a deeper checklist.
