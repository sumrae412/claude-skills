# CSS Typography Templates

## Baseline Template

```css
/* TYPOGRAPHY BASELINE — Practical Typography (Butterick) */

*, *::before, *::after { box-sizing: border-box; }

html {
  font-size: clamp(16px, 2.5vw, 20px);       /* 15–25px range, fluid */
  -webkit-text-size-adjust: 100%;
}

body {
  font-family: /* your-font, */ Georgia, 'Times New Roman', serif;
  line-height: 1.38;                           /* 120–145% sweet spot */
  color: #1a1a1a;
  background: #fefefe;
  text-rendering: optimizeLegibility;
  font-feature-settings: "kern" 1, "liga" 1;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* TEXT CONTAINER: LINE LENGTH */
main, article, .prose {
  max-width: min(65ch, 90vw);                  /* 45–90 chars */
  margin: 0 auto;
  padding: 0 clamp(1rem, 4vw, 2rem);
}

/* PARAGRAPHS — space-between (default for web) */
p { margin: 0 0 0.75em 0; }

/* HEADINGS — subtle, spaced, bold */
h1, h2, h3, h4 {
  line-height: 1.15;
  hyphens: none;
  page-break-after: avoid;
  font-weight: 700;
}
h1 { font-size: 1.5em; margin: 2.5em 0 0.5em; }
h2 { font-size: 1.25em; margin: 2em 0 0.4em; }
h3 { font-size: 1.1em; margin: 1.5em 0 0.3em; }

/* ALL CAPS — always letterspaced */
.caps {
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-feature-settings: "kern" 1;
}

/* SMALL CAPS — real only */
.small-caps {
  font-variant-caps: small-caps;
  letter-spacing: 0.05em;
  font-feature-settings: "smcp" 1, "kern" 1;
}

/* BLOCK QUOTES */
blockquote {
  margin: 1.5em 2em;
  font-size: 0.92em;
  line-height: 1.3;
}

/* TABLES */
table { border-collapse: collapse; width: 100%; }
th, td { padding: 0.5em 1em; text-align: left; vertical-align: top; border: none; }
thead th { border-bottom: 1.5px solid currentColor; font-weight: 600; }

/* Numeric data: tabular lining figures */
.data-table td {
  font-feature-settings: "tnum" 1, "lnum" 1;
  font-variant-numeric: tabular-nums lining-nums;
}

/* LISTS */
ul, ol { padding-left: 1.5em; margin: 0 0 1em; }
li { margin-bottom: 0.3em; }

/* HORIZONTAL RULES */
hr { border: none; border-top: 1px solid currentColor; opacity: 0.3; margin: 2em 0; }

/* LINKS */
a {
  color: inherit;
  text-decoration-line: underline;
  text-decoration-thickness: 1px;
  text-underline-offset: 2px;
}

/* CODE */
code {
  font-family: 'SF Mono', 'Fira Code', Consolas, monospace;
  font-size: 0.88em;
  padding: 0.1em 0.3em;
  border-radius: 3px;
  background: rgba(0,0,0,0.04);
}

/* RESPONSIVE */
@media (max-width: 600px) {
  blockquote { margin: 1em 1em; }
  table { font-size: 0.9em; }
}

/* DARK MODE */
@media (prefers-color-scheme: dark) {
  body {
    color: #e0e0e0;
    background: #1a1a1a;
    font-weight: 350;           /* dark bg makes text appear heavier */
    -webkit-font-smoothing: auto;
  }
}

/* PRINT */
@media print {
  body { font-size: 11pt; line-height: 1.3; }
  main { max-width: none; }
  h1, h2, h3 { page-break-after: avoid; }
  p { orphans: 2; widows: 2; }
}
```

---

## Fluid Typography with Clamp

```css
body { font-size: clamp(16px, 2.5vw, 20px); }
main { max-width: min(65ch, 90vw); margin: 0 auto; padding: 0 clamp(1rem, 4vw, 2rem); }
h1 { font-size: clamp(1.5rem, 4vw, 2.5rem); }
h2 { font-size: clamp(1.25rem, 3vw, 1.75rem); }
```

## OpenType Features

```css
/* Body text */
.body { font-feature-settings: "kern" 1, "liga" 1, "calt" 1; }

/* Body with oldstyle figures */
.prose { font-feature-settings: "kern" 1, "liga" 1, "calt" 1, "onum" 1; }

/* Data tables — tabular lining */
.data-table td { font-feature-settings: "kern" 1, "tnum" 1, "lnum" 1; }

/* Small caps */
.small-caps { font-feature-settings: "kern" 1, "smcp" 1; letter-spacing: 0.05em; }

/* All caps with capital spacing */
.all-caps { text-transform: uppercase; letter-spacing: 0.06em; font-feature-settings: "kern" 1, "cpsp" 1; }
```

## React/JSX Pattern

```jsx
// WRONG
<p>"Hello," she said. "It's a beautiful day..."</p>
<p>Pages 1-10</p>

// RIGHT (paste actual UTF-8 chars or use JSX expressions)
<p>{'\u201C'}Hello,{'\u201D'} she said. {'\u201C'}It{'\u2019'}s a beautiful day{'\u2026'}{'\u201D'}</p>
<p>Pages 1{'\u2013'}10</p>
```
