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

## Empathy Map

Use this grid to organize raw source material before synthesizing the Persona Card. For each source, slot observations into the right quadrant:

```
+-------------------------+-------------------------------+
|         SAYS            |            THINKS             |
| Direct quotes from      | Worries and concerns          |
| talks, articles,        | Aspirations inferred from     |
| interviews              | their content and choices      |
+-------------------------+-------------------------------+
|         DOES            |            FEELS              |
| Observable actions,     | Emotional patterns —          |
| workarounds, tools      | frustrations, delights,       |
| they use publicly       | anxieties expressed publicly  |
+-------------------------+-------------------------------+
```

This is a working tool, not a deliverable. Use it to spot patterns across sources before writing the card.

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

### Jobs-to-Be-Done
Primary: When [situation], I want to [motivation], so I can [expected outcome].
- Functional: [practical task to accomplish]
- Emotional: [how they want to feel]
- Social: [how they want to be perceived]

### Empathy Map
- **Says**: [direct quotes from public sources — interviews, talks, articles]
- **Thinks**: [worries, aspirations, concerns inferred from content]
- **Does**: [observable behaviors, workarounds, tools they use]
- **Feels**: [emotional patterns — frustrations, delights, anxieties]

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
