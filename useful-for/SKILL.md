---
name: useful-for
description: Use when the user pastes external content (articles, transcripts, repos, tweets, PRs, docs, screenshots, other AI chat exports) and asks whether it's useful for a specific project, skill, or system. Triggers on phrasings like "is any of this useful for X", "can we use anything from this for X", "search this repo and find skills that would improve X", "does this apply to X", or pasted content + a named target. Produces a structured triage with relevance scoring and concrete next actions.
user-invocable: true
---

# Useful For

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Triages pasted content against a named target (project, skill, system, workflow) and returns a structured verdict: what's worth pulling, where it goes, what to skip, and confidence.

**Announce once:** "Running useful-for triage against <target>."

---

## When to invoke

Triggers:
- User pastes content + asks "is any of this useful for <X>"
- User pastes content + asks "can we use anything from this to improve <X>"
- User says "search this repo/article/transcript for skills that would improve <X>"
- User shares a link/paste and names a target project or skill

Do NOT invoke for:
- Content review without a named target ("what do you think of this article")
- Generic summarization requests
- Code review of the user's own code

---

## Required inputs

Before producing output, confirm you have:
1. **The content** (pasted text, file path, URL, or repo path)
2. **The target** — must be specific: project name, skill name, workflow, or named system. If ambiguous, ask ONE question: "Target is <best guess> — confirm or correct?"

If the target is broad ("my setup"), narrow it to a specific surface before triaging.

---

## Output format

```
## Useful-For Triage: <content source> → <target>

### Verdict
<one line: high-value / some-value / skip, with confidence 1-5>

### Pull (ranked by value)
1. **<item>** — <one-line what it is>
   - Where it goes: <specific skill file / CLAUDE.md section / MEMORY entry / new skill>
   - How to apply: <concrete change, not vague "consider X">
   - Confidence: <1-5>

2. ...

### Skip (with reasons)
- <item> — <why not: already have it / doesn't fit / low ROI / wrong scope>
- ...

### Open questions
- <anything that needs user input before pulling>

### Suggested next action
<one concrete step: "update skills/X/SKILL.md with item 1" or "no action — file and move on">
```

---

## Rules

### Be specific about placement
Never say "could be useful for claude_flow." Say: *"Add to `skills/claude-flow/SKILL.md` under the Phase 2 exploration section"* or *"New MEMORY entry titled X"*.

### Rank by value, not order in source
Extractions are ranked by estimated impact on the target, not by where they appeared in the pasted content.

### Skip aggressively
Most content has 0-2 items worth pulling. A triage that returns 8 "maybe useful" items is failing. If nothing clears the bar, say so: `### Verdict: skip (confidence 5)` — that's a valid and common outcome.

### Don't paraphrase the source
Extract the specific claim, pattern, line of code, or technique. If you can't point at a specific thing, it's not an extract — it's filler.

### Confidence scale
- **5** — specific, tested, directly fits a gap the target has
- **4** — specific and plausibly fits, needs a small adaptation
- **3** — interesting idea, unclear fit, would need experimentation
- **2** — tangentially related
- **1** — mentioned only for completeness; probably skip

Do not output items below 3 in the Pull section. Everything ≤2 goes in Skip.

### Never invent
If the content doesn't mention something, don't hallucinate that it does. If you're unsure what the target currently has (e.g., "does skill X already cover this?"), list it as an Open question, not a Pull.

---

## Handoff

When the user approves a Pull item, the next step is usually one of:
- Edit an existing skill → use `superpowers:writing-skills`
- Update CLAUDE.md → use `claude-md-management:claude-md-improver`
- Add a memory → write to the user's memory system directly per auto-memory rules
- Create a new skill → use `anthropic-skills:skill-creator`

State the handoff target in the Suggested next action line so the user knows what comes next.
