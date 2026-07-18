---
name: structured-prompt-builder
description: "Build a production-ready XML-structured prompt through an interactive critique loop — drafts with Anthropic's Prompting 101 component framework, audits against a checklist, and iterates until clean and efficient. Use whenever the user asks to draft or design a prompt, system prompt, or LLM instruction set — classification, extraction, document analysis, multi-step reasoning, or any output-format-sensitive task — or describes a production LLM workflow without asking for a prompt. NOT for managing prompts in production at scale or analyzing performance across prompt versions (use evals for regression gates and production sampling), or optimizing session context for an active agent (use context-engineering)."
---

# Structured Prompt Builder

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Skip the audit checklist re-read on iterations 2+ — apply it from working memory.
- Don't re-render unchanged sections of the prompt during iteration; show only the diff.
- For simple prompts that pass the audit on v1, ship without belaboring the loop.

Drafts a prompt, audits it against the checklist, iterates with the user until clean.

## When to use

Use for prompts that:
- Drive a production workflow (API calls, automation, agents)
- Need parseable / structured output
- Involve multi-step reasoning over inputs
- Must handle ambiguous data reliably

**Skip this skill** for casual chat, single-turn Q&A, or one-off creative tasks. The framework + audit overhead is wasted there.

## Workflow

### Phase 1 — Initial draft

1. If the task is clear from the conversation, go to step 2. If a single piece of information would change the structure (e.g., "is this for an API call or a chat interface?"), ask ONE question. Otherwise, draft.
2. Render v1 using the template below. Include only the components that fit the task. **Skip components rather than pad them.**

### Phase 2 — Self-audit

3. Apply the audit checklist (next section) to v1. For each rule, decide pass (✅) or flag (⚠️). Each flag must point to a specific span or omission, not a vibe.

### Phase 3 — Present + iterate

4. Output to the user, in this order:
   - The prompt draft (in a code block)
   - Audit results (compact list format below)
   - One question: fix all / fix specific / ship as-is

   Audit format:
   ```
   ✅ R1, R2, R5, R10, R11, R12, R13
   ⚠️ R3 — "key points" is undefined
   ⚠️ R6 — role missing domain and audience
   ⚠️ R9 — no escape hatch for empty/garbled input
   ```

5. If user picks fixes, produce v2 addressing those flags, re-audit, loop.
6. When the user says "ship" / "looks good" / equivalent, output the final prompt as a clean code block with no audit annotations.

### Stopping criteria

Stop iterating when ANY of these is true:
- User explicitly ships
- All checklist rules pass AND user confirms they're satisfied
- User waives remaining flags ("ignore R8, this is too simple")

## The audit checklist

### Structural rules

**R1. Components in correct position.** Check: system content in system, user content in user, prefill in assistant. Common fix: static reference info that drifted into the user message belongs in system.

**R2. Background = reference data only.** Check: no "if/then" logic in `<background>`. Common fix: move decision rules from background to instructions.

**R3. Instructions = procedure + decision rules.** Check: numbered steps, specific about ordering, includes if/then logic. Common fix: replace vague verbs ("extract key points") with specific operations ("for each section in <background>, scan for matching content"). **Does not apply to agent prompts** — agents need heuristics + invariants, not numbered scripts. If the prompt drives a tool-using, multi-turn, or side-effecting agent, route to `agent-prompt-architecture` instead.

