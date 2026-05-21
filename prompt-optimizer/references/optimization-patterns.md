# Optimization Patterns

Proven before/after patterns and technique combination guides.

---

## Pattern 1: Ambiguous Request → Structured Breakdown

**Before:**
> "Write something about our product launch."

**After:**
> "You are a B2B SaaS marketing copywriter. Write a 300-word internal announcement for our Q3 product launch, aimed at the sales team. Tone: energetic but professional. Include: what's launching, key customer benefits (top 3), and one clear call to action (book a demo). Do not use jargon or technical specs."

**Techniques applied:** Role-Play, Audience Persona, Length Specification, Format Specification, Negative Constraints

---

## Pattern 2: Generic Task → Technique Enhancement

**Before:**
> "Help me debug this code."

**After:**
> "You are a senior Python engineer. Review the following code for bugs.
> Step 1: Identify any syntax errors.
> Step 2: Identify any logical errors.
> Step 3: Suggest a fix for each issue, with a brief explanation of why it's a bug.
> Format your response as a numbered list, one issue per item.
> [code here]"

**Techniques applied:** Expert Persona, Step-by-Step Decomposition, Format Specification

---

## Pattern 3: Missing Context → Scenario Framing

**Before:**
> "Summarize this document."

**After:**
> "Summarize the following document for a non-technical executive who has 2 minutes to read it.
> Focus on: business impact, key decisions required, and recommended next steps.
> Length: 150 words maximum.
> Do not include technical details or implementation specifics.
> [document here]"

**Techniques applied:** Audience Persona, Contextual Priming, Length Specification, Negative Constraints, Section Headers

---

## Pattern 4: Weak Instructions → Actionable Steps

**Before:**
> "Make this email better."

**After:**
> "Revise the following email draft using these criteria:
> 1. Lead with the main ask in the first sentence
> 2. Remove filler phrases ('I hope this finds you well', 'please don't hesitate')
> 3. Keep it under 100 words
> 4. End with a single, specific call to action
> Preserve the original tone and all factual content.
> [email here]"

**Techniques applied:** Checklist Prompting, Negative Constraints, Length Specification, Grounding Constraints

---

## Pattern 5: Open-Ended Creative → Constrained Creative

**Before:**
> "Write a tagline for our product."

**After:**
> "Generate 10 tagline options for [product name], a [one-sentence product description].
> Target audience: [audience].
> Tone: [tone].
> Constraints: under 8 words each, no clichés, no use of the words 'smart,' 'simple,' or 'powerful.'
> After the list, mark your top 3 with a brief reason for each."

**Techniques applied:** Brainstorming Mode, Audience Persona, Negative Constraints, Priority Ordering

---

## Pattern 6: Factual Task → Grounded + Verified

**Before:**
> "What are the benefits of X?"

**After:**
> "Based only on the following source material, list the benefits of X.
> For each benefit: state the benefit, quote or paraphrase the supporting evidence, and rate your confidence (High/Medium/Low).
> If a benefit isn't supported by the source material, do not include it.
> [source material here]"

**Techniques applied:** Retrieval Augmentation, Confidence Signaling, Grounding Constraints, Negative Constraints

---

## Pattern 7: Analysis Task → Multi-Perspective

**Before:**
> "Analyze this business decision."

**After:**
> "Analyze the following decision from three perspectives:
> 1. Financial: ROI, costs, risks
> 2. Operational: implementation complexity, resource requirements
> 3. Strategic: alignment with long-term goals, competitive impact
> For each perspective, give a 2-3 sentence assessment and a verdict (Favorable / Neutral / Unfavorable).
> End with an overall recommendation and the single biggest risk to mitigate.
> [decision here]"

**Techniques applied:** Framework Application, Perspective Shifting, Section Headers, Format Specification, Priority Instructions

---

## Technique Combination Guide

| Goal | Primary Technique | Pair With |
|------|------------------|-----------|
| Consistent style | Few-Shot Learning | Negative Constraints |
| Better reasoning | Chain of Thought | Assumption Listing |
| Reduce hallucination | Grounding Constraints | Confidence Signaling |
| Complex analysis | Step-by-Step Decomposition | Tree of Thoughts |
| Creative output | Constraint-Based Creativity | Brainstorming Mode |
| Exec communication | Audience Persona | Layered Output |
| Code generation | Expert Persona | Edge Case Identification |
| Decision-making | Framework Application | Devil's Advocate |

---

## Signs a Prompt Is Already Well-Optimized

- Anyone reading it would interpret it the same way
- The desired output format is explicit
- The audience is named
- At least one constraint (positive or negative) is present
- For complex tasks: reasoning steps or examples are included
- Success criteria are stated or inferable
