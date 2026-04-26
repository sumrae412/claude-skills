---
name: brevity
description: Use when the user asks for terse output, wants to minimize output token cost ("caveman mode", "no preamble", "just the answer", "/brevity", "be brief"), or is running a long iterative session where chat overhead compounds. Strips preamble, postamble, re-statement, and narrative filler — keeps only load-bearing content.
user-invocable: true
---

# Brevity Mode

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Cuts output tokens by removing the parts of answers that don't carry information: preamble, postamble, restatement, and narrative filler. Keep code, file paths, numbers, tables, and direct conclusions.

**Announce once per session:** "Brevity mode on — terse output, no preamble."

---

## Rules

### Always strip

- **Preamble:** "Let me X", "I'll now Y", "Great question —", "Sure, I can help with that"
- **Postamble:** "Let me know if X", "Hope this helps", "Feel free to ask", closing summaries of what was just shown
- **Restatement:** Prose after a code block that re-describes what the code does
- **Narrative filler:** "As you can see", "Now that we have X", "The next step is to..."
- **Apology/hedge filler:** "I think", "It seems like", "This might be" — unless uncertainty is load-bearing

### Keep

- **Direct answer** to the question, first line
- **Code, diffs, commands, file paths** — verbatim
- **Numbers, counts, and decisions** — "24 failures", "ship", "abandon"
- **One-sentence rationale** only when non-obvious
- **Uncertainty markers** when genuine: "unverified", "not tested"

### Format

- Bullets over paragraphs. One bullet = one fact.
- Tables for any comparison of ≥3 items.
- No headers for short answers (under ~100 words).
- Trailing line: what's next, if anything. One sentence.

---

## Length Targets

| Task | Target |
|------|--------|
| Direct Q ("which file?") | ≤20 words, no headers |
| Status update | ≤40 words |
| Code review finding | bullet + file:line, no prose |
| End-of-turn summary | 1–2 sentences |
| Multi-step result | bullets only, no narrative |

---

## When NOT to use

- Teaching/explanation tasks where the user asks "why" or "how does X work"
- First-time setup or onboarding flows
- Post-mortems and retrospectives
- Any task where the user has asked for a thorough walkthrough

Brevity is opt-in. If the user asks a follow-up that needs more context, expand — don't stay minimal by reflex.

---

## Subagent Guidance

When dispatching subagents under brevity mode, add to the prompt:

> Report under 100 words. No preamble, no postamble. Bullets for findings. File:line for any code reference.

This carries the saving into fan-outs where overhead otherwise multiplies by N agents.

---

## Interaction With Other Skills

- **`claude-flow`** — Phase 6 haiku reviewers already use overshoot + structured output; brevity adds the "no preamble" clause to their prompts.
- **`debate-team`** — critics already write structured findings; brevity caps the Lead/Judge synthesis length.
- **`research`** — synthesizer output should stay within brevity targets; raw Wave 1/2 scratchpads are exempt (they're internal).

Do not apply brevity to artifact deliverables (plans, specs, ADRs, docs) — those need full context for future readers.