**R4. Guardrails = escape hatches + hard stops.** Check: no overlap with `<instructions>`. Guardrails are the rules that apply *regardless of which step Claude is on* (don't invent data, return X when uncertain). Common fix: pull "do not" statements out of instructions into guardrails.

**R5. No empty or placeholder sections.** Check: every XML tag has substantive content. Common fix: delete the tag rather than leave `[TODO]` or empty.

**R12. Long inputs before the immediate task.** Check: when input data is large (docs, transcripts, code >1K tokens), `<input_data>` appears in the user message BEFORE the `<task>` statement. Common fix: move the task statement to the end so the model sees the input first, then the instruction. ~30% quality lift on long-context tasks; critical for Claude 2.1+.

### Content rules

**R6. Role is specific.** Check: includes domain + task + register/audience. "You summarize text" fails. "You summarize engineering standup transcripts for someone who missed the meeting" passes.

**R7. Output format uses enums where applicable.** Check: categorical fields list allowed values explicitly. Common fix: replace `"category": str` with `"category": "urgent" | "normal" | "spam"`.

**R8. At least one negative or edge-case example.** Check: examples cover what should NOT trigger the main behavior, or what to do when input is malformed. Common fix: add an example showing the escape hatch firing.

**R9. Escape hatch defined for uncertain inputs.** Check: `<guardrails>` or `<output_format>` specifies what to return when the model can't determine the answer confidently. Common fix: add `"needs_review"` / `null` / `"insufficient_input"` as a valid output value, with a guardrail telling the model when to use it.

**R10. No aggregation rules in `<instructions>`.** Check: rules like "drop low-severity flags if there are 3+ medium ones" or "deduplicate before output" — these are post-processing operations, not per-item reasoning. Common fix: move them to a code-side post-processor, or split into a second prompt.

**R13. Positive framing in instructions.** Check: `<instructions>` use "do X" constructions rather than "don't do Y". Common fix: rewrite "don't use bullets" as "write in flowing prose". Negative phrasing is fine in `<guardrails>` for hard stops ("do not invent data") but procedural steps should be affirmative.

### Efficiency rules

**R11. No redundancy.** Check: each constraint appears in exactly one place. Common fix: if a rule is restated across `<tone>`, `<instructions>`, and `<task>`, pick the most appropriate location and delete the others.

## The 10-component framework

| # | Component                    | Required?       | Location           |
|---|------------------------------|-----------------|--------------------|
| 1 | Task context / role          | ✅              | system             |
| 2 | Tone context                 | recommended     | system             |
| 3 | Background data / schema     | when applicable | system (cacheable) |
| 4 | Detailed instructions        | ✅ for complex  | system             |
| 4b| Guardrails / escape hatches  | when applicable | system             |
| 5 | Examples (few-shot)          | for tricky cases| system             |
| 6 | Conversation history         | when applicable | messages           |
| 7 | Immediate task + reminders   | ✅              | user               |
| 8 | Think step-by-step guidance  | recommended     | user               |
| 9 | Output formatting            | for parsed output| user              |
| 10| Prefilled response           | optional        | assistant          |

Stable/cacheable context goes first so it primes the model. Dynamic content and the immediate ask go last so they're the most recent thing in context when Claude generates.

## Template

```xml
<!-- ============ SYSTEM PROMPT ============ -->

<role>
[1. Task context: who Claude is, what it's doing, what domain]
</role>

<tone>
[2. Tone context: factual, confident, formal, etc.]
</tone>

<background>
[3. Static REFERENCE DATA only: schemas, rubrics, taxonomies.
No if/then logic. Cacheable.]
</background>

<instructions>
[4. Procedure + decision rules. Numbered, ordered.]
</instructions>

<guardrails>
[4b. Escape hatches, confidence thresholds, hard stops.]
</guardrails>

<examples>
  <example>
    <input>[realistic input]</input>
    <reasoning>[how to think about it]</reasoning>
    <o>[expected output in target format]</o>
  </example>
  <!-- Include at least one negative/edge-case example -->
</examples>

<!-- ============ USER MESSAGE ============ -->

<input_data>
[6. Conversation history if applicable, OR 7. the actual input for this call]
</input_data>

<task>
[7. Immediate task — restate what you want NOW.]
</task>

<thinking_guidance>
[8. Optional: how to reason. Skip if using extended thinking.]
</thinking_guidance>

<output_format>
[9. Exact format. Use enums for categorical fields.]
</output_format>

<!-- ============ ASSISTANT PREFILL (optional) ============ -->

[10. Prefill to force format. Skip if you want reasoning preamble.]
```

## Worked example

A full v1 → audit → v2 iteration (Zoom-transcript summarizer: 6 flags, then all
13 rules passing) lives in `references/worked-example.md`. Load it when you need
a concrete model of audit strictness or of how a "fix all" revision should look.

## Reasoning-style variant: Chain of Draft (low-cost CoT)

When the prompt asks the model to reason step-by-step (`<thinking_guidance>`, extended thinking, or an explicit "think step by step" instruction) AND the task is token-sensitive / high-volume — batch classification, extraction, arithmetic-style scoring — offer **Chain of Draft** as the cheaper variant of Chain-of-Thought.

- **Chain-of-Thought:** intermediate reasoning in full prose. Accurate, verbose, expensive.
- **Chain of Draft:** constrain each reasoning step to a **~5-word budget** — terse shorthand, one draft line per step, answer last. Reported to roughly match CoT accuracy on arithmetic / GSM8k-style tasks at a fraction of the reasoning tokens.

Instruction to drop into `<thinking_guidance>`: *"Think step by step, but keep each step to a minimal draft of about five words. Return the final answer after the drafts."* Skip it for open-ended generative tasks where the reasoning trace is itself the product, or where auditing full traces is the point.

Source: arXiv, "Chain of Draft: Thinking Faster by Writing Less" (from the 2026-07-14 /articles triage).

## Edge cases & gotchas

- **Data vs. rules:** `<background>` holds reference data only. Decision logic goes in `<instructions>`. Mixing them breaks caching when rules change.
- **Always specify an escape hatch in `<guardrails>`.** Without one, Claude falls back to "best guess" on uncertain inputs — usually the worst possible behavior in production.
- **Cacheability:** Anything in `<background>` should be stable across calls. If it changes per call, it's input data, not background.
- **Aggregation belongs in code.** Rules like "drop low flags if 3+ mediums exist" or "deduplicate" are post-processing. The model can sort of do them, but unreliably. Move to a Python post-processor.
- **Extended thinking is a crutch for prompt engineering.** With thinking enabled, you can skip `<thinking_guidance>` — but inspect the thinking traces to find prompt weaknesses.
- **The audit is not a quality guarantee.** Passing every rule means the prompt is *structurally clean*, not that it produces good outputs. Test with real inputs.
