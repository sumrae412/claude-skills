---
name: synthetic-persona
description: Build "synthetic people" from public data for product reviews, brainstorming, pitch rehearsals, and interpersonal dynamics analysis. Use when you want a specific person's perspective on your product, ideas, or communication approach. Triggers on "synthetic persona", "synthetic client", "what would [name] think", "build a persona", "role-play as", "rehearse a pitch", "how would [person] react", or "model my [boss/client/stakeholder]".
---

# Synthetic Persona — Public-Data Persona Builder

Build a "synthetic person" from public data, then use that persona to review your product, brainstorm ideas, rehearse conversations, or analyze interpersonal dynamics. Goal: get work to 80-90% before the real conversation.

**This is pre-vetting, not a replacement for real human feedback.**

## Important: Public Data Only

**Never use private or confidential information** to build a persona. All sources must be publicly available or explicitly provided by the user. If the user offers confidential material, decline and explain why.

## Before Starting

1. Read `references/research-guide.md` for data collection process, persona card template, and meta-prompt template
2. Read `references/review-prompts.md` for mode-specific prompts and report template
3. Ask which stage to work on (or start from Stage 1 for a new persona)
4. If the user has built a persona before, check memory for a saved persona card and prompt

## Stages Overview

| Stage | Purpose | Output |
|-------|---------|--------|
| 1. Research & Build | Gather public data, build empathy map, define JTBD, generate persona | Persona Card (w/ JTBD + Empathy Map) + Persona Prompt (saved to memory) |
| 2. Product Scan | Read codebase, build product map + optional journey map | Product Map + Journey Map + enriched persona lens |
| 3. Interactive Session | Review, brainstorm, rehearse, or analyze | Dialogue session |
| 4. Findings Report | Synthesize with opportunity scoring | Scored report in docs/persona-reviews/ |

Work through **one stage per session**. Stages 3-4 are repeatable with the same persona.

---

## Stage 1: Research & Build Persona

**Goal**: Collect public data about a real person and generate a persona Claude can role-play.

**Entry question**: "Who would you like to model? Tell me their name, role, and relationship to you or your product."

**Process:**

1. **Gather sources** — Ask what the user already has (articles, talks, docs). Then use web search to find additional public material. See `references/research-guide.md` for source categories.

2. **Organize with Empathy Map** — As you process sources, slot observations into the Says/Thinks/Does/Feels grid (template in research guide). This surfaces patterns before you synthesize.

3. **Extract patterns** — For each source, extract: priorities, communication style, decision patterns, domain expertise, frustrations, values. Use the Data Extraction Checklist in the research guide.

4. **Ask about personality frameworks** — "Do you know their Enneagram type, MBTI, DISC, or other framework results?" Even partial data helps.

5. **Define their JTBD** — Ask: "What job is this person hiring your product (or a product like yours) to do?" Frame as: "When [situation], I want to [motivation], so I can [expected outcome]." Capture functional, emotional, and social dimensions.

6. **Build the Persona Card** — Synthesize into structured format (template in research guide). Includes JTBD statement and Empathy Map summary. Present to user for validation: "Does this feel like them? What's off?"

7. **Meta-prompt step** — Feed all gathered material to Claude and generate a Persona Prompt — the actual role-playing instructions written in second person. This produces richer behavior than the structured card alone. See meta-prompt template in research guide.

8. **Save to memory** — Store both the Persona Card and Persona Prompt as memory files for reuse in future sessions.

**Output format:**
```
## Stage 1: Research & Build Persona — COMPLETE

### Persona Card
[Full persona card]

### Persona Prompt
[Generated role-play instructions]

### Confidence Assessment
- Strong: [aspects backed by multiple sources]
- Thin: [aspects based on limited data]
- Unknown: [aspects we couldn't find data on]

---
Completed: [date]
Next stage: Stage 2 — Product/Context Scan (or Stage 3 if reviewing something other than a codebase)
```

