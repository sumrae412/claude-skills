# UX Persona Schema — Structured JSON Add-On

Optional structured schema for personas used in UX reviews, usability walkthroughs, or automated user-testing harnesses. Complements the narrative Persona Card with machine-parseable fidelity knobs.

Adapted from [ncklrs/claude-chrome-user-testing](https://github.com/ncklrs/claude-chrome-user-testing) (MIT). Use this schema when:

- The persona will drive a Playwright/website-tester walkthrough
- You need consistent numeric behavior (timing, patience thresholds)
- You want first-person expressions pre-baked for realistic narration
- The review mode is UX/usability rather than strategic/executive

Skip this layer when the persona is for pitch rehearsal or executive brainstorming — the narrative card is enough.

---

## Schema

```json
{
  "id": "kebab-case-unique-id",
  "name": "Display Name",
  "category": "custom",
  "techComfort": 1-10,
  "patience": 1-10,

  "genderVariants": {
    "male":    { "name": "...", "pronouns": "he/him",     "age": N, "background": "2-3 sentences", "additionalTraits": ["..."] },
    "female":  { "name": "...", "pronouns": "she/her",    "age": N, "background": "2-3 sentences", "additionalTraits": ["..."] },
    "neutral": { "name": "...", "pronouns": "they/them",  "age": N, "background": "2-3 sentences", "additionalTraits": ["..."] }
  },

  "traits": {
    "readingSpeed":    "slow | medium | fast",
    "clickConfidence": "hesitant | normal | decisive",
    "errorRecovery":   "gives-up | persistent | adaptive | escalates",
    "scrollBehavior":  "methodical | searching | impatient",
    "formFilling":     "careful | rushed | thorough"
  },

  "preferences": {
    "prefersVisual":    true|false,
    "expectsMobile":    true|false,
    "trustsAutofill":   true|false,
    "readsInstructions":true|false
  },

  "timing": {
    "baseReadingWPM":     100-400,
    "clickDelay":         200-2500,
    "hoverBeforeClick":   100-1000,
    "confusionPause":     3000-25000,
    "successPause":       300-1000,
    "pageLoadTolerance":  2000-10000,
    "formFieldPause":     400-1200
  },

  "narrationStyle": {
    "vocabulary":           "formal | casual | technical | simple",
    "frustrationThreshold": 1-10,
    "verbosity":            "terse | normal | chatty",
    "expressions":          ["10-15 first-person phrases"]
  },

  "frustrationTriggers": ["8-15 items"],
  "positiveReactions":   ["8-15 items"],
  "typicalBehaviors":    ["8-12 items"],

  "mentalModels": {
    "formsAre":     "...",
    "buttonsAre":   "...",
    "websitesAre":  "...",
    "errorsAre":    "...",
    "passwordsAre": "...",
    "accountsAre":  "..."
  }
}
```

---

## UX-Specific Trait Correlations

Use alongside the decision/communication correlations in `research-guide.md`. These focus on *interaction fidelity* rather than strategic style.

### Tech Comfort → Interaction Profile

| techComfort | readingSpeed | clickConfidence | errorRecovery          | baseReadingWPM | clickDelay  |
|-------------|--------------|-----------------|------------------------|----------------|-------------|
| 1-3 (Low)   | slow         | hesitant        | gives-up / escalates   | 100-150        | 1500-2500ms |
| 4-6 (Medium)| medium       | normal          | persistent             | 150-250        | 600-1500ms  |
| 7-10 (High) | fast         | decisive        | adaptive               | 250-400        | 200-600ms   |

### Patience → Tolerance Profile

| patience    | confusionPause | pageLoadTolerance | frustrationThreshold |
|-------------|----------------|-------------------|----------------------|
| 1-3 (Low)   | 3000-5000ms    | 2000-3000ms       | 3-4                  |
| 4-6 (Medium)| 8000-12000ms   | 5000-7000ms       | 5-6                  |
| 7-10 (High) | 15000-25000ms  | 8000-10000ms      | 7-9                  |

### Vocabulary → Expression Style

- **Formal**: "I don't quite understand what this is asking." / "This seems unnecessarily complicated."
- **Casual**: "Okay so... where do I click?" / "Ugh, seriously?"
- **Technical**: "The form validation seems off." / "Why isn't this responsive?"
- **Simple**: "I don't know." / "What does this mean?" / "Help?"

---

## Frustration Trigger Categories

Ensure coverage across multiple categories — a persona with only "Technical" frustrations is flat.

1. **Technical**: slow loads, errors, crashes, timeouts
2. **Design**: confusing layout, small text, poor contrast, cluttered screens
3. **Process**: too many steps, repeated info, no progress save, forced signup
4. **Trust**: unclear pricing, hidden fees, spam concerns, dark patterns
5. **Accessibility**: hard to read, no keyboard support, poor mobile, no captions

---

## Mental Models — UX-Specific Keys

The narrative Persona Card uses domain-general mental models (meetings, data, risk). For UX personas, add/replace with these interaction-specific keys:

| Key            | Prompt                                          |
|----------------|-------------------------------------------------|
| `formsAre`     | How does this user perceive forms?              |
| `buttonsAre`   | What do buttons represent to them?              |
| `websitesAre`  | What role do websites play in their life?       |
| `errorsAre`    | Whose fault are errors? (self vs. system)       |
| `passwordsAre` | Security tool, nuisance, or afterthought?       |
| `accountsAre`  | Identity anchor, necessary evil, or convenience?|

---

## Gender Variants

Three variants (male/female/neutral) per persona enable inclusive testing without duplicating the schema. Keep the *traits*, *timing*, and *mental models* identical across variants — only `name`, `pronouns`, `age`, `background`, and `additionalTraits` vary.

Genuinely gender-neutral names: Jordan, Alex, Taylor, Casey, Riley, Morgan, Quinn, Avery.

Name conventions by background:

- **Professional/Corporate**: Michael, Jennifer, David, Sarah
- **Healthcare**: Marcus, Priya, Elena, James
- **Retail/Service**: Frank, Linda, Mike, Teresa
- **Student/Young**: Jayden, Zara, Alex, Madison
- **Senior/Elderly**: Harold, Dorothy, Richard, Barbara
- **Technical**: Raj, Sarah, Wei, Brandon

---

## Validation Checklist (pre-save gate)

Before saving a UX persona JSON, confirm:

- [ ] `id` is kebab-case and unique
- [ ] `techComfort` and `patience` are 1-10
- [ ] All three gender variants complete
- [ ] Timing values within ranges above
- [ ] ≥8 items each in `frustrationTriggers`, `positiveReactions`, `typicalBehaviors`
- [ ] ≥10 items in `narrationStyle.expressions`
- [ ] All 6 `mentalModels` keys present
- [ ] Trait correlations consistent with `techComfort`/`patience` levels (flag genuine contradictions as notable, not errors)
- [ ] Frustration triggers span ≥3 categories

---

## Seed Archetypes

Starting templates (adapt, don't use verbatim):

- **boomer-tech-averse** — patience 7, techComfort 2, formal, gives-up on errors
- **power-user** — patience 4, techComfort 9, technical, adaptive recovery
- **distracted-parent** — patience 3, techComfort 6, casual, rushed formFilling
- **low-vision-user** — reading slow, expects large hit targets, accessibility triggers heavy
- **keyboard-only-user** — techComfort 8, triggers on tab-trap/no-focus-ring
- **non-native-english** — medium reading, simple vocabulary, triggers on idioms
- **screen-reader-user** — techComfort 9 (assistive tech), triggers on missing alt/ARIA
- **busy-executive** — patience 2, techComfort 7, terse, triggers on verbose UI
- **cognitive-adhd** — patience 3, triggers on cluttered screens, positive on progress indicators
- **genz-digital-native** — techComfort 9, impatient scroll, expects mobile-first

Full reference library at the upstream repo: https://github.com/ncklrs/claude-chrome-user-testing/tree/main/skills/user-testing/personas

---

## Example Output

See "Rushed Hospital Nurse" in the upstream repo's `skills/persona-generator/SKILL.md` for a complete filled-in example.
