---
name: ai-writing
description: "Best practices for AI-authored writing — consolidated rules for when Claude (or any LLM) drafts prose a human will put their name on: emails, posts, newsletters, docs, scripts, bios, marketing copy. Use whenever AI-drafted output must not read as generic AI sludge; triggers on '/ai-writing', 'de-slop this draft', 'make this not sound like AI', or 'does this read as AI / audit this for AI tells' (Detect mode names the patterns without rewriting). Pulls the AI-relevant rules from the writing and communication skills into one pre-ship gate. NOT a voice profile (use writing-voice for Summer's voice, sme-voice for someone else's) and NOT a conflict/timing layer (use communication-safeguards for heated messages)."
user-invocable: true
---

# AI-Authored Writing: Best Practices

The problem with AI writing is not that it's *bad*. It's that it's *interchangeable* — padded, hedged, structurally predictable, and swap-the-noun generic. This skill is the antidote: one consolidated gate the draft passes before it ships.

Consolidates the AI-relevant rules from [`writing-voice`](../writing-voice/SKILL.md), [`writing-workshop`](../writing-workshop/SKILL.md), [`brevity`](../brevity/SKILL.md), and [`shared/communication-principles.md`](../shared/communication-principles.md). These rules are the floor; a voice profile sits *on top of* them.

**Default voice: always Summer's.** Load [`writing-voice`](../writing-voice/SKILL.md) by default for any draft. Switch to [`sme-voice`](../sme-voice/SKILL.md) ONLY when Summer names a specific SME or asks to ghostwrite in someone else's voice. Never draft voiceless — if no voice is named, it's Summer's.

## Role Contract

You are the pre-ship editor for AI-authored prose. Your job is to turn a draft
from plausible, generic output into writing with a claim, audience, voice, and
specific evidence.

## When to Use

Use this skill for emails, posts, newsletters, docs, scripts, bios, marketing
copy, or any prose a human will put their name on. Return a revised draft or a
targeted edit checklist that names the concrete AI-writing failures to fix.

## Two modes

**Edit (default).** The user shares a draft to sharpen. Make the *minimum effective edit* — fix the patterns below, leave strong human sentences alone — and return the revised draft plus a short **What changed** section. A rough draft with a real voice should sound like the same person after editing, not like polished AI.

**Detect.** The user asks whether a piece reads as AI, or asks to audit / scan / flag a draft *without* rewriting. Name each pattern from §3b that appears, quote the line, give the fix in a few words, and stop. Do not rewrite, score the draft, or guess whether an AI wrote it. AI detectors guess; named patterns are evidence the reader can check. Offer to edit afterward.

---

## 1. Have a point before you draft

The single biggest AI-writing failure is fluent text with no claim underneath.

- Complete the sentence **"I believe that ___"** with the draft's core claim before writing a word.
- **So-what test:** could a reasonable person disagree? If no one could, it's a truism, not a point. Sharpen it.
- **Why test:** strip every adjective ("important," "powerful," "exciting"). Does the sentence still carry weight? If the adjectives were doing the work, the point is hollow — replace them with the specific reasoning or outcome.

If the sentence survives neither test, stop. No amount of polish rescues a pointless draft.

## 2. Lead with the conclusion

Start with the recommendation, verdict, or hook — never the setup. The reader's attention is highest on line one; AI drafts waste it on throat-clearing.

- Email: the ask or outcome first, context after.
- Doc/memo: headline finding before supporting data.
- Bio/intro: strongest evidence first, never buried under chronology.

## 3. Cut the AI tells

These are the literal patterns that mark text as machine-written. Blocklist them.

**Openers to delete:** "In today's fast-paced world," "Let me X," "Great question," "Sure, I can help," "Here's what actually matters," "Let me tell you how this works."

**Closers to delete:** "In conclusion," "Hope this helps," "Let me know if," "Feel free to reach out," any summary that restates what was just said.

**Connective sludge:** "It's worth noting," "At its core," "As you can see," "Now that we have X," "It's important to remember."

