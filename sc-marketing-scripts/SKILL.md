---
name: sc-marketing-scripts
description: Write DeepLearning.AI course scripts — Lesson Zero (L0) introductory videos and marketing teasers featuring Andrew Ng and course instructors. Use this skill whenever asked to write, review, or improve a course intro script, L0 script, marketing script, teaser video script, or any video content for a DeepLearning.AI shortcourse. Also use when asked to check a script against DL.AI guidelines, apply Andrew Ng's voice, or evaluate script quality for course launch materials.
---

# SC Marketing Scripts

Internal guide for writing introductory lessons (Lesson Zero / L0) and marketing teaser scripts for DeepLearning.AI short courses.

---

## Core Principles

### Voice & Tone
- Conversational and collegial — one engineer to another
- Avoid: "should," "understand," "simple," "simply," marketing hype, hyperbole
- Don't say "this is the best tool for xyz" — say "this is a fast and efficient tool for xyz"
- Use active voice: "You instruct the LLM" not "The LLM produces"
- Avoid "Whether you..." openers — salesy, not Andrew's voice
- Prefer direct declarative structure: "In this course, you'll..."

### Hook Immediately
- First 15 seconds must state the course name and what learners will get from it
- Don't open with problem framing or context before introducing the course
- Andrew's standard opener: "I'm excited to introduce [Course Name]..."

### Inverted Pyramid — Teach Early
- Lesson Zero should explain and teach something as early as possible
- Don't structure L0 like a mystery novel that builds to a reveal — give learners the key insight upfront
- A brief concrete example early is better than a long list of topics they'll "learn about later"

### Clarity Over Buzzwords
- When naming a technical concept, follow it immediately with a plain-language explanation
  - ❌ "You'll use prefix caching and tool use"
  - ✅ "You'll use techniques like prefix caching — which reduces costs by reusing repeated context — and tool use, which lets the model take real-world actions"
- **Pick 2–3 concepts max and explain each one.** A short explained list beats a long unexplained one.
- If the list is longer, make it an **explicit numbered list** (slides help) so structure is clear — don't run concepts together in prose
- Emphasize **development-time** benefits, not just post-deployment. Most learners are actively building, not shipping to production yet.

### What We Write Scripts For
- Lesson Zero (L0) intro video — talking head only
- Marketing teaser video — talking head only
- Lesson talking heads (THs)
- **NOT** for lesson screencasts

### Speakability
Scripts are read aloud on a teleprompter — test sentences by reading them out loud before finalizing.

Common speakability fixes:
- Break up compound sentences: "X, and you'll also Y, and then Z" → three separate sentences
- Avoid pronoun ambiguity: "SGLang solves this" → "SGLang solves that memory bottleneck"
- Avoid "Whether you..." — awkward to deliver and salesy; use "If you're..." or a direct declarative instead
- Cut filler affirmations like "Great point—" before Andrew's response
- Vague closers like "that foundation sets up everything that follows" should be replaced with something specific — what does the learner get to do *next*?
- Avoid reusing the same structural phrase ("In this lesson," "In this video") across consecutive slides — flag and replace the second instance

### Lesson 1 Preview Guidance
The Lesson 1 preview at the end of L0 should tease the content of *both* Lesson 1 *and* what it unlocks in Lesson 2, so learners feel momentum. Pattern:

> "In Lesson 1, [specific thing you'll do/learn]. By the end, you'll understand [key insight], and you'll be ready to [what Lesson 2 builds on that]."

❌ "Before you start optimizing, it's important to understand where the bottlenecks are." — generic, could apply to any course
✅ "In Lesson 1, we'll walk through how a model processes a single request — from input tokens to the final generated response. By the end, you'll understand exactly why inference gets expensive, and you'll be ready to dive into the optimization that makes large-scale LLM serving viable."

### Don't Condescend
Avoid framing that implies the learner doesn't know something obvious or that concepts "won't make sense" without the course.
- ❌ "Once you see how much work goes into a single token, the optimizations will make a lot more sense."
- ✅ "Once you see what's happening at the token level, every optimization we build from there will click into place."

### Teleprompter Note
- Google Doc must be in **Edit mode** (not View mode) for updates to appear on the teleprompter
- Remove spacing between paragraphs manually in Edit mode before filming

---

## Marketing Teaser (≤3 minutes)

