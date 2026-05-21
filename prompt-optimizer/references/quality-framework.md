# Prompt Quality Framework

## Evaluation Dimensions

### 1. Clarity
**What it measures:** Is the prompt unambiguous? Could it be misread?

| Rating    | Criteria |
|-----------|----------|
| Poor      | Multiple valid interpretations; task is unclear |
| Fair      | Intent is guessable but requires inference |
| Good      | Clear main task, minor ambiguities |
| Excellent | Zero ambiguity; any reader would interpret it identically |

**Anti-patterns:** Vague verbs ("handle," "deal with," "do something about"), undefined pronouns, contradictory instructions.

---

### 2. Specificity
**What it measures:** Are requirements, constraints, and scope clearly defined?

| Rating    | Criteria |
|-----------|----------|
| Poor      | No constraints or requirements stated |
| Fair      | Some requirements but key details missing |
| Good      | Most constraints defined; minor gaps |
| Excellent | All constraints explicit; edge cases addressed |

**Anti-patterns:** "Be creative," "make it good," "about X pages," no mention of audience or output format.

---

### 3. Structure
**What it measures:** Is the prompt logically organized? Does the order of information make sense?

| Rating    | Criteria |
|-----------|----------|
| Poor      | Random order; context buried or missing |
| Fair      | Roughly ordered but jumps around |
| Good      | Clear sections; logical flow |
| Excellent | Optimal structure for the task type; sections clearly delineated |

**Anti-patterns:** Instructions scattered throughout, context given after the task, important caveats buried at the end.

---

### 4. Completeness
**What it measures:** Does the prompt include all necessary context, background, and instructions?

| Rating    | Criteria |
|-----------|----------|
| Poor      | Critical information missing; model must guess |
| Fair      | Main task described but background/constraints absent |
| Good      | Most needed information present |
| Excellent | All context, constraints, examples, and success criteria included |

**Anti-patterns:** No audience specification, no output format, no examples for complex tasks, missing domain context.

---

### 5. Tone
**What it measures:** Is the voice and register appropriate for the task and intended output?

| Rating    | Criteria |
|-----------|----------|
| Poor      | Tone actively conflicts with the task goal |
| Fair      | Neutral but mismatched to context |
| Good      | Appropriate tone specified |
| Excellent | Tone specified with examples or persona guidance |

**Anti-patterns:** Casual tone for professional outputs, overly formal for creative tasks, no tone guidance for tone-sensitive content.

---

### 6. Constraints
**What it measures:** Are boundaries, limitations, and "do not" rules clear?

| Rating    | Criteria |
|-----------|----------|
| Poor      | No constraints; anything goes |
| Fair      | Implied constraints only |
| Good      | Key constraints stated explicitly |
| Excellent | Both positive ("do this") and negative ("don't do this") constraints present |

**Anti-patterns:** No word/length limit, no format restrictions, no out-of-scope guidance.

---

## Scoring Summary Template

```
Dimension      | Rating    | Key Issue
---------------|-----------|----------
Clarity        | Good      | Minor ambiguity in "final output" 
Specificity    | Fair      | No audience or length specified
Structure      | Excellent | Well-organized
Completeness   | Poor      | No examples; missing domain context
Tone           | Good      | Appropriately specified
Constraints    | Fair      | No format constraints

Overall: Fair — address Completeness and Specificity first
```

## Common Anti-Patterns to Avoid

1. **The vague imperative** — "Write a good essay about climate change." What kind? For whom? How long?
2. **The assumed expert** — Asking for technical output without specifying the reader's expertise level.
3. **The buried constraint** — Putting the most important limitation at the end as an afterthought.
4. **The missing example** — For complex or stylistic tasks, not showing what "good" looks like.
5. **The open scope** — No guidance on what's out of scope, leading to over- or under-delivery.
6. **The contradictory instruction** — "Be concise but thorough" without defining the balance point.
