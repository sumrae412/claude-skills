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
- [ ] **Known frustrations** — Pain points they've expressed publicly. **Count sources**: note how many sources mention each frustration (e.g., "slow tools — 4/6 sources")
- [ ] **Anti-priorities** — What they explicitly do NOT care about or dismiss
- [ ] **Values** — Non-negotiables, principles they return to repeatedly
- [ ] **Blind spots** — Topics they rarely address or seem less informed about
- [ ] **Stress triggers** — Situations that create tension or frustration for them
- [ ] **Stress reactions** — How they behave under pressure (more formal? withdrawn? escalating? blunt?)
- [ ] **Speech patterns** — Characteristic phrases, framing patterns, recurring language (e.g., "at the end of the day...", "the data shows...")
- [ ] **Mental models** — How they conceptualize key abstractions (meetings, data, risk, tools, feedback). Derive from how they talk about these things, not from generic role assumptions.
- [ ] **Positive reactions** — What excites, impresses, or delights them. Count sources like frustrations. A persona without positives is a caricature.

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

### Known Frustrations (Evidence-Counted)
- [Frustration] (mentioned in X/Y sources)
- [Frustration] (mentioned in X/Y sources)
- [Frustration with 1 source = LOW CONFIDENCE]

### Anti-Priorities ("Don't Care About")
[What this person explicitly does NOT value, dismisses, or deprioritizes.
Features in this bucket should not appear as findings in reviews.]

### Stress Triggers & Reactions
- **Triggers**: [Situations that create tension — e.g., being asked to repeat themselves, lack of data, scope creep]
- **Reactions**: [How they behave under pressure — e.g., becomes more formal, withdraws, escalates, gets blunt]

### Speech Patterns
- Characteristic phrases: [e.g., "at the end of the day...", "show me the data"]
- Framing patterns: [how they structure arguments — leads with data? stories? analogies?]
- Example quotes from sources: ["direct quote 1", "direct quote 2"]

### Decision Pattern
[How they evaluate — ROI-focused? User-first? Risk-averse? Data-driven? Gut-feel?]

### Mental Models
How this person conceptualizes key abstractions in their domain. These shape what they expect from products and conversations — mismatches cause confusion.

- **Meetings are**: [e.g., "decision-making forums, not status updates"]
- **Data is**: [e.g., "the starting point, not the answer"]
- **Risk is**: [e.g., "something to manage, not avoid"]
- **New tools are**: [e.g., "guilty until proven innocent — must earn their place"]
- **Feedback is**: [e.g., "a gift — direct and frequent is best"]
- **[Domain-specific]**: [add 2-3 entries relevant to their field — e.g., "ROI is: the first question, always"]

*Derive from public statements. If someone says "I don't do meetings without an agenda," their mental model of meetings is "structured decision points." If they say "show me the dashboard," data is a visual artifact, not a narrative.*

### Positive Reactions
What excites, impresses, or delights this person — the counterpart to frustrations. These are equally important for realistic persona fidelity; a persona that only complains is a caricature.

- [e.g., "Clean, simple interfaces that respect their time"]
- [e.g., "When data is presented visually with clear takeaways"]
- [e.g., "Products that handle edge cases gracefully"]
- [e.g., "Direct communication without corporate jargon"]
- [5-10 specific positive reactions, evidence-counted where possible]

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
**Overall confidence**: [High / Medium / Low]

| Source Count | Confidence | Implication |
|---|---|---|
| 1-2 sources | Low | Exploratory — flag heavily, validate everything |
| 3-5 sources | Medium | Directional — useful but verify key conclusions |
| 6+ sources | High | Production — confident enough to act on |

- **Total sources used**: [N]
- **Strong areas**: [aspects backed by 3+ sources]
- **Thin areas**: [aspects based on 1-2 sources — flag as LOW CONFIDENCE in sessions]
- **Unknown**: [aspects we couldn't find data on]
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
3. What excites them and what frustrates them (both sides — a persona that only complains is a caricature)
4. How they make decisions (what evidence they need, what they trust)
5. Their domain expertise and blind spots
6. Characteristic phrases or framing patterns from their public communications
7. How they'd react to being presented with something new (skeptical? enthusiastic? methodical?)
8. Their mental models — how they conceptualize key abstractions like meetings, data, risk, new tools, and feedback. These shape expectations and where mismatches cause confusion.
9. What delights them — specific positive reactions grounded in source material, not generic enthusiasm

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

---

## Trait Correlation Table

Use this table to ensure internal consistency when building a persona. Traits should correlate — a data-driven decision maker who communicates via gut-feel stories is a contradiction (unless you have source evidence for it).

### Decision Style → Expected Correlations

| Decision Style | Communication | Risk Tolerance | Frustration Profile | Positive Profile |
|----------------|---------------|----------------|---------------------|------------------|
| **Data-driven** | Asks for evidence, metrics-first | Moderate — wants proof before acting | Vague claims, hand-waving, "trust me" | Dashboards, clear benchmarks, A/B results |
| **Intuition / gut-feel** | Story-driven, anecdotal | Higher — comfortable with ambiguity | Over-analysis, death by committee | Bold moves, quick decisions, momentum |
| **Consensus-driven** | Diplomatic, inclusive | Low — needs buy-in before moving | Being steamrolled, unilateral decisions | Alignment, everyone heard, shared ownership |
| **ROI-focused** | Direct, bottom-line oriented | Calculated — risk vs. reward | Wasted resources, unclear value prop | Clear payback periods, efficiency gains |
| **User-first** | Empathetic, design-oriented | Moderate — will take risks for UX | Ignoring user feedback, tech-driven decisions | User delight, reduced friction, testimonials |

### Tech Comfort → Expected Correlations

| Tech Comfort | Mental Model of Tools | Error Tolerance | Feedback Style |
|--------------|----------------------|-----------------|----------------|
| **Power user** | "Tools should be configurable" | High — will debug, workaround | Specific, technical, solution-oriented |
| **Competent** | "Tools should just work" | Moderate — expects clear error messages | Pragmatic, feature-request style |
| **Casual** | "Tools should be invisible" | Low — confused by errors | General, outcome-focused ("it doesn't work") |
| **Reluctant** | "Tools are a necessary evil" | Very low — errors confirm distrust | Emotional, avoidance-oriented |

### Communication Style → Expected Correlations

| Communication | Decision Speed | Meeting Style | Conflict Approach |
|---------------|---------------|---------------|-------------------|
| **Direct / blunt** | Fast | Short, agenda-driven | Head-on, explicit |
| **Diplomatic** | Moderate | Inclusive, longer | Indirect, seeks compromise |
| **Data-first** | Deliberate | Structured, presentation-heavy | Evidence-based rebuttal |
| **Story-driven** | Variable | Conversational, tangential | Reframes via narrative |
| **Terse** | Fast | Minimal, async-preferred | Brief pushback, moves on |

**When to override correlations:** If source material shows a genuine contradiction (e.g., a data-driven executive who makes gut-feel hiring decisions), keep it — real people are inconsistent. Flag it in the persona card as a notable trait, not a bug.