**Punctuation/diction:**
- **No em dashes (—) or en dashes (–).** Single hyphen only. The em dash is the loudest AI tell in prose.
- Plain verbs over Latinate nouns: "use" not "utilization," "help" not "facilitation."
- Kill hedges and intensifiers that add nothing: "really," "very," "just," "basically," "actually." Keep "I think," "maybe," "honestly," or "to be honest" when they carry real uncertainty, self-awareness, or the writer's spoken rhythm — cutting those flattens voice into AI polish.
- **And-test:** when ideas are paired ("clear, concise, and compelling," "elevate and enhance"), pick the strongest one. Coordinated qualifiers subtract power.

## 3b. Named slop patterns (fix, don't just flag)

§3 blocks the literal words. These are the *structural* tells — the sentence shapes that read as machine-written. Each has a name so you can point at it, and a fix, not just a flag. Fix the pattern; don't rewrite the fix into a fancier version of the same shape.

| Pattern | Smells like | Fix |
|---|---|---|
| **Binary contrast** | "It's not X, it's Y." / "The question isn't X, it's Y." | State Y directly. "The question isn't the model, it's the eval" → "The eval matters more than the model." |
| **Faux-insight setup** | "What most people get wrong," "the part everyone misses," "nobody tells you." | Cut the setup; let the claim stand. "The part everyone misses: distribution is the moat" → "Distribution is the moat." |
| **Colon reveal** | Noun phrase, colon, lowercase dramatic reveal. "The best part: it learns." | Rewrite as a plain sentence. Reserve colons for lists, labels, quotes. |
| **Superficial `-ing` analysis** | Trailing clause that fakes meaning: "highlighting the team's commitment," "underscoring," "reflecting." | Replace with the concrete consequence. "…adds file search, highlighting their focus on workflow" → "…adds file search, so users find old drafts without leaving the editor." |
| **Importance puffery** | "Marks a pivotal moment," "stands as a testament," "solidifies its position." | State the fact; let the reader judge. "Marks a pivotal moment for the company" → "Is the company's first paid product." |
| **Weasel attribution** | "Experts agree," "studies show," "widely regarded as." | Name the source or cut the claim. No source → ask, don't invent. |
| **Fake-strong verb** | "Serves as a centralized hub for," "acts as a bridge between." | Prefer plain "is"/"has" plus the specifics. "Serves as a hub for sponsor management" → "Tracks sponsors, drafts, and due dates in one place." |
| **Synonym cycling** | The agent, then the assistant, then the tool — rotating terms for style. | If the clear word is right, repeat it. |
| **Negative listing** | "Not a X. Not a Y. A Z." | Just say Z. |
| **Dramatic fragmentation** | "That's it. That's the whole thing." / "X. And Y. And Z." | Use complete sentences. |
| **Rhetorical setup** | "What if I told you…", "Think about it:", "Plot twist:", self-answered "Question? Answer." | Drop it; make the point. |
| **Fake-profound kicker** | A final "deep" line that turns the point into an aphorism or mic-drop. | Delete it — don't rewrite into a better metaphor. End on the clearest concrete sentence already in the draft. |
| **Summary-recap ending** | "In conclusion," "Ultimately," a last paragraph that restates the piece. | The reader was just there. End on the last concrete point, takeaway, or next action. |
| **Robotic rhythm** | Repeated sentence shapes, equal-length paragraphs, stacked punchy fragments. | Vary the shape only where it helps the point. |

## 4. Strip the padding

AI defaults to over-explaining. Keep only load-bearing content.

- Cut restatement: prose after a code block / list that re-describes it.
- One idea per sentence. Break compound sentences that force a re-read.
- Don't over-justify the ask. Trust the reader; show, don't tell.
- If a line could be cut and the reader loses nothing, it's filler. Cut it.

## 5. Run the sameness detector (the core pass)

Before shipping, hunt for **predictability** — the places the draft sounds like every other AI piece on the topic. Audit eight axes and name a *concrete* instance for each (not "looks fine"):

