# Pitch Deck Design Guide

This is both a design philosophy document AND a production code system. Read it fully before writing any code.

---

## The 3 Principles

Every slide must satisfy all three. In order of application:

### 1. Legible
Large, bold, high-contrast. Readable from the back of a 500-person room.
- Minimum: ~50pt for body, ~65pt+ for key headlines
- Helvetica Bold for all headlines. Courier New (monospace) for all labels, tags, and metadata.
- White background, black text — always. No dark slides.
- No thin weights. No medium-gray text on white.

### 2. Simple
One idea per slide. Billboard, not essay.
- The headline IS the message. Everything else is supporting evidence.
- If you need two ideas, use two slides.
- Strip ruthlessly. If an element doesn't serve the one idea, cut it.
- ~7 words maximum in a headline. If you're writing sentences, you're writing too much.

### 3. Obvious
Understood at a glance. Conclusion written explicitly.
- Never make the investor calculate, infer, or read a chart to understand the point.
- Write the insight on the slide: "18% MoM, 4 months straight" — not an unlabeled line going up.
- The stranger test: show to someone unfamiliar with the company. Within 3 seconds they should state the idea correctly.

---

## The Design System

### Palette

```javascript
const C = {
  offwhite: "F0F0F0",   // slide background — NOT pure white
  white:    "FFFFFF",   // card backgrounds
  black:    "0A0A0A",   // headlines and primary text
  accent:   "002FA7",   // Klein Blue — OR founder's brand colour if provided
  gray:     "888888",   // secondary text, subtext, captions
  midgray:  "444444",   // section labels, monospace tags
};
```

**Accent colour rule:** Always ask the founder if they have a brand colour. If yes, use it in place of `#002FA7`. If no, default to Klein Blue. The accent is used for:
- Section label text (top-left monospace)
- Numbered tags on cards (01, 02, 03...)
- The key result stat (the most important number on the slide)
- Nothing else.

### Typography

```javascript
const SERIF = "Helvetica";    // all headlines — bold, massive
const MONO  = "Courier New";  // all labels, tags, metadata, card headings — creates editorial feel
```

**Font rules:**
- Headlines: Helvetica, bold, 52–80pt depending on length. Shorter = bigger.
- Section label (top-left): Courier New, 9.5pt, bold, `charSpacing: 1.5`, accent colour
- Card tags (01, 02...): Courier New, 9–10pt, bold, accent colour
- Card headings: Courier New, 12–14pt, bold, black
- Supporting text: Helvetica, 12–14pt, gray
- Metadata (price, email, slide number): Courier New, 8–10pt, gray

### Slide Background

```javascript
s.background = { color: C.offwhite }; // F0F0F0 — every single slide
```

Never pure white (`FFFFFF`) for slide backgrounds. The off-white creates the editorial quality of the reference. White is reserved for card surfaces only.

### Logo Mark

Every slide gets the founder's logo in the top-right corner. If a logo file is provided, encode it as base64 PNG and embed it. Position: `x: 9.2, y: 0.18, w: 0.55, h: 0.56`.

```javascript
s.addImage({ data: logoB64, x: 9.2, y: 0.18, w: 0.55, h: 0.56 });
```

If no logo is provided, skip this element — do not substitute a placeholder.

### White Cards

The signature element of this design system. Used for ALL supporting content: stats, steps, team bios, problem items, ask points.

```javascript
s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
  x, y, w, h,
  fill: { color: "FFFFFF" },
  line: { color: "E8E8E8", width: 1 },
  rectRadius: 0.12,
  shadow: { type: "outer", color: "000000", blur: 12, offset: 3, angle: 135, opacity: 0.07 },
});
```

**Card rules:**
- Always rounded corners (`rectRadius: 0.12`)
- Always subtle border (`E8E8E8`)
- Always soft shadow (opacity 0.07 max — barely visible, just enough to lift off background)
- Background always pure white `FFFFFF`
- Internal padding: leave 0.2–0.25" from card edge to text

### Section Label

Top-left of every content slide (not the cover):

