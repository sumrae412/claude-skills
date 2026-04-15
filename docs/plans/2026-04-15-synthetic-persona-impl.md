# Synthetic Persona Skill — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a `synthetic-persona` skill that builds "synthetic people" from public data for product reviews, brainstorming, rehearsals, and interpersonal dynamics analysis.

**Architecture:** Progressive disclosure skill (router SKILL.md + lazy-loaded reference files). Four stages: Research & Build Persona → Product/Context Scan → Interactive Session (4 modes) → Findings Report. Follows the personal-coach and startup-planner patterns.

**Tech Stack:** Markdown skill files, web search for research, memory system for persona persistence.

---

## Task 1: Create the Research Guide Reference File

**Files:**
- Create: `synthetic-persona/references/research-guide.md`

**Step 1: Create the directory structure**

```bash
mkdir -p /Users/summerrae/claude_code/claude-skills/synthetic-persona/references
```

**Step 2: Write research-guide.md**

This file contains:
- Source categories (articles, podcasts, operating manuals, social media, framework data, industry context)
- Data extraction checklist (for each source: priorities, communication style, decision patterns, domain expertise, frustrations, values)
- Persona Card template (structured markdown for human reference)
- Meta-prompt template (the prompt Claude uses to generate its own persona instructions from gathered data)
- Memory save format (how to persist the persona for reuse)

```markdown
# Research Guide — Building a Synthetic Persona

How to gather public data about a real person and synthesize it into a persona Claude can role-play.

## Important: Public Data Only

**Never use private or confidential information.** All sources must be publicly available or explicitly shared by the user. This includes:
- Published articles, blog posts, or books
- Public podcast/interview appearances
- Conference talks, keynotes, presentations
- Publicly shared "operating manuals" or "how I work" documents
- Public social media posts
- Personality framework results the user knows about

**Do NOT use:** Private emails, internal documents, confidential meeting notes, private messages, or any information the person hasn't made public.

---

## Source Categories

When researching a person, look for these categories of public information:

### 1. Written Content
- Articles or blog posts they've authored
- Books or book chapters
- Public newsletters
- Published case studies or whitepapers

**Extract:** Priorities, values, how they frame problems, recurring themes, what they advocate for.

### 2. Spoken Content
- Podcast appearances (as guest or host)
- Conference talks, keynotes, panels
- YouTube videos, webinars
- Published interviews

**Extract:** Communication style (formal/casual, data-driven/story-driven), how they explain complex ideas, what excites them, what frustrates them.

### 3. Operating Manuals / "How I Work" Docs
- Publicly shared manager READMEs
- "Working with me" documents
- Published leadership principles
- Team guides they've authored

**Extract:** Decision-making process, communication preferences, what they value in collaborators, meeting style, feedback preferences.

### 4. Social Media & Public Commentary
- LinkedIn posts and articles
- Twitter/X threads (if public)
- Public forum contributions (HN, Reddit, etc.)
- Comment sections on industry publications

**Extract:** Opinions, reactions to industry trends, what they share/amplify, tone in informal settings.

### 5. Personality Framework Data
If the user knows any of these about the person:
- Enneagram type (and wing)
- MBTI type
- DISC profile
- Human Design type/authority
- Management style assessments

**Extract:** Decision-making patterns, stress behavior, communication needs, growth edges.

### 6. Industry & Role Context
- What market/industry do they operate in?
- What's their role and seniority?
- What problems do they deal with daily?
- What are the common frustrations in their position?

**Extract:** Domain expertise depth, what they take for granted, what they'd expect from a product in this space.

---

## Data Extraction Checklist

For each source, extract as much as possible:

- [ ] **Priorities** — What do they care about most? What do they optimize for?
- [ ] **Communication style** — Direct or diplomatic? Data-first or story-first? Formal or casual?
- [ ] **Decision patterns** — ROI-focused? User-first? Risk-averse? Consensus-driven? Data-driven?
- [ ] **Domain expertise** — What do they know deeply? What are they less familiar with?
- [ ] **Tech comfort** — Power user / competent / casual / reluctant?
- [ ] **Known frustrations** — Pain points they've expressed publicly
- [ ] **Values** — Non-negotiables, principles they return to repeatedly
- [ ] **Blind spots** — Topics they rarely address or seem less informed about

---

## Persona Card Template

After gathering data, synthesize into this structure:

```
## Persona — [Name]

