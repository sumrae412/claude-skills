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
- User asks "should we adopt <external framework> patterns into <our system>" — this skill triages the framework's surface against the target's existing coverage. Validated 2026-05-01 against github/spec-kit (~80-item extension catalog) → claude-flow Phase 0–6: 2 real gaps surfaced (phantom-completion audit, spec-references-as-context gate, both shipped in claude-skills PR #67), rest skipped as overlap.

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

## Depth & Analysis Protocol

### Step 1 — Classify the source

Before any analysis, identify the source type. The rest of the protocol depends on getting this right.

| Source type | Examples | What to extract |
|---|---|---|
| **Repo** | GitHub URL, local `~/code/` path, PR diff | Architecture patterns, module boundaries, data flow, approach — how it's built, not what it says |
| **Article** | Blog post, newsletter, docs, essay | Specific claims, techniques, data points — not the topic, the transferable mechanism |
| **Transcript** | Talk, interview, podcast | Frameworks, cited references, heuristics — prosier than an article, same extraction rules |
| **Snippet** | A paste of code, a config file, a quote | Direct pattern match against the target's existing code or config |
| **Screenshot** | UI image, diagram | Visual patterns, layout, interaction model — compare against the target's UI surface |
| **Multi-source** | 3+ items in one turn | Triage each independently against the target, then synthesize overlaps across items |

### Step 2 — Set depth budget

Default to **Depth 1** and escalate only when the source justifies it.

**Depth 1 — Quick scan (default).** Single-pass skim of the most accessible surface (README for repos, headline + first 3 paragraphs for articles, the full paste for snippets). Extract only surface-level matches. If nothing clears the `confidence ≥ 3` bar, stop. This is the correct depth for >80% of triages.
→ *Cost: minimal — one pass, no subagents, no file exploration.*

**Depth 2 — Targeted extraction.** Only if Depth 1 found ≥1 item at `confidence ≥ 4` that would materially improve the target. Dispatch a single cheap subagent to explore the specific area of overlap. Max 1 subagent dispatch for articles, 2 for repos. The subagent brief must name the specific gap it's investigating, not "explore this repo broadly."
→ *Cost: moderate — one subagent dispatch, limited targeted file reads.*

**Depth 3 — Full audit.** Only if Depth 2 confirmed high-value overlap AND the target is a core project (courierflow_beta, claude-skills, henry) or the user explicitly said "go deep." Multiple subagents, file-by-file comparison against the target's relevant sections. State the estimated cost in the output before proceeding.
→ *Cost: higher — multiple dispatches, multiple file reads.*

State the depth tier in the Verdict line. A Depth 1 verdict that should have been Depth 2 is the failure mode this section exists to prevent.

### Repo analysis protocol

When the source is a repo, this replaces the generic single-pass skim:

1. **README + top-level tree** — one subagent or direct read (glob the top 2 levels). Understand purpose, stack, structure. Do NOT read deeper files yet.
2. **Map against the target's known gaps** — what does the target lack that this repo does well? Name the specific gaps before naming matches.
3. **Deepen only where overlap exists** — if step 2 found 1-2 specific areas, dispatch a subagent to explore those exact files or subdirectories. Do NOT explore randomly or read files unrelated to the mapped overlap.
4. **Extract the pattern, not the code** — what approach did the repo use? What tradeoffs did it make? When the pattern IS the deliverable (config file, direct utility function, workflow definition), extract verbatim. Otherwise extract the approach and leave implementation to the target's existing idioms.
5. **Check for anti-patterns too** — sometimes the most useful finding is "they tried X and it caused Y problem." That saves the target from repeating the mistake.

Steps 1-2 are Depth 1. Step 3 escalates to Depth 2. Steps 4-5 apply at whatever depth you reached.

### Article/content analysis protocol

When the source is an article, transcript, or document:

1. **Extract specific claims** — not "the article is about prompt caching" but "the article claims grouping system prompts by session ID reduced cache misses by 37%." A claim needs: technique, result, context.
2. **Check each claim against the target** — does the target already do this? Need it? Have something adjacent that the same technique could improve?
3. **Flag the transferable mechanism** — strip the domain wrapper. A SaaS scheduling algorithm for restaurant waitlists might map to a queue system in a completely different domain. The pattern, not the wrapper.
4. **One pass unless a claim justifies verification** — do NOT re-read the article. If extraction feels shallow, the problem is extraction methodology (summarizing instead of extracting), not needing more passes.
5. **Note confidence-eroding signals** — no benchmarks, vendor blog, single data point, purely theoretical. Flag these alongside the claim so the user can weigh them.

### Stopping criteria

Stop going deeper — at any depth — when any of:

- The last pass found no items above confidence 3.
- The estimated remaining value net of analysis cost is negative (one more subagent costs ~3K tokens; would it find something worth that?).
- The source is structurally different from the target (different domain, stack, scale, or problem class) — unrelated repos stay at Depth 1.
- You've dispatched ≥2 subagents for one source without user approval for more.
- The target's most closely related files have been checked and the patterns don't match. Naming what was checked and what didn't match is more useful than checking more files.

---

## Output format

```
## Useful-For Triage: <content source> → <target>

### Verdict
<one line: high-value / some-value / skip, with confidence 1-5 and depth tier>

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

### State the depth tier
Every Verdict includes the depth tier: `Verdict: some-value (Depth 1)`. The tier tells the user how hard the analysis tried. A Depth 1 skip on an unrelated repo is correct. A Depth 1 verdict on a repo that clearly overlaps is a failure — escalate.

### Follow the repo protocol
When the source is a repo, the Repo Analysis Protocol is required, not optional. A README skim alone does not count as a repo triage. If you can't access the repo (private, no permission, URL broken), say so in the Verdict and offer alternatives.

### Name what was checked even on a skip
A `Verdict: skip` must name what was checked, not just state the conclusion. "Skipped the README and found no overlap with CourierFlow's stack" is better than "no relevance found." The user needs to know the analysis was real, not guessed.

---

## Handoff

When the user approves a Pull item, the next step is usually one of:
- Edit an existing skill → use `superpowers:writing-skills`
- Update CLAUDE.md → use `claude-md-management:claude-md-improver`
- Add a memory → write to the user's memory system directly per auto-memory rules
- Create a new skill → use `anthropic-skills:skill-creator`

State the handoff target in the Suggested next action line so the user knows what comes next.