**Purpose:** Get people excited to sign up. Less comprehensive than L0, more energetic. Should not sound like a condensed version of L0 — different energy, different emphasis.

**Format:** Co-narrated by Andrew + instructors, with B-roll from course screencasts.

**Note:** In shorter marketing videos, the full instructor self-introduction ("Hi, I'm [Name], [Title] at [Company]") is often omitted. Andrew's intro of the instructor is sufficient.

### Structure

1. **Andrew opens** — course name, partnership, instructor intro, hook
2. **Instructor(s)** — highlights of what you'll learn (1 sentence each, concrete)
3. **Andrew or Instructor closes** — brief energetic sign-off

### Template

```
[Andrew]:
"I'm excited to introduce [Course Name], built in partnership with [Company]
and taught by [Instructor Name(s)].

[1–2 sentence hook: what becomes possible or what problem this solves.
No buzzwords without explanation.]

I'm delighted to introduce [Instructor Name], [Title at Company].
[1–2 sentences on what they do / their connection to the developer community.]"

[Instructor 1]:
"Thanks Andrew! In this course, you'll learn to… [one concrete sentence]"

[Instructor 2 (if applicable)]:
"You'll also learn… [one concrete sentence]"

[Andrew]:
"[Optional: banter or quippy remark if it fits naturally]"

[Instructor]:
"I hope you enjoy the course!"

(B-roll: relevant course screencasts)
```

### Marketing Script Anti-Patterns
- Listing tool names without a one-line explanation of what they do — just buzzwords
- Framing all benefits as post-production ("once you deploy...") — mention development-time value
- Making it sound like a comprehensive overview — this should create excitement, not cover everything
- Matching the structure or content of L0 too closely — these are different videos with different goals

---

## Lesson Zero / L0 (5–6 minutes)

**Purpose:** Overview of the course, explain why it matters, teach something immediately. Create excitement for Lesson 1.

**Note:** Andrew narrates a fair amount in L0 — this is the one video he'll appear in, so give him meaningful lines beyond just intro/outro.

### Structure

1. **Andrew** — welcome + course name, motivating context with concrete example, what learners will gain (teach something early), introduces instructor
2. **Instructor** — thanks Andrew, adds their perspective, expands on what will be covered
3. **Andrew** — numbered list of course topics with explanations (slides); connects to instructor
4. **Instructor** — genuine take on why this matters, especially during development
5. **Andrew voiceover** — acknowledgments slide with pronunciation guide
6. **Back to TH** — Instructor previews Lesson 1; Andrew closes with "Let's get started"

### Template

```
[Andrew]:
"Welcome to [Course Name], built in partnership with [Company].

[Motivating context: what's changing / what's now possible — 1–2 sentences]
[Concrete example Andrew can relate to — a personal anecdote or specific scenario
that makes the problem real, not abstract]

[Teach something early: a key insight or small concept the learner can take away
right now, before the course outline]

I'm delighted that our instructor for this course is [Instructor Name], [Title]."

[Instructor]:
"Thanks Andrew! [Genuine enthusiasm — 1 sentence]"

[Andrew — with slides]:
"In this course, you'll learn how to:
1. [Capability 1] — [plain-language explanation of what this means and why it helps]
2. [Capability 2] — [plain-language explanation]
3. [Capability 3] — [plain-language explanation]

[Instructor name] will go through these concepts using [specific tools/libraries]."

[Instructor]:
"[Your genuine perspective on why this topic matters. Focus on development-time
value — how these techniques help while building, not just after deployment.]"

[Switch to acknowledgments slide — Andrew voiceover]:
"Many people worked to make this course. From [Company]: [names — spell phonetically
if pronunciation is unclear]. From DeepLearning.AI: [names]."

[Switch back to TH — Instructor + Andrew]

[Instructor]: "The first lesson will be about…"
[Andrew]: "Sounds great! Let's get started."
```

### L0 Concept List Guidance
- If covering 3–4 concepts: make it an **explicit numbered list with explanations** (slides)
- If covering 5+ concepts: **cut some**. Pick the most important 3 and explain them well. Listing everything without explanation leaves learners unsatisfied.
- Each list item should tell the learner what they'll be able to *do*, not just what topic is covered

---

## Diagram Walkthroughs

