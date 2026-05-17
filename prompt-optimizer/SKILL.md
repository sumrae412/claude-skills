---
name: prompt-optimizer
description: >
  Evaluate and optimize prompts using proven prompting techniques and frameworks.
  Activate whenever the user asks to "optimize," "improve," "evaluate," or "fix" a prompt,
  asks if a prompt is "good" or "clear," wants "better versions" of a prompt, asks why
  a prompt is producing poor results, or wants prompt engineering guidance. Also trigger
  when the user shares a prompt and seems unsatisfied with Claude's outputs — even if
  they don't explicitly ask for optimization. Do not use when the user wants the task
  executed directly ("just do it").
---

# Prompt Optimizer

Evaluate prompt quality and generate optimized, copy-paste-ready versions using
evidence-based techniques and frameworks.

---

## Step 1: Extract Intent (Nine Dimensions)

Before evaluating, extract what the prompt is trying to accomplish:

1. **Task** — What action should the model perform?
2. **Input** — What data or context is provided?
3. **Output** — What should the response look like?
4. **Constraints** — What limits apply (length, format, scope)?
5. **Context** — What background does the model need?
6. **Audience** — Who will read the output?
7. **Memory** — Are there prior decisions or context to carry forward?
8. **Success criteria** — How do you know the response is good?
9. **Examples** — Are there reference examples?

Missing dimensions are the primary source of weak prompts.

---

## Step 2: Classify (Case A vs. Case B)

**Case A** — The user provided real, specific content (a document, code, actual data).
→ Embed the content directly into the optimized prompt.

**Case B** — The user described a *type* of task they want to repeat.
→ Write a self-contained, reusable prompt that invites the user to provide inputs in the
next turn. Use clear input labels (e.g., `<document>`, `<code>`), not vague placeholders.

**The "no placeholders" rule:** The optimized prompt must be copy-paste-sendable as-is.
Never output `[fill in X]` fields. Handle missing content explicitly — don't leave blanks.

---

## Step 3: Evaluate Quality

Load `references/quality-framework.md` for full rubrics. Quick assessment dimensions:

| Dimension | What to check |
|-----------|---------------|
| Clarity | Is there only one valid interpretation? |
| Specificity | Are requirements, scope, and format defined? |
| Structure | Is information in logical order? (Long context first, task last) |
| Completeness | Are all nine intent dimensions addressed? |
| Tone | Is voice appropriate and specified? |
| Constraints | Are "do" and "don't" rules explicit? |

**Key anti-patterns to catch** (load `references/anti-patterns.md` for full list):
- Vague task verbs ("handle," "deal with," "make it good")
- Assumed prior knowledge the model doesn't have
- Instructions that say "don't X" instead of "do Y" (prefer positive framing)
- No success criteria
- Adding CoT to reasoning-native models (O1, O3, etc.) — degrades output
- Contradictory instructions without priority rules

---

## Step 4: Select Techniques

Load `references/prompt-techniques.md` for the full catalog of 58 techniques.

| Weakness | Apply |
|----------|-------|
| Vague goal | Expert Persona + Task Decomposition |
| Missing reasoning | Chain of Thought (not for O1/O3 models) |
| No examples | Few-shot Learning |
| Too broad | Template structure (CO-STAR, RISEN, or RTF) |
| Hallucination risk | Grounding anchors + Confidence signaling |
| Long document input | Long-input-first ordering + Quote extraction |
| Style drift | Style-matching (write the prompt in the style you want back) |
| Instruction not followed | Add "explain the why" rationale to key instructions |

Template frameworks (see `references/templates.md`): CO-STAR, RISEN, RTF

---

## Step 5: Write the Optimized Prompt

1. **Long inputs first, task last** — ~30% quality lift on long-context tasks
2. **Positive framing over negative** — "Write in flowing prose" beats "don't use bullets"
3. **Explain the why** — Attach rationale to key instructions; models follow them more reliably
4. **Match style to desired output** — Prose prompt → prose output; terse prompt → terse output
5. **Grounding anchors** — "Pull relevant quotes into `<quotes>` tags, then answer from those"
6. **Closing reasoning line** — End with one instruction signaling reasoning depth
7. **XML tags** — Use for multiple sections; skip for simple prompts
8. **Role assignment** — Only when it meaningfully steers output

---

## Step 6: Deliver

1. **Diagnosis** — What's weak and why (brief)
2. **Optimized prompt** — Code block, copy-paste ready, zero placeholders
3. **What changed** — Techniques applied and why
4. Optionally: **Variant B** — Different technique combination for alternate framing

---

## Scripts

```bash
python3 scripts/evaluate.py "Your prompt here"
python3 scripts/optimize.py "Your prompt here" --techniques "few-shot,cot"
python3 scripts/optimize.py --list-techniques
```

## Reference Files

- `references/quality-framework.md` — evaluation rubrics and scoring guidelines
- `references/prompt-techniques.md` — catalog of 58 techniques
- `references/optimization-patterns.md` — before/after examples, technique pairings
- `references/templates.md` — CO-STAR, RISEN, RTF, and 9 other frameworks
- `references/anti-patterns.md` — 35 anti-patterns organized by category