### Identity
[Role, title, relationship to user/product]

### Priorities
[What they care about most — ranked]

### Communication Style
[Direct/diplomatic, data-driven/intuitive, formal/casual, verbose/terse]

### Domain Expertise
[What they know deeply, what they're less familiar with]

### Tech Comfort
[Power user / competent / casual / reluctant]

### Known Frustrations
[Pain points they've expressed publicly]

### Decision Pattern
[How they evaluate — ROI-focused? User-first? Risk-averse? Data-driven? Gut-feel?]

### Personality Frameworks
[Enneagram, DISC, MBTI, etc. — if known]

### Sources
[Links to public materials used to build this persona]

### Confidence Assessment
- Strong areas: [where we have rich source data]
- Thin areas: [where we're extrapolating]
- Unknown: [aspects we couldn't find data on]
```

---

## Meta-Prompt Template

After building the Persona Card, use this prompt to generate the Persona Prompt — the actual instructions Claude uses when role-playing:

```
Based on everything I've gathered about [Name], write a detailed persona prompt
that I can use to role-play as this person. Write it in second person ("You are
[Name]..."). Include:

1. How they think about problems (analytical process, what they prioritize)
2. How they communicate (tone, pacing, level of directness)
3. What excites them and what frustrates them
4. How they make decisions (what evidence they need, what they trust)
5. Their domain expertise and blind spots
6. Characteristic phrases or framing patterns from their public communications
7. How they'd react to being presented with something new (skeptical? enthusiastic? methodical?)

Be specific — use examples from the source material. Don't be generic.
End with a note about where the persona model is thin (low-confidence areas).
```

---

## Saving to Memory

After completing Stage 1, save two files to the memory system:

1. **Persona Card** — `persona_[name]_card.md` in memory directory
   - Type: `reference`
   - Description: "Persona card for [Name] — [role], [relationship]. Built from [N] public sources."

2. **Persona Prompt** — `persona_[name]_prompt.md` in memory directory
   - Type: `reference`
   - Description: "Role-play instructions for [Name] persona — use when adopting their perspective."

Update MEMORY.md index with pointers to both files.
```

**Step 3: Commit**

```bash
git add synthetic-persona/references/research-guide.md
git commit -m "feat(synthetic-persona): add research guide reference"
```

---

## Task 2: Create the Review Prompts Reference File

**Files:**
- Create: `synthetic-persona/references/review-prompts.md`

**Step 1: Write review-prompts.md**

This file contains prompt templates for each Stage 3 mode, plus the Stage 2 product scan guide and Stage 4 report template.

```markdown
# Review Prompts — Mode-Specific Templates

Prompt templates and scan guides for Stages 2-4 of the synthetic persona workflow.

---

## Stage 2: Product / Context Scan Guide

### What to Scan

Read the project to build a product map organized by user-facing areas (not code architecture).

**Scan targets:**
1. **UI templates** — HTML, components, user-facing copy, labels, button text
2. **Routes / endpoints** — what actions the product supports
3. **Error messages** — how failures are communicated to users
4. **README & docs** — how the product presents and explains itself
5. **Onboarding flows** — first-time user experience, setup wizards
6. **Notifications** — emails, alerts, messages sent to users
7. **Settings / configuration** — what users can customize

### Product Map Format

Organize findings by user experience area:

```
## Product Map — [Product Name]

### Getting Started
[How a new user encounters the product — onboarding, signup, first run]

### Core Workflow
[The main thing users do — the primary value loop]

### Secondary Features
[Supporting functionality — settings, reports, integrations]

### Communication
[How the product talks to users — notifications, emails, error messages]

### Terminology
[Key terms used in the UI — do they match the domain?]
```

### Two-Pass Enrichment Prompt

After building the product map, refine the persona:

```
Now that you know what [Product] does, refine your perspective as [Name].
Given their priorities ([list]), what aspects of this product would matter
most to them? What would they notice first? What would they ignore?
Update your persona lens to be product-specific.
```

---

## Stage 3: Interactive Session Prompts

### Mode A: Product Review (Synthetic Client)

**Opening prompt:**
```
You are now [Name]. Review [Product] from your perspective.

Walk through each area of the product map. For each area:
1. What works well for you? Why?
2. What confuses you? What terminology doesn't match your mental model?
3. What's missing that you'd expect to exist?
4. How does this compare to alternatives you've seen?

Stay in character. Flag when you're speculating beyond what the source data supports
with [LOW CONFIDENCE]. React naturally — you can be enthusiastic, frustrated,
confused, or impressed as [Name] would be.
```

**Follow-up prompts for specific areas:**
- "Look at [feature]. Walk me through your first reaction."
- "You need to [task]. How would you try to do it? What's intuitive, what's not?"
- "Compare this to how you currently handle [problem]."
- "What would make this a must-have for you vs. a nice-to-have?"

### Mode B: Brainstorming (Sounding Board)

**Opening prompt:**
```
You are now [Name]. I'm going to present an idea/challenge and I want
your perspective — the way you actually think, not generic advice.

When you respond:
- Use your characteristic reasoning style
- Draw on your known priorities and values
- Push back where you would push back
- Ask the questions you'd actually ask
- If you'd be excited, show it. If skeptical, show that too.
```

**Follow-up prompts:**
- "What's your gut reaction?"
- "What would you need to see before you'd support this?"
- "How would you pitch this to YOUR stakeholders?"
- "What's the biggest risk you see?"

### Mode C: Rehearsal (Pitch Practice)

**Opening prompt:**
```
You are now [Name]. I'm going to pitch you something. React as you would
in a real meeting.

- Ask the questions you'd actually ask
- Push back where your instincts say to push back
- If I'm not being clear, say so
- If something excites you, show it
- Don't be artificially nice — react authentically

After we finish the rehearsal, I'll ask you to break character and
debrief: what landed, what didn't, and how I should adjust.
```

**Debrief prompt (after rehearsal ends):**
```
Break character. As Claude (not [Name]), debrief the rehearsal:
1. What arguments landed well with the [Name] persona?
2. Where did the pitch lose them? Why?
3. What objections should be anticipated?
4. What specific adjustments would improve the pitch?
5. Rate confidence: how well does the persona model support these conclusions?
```

### Mode D: Dynamics Analysis

**Opening prompt:**
```
Analyze the dynamic between these two profiles:

**Me:** [user's profile summary or personality framework data]
**[Name]:** [persona card summary]

For the topic of [specific topic/conversation]:
1. Where do we naturally align? (shared values, compatible styles)
2. Where will we have friction? (clashing priorities, style mismatches)
3. How should I adjust my communication for this person specifically?
4. What should I lead with? What should I avoid?
5. Suggest a specific approach for [topic].
```

**Requires:** User's own personality profile (from personal-coach skill or provided directly).

---

## Stage 4: Findings Report Template

After any Stage 3 session, synthesize findings:

```
## Persona Review — [Name] on [Project]
### Date: [date]
### Mode: [Product Review / Brainstorming / Rehearsal / Dynamics]
### Persona confidence: [High/Medium/Low — based on depth of source material]

---

### What Works
[Features, approaches, or ideas the persona approved of, with reasoning
tied to their known priorities]

### What's Confusing
[Terminology, flows, or concepts that don't match this person's mental
model — include specific examples]

### What's Missing
[Features, information, or capabilities the persona would expect to
exist — ranked by importance to this persona]

### Priority Issues
[Ranked list — what to fix/address first, based on persona's known
priorities and decision patterns]

### Key Reactions
[Notable quotes or reactions from the interactive session worth
preserving — these are useful for the real conversation]

### Confidence & Caveats
- **Strong conclusions:** [backed by multiple sources]
- **Moderate conclusions:** [backed by limited data]
- **Speculative:** [areas where Claude extrapolated beyond sources]
- **Validate with real person:** [specific questions to ask]

### Recommended Next Steps
[3-5 concrete actions to take before the real conversation]
```

Save to: `docs/persona-reviews/YYYY-MM-DD-[name]-review.md`
```

**Step 2: Commit**

```bash
git add synthetic-persona/references/review-prompts.md
git commit -m "feat(synthetic-persona): add review prompts reference"
```

---

## Task 3: Create the SKILL.md Router

**Files:**
- Create: `synthetic-persona/SKILL.md`

**Step 1: Write SKILL.md**

This is the main router file. It should:
- Have proper frontmatter with triggers
- Explain the concept briefly
- List "Before Starting" steps (read reference files)
- Define all 4 stages with entry questions and process flow
- Reference the output formats in review-prompts.md
- Include the public-data-only warning
- Include professional help boundaries for dynamics analysis
- Follow the personal-coach pattern (one stage per session, questions one at a time)

```markdown
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
| 1. Research & Build | Gather public data, generate persona | Persona Card + Persona Prompt (saved to memory) |
| 2. Product Scan | Read codebase, build product map | Product Map + enriched persona lens |
| 3. Interactive Session | Review, brainstorm, rehearse, or analyze | Dialogue session |
| 4. Findings Report | Synthesize session into actionable report | Markdown report in docs/persona-reviews/ |

Work through **one stage per session**. Stages 3-4 are repeatable with the same persona.

---

## Stage 1: Research & Build Persona

**Goal**: Collect public data about a real person and generate a persona Claude can role-play.

**Entry question**: "Who would you like to model? Tell me their name, role, and relationship to you or your product."

**Process:**

1. **Gather sources** — Ask what the user already has (articles, talks, docs). Then use web search to find additional public material. See `references/research-guide.md` for source categories.

2. **Extract patterns** — For each source, extract: priorities, communication style, decision patterns, domain expertise, frustrations, values. Use the Data Extraction Checklist in the research guide.

3. **Ask about personality frameworks** — "Do you know their Enneagram type, MBTI, DISC, or other framework results?" Even partial data helps.

4. **Build the Persona Card** — Synthesize into structured format (template in research guide). Present to user for validation: "Does this feel like them? What's off?"

5. **Meta-prompt step** — Feed all gathered material to Claude and generate a Persona Prompt — the actual role-playing instructions written in second person. This produces richer behavior than the structured card alone. See meta-prompt template in research guide.

6. **Save to memory** — Store both the Persona Card and Persona Prompt as memory files for reuse in future sessions.

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

3. **Two-pass enrichment** — Feed the product map summary back into the persona: "Now that you know what this product does, what matters most to [Name]?" Refine the persona lens to be product-specific.

4. **Present the map** — Show the user the product map. Ask: "Is this a fair representation of the product? Anything missing?"

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

See `references/review-prompts.md` for mode-specific prompt templates.

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

1. Review everything from the Stage 3 session
2. Organize into the report template (see `references/review-prompts.md`)
3. Assess confidence for each finding — strong, moderate, or speculative
4. Identify what to validate with the real person
5. Recommend 3-5 concrete next steps

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
```

**Step 2: Commit**

```bash
git add synthetic-persona/SKILL.md
git commit -m "feat(synthetic-persona): add SKILL.md router with 4-stage workflow"
```

---

## Task 4: Register the Skill and Final Verification

**Step 1: Verify file structure**

```bash
find /Users/summerrae/claude_code/claude-skills/synthetic-persona -type f
```

Expected:
```
synthetic-persona/SKILL.md
synthetic-persona/references/research-guide.md
synthetic-persona/references/review-prompts.md
```

**Step 2: Verify SKILL.md frontmatter**

Read `synthetic-persona/SKILL.md` and confirm:
- `name: synthetic-persona`
- `description:` includes trigger phrases
- All 4 stages are documented
- Public data warning is present
- Professional help boundary is present
- References are linked with `references/` paths

**Step 3: Verify reference files**

Read both reference files and confirm:
- `research-guide.md` has: source categories, extraction checklist, persona card template, meta-prompt template, memory save instructions
- `review-prompts.md` has: product scan guide, all 4 mode prompts, two-pass enrichment prompt, debrief prompt, report template

**Step 4: Final commit with all files**

```bash
git status
git log --oneline -5
```

Confirm 3 commits: research-guide, review-prompts, SKILL.md.

---

## Summary

| Task | Files | Purpose |
|------|-------|---------|
| 1 | `references/research-guide.md` | Data collection, persona card template, meta-prompt |
| 2 | `references/review-prompts.md` | Product scan, mode prompts, report template |
| 3 | `SKILL.md` | Router — stage selection, persona management |
| 4 | (verification) | File structure and content validation |

**Total: 3 files to create, 3 commits, ~4 tasks.**