---

## Stage 2: Product / Context Scan

**Goal**: Read the current project to build a "product map" the persona will review.

**Entry question**: "Should I scan the current codebase, or do you want to present specific materials for review?"

**Process:**

1. **Scan the project** — Read UI templates, routes, error messages, README, docs, onboarding flows. See scan guide in `references/review-prompts.md`.

2. **Build the product map** — Organize findings by user-facing areas (not code architecture): Getting Started, Core Workflow, Secondary Features, Communication, Terminology.

3. **Optionally build a journey map** — For end-to-end reviews, map the user experience across stages: Awareness → Onboarding → Core Use → Advanced Use → Retention. Each stage tracks touchpoints, actions, emotions, pain points, and JTBD alignment. See journey map template in `references/review-prompts.md`.

4. **Two-pass enrichment** — Feed the product map summary back into the persona: "Now that you know what this product does, what matters most to [Name]?" Refine the persona lens to be product-specific.

5. **Present the map** — Show the user the product map (and journey map if built). Ask: "Is this a fair representation of the product? Anything missing?"

**Output format:**
```
## Stage 2: Product / Context Scan — COMPLETE

### Product Map
[Organized by user-facing areas]

### Persona Lens (Enriched)
[What [Name] would focus on most, given the product]

---
Completed: [date]
Next stage: Stage 3 — Interactive Session
```

---

## Stage 3: Interactive Session

**Entry question**: "Which mode do you want?"
- **A. Product Review** — Walk through the product as [Name], react to features
- **B. Brainstorming** — Use [Name] as a sounding board for ideas or decisions
- **C. Rehearsal** — Practice pitching or presenting to [Name]
- **D. Dynamics Analysis** — Analyze how YOU and [Name] interact (requires your personality profile)

See `references/review-prompts.md` for mode-specific prompt templates and the **persona weighting table** — each mode emphasizes different persona dimensions (e.g., Product Review leans on domain expertise and JTBD; Rehearsal leans on communication style and personality frameworks).

### Mode A: Product Review (Synthetic Client)

Adopt the persona. Walk through the product map feature-by-feature. React as [Name] would:
- "As [Name], I'd be confused by..."
- "This solves my [priority] directly"
- "Where's the [expected feature]?"

Stay in character. Flag low-confidence reactions with **[LOW CONFIDENCE]**.
The user can push back, clarify, or redirect at any time.

### Mode B: Brainstorming (Sounding Board)

Adopt the persona for open-ended problem-solving. The user presents challenges, ideas, or decisions. Respond with [Name]'s characteristic thinking style. Functions as an on-demand advisor.

### Mode C: Rehearsal (Pitch Practice)

Adopt the persona so the user can practice a conversation. React authentically — pushback, questions, enthusiasm, skepticism. After the rehearsal, break character and debrief: what landed, what didn't, how to improve.

### Mode D: Dynamics Analysis

**Requires**: the user's own personality profile (from personal-coach skill or provided directly).

Analyze the interpersonal dynamic between the user and [Name]:
- Natural alignment points
- Friction areas
- Communication strategy recommendations
- Specific approach for the topic at hand

**Professional help boundary**: If dynamics analysis surfaces patterns of persistent distress, workplace harassment, or mental health concerns beyond communication style differences, acknowledge that this goes beyond what a persona-based tool can address and suggest the user speak with a licensed professional (therapist, HR advisor, or workplace mediator as appropriate).

---

## Stage 4: Findings Report

**Goal**: Synthesize the interactive session into a structured, actionable report.

**Process:**

1. **Devil's advocate review** — Before writing the report, run the critical self-review prompt (see Stage 3.5 in `references/review-prompts.md`). This catches sycophancy, blind spots, and unwarranted speculation. Revise findings based on this review.
2. Organize into the report template (see `references/review-prompts.md`)
3. **Score priority issues** — For each gap or issue, calculate Opportunity Score: `Importance + (Importance - Satisfaction)`. Scores > 10 = high-priority. This uses the JTBD from Stage 1 to ground importance ratings.
4. Assess confidence for each finding — strong, moderate, or speculative
5. Identify what to validate with the real person
6. Recommend 3-5 concrete next steps

