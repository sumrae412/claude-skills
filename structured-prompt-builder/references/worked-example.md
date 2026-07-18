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
✅ R1, R2, R5, R10, R11, R12, R13
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
✅ R1–R13 all pass
```

Ready to ship, or want to refine any section?