```javascript
s.addText("THE PROBLEM", {
  x: 0.5, y: 0.22, w: 5, h: 0.26,
  fontSize: 9.5, bold: true, color: C.accent,  // or C.midgray for neutral sections
  fontFace: MONO, charSpacing: 1.5, margin: 0,
});
```

Use accent colour for the label when the slide is a key reveal (Problem, Market, Team). Use `C.midgray` for neutral sections (Product, Traction, Ask).

### Slide Number

Bottom-right, every slide:

```javascript
s.addText(`${n} / ${TOTAL}`, {
  x: 8.8, y: 5.35, w: 1.0, h: 0.2,
  fontSize: 8, color: C.gray, fontFace: MONO,
  align: "right", margin: 0,
});
```

---

## Layout System

### The Master Layout Pattern

Every content slide follows the same two-column structure from the reference design:

```
LEFT COLUMN (x: 0.5 to 5.2)     RIGHT COLUMN (x: 5.5 to 9.7)
─────────────────────────────    ──────────────────────────────
Section label (top)               Logo mark (top-right)
Big bold headline (50–80pt)       White cards stacked or in grid
1–2 line subtext (gray, 13–14pt)  (stats / steps / team bios / items)
```

The headline does all the work. The right column provides the evidence.

### Slide-Specific Layouts

**Cover:**
- Left: Giant company name (140–160pt), tagline (16–18pt gray), raise amount (monospace, bottom)
- Right: 3 stacked stat cards

**Problem:**
- Left: 3-line headline ("Restaurant / owners are / flying blind."), 2-line subtext
- Right: 4 numbered cards stacked (01–04), monospace caps label, no body text

**Product:**
- Left: 2-line outcome headline ("Clean P&L. / No effort."), 1-line subtext
- Right: 2×2 grid of step cards (number in blue, step name in mono bold, description in gray)

**Market:**
- Left: 2-line TAM headline ("$180M ARR. / US alone."), 2-line subtext, "THE MATH" card at bottom
- Right: 2 stacked number cards (total count, then addressable ARR in accent blue)

**Traction:**
- Left: 2-line growth headline ("18% MoM. / 4 months."), line chart below
- Right: 3 stacked stat cards (ARR in accent blue, customer count in black, notable customers)

**Team:**
- Full-width headline (both columns), 2-line (55–65pt)
- Bottom half: 2 cards side by side. Each: role tag (grey pill), credential in mono bold, 2-sentence why-it-matters in gray

**Ask / Conclusion:**
- Left: Giant raise amount (65–72pt), full width
- Bottom: 4 numbered row-cards spanning full width. Each: number left, bold label center-left, gray description right

---

## PptxGenJS Code Patterns

### Setup

```javascript
const pptxgen = require("pptxgenjs");
const fs = require("fs");

let pres;

function newSlide() {
  const s = pres.addSlide();
  s.background = { color: "F0F0F0" };
  // Logo — only if logo file provided
  s.addImage({ data: logoB64, x: 9.2, y: 0.18, w: 0.55, h: 0.56 });
  return s;
}

(async () => {
  pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10" × 5.625"
  // ... build slides ...
  await pres.writeFile({ fileName: "pitch.pptx" });
})();
```

### Card Helper

Always use a helper to keep shadow objects fresh (PptxGenJS mutates them):

```javascript
function card(s, x, y, w, h) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: "FFFFFF" },
    line: { color: "E8E8E8", width: 1 },
    rectRadius: 0.12,
    shadow: { type: "outer", color: "000000", blur: 12, offset: 3, angle: 135, opacity: 0.07 },
  });
}
// NEVER reuse a shadow object — always create fresh. PptxGenJS mutates options in-place.
```

### Numbered Card Pattern (Problem / Ask slides)

```javascript
const items = [
  { n: "01", t: "LABEL IN MONO CAPS" },
  { n: "02", t: "SECOND ITEM" },
];
items.forEach((item, i) => {
  const cy = 0.62 + i * 1.18;
  card(s, 5.6, cy, 4.15, 1.0);
  s.addText(item.n, {
    x: 5.82, y: cy + 0.1, w: 0.6, h: 0.3,
    fontSize: 9, color: C.gray, fontFace: MONO, margin: 0,
  });
  s.addText(item.t, {
    x: 5.82, y: cy + 0.42, w: 3.7, h: 0.38,
    fontSize: 13, bold: true, color: C.black,
    fontFace: MONO, margin: 0,
  });
});
```

