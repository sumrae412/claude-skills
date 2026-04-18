# PersonaTester 3D Testing-Behavior Schema

Adapted from iGUITest (Li et al., "PersonaTester: Behavioral Personas for GUI Testing").

## Why layered on top of personas

A persona tells you *who* is using the app. A testing style tells you *how they explore*. Two users with identical demographics behave very differently if one is a meticulous sequential tester and the other a random clicker.

The authors report 117–126% more unique bugs from a 3D-schema pool than from one-persona-one-style baselines.

## The 3 dimensions (orthogonal)

### Dimension 1 — Mindset (2 values)

- **`sequential`** — follows the app's happy path. Reads labels, takes buttons in order, expects the app to guide them.
- **`divergent`** — explores off-path. Opens unrelated menus, clicks secondary features, backtracks to compare options.

### Dimension 2 — Strategy (3 values)

- **`click`** — interacts via buttons, links, menu items. Avoids text input unless required.
- **`core_function`** — stays focused on features directly tied to the stated goal.
- **`input_oriented`** — exercises forms, search, text areas heavily.

### Dimension 3 — Habit (2 values)

- **`valid_short`** — realistic, minimal-length valid inputs.
- **`invalid`** — edge inputs: empty strings, long strings, special chars, wrong types, boundary values, XSS-ish payloads.

## Full matrix

2 × 3 × 2 = 12 style combinations per persona.

## Stratified sampling (default `testing_styles_per_persona = 2`)

For each persona, pick 2 styles such that:

- The 2 styles differ on **≥2 of 3** dimensions.
- Globally, each value on each dimension is hit by ~equal numbers of personas.

Use a seeded PRNG; record the seed in `$testing_matrix.matrix_metadata.seed` for reproducibility.

### Example assignment (5 personas × 2 styles)

| Persona | Style A | Style B |
|---|---|---|
| p01 | (sequential, click, valid_short) | (divergent, input_oriented, invalid) |
| p02 | (sequential, core_function, valid_short) | (divergent, click, invalid) |
| p03 | (divergent, input_oriented, valid_short) | (sequential, click, invalid) |
| p04 | (sequential, input_oriented, valid_short) | (divergent, core_function, invalid) |
| p05 | (divergent, click, valid_short) | (sequential, core_function, invalid) |

Global coverage: sequential×5, divergent×5; click×4, core_function×3, input_oriented×3; valid_short×5, invalid×5.

## Prompting

Append to the persona role-play prompt (GUI cells only):

```
Your testing style for this session:
- Mindset: <mindset description>
- Strategy: <strategy description>
- Habit: <habit description>

Act this style without mentioning it. Don't explain what you're "trying to test" —
just use the app the way someone with this style and this persona naturally would.
```

## Not applicable to

- **API** apps — no GUI surface to explore differently.
- **CLI** apps — command surface is linear; the "strategy" axis doesn't map.
- **Chatbot** apps — turn-based conversation; the persona's `communication_style` already covers variation.

For these kinds, Phase 3 sets `testing_style = null`. Persona variation alone drives coverage.
