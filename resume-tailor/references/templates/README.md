# Templates

Canonical visual + structural templates for all resume-tailor outputs. Load this file at the start of Phase 5.

Files in this directory:

- `resume-template.docx` — authoritative DOCX style source (fonts, margins, heading styles, spacing)
- `resume-template.md` — extracted markdown view of the same template
- `cover-letter-template.docx` — authoritative DOCX style source for letters
- `cover-letter-template.md` — extracted markdown view

Both templates are **single-column, ATS-safe**. No tables, no text boxes, no multi-column layouts.

## Resume conventions (extracted)

**Name and headline — required pandoc custom-style divs.** The template defines four distinct Word paragraph styles (`Title`, `Subtitle`, `Heading 1`, `Heading 2`). If the name is written as a plain markdown `# Name` heading, pandoc renders it as `Heading 1` — identical to section headings like `SKILLS`, which collapses the template's visual hierarchy. To invoke the template's `Title` and `Subtitle` styles, wrap the name and headline in `custom-style` divs:

```markdown
::: {custom-style="Title"}
Firstname Lastname
:::

::: {custom-style="Subtitle"}
Short one-line headline — what the user does, best framed for the target role
:::
```

This is required for every resume, not optional.

**Section order:**

1. `::: {custom-style="Title"}` name div
2. `::: {custom-style="Subtitle"}` headline div
3. Contact line (`City · email · phone · linkedin · portfolio`) as body text — single line with `·` separators is fine; multiple lines also work
4. Summary paragraph (optional) — body text **with no `## Summary` heading**. The template has no Summary style.
5. `# SKILLS` — short prose or comma-separated list
6. `# EXPERIENCE` — roles in reverse chronological order
7. `# EDUCATION`
8. `# PUBLICATIONS & PRESENTATIONS` (optional)
9. `# AWARDS` (optional — include only if the user has relevant awards)

**Heading style:** top-level section headings are **ALL CAPS** (`# SKILLS`, `# EXPERIENCE`, `# EDUCATION`, `# PUBLICATIONS & PRESENTATIONS`, `# AWARDS`). Do not title-case them.

**Role heading format:** `## Company Name, Location - Job Title`. **No italics on the title** — the template's Heading 2 style already applies visual emphasis; wrapping the title in `*...*` produces double emphasis and drifts from the template. Location is city + state (or city only, international) — not a full street address. If a role has no location (`## University of Oregon - Adjunct Faculty`), omit the location slot.

**Date line:** `MONTH 20XX - PRESENT` or `MONTH 20XX - MONTH 20XX`. Three-letter month abbreviations are acceptable (`JAN 2024 - PRESENT`) if the user's source resume uses them, but be consistent within the document.

**Bullets:** plain hyphen bullets. Each bullet is one sentence or one clause. Past tense for finished roles, present tense for the current role.

**Contact block order:** street (optional — city + state is enough per `output-formats.md` "What to Omit"), city/state/zip, phone, email. One line per field.

## Cover letter conventions (extracted)

**Top block order:**

1. `**Your Name**` (bold)
2. Street address
3. City, ST zip
4. Phone (formatted `(XXX) XXX-XXXX`)
5. Email
6. Blank line
7. Date — **ordinal format**, e.g. `4th September 20XX`, `21st March 2026`
8. Blank line
9. `**Recipient Name**` (bold) — skill rule: use `Dear Hiring Manager,` unless the user names a specific recipient
10. Recipient title + company
11. Recipient address (optional — include only if the user has it)
12. Blank line
13. Greeting (`Dear <Name>,` or `Dear Hiring Manager,`)

**Body:** 3–4 paragraphs per the structure in `output-formats.md` §3.

**Sign-off:** keep the skill's `Regards,` rule (see `output-formats.md` §3). The template's `Sincerely,` is a stock placeholder — the skill's rule overrides it for consistency across all letters.

**Signature:** `**Your Name**` on a new line after the sign-off, bold to match the top-block name.

## DOCX rendering

When converting the markdown outputs to DOCX, use these template files as the **style source** so every output inherits the user's fonts, heading styles, margins, and spacing:

```bash
# Resume
pandoc /path/to/Summer_Rae_Resume_<Company>.md \
  --reference-doc=/Users/summerrae/claude_code/claude-skills/resume-tailor/references/templates/resume-template.docx \
  -o /path/to/Summer_Rae_Resume_<Company>.docx

# Cover letter
pandoc /path/to/Summer_Rae_CoverLetter_<Company>.md \
  --reference-doc=/Users/summerrae/claude_code/claude-skills/resume-tailor/references/templates/cover-letter-template.docx \
  -o /path/to/Summer_Rae_CoverLetter_<Company>.docx
```

The `--reference-doc` flag pulls styles (Heading 1, Heading 2, body font, page margins) from the template and applies them to the generated DOCX. Content comes from the markdown; visual presentation comes from the template.

If the `anthropic-skills:docx` plugin is used instead of pandoc, pass the template path as the style source if the plugin supports it; otherwise fall back to pandoc for template-driven renders.

## When to deviate

Deviate from template conventions only when:

- The user explicitly asks for a different layout, header style, or sign-off
- The JD or target region requires a different convention (e.g. EU CV with photo, academic CV with publications-heavy section)

Record the deviation in the session so the next turn doesn't silently revert.
