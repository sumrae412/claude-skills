---
name: sc-marketing-scripts
description: Write or review DeepLearning.AI course scripts — Lesson Zero (L0) intros, marketing teasers, Andrew Ng voice, DL.AI guideline checks.
---

# SC Marketing Scripts

Internal guide for writing introductory lessons (Lesson Zero / L0) and marketing teaser scripts for DeepLearning.AI short courses.

---

## Core Principles

Load `shared/communication-principles.md` before drafting any script. The principles there (audience-centered focus, lead with the conclusion, plain-language simplicity, medium calibration, preparation) apply on top of the course-specific rules below. The course-specific rules refine and extend — they do not replace.

### Voice & Tone
- Conversational and collegial — one engineer to another
- Avoid: "should," "understand," "simple," "simply," marketing hype, hyperbole
- Don't say "this is the best tool for xyz" — say "this is a fast and efficient tool for xyz"
- Use active voice: "You instruct the LLM" not "The LLM produces"
- Avoid "Whether you..." openers — salesy, not Andrew's voice
- Prefer direct declarative structure: "In this course, you'll..."
- Always speak directly to the learner — use "you will learn," "you will build," "you will understand," not "we will cover" or "students will learn." The learner is always the subject of what happens in the course.

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

### Concrete Over Categorical
Name the specific things, not the abstract category they belong to.
- ❌ "a different generation paradigm entirely"
- ✅ "from text to images"
- ❌ "a new optimization technique"
- ✅ "a radix tree cache"

### Purpose Framing Over Output Framing
Frame around what the tool *does* or *is used for*, not just what it *produces*.
- ❌ "here's what SGLang produces with it"
- ✅ "here's what SGLang uses it for"
- ❌ "the output is..."
- ✅ "SGLang uses this to..."

### Talking Head Intro Length
Lesson-specific talking head intros (not L0) should be tight — ~20 seconds max:
- One sentence of context (what came before)
- One sentence of what's new in this lesson
- Done. No preview lists, no expanded setup.

### Cut Vague Endings
If a sentence ending doesn't add specific information, cut it rather than replacing with something generic.
- ❌ "...to get high quality visual output"
- ✅ [cut — the example already showed the quality]
- ❌ "...and that's what makes this powerful"
- ✅ [end on the specific fact, not the editorial]

### What We Write Scripts For
- Lesson Zero (L0) intro video — talking head only
- Marketing teaser video — talking head only
- Lesson talking heads (THs)
- **NOT** for lesson screencasts

### Iteration Protocol
- When the user rewrites a sentence and keeps their version, accept it — do not re-suggest the same alternative in subsequent turns
- Flag issues once; if the user declines the fix, move on
- Only re-raise a concern if it creates a new problem downstream

### Writing Like a Human
- Simple language — short sentences, plain words
- No AI-giveaway phrases — never use: "dive into," "unleash," "game-changing," "revolutionary," "transform," "delve," "it's worth noting," "in conclusion," "leverage" (as a verb)
- Direct and concise — remove unnecessary words
- Natural tone — starting with "And" or "But" is fine
- No marketing hype — avoid promotional language
- No forced friendliness — be honest and direct
- No fluff — cut unnecessary adjectives and adverbs
- Clarity first — if a sentence has to be read twice, rewrite it

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
✅ "In Lesson 1, we'll walk through how a model processes a single request — from input tokens to the final generated response. By the end, you'll understand exactly why inference gets expensive, and you'll be ready to tackle the optimization that makes large-scale LLM serving viable."

### Don't Condescend
Avoid framing that implies the learner doesn't know something obvious or that concepts "won't make sense" without the course.
- ❌ "Once you see how much work goes into a single token, the optimizations will make a lot more sense."
- ✅ "Once you see what's happening at the token level, every optimization we build from there will click into place."

### Teleprompter Note
- Google Doc must be in **Edit mode** (not View mode) for updates to appear on the teleprompter
- Remove spacing between paragraphs manually in Edit mode before filming

---

## Course Map / Overview Slides

These slides appear at the start of each lesson and show where the current lesson fits in the overall course. The script should NOT just describe what's on the slide or restate the lesson list.

**Goal:** Help the learner understand why what they're doing in this lesson matters and how it connects to the broader arc of the course.

**Pattern:**
- Acknowledge what they've already built (1 sentence, specific)
- Name what's new in this lesson and why it's a meaningful step, not just the next item on a list
- Optionally, gesture at what it unlocks in the lesson(s) ahead