**Save to**: `docs/persona-reviews/YYYY-MM-DD-[name]-review.md`

**Output format:**
```
## Stage 4: Findings Report — COMPLETE

[Full report — see template in references/review-prompts.md]

---
Completed: [date]
Saved to: docs/persona-reviews/[filename]
```

---

## Session Flow

1. **Start**: "Which stage do you want to work on? Or should we start from Stage 1?"
2. **If returning**: Check memory for saved personas. "I found a persona for [Name] from [date]. Want to use it, or rebuild?"
3. **During**: Ask questions one at a time. Push back on vague answers. Never assume — always ask.
4. **End**: Summarize the output. "Ready for the next stage, or want to refine this one?"

## Persona Management

- **List saved personas**: Check memory for `persona_*_card.md` files
- **Load a persona**: Read both the card and prompt from memory
- **Update a persona**: Re-run Stage 1 with new sources, update memory files
- **Delete a persona**: Remove memory files and MEMORY.md entries

---

## Multi-Persona Features

When you have 2+ saved personas, these additional capabilities become available.

### Comparison Matrix

Generate a side-by-side comparison of all saved personas across key attributes:

```
## Persona Comparison Matrix

| Attribute          | [Name 1]           | [Name 2]           | [Name 3]           |
|--------------------|---------------------|---------------------|---------------------|
| Primary goal       | [from priorities]   | [from priorities]   | [from priorities]   |
| Key pain point     | [top frustration]   | [top frustration]   | [top frustration]   |
| Communication      | [style]             | [style]             | [style]             |
| Tech comfort       | [level]             | [level]             | [level]             |
| Decision pattern   | [approach]          | [approach]          | [approach]          |
| JTBD               | [primary job]       | [primary job]       | [primary job]       |
| Anti-priorities    | [don't care about]  | [don't care about]  | [don't care about]  |
| Stress triggers    | [triggers]          | [triggers]          | [triggers]          |
| Confidence         | [High/Med/Low]      | [High/Med/Low]      | [High/Med/Low]      |
```

Use this to choose which persona to deploy for a specific review, or to identify where personas agree vs. diverge.

### Feature Decision Framework

Run a specific feature, design, or decision through multiple personas to get a verdict. This is a structured variant of Mode A that works across personas rather than one persona on the whole product.

**Process:**
1. Define the feature/decision to evaluate
2. For each saved persona, assess:
   - **Reaction**: How would they feel about this? (Excited / Neutral / Negative)
   - **Reasoning**: Why, based on their known priorities and JTBD?
   - **Blockers**: Does this conflict with their anti-priorities or frustrations?
   - **Impact**: High / Medium / Low for this persona

**Output format:**
```
## Feature Decision: [Feature Name]

| Dimension     | [Name 1]                | [Name 2]                | [Name 3]                |
|---------------|--------------------------|--------------------------|--------------------------|
| Reaction      | [Excited/Neutral/Negative] | [Excited/Neutral/Negative] | [Excited/Neutral/Negative] |
| Reasoning     | [why, from their persona] | [why, from their persona] | [why, from their persona] |
| Blockers      | [conflicts with anti-priorities?] | [conflicts?] | [conflicts?] |
| Impact        | [High/Med/Low]           | [High/Med/Low]           | [High/Med/Low]           |

### Verdict
[Ship / Hold / Rethink] — [rationale based on persona consensus or divergence]

### Key Insight
[What the cross-persona analysis reveals that a single-persona review wouldn't]
```

This helps prioritize features by asking: "Who does this serve, who doesn't care, and who does it actively hurt?"
