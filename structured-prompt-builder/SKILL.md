---
name: structured-prompt-builder
description: Build a production-ready XML-structured prompt through an interactive critique loop. The skill drafts a prompt using Anthropic's 10-component framework from Prompting 101, then audits it against an 11-rule checklist and iterates with the user until the prompt is clean and efficient. Use this skill whenever the user asks to draft, design, or improve a prompt, system prompt, or LLM instruction set — especially for classification, extraction, document analysis, multi-step reasoning, or any task where output format matters. Trigger on phrases like "write a prompt for", "design a system prompt", "prompt template", "prompt structure", or "how should I prompt Claude to do X". Also trigger when the user describes a production LLM workflow without explicitly asking for a prompt — they probably need one. NOT for managing prompts in production at scale (use prompt-governance). NOT for analyzing performance across prompt versions (use prompt-optimization). NOT for optimizing session context for an active agent (use context-engineering).
---

# Structured Prompt Builder

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Skip the audit checklist re-read on iterations 2+ — apply it from working memory.
- Don't re-render unchanged sections of the prompt during iteration; show only the diff.
- For simple prompts that pass the audit on v1, ship without belaboring the loop.

Drafts a prompt, audits it against 11 rules, iterates with the user until clean.

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

3. Apply the 11-rule checklist (next section) to v1. For each rule, decide pass (✅) or flag (⚠️). Each flag must point to a specific span or omission, not a vibe.

### Phase 3 — Present + iterate

4. Output to the user, in this order:
   - The prompt draft (in a code block)
   - Audit results (compact list format below)
   - One question: fix all / fix specific / ship as-is

   Audit format:
   ```
   ✅ R1, R2, R5, R10, R11
   ⚠️ R3 — "key points" is undefined
   ⚠️ R6 — role missing domain and audience
   ⚠️ R9 — no escape hatch for empty/garbled input
   ```

5. If user picks fixes, produce v2 addressing those flags, re-audit, loop.
6. When the user says "ship" / "looks good" / equivalent, output the final prompt as a clean code block with no audit annotations.

### Stopping criteria

Stop iterating when ANY of these is true:
- User explicitly ships
- All 11 rules pass AND user confirms they're satisfied
- User waives remaining flags ("ignore R8, this is too simple")

## The 11-rule audit checklist

### Structural rules

**R1. Components in correct position.** Check: system content in system, user content in user, prefill in assistant. Common fix: static reference info that drifted into the user message belongs in system.

**R2. Background = reference data only.** Check: no "if/then" logic in `<background>`. Common fix: move decision rules from background to instructions.

**R3. Instructions = procedure + decision rules.** Check: numbered steps, specific about ordering, includes if/then logic. Common fix: replace vague verbs ("extract key points") with specific operations ("for each section in <background>, scan for matching content").

