---
name: product-sprint
description: 7-stage rapid product sprint — user research (debate technique), context-primed PRD, stakeholder persona, interactive prototype, pitch with stakeholder rehearsal, personal OS lens, and demo judging. Takes an idea from insight to validated vision in ~30 minutes. Triggers on "product sprint", "rapid PM", "validate idea", "quick PRD", "prototype an idea", "debate technique", "product pitch", "demo judge", "stakeholder rehearsal", "personal OS", or "20-minute PM cycle".
---

# Product Sprint

A guided 7-stage product sprint combining Marily Nika's AI-Enhanced PM Cycle with Hiten Shah's stakeholder cloning and Personal OS workflows. Takes a product idea from raw insight to validated, stakeholder-tested vision with tangible deliverables.

**Speed is the point.** Each stage produces a concrete artifact that feeds the next. Deeper analysis is available via connected skills at each exit point.

## Before Starting

1. Read `references/debate-technique.md` for the Stage 1 debate framework
2. Read `references/segmentation-matrix.md` for the Stage 1 customer segmentation framework
3. Read `references/prd-template.md` for Stage 2 PRD structure
4. Read `references/stakeholder-clone.md` for Stage 3 and Stage 5 stakeholder simulation
5. Ask: "What's your product idea? Describe it in 1-2 sentences."
6. Ask which stage to start from (default: Stage 1)

## Stage Flow

```
Idea → Stage 1 (Research) → Stage 2 (PRD) → Stage 3 (Stakeholder Persona)
     → Stage 4 (Prototype) → Stage 5 (Pitch + Rehearsal)
     → [Stage 6 (Personal OS)] → [Stage 7 (Judge)]
```

Stages 1-5 are the core sprint. Stages 6-7 are optional but valuable.
Each stage accepts external input — users can skip ahead if they bring their own research, PRD, etc.

---

## Stage 1: Rapid User Research (The Debate Technique)

**Goal**: Validate the idea and extract the minimum feature set needed for product-market fit.

**Time**: ~5 minutes

**Process**:
1. Take the user's idea (1-2 sentences)
2. Use WebSearch to find real user opinions — target Reddit, forums, review sites, Hacker News
3. Search for: `[product concept] site:reddit.com`, `[product concept] opinions forum`, `[product concept] complaints reviews`
4. Read `references/debate-technique.md` and run the debate:
   - Create **Agent PRO** (enthusiastic early adopter) and **Agent CON** (skeptical pragmatist)
   - Have them debate 10+ rounds using evidence from real user opinions
   - Each round: PRO makes a case → CON rebuts → PRO counters
   - Track which arguments CON concedes vs. holds firm on
5. Synthesize into the **Minimum Feature Set** — features that convinced the skeptic

6. After the debate, build a **Customer Segmentation Matrix**:
   - Read `references/segmentation-matrix.md` for the framework
   - Choose two behavioral axes relevant to this product's users
   - Build a 3x3 (or 2x2) grid with named segments
   - Estimate percentage distribution across segments
   - For each major segment (>10%), define: core need, discovery path, retention driver

**Output**:
```
## Stage 1: Rapid User Research — COMPLETE

### Key User Sentiment
[2-3 sentence summary of what real users say]

### The Debate (10 rounds)
[Condensed debate with key turning points]

### Minimum Feature Set
1. [Feature] — convinced skeptic because [reason]
2. [Feature] — ...
3. [Feature] — ...

### Critical Concerns to Address
- [Concern the skeptic never conceded]

### Customer Segmentation Matrix
**Axes**: [Axis 1] x [Axis 2]

| | [Low] | [Mid] | [High] |
|---|---|---|---|
| **[Axis 2 High]** | [Segment] (~X%) | [Segment] (~X%) | [Segment] (~X%) |
| **[Axis 2 Mid]** | [Segment] (~X%) | [Segment] (~X%) | [Segment] (~X%) |
| **[Axis 2 Low]** | [Segment] (~X%) | [Segment] (~X%) | [Segment] (~X%) |

**Primary segments** (>10%):
- [Segment]: needs [X], discovers via [Y], retains because [Z]
- [Segment]: needs [X], discovers via [Y], retains because [Z]
```

**Deep-dive exits** (offer after completing):
- "Want deeper competitive analysis?" → invoke `/competitive-brief`
- "Want formal market validation with TAM/SAM/SOM?" → invoke `/startup-analysis`