When a slide contains a multi-panel or sequential diagram:
- Walk through each panel left to right, naming what the learner is seeing before explaining it
- Don't summarize across all panels before walking them individually — the learner needs to know where to look first
- Use the panel labels or visual cues ("in the first panel," "at the point of difference") to anchor the narration
- Match the visual order; don't jump ahead or reorder for narrative convenience

---

## Review Checklist

Before finalizing any script:

- [ ] All sentences pass a read-aloud test — no pronoun ambiguity, no compound run-ons
- [ ] Lesson 1 preview is specific and teases what Lesson 2 unlocks (not generic)
- [ ] No condescending framing ("this will make more sense once you...")
- [ ] No filler affirmations ("Great point—") before Andrew responses
- [ ] First 15 seconds: course name stated + what learners will gain
- [ ] Andrew's opener uses "I'm excited to introduce..." pattern
- [ ] No "Whether you..." openers
- [ ] All technical terms explained inline on first use
- [ ] No banned words: "should," "understand," "simple," "simply," superlatives
- [ ] Instructor self-intro kept brief or omitted in marketing scripts
- [ ] Active voice throughout
- [ ] Concrete example or scenario present (not just abstract benefits)
- [ ] Development-time value mentioned (not only post-deployment framing)
- [ ] Concept list is 2–3 items max, each explained — not a buzzword dump
- [ ] L0 teaches something early (inverted pyramid)
- [ ] Marketing script sounds different from L0 (different energy/emphasis)
- [ ] Pronunciation guide included for acknowledgments names if non-obvious
- [ ] Google Doc in Edit mode before filming

---

## Reference Examples

See `references/example-scripts.md` for fully annotated Marketing Teaser and L0 scripts from the NAT (NVIDIA NeMo Agent Toolkit) course. Read this file when:
- Writing a new script and want a concrete quality benchmark
- Reviewing a draft and need examples of correct patterns
- Checking whether a script matches the approved style

---

## After Every Session

At the end of any session where this skill was used, always run the session learnings skill to capture new patterns, fixes, and examples discovered during the session. Update this skill's SKILL.md and repackage it before closing.

If the session produced a finalized or near-final script, add it to `references/example-scripts.md` with annotations explaining what's working and why.

---

## Common Mistakes

| Pattern | Problem | Fix |
|---|---|---|
| "Whether you're deploying or just curious..." | Salesy opener, awkward to deliver | "If you're deploying models or just curious about what happens under the hood, let's dive in." |
| "Great point—" filler from Andrew | Padding; kills pacing | Cut it; let Andrew's line stand on its own |
| "That foundation sets up everything that follows" | Generic, uninspiring | Name specifically what the learner unlocks next |
| "Once you see X, Y will make more sense" | Subtly condescending | "Once you see X, Y will click into place" |
| Ambiguous "this" or "it" referring to prior sentence | Unclear on teleprompter; easy to misread | Replace with explicit noun: "that memory bottleneck," "that gap" |
| "Whether you're a beginner or expert..." | Salesy, not Andrew's voice | Start with "In this course, you'll..." |
| "You'll use Phoenix and OpenTelemetry" | Assumes prior knowledge | "You'll use Phoenix and OpenTelemetry — tools that visualize your agent's decisions in real time" |
| Long instructor bio before course intro | Loses viewer in first 15s | Course name + hook first, then instructor |
| Listing 5+ techniques without explanation | Buzzword dump, unsatisfying | Pick 2–3, explain each in plain language |
| All benefits framed as post-deployment | Undersells dev-time value | "This helps while you're building, not just after you ship" |
| L0 concept list with no explanations | Learner doesn't know what any of it means | Each list item needs a one-line plain-language description |
| Marketing script mirrors L0 structure | Redundant, not exciting | Marketing = highlights + excitement; L0 = teaching + overview |
| Abstract labels in examples (Q1, Q2, Q3) | Too vague; learner doesn't know what they refer to | Spell out the actual content: "What's the main topic?", "Who are the key people?" |
| Defining technical terms (hit/miss) before the example | Reads like a glossary, kills narrative flow | Weave the definition into the walkthrough as the term appears naturally |
| Transition sentence with no specifics ("now you're ready for the next level") | Meaningless — could apply to anything | Name the specific concept or action coming next |
| SME notes integrated without checking which slide they fit | Notes may belong to a different slide | Read the slide content first, then map SME notes to where they add explanatory value |