**Do NOT:**
- Repeat anything already said in the talking head intro for the same lesson
- Just narrate the bullet list on the slide ("Lesson 1 covered X, Lesson 2 covered Y...")
- Use generic transitions ("now we move on to the next topic")

**Example (L4):**
❌ "You've completed three lessons. This lesson is Lesson 4, where we move into diffusion."
✅ "The first three lessons gave you the full LLM inference stack. This lesson adds a second modality — diffusion models. SGLang handles both with the same framework, and by the end you'll see why that matters."

---

## Marketing Teaser (≤3 minutes)

**Purpose:** Get people excited to sign up. Less comprehensive than L0, more energetic. Should not sound like a condensed version of L0 — different energy, different emphasis.

**Format:** Co-narrated by Andrew + instructors, with B-roll from course screencasts.

**Note:** In shorter marketing videos, the full instructor self-introduction ("Hi, I'm [Name], [Title] at [Company]") is often omitted. Andrew's intro of the instructor is sufficient.

### Structure

1. **Andrew opens** — course name + instructor credential woven in inline; 2–3 sentence problem hook; 1 sentence course overview
2. **Instructor** — picks up from Andrew's problem framing; motivation/analogy; bridges to course
3. **Andrew closes** — what the learner will do + concrete outcome + call to action

**Key notes:**
- Instructor does NOT self-introduce — Andrew carries the introduction inline
- Andrew carries the CTA
- 250–300 words total

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

1. **Andrew** — welcome, problem framing, high-level course overview in prose (NOT a numbered list on camera), introduces instructor
2. **Instructor** — thanks Andrew, connects to problem, motivation/analogy, course arc
3. **Andrew** — why this tool/framework was chosen; concrete outcome naming the specific thing built
4. **Andrew voiceover** — acknowledgments
5. **Instructor** — Lesson 1 preview + energetic closer
6. **Andrew** — final call to action

**Note:** Andrew does NOT read a numbered list on camera. Course overview should be delivered in natural prose. Andrew delivers the final CTA.

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

## Lesson Talking Heads (THs)

**Purpose:** 1–3 sentences max, spoken by the instructor (not Andrew).

**Pattern:**
- Connect to the prior lesson OR name the core tension
- State what the learner will build
- Close with an energetic line tied to the lesson theme

**Anti-patterns:**
- "Let's dive in" is banned
- Don't repeat the lesson title verbatim
- Don't open cold — always connect to what came before or name the tension
- No more than 3 sentences

**Conclusion TH:**
- Recap the full arc of the course
- Key takeaway — a principle, not a list
- What's next for the learner
- Genuine sign-off

---

## Review Checklist

Before finalizing any script:

- [ ] Run through the checklist at the end of `shared/communication-principles.md` first — audience-centered, leads with the conclusion, plain language, tuned to the medium
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
- [ ] Course map slide script explains why the current lesson matters — not just what's on the list
- [ ] Lesson TH intros are ~20 seconds — one sentence of context, one sentence of what's new
- [ ] Sentences end on specific facts, not vague editorial payoffs
- [ ] No AI-giveaway phrases: "dive into," "unleash," "game-changing," "revolutionary," "transform," "delve," "it's worth noting," "in conclusion," "leverage" (as a verb)
- [ ] No marketing hype or forced enthusiasm
- [ ] No unnecessary adjectives or adverbs
- [ ] Learner is always addressed directly — "you will learn/build/understand," never "we will cover"
- [ ] No "we will" — replace with "you will"
- [ ] Instructor does not self-introduce in marketing script
- [ ] Concrete outcome names the specific thing built — not just "a working app"
- [ ] "In this course" used no more than once per speaker turn
- [ ] Andrew does NOT read a numbered list on camera in L0
- [ ] Instructor delivers the Lesson 1 preview and energetic closer in L0; Andrew delivers the final CTA

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
| "Whether you're deploying or just curious..." | Salesy opener, awkward to deliver | "If you're deploying models or just curious about what happens under the hood — this course will get you there." |
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
| Course map slide just narrates the lesson list | Misses the point of the slide | Explain why this lesson matters and how it connects to the broader arc |
| Categorical framing ("a different paradigm") | Abstract, not informative | Name the specific things: "from text to images" |
| Output framing ("here's what SGLang produces") | Passive; puts system before learner | Purpose framing: "here's what SGLang uses it for" |
| Vague sentence endings ("...to get high quality output") | Adds no information | Cut it — let the specific example do the work |
| Lesson TH intro longer than ~20 seconds | Over-explains; learner already has context | One sentence of prior context + one sentence of what's new |
| Re-suggesting a phrasing the user already declined | Ignores user's judgment | Accept the user's version; move on |
