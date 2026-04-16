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

### Journey Map Option

For deeper product reviews, optionally map the user's end-to-end experience across stages. This is more structured than the feature-by-feature product map above.

```
## Journey Map — [Persona Name] using [Product]

### Stages: Awareness → Onboarding → Core Use → Advanced Use → Retention

For each stage:
- **Touchpoints:** [Where they interact with the product]
- **Actions:** [What they do]
- **Emotions:** [Satisfied / Neutral / Frustrated]
- **Pain Points:** [Friction at this stage]
- **Opportunities:** [How we could improve this stage]
- **JTBD Alignment:** [Does this stage help them do their job?]
```

Use the journey map when reviewing a product end-to-end. Use the product map when reviewing specific feature areas. The persona reacts at each journey stage, not just feature-by-feature.

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

### Mode-Specific Persona Weighting

Each mode should emphasize different dimensions of the persona card. Don't load everything equally — lean on what matters most for the task:

| Mode | Primary Dimensions | Secondary Dimensions |
|------|-------------------|---------------------|
| A. Product Review | Domain expertise, known frustrations, tech comfort, JTBD | Communication style, priorities |
| B. Brainstorming | Decision patterns, values, priorities | Communication style, domain expertise |
| C. Rehearsal | Communication style, personality frameworks, known priorities | Decision patterns, frustrations |
| D. Dynamics | Personality frameworks, stress behavior, growth edges | Communication style, values |

When adopting the persona, front-load the primary dimensions in your responses. Reference secondary dimensions when they're relevant but don't force them.

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

## Stage 3.5: Devil's Advocate Review (Quality Gate)

Before writing the Stage 4 report, run a critical self-review to catch sycophancy, blind spots, and unwarranted speculation. This sharpens the findings.

**Devil's advocate prompt:**
```
Step back from the [Name] persona. As Claude, critically review the
session you just conducted:

1. Where were you being too generous or agreeable? Synthetic personas
   tend toward sycophancy — identify moments where the real [Name]
   would have been harsher or more skeptical.

2. What did you miss? Given [Name]'s known priorities and frustrations,
   what aspects of the product should you have challenged but didn't?

3. Where were you speculating without flagging it? Identify any reactions
   that weren't grounded in the source material.

4. What would the REAL [Name] push back on that you let slide?

5. Rate your overall persona fidelity: How well did this session reflect
   the actual person vs. a generic reviewer? What was authentic, what
   was filler?

Revise your key findings based on this review before writing the report.
```

Run this BEFORE Stage 4. Incorporate the corrections into the findings report.

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

### Priority Issues (Opportunity Scored)
Ranked using Opportunity Score = Importance + (Importance - Satisfaction).
Scores > 10 indicate high-priority gaps.

| Issue | Importance (1-10) | Satisfaction (1-10) | Opp. Score | Action |
|-------|-------------------|---------------------|------------|--------|
| [gap] | [how much persona cares] | [how well product addresses it] | [calculated] | [fix/add/improve] |

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
