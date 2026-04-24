---
name: sc-marketing-scripts
description: Write, review, or improve DeepLearning.AI course scripts — Lesson Zero (L0) introductory videos, marketing teasers, Course Map/Overview slides, diagram walkthroughs, Talking Heads (THs). Covers Andrew Ng voice, DL.AI guidelines, teleprompter-aware phrasing, iteration protocol, and an annotated library of reference scripts. Use whenever asked to write, review, or improve any course intro / L0 / marketing / teaser / short-course video script, or evaluate script quality for course launch materials. Supersedes the bundled anthropic-skills:sc-marketing-scripts — this version has curated references (core-principles, script-formats, review-checklist, common-mistakes, example-scripts) and a progressive-disclosure loader the bundled version lacks.
---

# SC Marketing Scripts

Internal guide for writing introductory lessons (Lesson Zero / L0) and marketing teaser scripts for DeepLearning.AI short courses.

---


## Workflow

This skill uses progressive disclosure. Load the reference file for the task you're doing; skip the others to keep context lean.

1. **Before writing OR reviewing any script → load [`references/core-principles.md`](references/core-principles.md).**
   Voice & tone (Andrew Ng's voice), hook immediately, inverted pyramid, clarity over buzzwords, concrete over categorical, purpose framing, TH intro length, cut vague endings, what we write scripts for, iteration protocol, writing like a human, speakability, Lesson 1 preview guidance, don't condescend, teleprompter note. Foundational — always applies.

2. **When writing a specific script type → load [`references/script-formats.md`](references/script-formats.md).**
   Format-specific templates for Course Map / Overview Slides, Marketing Teaser (≤3 min), Lesson Zero / L0 (5–6 min), Diagram Walkthroughs, Lesson Talking Heads (THs). Load when you know which script type you're writing.

3. **When reviewing a draft → load [`references/review-checklist.md`](references/review-checklist.md).**
   The full review checklist plus pointers to the annotated reference examples in `references/example-scripts.md`.

4. **When reviewing — always pair with → load [`references/common-mistakes.md`](references/common-mistakes.md).**
   Pattern → Problem → Fix table of ~25 recurring anti-patterns (salesy openers, filler, vague endings, condescension, etc.).

---

## After Every Session

At the end of any session where this skill was used, always run the session learnings skill to capture new patterns, fixes, and examples discovered during the session. Update this skill's SKILL.md and repackage it before closing.

If the session produced a finalized or near-final script, add it to `references/example-scripts.md` with annotations explaining what's working and why.
