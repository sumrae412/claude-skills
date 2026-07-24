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
- Introduce a technical term only when it earns its place in this script — then teach it in the same breath. A term the learner never needs again is jargon; cut it.
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

### Anchor to What They Already Know
Explain the new idea by mapping it onto something the learner already understands, then say where the comparison stops.
- Build the explanation on prior knowledge, not on what you wish the learner already knew. "An embedding is like giving each word an address in a city, where similar words live on the same street."
- Name the break-point. Every analogy leaks; say where. "That address picture holds until you remember the city has hundreds of dimensions, not two — so 'nearby' means something math does, not something you can point at."
- A good anchor does more work than three careful sentences of abstraction. Reach for it before you reach for precision.

### Honest Limit — Name Where the Simple Version Bends the Truth
Simplify without falsifying. When a simplification drops something real, say so in one line and decide whether it matters for this lesson.
- Never say something false to make it land. "A token is roughly a word" is fine; "a token is a word" is wrong, and learners carry the wrong version into the next lesson.
- Flag, then judge. "For now, think of it as one word per token — we'll see it's actually word-pieces when we hit tokenization." If the caveat doesn't matter yet, drop it; if it will trip them later, plant the one-line flag now.
- This is the teaching version of not overselling: the credibility you keep is the learner's trust that what you told them is true.

### Pre-empt Where They'll Get Lost
Before finalizing, find the one or two places this specific learner most likely misunderstands, and write the exact line that clears each.
- Predict the stumble, don't discover it in the edit. The usual culprits: a term used a beat before it's defined, an analogy pushed past its break-point, a step that's obvious to you but skips a rung for them.
- Write the fix as a spoken line, not a note-to-self. "If you're wondering why we don't just use a bigger model — that's exactly the trade-off the next lesson measures."
- Two clears, maximum. More than that means the explanation itself needs restructuring, not patching.

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
Aim at the real learner's level, not a stereotype of it — and miss in neither direction. Talking down insults them; talking over their head loses them. The curse of knowledge is the expert's blind spot: forgetting what it was like not to know. Set the floor (what you can safely assume they know) and the ceiling (what this script must not require) before you write, and pitch between them.

Avoid framing that implies the learner doesn't know something obvious or that concepts "won't make sense" without the course.
- ❌ "Once you see how much work goes into a single token, the optimizations will make a lot more sense."
- ✅ "Once you see what's happening at the token level, every optimization we build from there will click into place."

### Teleprompter Note
- Google Doc must be in **Edit mode** (not View mode) for updates to appear on the teleprompter
- Remove spacing between paragraphs manually in Edit mode before filming

---