**R4. Guardrails = escape hatches + hard stops.** Check: no overlap with `<instructions>`. Guardrails are the rules that apply *regardless of which step Claude is on* (don't invent data, return X when uncertain). Common fix: pull "do not" statements out of instructions into guardrails.

**R5. No empty or placeholder sections.** Check: every XML tag has substantive content. Common fix: delete the tag rather than leave `[TODO]` or empty.

### Content rules

**R6. Role is specific.** Check: includes domain + task + register/audience. "You summarize text" fails. "You summarize engineering standup transcripts for someone who missed the meeting" passes.

**R7. Output format uses enums where applicable.** Check: categorical fields list allowed values explicitly. Common fix: replace `"category": str` with `"category": "urgent" | "normal" | "spam"`.

**R8. At least one negative or edge-case example.** Check: examples cover what should NOT trigger the main behavior, or what to do when input is malformed. Common fix: add an example showing the escape hatch firing.

**R9. Escape hatch defined for uncertain inputs.** Check: `<guardrails>` or `<output_format>` specifies what to return when the model can't determine the answer confidently. Common fix: add `"needs_review"` / `null` / `"insufficient_input"` as a valid output value, with a guardrail telling the model when to use it.

**R10. No aggregation rules in `<instructions>`.** Check: rules like "drop low-severity flags if there are 3+ medium ones" or "deduplicate before output" — these are post-processing operations, not per-item reasoning. Common fix: move them to a code-side post-processor, or split into a second prompt.

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

## Worked example: one full iteration

**User asks:** "Help me write a prompt to summarize Zoom transcripts for my team."

### v1 (initial draft)

```xml
<role>You summarize meeting transcripts.</role>

<instructions>
1. Read the transcript.
2. Extract key points.
3. Write a summary.
</instructions>

<input_data>{{transcript}}</input_data>

<task>Summarize this meeting.</task>
```

### Audit results

```
✅ R1, R2, R5, R10, R11
⚠️ R3 — "extract key points" is undefined; no procedure for what counts
⚠️ R4 — no guardrails for empty/garbled transcripts
⚠️ R6 — role missing domain and audience
⚠️ R7 — no output format; will return free prose
⚠️ R8 — no examples
⚠️ R9 — no escape hatch
```

**6 flags.** Fix all, fix specific, or ship as-is?

### v2 (after "fix all")

```xml
<role>
You summarize Zoom transcripts of engineering team standups and design
reviews. Your audience is a teammate who missed the meeting and wants
to catch up in under two minutes.
</role>

<tone>
Concise and factual. Do not infer intent or sentiment the speaker
did not state.
</tone>

<background>
<summary_sections>
  <decisions>Things explicitly agreed to, with the decider named</decisions>
  <action_items>Tasks assigned, with owner and (if stated) deadline</action_items>
  <open_questions>Questions raised but not resolved during the meeting</open_questions>
  <context>Key info shared: links, numbers, status updates</context>
</summary_sections>
</background>

<instructions>
1. Read the full transcript end-to-end.
2. For each section in <summary_sections>, scan the transcript for matching content.
3. For each item, attribute it to the speaker who stated it.
4. Skip greetings, off-topic chat, and repeated points.
</instructions>

<guardrails>
- Do not invent decisions or action items that were not explicitly stated.
- If the transcript is under 200 words or appears garbled (high noise,
  unintelligible spans), return summary_status "insufficient_input"
  with all section arrays empty.
- If speaker attribution is unclear for an item, set its speaker
  field to "unknown" rather than guessing.
</guardrails>

<examples>
  <example>
    <input>
      [Alice, 0:30] OK so we agreed Bob will own the migration script,
      target end of next week.
      [Bob, 0:45] Yep, I'll have a draft by Wednesday.
      [Alice, 1:02] One open question — do we backfill or start fresh?
      Let's table that for next standup.
    </input>
    <reasoning>One decision (Bob owns migration), one action item with
      owner and deadline, one open question. No filler.</reasoning>
    <o>
{
  "summary_status": "complete",
  "decisions": [{"text": "Bob will own the migration script", "decider": "Alice"}],
  "action_items": [{"task": "Draft migration script", "owner": "Bob", "deadline": "Wednesday"}],
  "open_questions": ["Backfill existing data or start fresh?"],
  "context": []
}
    </o>
  </example>
  <example>
    <input>
      [unknown, 0:02] *static* ...think we should... *cuts out*
      [unknown, 0:08] yeah... *static*
    </input>
    <reasoning>Garbled, no intelligible content. Escape hatch fires.</reasoning>
    <o>
{
  "summary_status": "insufficient_input",
  "decisions": [],
  "action_items": [],
  "open_questions": [],
  "context": []
}
    </o>
  </example>
</examples>

<input_data>
{{transcript}}
</input_data>

<task>
Summarize per <instructions> and <guardrails>.
</task>

<output_format>
Return JSON only:
{
  "summary_status": "complete" | "insufficient_input",
  "decisions": [{"text": str, "decider": str}],
  "action_items": [{"task": str, "owner": str, "deadline": str | null}],
  "open_questions": [str],
  "context": [str]
}
</output_format>
```

### Audit (v2)

```
✅ R1–R11 all pass
```

Ready to ship, or want to refine any section?

## Edge cases & gotchas

- **Data vs. rules:** `<background>` holds reference data only. Decision logic goes in `<instructions>`. Mixing them breaks caching when rules change.
- **Always specify an escape hatch in `<guardrails>`.** Without one, Claude falls back to "best guess" on uncertain inputs — usually the worst possible behavior in production.
- **Cacheability:** Anything in `<background>` should be stable across calls. If it changes per call, it's input data, not background.
- **Aggregation belongs in code.** Rules like "drop low flags if 3+ mediums exist" or "deduplicate" are post-processing. The model can sort of do them, but unreliably. Move to a Python post-processor.
- **Extended thinking is a crutch for prompt engineering.** With thinking enabled, you can skip `<thinking_guidance>` — but inspect the thinking traces to find prompt weaknesses.
- **The audit is not a quality guarantee.** Passing 11 rules means the prompt is *structurally clean*, not that it produces good outputs. Test with real inputs.