### Stat Card Pattern (Cover / Traction)

```javascript
const stats = [
  { v: "$143K ARR", l: "revenue" },
  { v: "18% MoM",   l: "growth" },
];
stats.forEach((st, i) => {
  const cy = 0.6 + i * 1.55;
  card(s, 6.3, cy, 3.35, 1.35);
  s.addText(st.v, {
    x: 6.55, y: cy + 0.12, w: 2.9, h: 0.68,
    fontSize: 30, bold: true, color: C.black,
    fontFace: SERIF, margin: 0,
  });
  s.addText(st.l, {
    x: 6.55, y: cy + 0.8, w: 2.9, h: 0.3,
    fontSize: 10, color: C.gray, fontFace: MONO, margin: 0,
  });
});
```

### Line Chart (Traction)

```javascript
s.addChart(pres.charts.LINE, [{
  name: "MRR",
  labels: ["Nov", "Dec", "Jan", "Feb", "Mar"],
  values: [6100, 7200, 8500, 10000, 11800],
}], {
  x: 0.4, y: 2.85, w: 5.8, h: 2.55,
  lineSize: 5,
  lineSmooth: false,
  chartColors: ["0A0A0A"],              // black line
  chartArea: { fill: { color: "F0F0F0" } },
  plotArea: { fill: { color: "F0F0F0" } },
  catAxisLabelColor: "888888",
  valAxisLabelColor: "888888",
  catAxisLineShow: false,
  valAxisLineShow: false,
  valGridLine: { color: "DDDDDD", size: 0.5 },
  catGridLine: { style: "none" },
  showLegend: false,
  showValue: true,
  dataLabelFormatCode: '"$"#,##0',
  dataLabelColor: "0A0A0A",
  dataLabelFontSize: 9,
  dataLabelFontBold: true,
  valAxisNumFmt: '"$"#,##0',
  showTitle: false,
});
```

---

## What to Never Do

| ❌ Never | ✓ Instead |
|---------|----------|
| Pure white (`FFFFFF`) slide background | Off-white `F0F0F0` |
| Dark / black slides | White background, black text — always |
| Sentences in headlines | 3–7 word billboard statements |
| Body copy paragraphs | 1-line gray subtext maximum |
| Decorative header/footer bars | Thin section label (monospace, top-left) |
| Bullets lists | Numbered white cards |
| Screenshots of the product | Numbered workflow steps in cards |
| Pie charts or bar charts for market | Bottoms-up math in a "THE MATH" card |
| Cumulative graphs | Month-over-month line chart |
| Accent lines under titles | Whitespace |
| Multiple fonts | Helvetica (headlines) + Courier New (labels) only |
| Shadows with opacity > 0.10 | Keep at 0.07 — barely visible |
| Re-using shadow option objects | Create a fresh object every call |
| 8-char hex colors for shadows | Use `color + opacity` separately |
| "#" prefix on any hex color | Bare 6-char hex only (PptxGenJS will corrupt the file) |

---

## QA Checklist

Before declaring done, verify every slide against these:

1. **Background** is `F0F0F0` (not `FFFFFF`)
2. **No text overflows** its containing shape — reduce font size or split to two slides
3. **Logo** appears top-right on every slide
4. **Section label** is present top-left on every content slide
5. **Headline** is ≤ 7 words and bold
6. **Supporting text** is max 1–2 lines, gray, small
7. **Cards** all have rounded corners, subtle border, soft shadow
8. **Accent colour** is used sparingly — not on every element
9. **Charts** use the offwhite background, not white or transparent
10. **No cumulative graphs**

Convert to images and do a visual pass before presenting:
```bash
python scripts/office/soffice.py --headless --convert-to pdf output.pptx
pdftoppm -jpeg -r 150 output.pdf slide
```
