---
name: writing-workshop
description: Edit, rewrite, ghostwrite, transform, or critique writing. Use for style mimicry from samples, brutal editing, audience rewrites, converting bullets into articles/posts/emails/reports, tightening drafts, LinkedIn bio/headline rewrites, adapting one idea for different readers, or auditing a draft for AI tells without rewriting.
---

# Writing Workshop

## Purpose

Help writing survive contact with readers. Choose the mode that matches the user's request and produce the artifact, not a lecture about writing.

## Communication Principles

Before editing or rewriting, load [`../shared/communication-principles.md`](../shared/communication-principles.md). Critique and rewrite modes both run the **§9 sameness-detector** pass on the draft *and* on your own rewrite: name concrete instances across the eight axes (ideas, structure, phrasing, examples, evidence, rhythm, emotional beats, usefulness), produce the diversification plan (cut / combine / sharpen / surprise / specify / restructure), and verify the rewrite passes the generic-swap test. A "tightened" draft that still sounds interchangeable is not done.

## Shared Rules

- Preserve the user's ideas unless they explicitly ask for new ones.
- Flag unclear, contradictory, unsupported, or missing claims instead of silently inventing.
- Match the target audience, format, and tone.
- Avoid filler praise. If the draft is weak, say why and fix it.
- Keep edits truth-preserving for professional bios, resumes, and claims of achievement.

## Mode Selection

Use **Style Mimic** when the user provides writing samples and wants new copy in their voice — for a *reusable* voice profile of a specific person (build once, apply repeatedly), use [`sme-voice`](../sme-voice/SKILL.md) instead.

Use **Brutal Editor** when the user wants a tough edit, teardown, ruthless cuts, or a publishable revision.

Use **Audience Rewrite** when the user wants one idea adapted for multiple audiences.

Use **Bullets To Piece** when the user provides notes/fragments and wants a finished article, post, email, or report.

Use **LinkedIn Positioning** when the user asks for LinkedIn headline/about/bio versions. For a full resume-to-JD rewrite, use `resume-tailor`.

Use **Slop Detect** when the user asks whether a draft reads as AI, or wants it audited / scanned / flagged for AI tells *without* a rewrite.

## Style Mimic

1. Analyze sentence rhythm, vocabulary, paragraph openings, idea endings, avoided habits, and the signature move.
2. Write the requested format in that voice.
3. Stay in the user's lane: do not add beliefs, claims, or expertise not present in the samples or prompt.

## Brutal Editor

Output:

1. **Cuts** - quote wasteful sentences/paragraphs and say why they add nothing.
2. **Weak Ideas** - vague, unsupported, or unearned claims.
3. **Missing** - reader questions the draft fails to answer.
4. **Structure** - opening, order, momentum, ending.
5. **Single Biggest Problem** - the one fix with the highest leverage.
6. **Edited Version** - cut ruthlessly and tighten every sentence.

## Audience Rewrite

Default audiences unless the user specifies others:

- complete beginner: no jargon, concrete analogy
- domain expert: precise terms, deeper than the original
- skeptic: lead with evidence and address the obvious objection
- journalist: headline plus two sentences
- executive: three sentences maximum, decision-oriented

Afterward, name which version was hardest to write well and why.

## Bullets To Piece

Use every supplied idea unless it is contradictory or irrelevant. Build connective tissue, a strong opening, and a closing that lands. Do not invent new ideas; expand only what the notes imply.

End with one line listing any fragments that were unclear or hard to place.

## LinkedIn Positioning

Produce five concise headline/about variants:

- authoritative
- conversational
- results-focused
- niche-specific
- minimal

Ban obvious sludge: `passionate`, `results-driven`, `innovative`, `leveraging`, `seasoned`, `dynamic`, `thought leader`.

Recommend the best version for the stated audience and explain in one sentence.

## Slop Detect

Audit for AI tells without rewriting. Name each pattern found, quote the line, give the fix in a few words, then stop.

1. Read the full draft.
2. Flag each named pattern from [`ai-writing`](../ai-writing/SKILL.md) §3b (binary contrast, faux-insight setup, colon reveal, superficial `-ing` analysis, importance puffery, weasel attribution, fake-strong verb, synonym cycling, negative listing, dramatic fragmentation, fake-profound kicker, summary-recap ending, robotic rhythm) plus the word/opener/closer blocklist.
3. Report per finding: `**Pattern** — "quoted line." → fix in a few words.`
4. Do not rewrite, score, or claim an AI wrote it — named patterns are checkable evidence, a detector verdict is a guess. Offer to run Brutal Editor afterward.

## See also

- [`sme-voice`](../sme-voice/SKILL.md) — when the style mimicry target is a specific SME with reusable voice profile (build once from samples, apply repeatedly).
- [`writing-voice`](../writing-voice/SKILL.md) — when drafting in Summer's own voice rather than mimicking someone else's.
- [`ai-writing`](../ai-writing/SKILL.md) — consolidated best-practices gate for AI-authored prose (sameness detector, AI-tell blocklist, generic-swap test).