**Accepts input from**: If user ran `product-management:product-brainstorming` first, use that output as the idea input.

---

## Stage 2: Context-Primed PRD Generation

**Goal**: Turn the minimum feature set into a structured PRD, enriched with domain-specific context.

**Time**: ~5 minutes

**Process**:
1. Take the Minimum Feature Set from Stage 1 (or user-provided features)
2. **Context priming** — before generating the PRD, ask:
   - "Do you have any domain-specific frameworks, docs, playbooks, or industry standards that should inform this PRD?" (e.g., HIPAA for health, PCI for payments, accessibility guidelines, internal design systems)
   - If yes: read/absorb the framework first, then apply it to the PRD — this is the "teach the framework, then apply to context" pattern
   - If no: proceed with general best practices
3. Ask exactly 3 targeted questions:
   - "Who is the primary target user? Be specific — job title, situation, pain level."
   - "What's the ONE constraint that shapes everything? (budget, timeline, platform, regulation)"
   - "How will you know this succeeded? Give me one metric."
4. Read `references/prd-template.md` and generate the PRD, incorporating absorbed frameworks

5. If Stage 1 produced a segmentation matrix, add a **Service Design per Segment** section:
   - For each major segment: map Must-Have features to that segment's core need
   - Identify which features serve multiple segments (shared infrastructure)
   - Design segment-specific touchpoints (onboarding flows, content, events, or tiers)
   - Flag any segment that's underserved by the current feature set

