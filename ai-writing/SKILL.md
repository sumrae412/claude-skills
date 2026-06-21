---
name: ai-writing
description: >
  Best practices for AI-authored writing — the consolidated rules for when Claude
  (or any LLM) drafts prose that a human will put their name on. Use whenever you
  ask an AI to write, draft, rewrite, summarize, or polish anything and you want
  the output to NOT read as generic AI sludge: emails, posts, newsletters, docs,
  scripts, bios, marketing copy. Triggers on "/ai-writing", "make this not sound
  like AI", "de-slop this draft", "best practices for AI writing", "write this so
  it doesn't read as ChatGPT". Pulls the AI-relevant rules from the writing and
  communication skills into one pre-ship gate. NOT a voice profile (use
  writing-voice for Summer's voice, sme-voice for someone else's) and NOT a
  conflict/timing layer (use communication-safeguards for heated messages).
user-invocable: true
---

# AI-Authored Writing: Best Practices

The problem with AI writing is not that it's *bad*. It's that it's *interchangeable* — padded, hedged, structurally predictable, and swap-the-noun generic. This skill is the antidote: one consolidated gate the draft passes before it ships.

Consolidates the AI-relevant rules from [`writing-voice`](../writing-voice/SKILL.md), [`writing-workshop`](../writing-workshop/SKILL.md), [`brevity`](../brevity/SKILL.md), and [`shared/communication-principles.md`](../shared/communication-principles.md). These rules are the floor; a voice profile sits *on top of* them.

**Default voice: always Summer's.** Load [`writing-voice`](../writing-voice/SKILL.md) by default for any draft. Switch to [`sme-voice`](../sme-voice/SKILL.md) ONLY when Summer names a specific SME or asks to ghostwrite in someone else's voice. Never draft voiceless — if no voice is named, it's Summer's.

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
- Kill hedges and intensifiers that add nothing: "really," "very," "just," "basically," "actually."
- **And-test:** when ideas are paired ("clear, concise, and compelling," "elevate and enhance"), pick the strongest one. Coordinated qualifiers subtract power.

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

## Pre-ship checklist

- [ ] Can complete "I believe that ___" with the core claim; it survives the so-what + why tests (§1).
- [ ] Opens with the conclusion / hook, not setup (§2).
- [ ] Zero AI tells: no em dashes, no hollow openers/closers, no connective sludge, ran the and-test (§3).
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
