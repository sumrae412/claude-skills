# Rendering to PDF

The output format from `SKILL.md` is Markdown. Three render options.

## Marp (recommended)

[Marp](https://marp.app/) is Markdown-driven and slide-aware. CLI works
without project setup.

### Frontmatter

Add to the top of the deck Markdown:

```yaml
---
marp: true
theme: default
size: 16:9
paginate: true
header: '[Company Name] — [Audience] — [Date]'
footer: 'Confidential'
---
```

### Slide separator

Marp uses `---` (horizontal rule) between slides. When rendering with
Marp, replace the `## Slide N — title` headings from SKILL.md output
with `---` between slides:

```markdown
---
marp: true
---

# Title slide
Tagline

---

# Problem
Concrete pain, named.

---
```

### Render

```bash
npx @marp-team/marp-cli@latest deck.md --pdf
# also: --pptx, --html, --images
```

### Speaker notes

Marp speaker notes use HTML comments. Visible in presenter mode and
exported in PDF as notes:

```markdown
# Slide title

Body content.

<!--
Speaker notes go here.
-->
```

### Custom theme

Write a CSS file, register with `--theme`:

```css
/* @theme custom */
section {
  background: #ffffff;
  font-family: 'Inter', sans-serif;
}
section h1 {
  color: #0a2540;
  font-size: 2.5em;
}
```

```bash
npx @marp-team/marp-cli@latest deck.md --theme custom.css --pdf
```

## Pandoc / Beamer

For academic / technical audiences who expect Beamer.

```bash
pandoc deck.md -t beamer -o deck.pdf --slide-level=2
```

Tradeoffs: Beamer themes are dense and dated; Marp's defaults look more
modern. Use Beamer only if the audience expects it.

## HTML + Chrome headless

For full design control or when Marp themes don't fit.

1. Generate HTML from the Markdown (Marp itself outputs HTML; alternatives:
   Reveal.js, Slidev).
2. Print with Chrome:

```bash
google-chrome --headless --disable-gpu --print-to-pdf=deck.pdf deck.html
```

Use when the deck needs custom CSS, brand assets, or animations beyond
Marp's themes.

## anthropic-skills:pptx (when .pptx is required)

If the audience requires PowerPoint (corporate gatekeepers, compliance
review, hand-off to a designer), invoke `anthropic-skills:pptx` after
drafting slide content here. That skill handles the .pptx file format
specifically.

## Quick comparison

| Tool | When | Setup | Look |
|---|---|---|---|
| Marp | default for most decks | one CLI command | modern, clean |
| Pandoc/Beamer | academic/technical audience | LaTeX install | dense, traditional |
| HTML + Chrome | custom branding, animations | more work | fully custom |
| `anthropic-skills:pptx` | .pptx required | skill handoff | depends on theme |

## Output validation

Before sharing:

```bash
# verify PDF page count matches slide count
pdfinfo deck.pdf | grep Pages

# preview the rendered PDF
open deck.pdf       # macOS
xdg-open deck.pdf   # Linux
```

If page count differs from your slide count, a `---` separator was missed
or a slide overflowed onto two pages. Fix the source and re-render.