**Output**: Complete PRD with:
- Problem Statement (tied to debate evidence from Stage 1)
- Target Users (from question 1, enriched by segmentation matrix if available)
- Feature Prioritization (MoSCoW — Must/Should/Could/Won't)
- Service Design per Segment (features mapped to segments, shared vs. segment-specific)
- Success Metrics (from question 3)
- Key Constraint (from question 2)
- Domain Framework Alignment (if frameworks were provided)
- Risks (from Stage 1 skeptic's unresolved concerns)

**Deep-dive exits** (offer after completing):
- "Want Business Model Canvas, market sizing, and Go/NoGo?" → invoke `/startup-planner` starting at Stage 8
- "Want an alternative PRD format?" → invoke `product-management:write-spec`

---

## Stage 3: Stakeholder Persona (Clone Your Decision-Maker)

**Goal**: Build an AI persona of the key stakeholder who will approve/fund/champion this product, so you can rehearse and tailor your approach in Stage 5.

**Time**: ~3 minutes

**Process**:
1. Ask: "Who is the key decision-maker for this product? (boss, investor, board member, customer)"
2. Gather context about them — ask one at a time:
   - "What's their role and what do they care about most?" (metrics, innovation, risk, revenue)
   - "How do they prefer to receive information?" (data-first, story-first, visual, concise exec summary)
   - "What are their known hot buttons or pet peeves?" (hates surprises, loves data, allergic to jargon)
   - "What would make them say NO immediately?" (too expensive, too risky, not aligned with strategy)
   - "Do you have any documents from them — operating manuals, memos, articles they've shared, past feedback?" (If yes, read and absorb)
3. Synthesize into a stakeholder persona

Read `references/stakeholder-clone.md` for the persona construction framework.

**Output**:
```
## Stage 3: Stakeholder Persona — COMPLETE

### [Name/Role] Profile
- **Decision style**: [data-driven / intuition-led / consensus-seeking]
- **Communication preference**: [concise / detailed / visual / narrative]
- **Top priorities**: [what they optimize for]
- **Instant NO triggers**: [what kills proposals]
- **What earns a YES**: [what they respond to]

### How to pitch to them
- Lead with: [what to open with]
- Emphasize: [what to stress]
- Anticipate these questions: [likely pushback]
- Avoid: [what to skip or downplay]

---
Completed: [date]
Next: Stage 4 — Interactive Prototype
```

**Connected skills**:
- For personality-framework-based analysis of this relationship → invoke `/personal-coach` Stage 3 (Interpersonal Dynamics)

---

## Stage 4: Interactive Prototype

**Goal**: Generate a functional UI prototype that makes the PRD tangible.

**Time**: ~5 minutes

**Process**:
1. Take the PRD from Stage 2 (or user-provided PRD)
2. Ask: "Which format?"
   - **React + Tailwind** — self-contained component, works in Claude artifacts or CodeSandbox
   - **HTML/CSS standalone** — opens directly in any browser, no build tools
3. Read `references/prototype-patterns.md` for patterns
4. Generate the prototype:
   - Dashboard layout reflecting the Must-Have features
   - Visual cues from the PRD (e.g., "Local Processing" badge if privacy was key)
   - Interactive elements where meaningful (toggle states, sample data)
   - Responsive design basics

**Key rules**:
- Prototype the MUST-HAVE features only — no scope creep
- Include realistic sample data, not lorem ipsum
- Visual hierarchy should match feature priority from PRD

**Output**: Working prototype code + brief description of what it demonstrates.

**Connected skills**:
- For higher design quality → invoke `frontend-design:frontend-design`
- For visual mockup images instead of code → invoke `/image-generation`

---

## Stage 5: Vision Pitch + Stakeholder Rehearsal

**Goal**: Create a compelling pitch package AND rehearse it against the stakeholder persona from Stage 3.

**Time**: ~5 minutes

**Process**:

### Part A: Build the Pitch (~3 minutes)
1. Take all prior outputs (research, PRD, stakeholder persona, prototype)
2. Generate three deliverables:

**Elevator Pitch** (30 seconds / ~75 words):
- Hook: The problem in one sentence
- Solution: What the product does
- Proof: One data point from Stage 1 research
- Ask: What you need from the audience

**Scene-by-Scene Storyboard** (6-8 scenes):
For each scene:
- Visual description (what the camera shows)
- Dialogue/voiceover (what's said)
- Key message (what the audience should feel/understand)
- Duration (seconds)

**Key Messaging Points**:
- Tagline (3-5 words)
- Three value pillars (one sentence each)
- Objection handlers (from Stage 1 debate — the skeptic's top 3 concerns + responses)

Read `references/pitch-script-template.md` for structure.

### Part B: Stakeholder Rehearsal (~2 minutes)
Using the Stage 3 persona, simulate presenting the pitch:

1. **Present the elevator pitch as if to the stakeholder**
2. **Generate the stakeholder's likely response** — in their voice, based on their profile:
   - What questions would they ask?
   - What would they push back on?
   - What would get them excited?
3. **Provide coached responses** to each objection — specific language the user can use
4. **Rate the pitch** from the stakeholder's perspective: Ready / Needs Work / Major Gaps
5. **Refine** — adjust the pitch based on the rehearsal, then present the final version

If no Stage 3 persona exists, ask: "Who are you pitching to? Give me a quick sketch — role, what they care about, what makes them say no." Build a lightweight persona on the spot.

**Output**: Complete pitch package + rehearsal transcript + refined pitch.

**Connected skills**:
- Script writing patterns informed by `sc-marketing-scripts`

---

## Stage 6: Personal OS Lens (Optional)

**Goal**: Reflect on the sprint through your own personality and working-style lens — identify blind spots, communication adjustments, and energy management for the work ahead.

**Time**: ~3 minutes

**Process**:
1. Ask: "Have you done a personality profile before? (Enneagram, MBTI, DISC, Human Design, or others)"
   - If yes: "What are your types?" and absorb them
   - If no: "I'll ask a few quick questions to get a rough sense of your working style" — ask 3-4 behavioral questions:
     - "When you're stressed about a project, do you tend to withdraw and research more, or push harder and take action?"
     - "In meetings, do you tend to speak first or wait until you've processed?"
     - "When facing conflict, do you confront directly, seek harmony, or analyze from the sidelines?"
2. Using their profile (or behavioral sketch), analyze the sprint outputs:

**Blind spot check**:
- "Given your [type], you may have over-indexed on [tendency] — here's what you might be missing"
- "Your PRD emphasizes [aspect] which aligns with your [framework trait] — but your target user might prioritize [different aspect]"

**Stakeholder compatibility**:
- If Stage 3 persona exists: "Your [type] communicating with a [stakeholder type] means you should [specific adjustment]"
- Identify friction points between their style and the stakeholder's

**Energy management**:
- "The next phase of this work (building/selling/iterating) will require [energy type] — based on your profile, here's how to sustain it"

**Output**:
```
## Stage 6: Personal OS Lens — COMPLETE

### Your Profile
[Type summary or behavioral sketch]

### Sprint Blind Spots
- [Potential blind spot 1 + mitigation]
- [Potential blind spot 2 + mitigation]

### Stakeholder Dynamics
- [How your style interacts with the decision-maker's]
- [One key communication adjustment]

### Energy Forecast
- [What the next phase demands]
- [How to sustain energy given your type]

---
Completed: [date]
```

**Connected skills**:
- For deeper personality-based coaching → invoke `/personal-coach` (full 4-stage system with profiles, interpersonal dynamics, and real-time coaching)

**Important**: Personality frameworks are lenses, not labels. This stage offers self-awareness patterns, not clinical assessment. For persistent work challenges involving stress, burnout, or interpersonal conflict, consider working with a licensed coach or therapist.

---

## Stage 7: Demo Judge (Optional)

**Goal**: Evaluate product pitches using structured criteria.

**Time**: ~3 minutes per pitch

**Process**:
1. User provides pitch content (text, demo description, or multiple pitches to compare)
2. Evaluate each pitch on four criteria (25% each):

| Criteria | What to assess |
|----------|---------------|
| **Innovation** | Novel approach? Solves a real unmet need? |
| **Impact** | Scale of potential impact? Who benefits and how much? |
| **Feasibility** | Can this actually be built? Realistic timeline/resources? |
| **Storytelling** | Compelling narrative? Clear problem→solution arc? |

3. Score each criterion 1-10 with specific reasoning
4. If multiple pitches: rank and select top entries

**Output**:
```
## Stage 7: Demo Judge — COMPLETE

### [Product Name] Scorecard
- Innovation: X/10 — [reasoning]
- Impact: X/10 — [reasoning]
- Feasibility: X/10 — [reasoning]
- Storytelling: X/10 — [reasoning]
- **Overall: X/40**

### Strengths
- [Top 2-3]

### Areas for Improvement
- [Top 2-3 with specific suggestions]

### Rankings (if multiple)
1. [Product] — X/40 — [one-line reason]
2. ...
```

**Important**: AI evaluation supplements but does not replace human judgment. For high-stakes decisions (funding, awards), always include human evaluators alongside this tool.

---

## Session Flow

1. **Start**: "What's your product idea? Describe it in 1-2 sentences." Then: "Want to start from Stage 1, or jump to a specific stage?"
2. **During**: Move through stages sequentially. After each stage, offer the deep-dive exit and ask "Ready for Stage [N+1]?"
3. **End**: Summarize all outputs. Suggest next steps: "You now have research, a PRD, a stakeholder-tested pitch, and a prototype. Want to go deeper with `/startup-planner` for business model work?"

### Cumulative Context Rule

Each stage's output becomes input context for every subsequent stage. Maintain a running project brief — don't treat stages as isolated. Specifically:
- Stage 2 PRD references Stage 1 debate evidence and segmentation matrix
- Stage 3 stakeholder persona is informed by which segments matter most
- Stage 4 prototype reflects PRD priorities shaped by segmentation
- Stage 5 pitch uses debate evidence as proof points and addresses stakeholder concerns

When the user provides additional context mid-sprint (documents, frameworks, competitor info), absorb it into the running brief — it informs all remaining stages, not just the current one.

## Output Format

After each stage:
```
## Stage X: [Name] — COMPLETE

[Stage output]

---
Completed: [date]
Next: Stage [X+1] — [name]
Deep-dive options: [list relevant connected skills]
```

## Connected Skills Map

| When you want... | Use... |
|-------------------|--------|
| Deeper competitive analysis | `/competitive-brief` |
| TAM/SAM/SOM market validation | `/startup-analysis` |
| Business Model Canvas + Go/NoGo | `/startup-planner` Stage 8+ |
| Alternative PRD format | `product-management:write-spec` |
| Higher design quality prototype | `frontend-design:frontend-design` |
| Visual mockup images | `/image-generation` |
| Marketing script patterns | `sc-marketing-scripts` |
| Idea brainstorming (pre-sprint) | `product-management:product-brainstorming` |
| Deep personality coaching | `/personal-coach` |
| Interpersonal dynamics | `/personal-coach` Stage 3 |
| Stakeholder relationship insights | `/personal-coach` Stage 3 + Stage 6 combo |

---

## After Every Session

Run `/session-learnings` to capture patterns discovered during the sprint.