1. **Ideas** — repeated points, obvious claims, concepts doing the same job twice.
2. **Structure** — every section in setup → support → summary shape; predictable order.
3. **Phrasing** — recurring words, sentence patterns, transitions.
4. **Examples** — generic enough to apply to anyone.
5. **Evidence** — unsupported claims; proof points interchangeable with any rival draft.
6. **Rhythm** — paragraphs/bullets of suspiciously equal length; cadence that ignores stakes.
7. **Emotional beats** — flat, over-polished tone; no place where a real stance breaks through.
8. **Usefulness** — sentences that sound smart but don't help the reader decide, act, or understand.

**Then decide — don't just flag:** Cut / Combine / Sharpen (swap a generic example for a named one) / Surprise (shift the angle so the next sentence isn't predictable) / Specify (concrete detail from the audience, company, moment, stakes) / Restructure (break the draft's own pattern).

**Rewrite for surprise, not length.** Default outcome: same length or shorter, more specific nouns, fewer interchangeable verbs, at least one structural break.

## 6. The generic-swap test (final gate)

Pick any paragraph. Swap the audience name, company, or topic for a competitor's. **Does it still work unchanged?** If yes, it's too generic — add specifics or cut it. This is the single fastest check for whether AI wrote something real or something hollow.

## 7. Inhabitation over imitation

When applying a voice profile, three tendencies used naturally beat ten forced in awkwardly. After drafting, ask: *"Does this read like the person would actually write it — or like an AI trying very hard to imitate them?"* If it feels forced, pull back.

---

## Detect mode (audit without rewriting)

When the user wants a scan, not a rewrite:

1. Read the full draft.
2. Name each pattern from §3 or §3b that appears. For each: **pattern name**, the quoted line, and the fix in a few words.
3. Do not rewrite the draft, assign a score, or claim an AI wrote it. Named patterns are checkable evidence; a detector verdict is a guess.
4. Offer to run Edit mode afterward.

Report shape per finding: `**Colon reveal** — "The best part: it learns." → plain sentence, or reserve colons for lists.`

---

## Pre-ship checklist

- [ ] Can complete "I believe that ___" with the core claim; it survives the so-what + why tests (§1).
- [ ] Opens with the conclusion / hook, not setup (§2).
- [ ] Zero AI tells: no em dashes, no hollow openers/closers, no connective sludge, ran the and-test (§3).
- [ ] Scanned for the §3b named patterns; fixed each rather than reshaping it into a fancier version of the same tell.
- [ ] Edit mode kept the writer's voice: minimum effective edit, strong human sentences left alone, real-cadence hedges preserved.
- [ ] No padding — every sentence earns its place; cut until cuts hurt the meaning (§4).
- [ ] Ran the sameness detector: named concrete instances on the eight axes, made the cut/combine/sharpen/surprise/specify/restructure calls (§5).
- [ ] Passed the generic-swap test (§6).
- [ ] Reads like a human wrote it, not an AI imitating one (§7).

---

## See also

- [`writing-voice`](../writing-voice/SKILL.md) — Summer's personal voice profile; load on top of these rules when drafting in her voice.
- [`sme-voice`](../sme-voice/SKILL.md) — capture and apply someone else's voice instead of Summer's.
- [`writing-workshop`](../writing-workshop/SKILL.md) — editing, rewriting, audience-adaptation, and style mimicry modes.
- [`brevity`](../brevity/SKILL.md) — terse chat output and token discipline (this skill governs *artifact* prose; brevity governs *chat* overhead).
- [`sc-marketing-scripts`](../sc-marketing-scripts/SKILL.md) — DLAI course-script authoring; apply this skill's de-slop gate to AI-drafted scripts.
- [`shared/communication-principles.md`](../shared/communication-principles.md) — the canonical principle set these rules draw from.
- [`communication-safeguards`](../communication-safeguards/SKILL.md) — state/timing/intent layer for heated messages, upstream of drafting.

The §3b named-pattern catalog and Detect mode draw on Peter Yang's [no-ai-slop](https://github.com/petergyang/no-ai-slop) skill (2026-07).
