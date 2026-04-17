---
name: typography
description: Typography rules — quote marks, dashes, spacing, hierarchy, HTML entities. Auto-apply when generating HTML/CSS/React/Jinja with visible text; audit on "fix the typography", "typography audit", "make this look professional".
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# Typography Skill

Rules distilled from Matthew Butterick's *Practical Typography*. These are permanent rules
from centuries of typographic practice — not trends or opinions.

**ENFORCEMENT (default):** When generating UI with visible text, apply every rule automatically.
Use correct HTML entities and proper CSS. Do not ask permission. Do not explain. Just produce
correct typography.

**AUDIT:** When reviewing existing code, identify violations and provide before/after fixes.

**Reference files** (read as needed):
- `references/css-templates.md` — CSS baseline template, responsive patterns, OpenType features
- `references/html-entities.md` — Entity table with all characters and codes

---

## Characters

### Quotes and Apostrophes — Always Curly

Straight quotes are typewriter artifacts. Use `&ldquo;` `&rdquo;` for double, `&lsquo;` `&rsquo;` for single. Apostrophes always use closing single quote `&rsquo;`.

The `<q>` tag auto-applies curly quotes when `<html lang="en">` is set.

### JSX/React Warning

**Unicode escapes (`\u2019`) do NOT work in JSX text content** — they render literally.

| Method | Works? |
|--------|--------|
| Actual UTF-8 char pasted in source | Yes (preferred) |
| `{'\\u2019'}` in JSX expression | Yes |
| `&rsquo;` HTML entity | HTML only, not JSX |
| `\u2019` bare in JSX text | **NO — renders literally** |

### Dashes — Three Distinct Characters

| Char | Entity | Use |
|------|--------|-----|
| - | `-` | Compound words (cost-effective) |
| – | `&ndash;` | Ranges (1–10), connections (Sarbanes–Oxley) |
| — | `&mdash;` | Sentence breaks—like this |

Never approximate with `--` or `---`.

### Ellipses

Use `&hellip;` (…), not three periods. Use `&nbsp;` on the text-adjacent side.

### Math and Measurement

Use `&times;` for multiplication, `&minus;` for subtraction. Dimensions: `8.5&Prime; &times; 14&Prime;`.

**Foot and inch marks** — the ONE exception to curly quotes. Must be STRAIGHT: `&#39;` for foot, `&quot;` for inch.

### Trademark and Copyright

Use `&copy;` `&trade;` `&reg;`, never `(c)` `(TM)` `(R)`. "Copyright ©" is redundant — word OR symbol, not both.

---

## Layout

### Line Length

45–90 characters per line. Enforce with `max-width: min(65ch, 90vw)` on text containers.

### Line Spacing

Body text: 120–145% of font size (`line-height: 1.3–1.45`). Headings: tighter (`1.1–1.2`).

### Paragraph Separation

Choose ONE: space-between (`margin-bottom: 0.75em`) OR first-line indent (`text-indent: 1.5em`). Never both.

### Headings

Bold, not italic. Smallest size increment needed to establish hierarchy. More space above than below. Never hyphenate headings.

### All Caps

Always letterspaced: `letter-spacing: 0.05–0.12em`. Without letterspacing, caps look cramped.

---

## Hierarchy Rules

1. **One primary action per screen** — make it unmissable
2. **Typography scale:** Use a mathematical ratio (1.25× between sizes)
3. **Weight hierarchy:** 400 body, 600 subheads, 700 heads — max 3 weights
4. **Font pairing:** Max 2–3 typefaces. Distinctive display + legible body.

---

## Quick Substitution Checklist

When generating any HTML/JSX with text, automatically fix:

- `"straight"` → `&ldquo;curly&rdquo;`
- `it's` → `it&rsquo;s`
- `--` → `&ndash;` or `&mdash;`
- `...` → `&hellip;`
- `(c)` → `&copy;`
- `12 x 34` → `12 &times; 34`
- `Pages 1-10` → `Pages 1&ndash;10`

---

## Guardrails

- These rules are permanent typographic standards, not stylistic opinions — apply them universally
- When auditing, flag violations but do not change meaning or content
- Enforcement applies only to visible text — do not alter code identifiers, variable names, or string literals that are not user-facing

## Next Steps

- Use `/design-audit` for systematic visual review of existing interfaces
- If your project has a design system, check its typography tokens for consistency with these rules
