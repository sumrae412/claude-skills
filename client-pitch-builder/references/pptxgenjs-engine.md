# PptxGenJS Engine Reference

Source: `https://github.com/sgatwork/YC-Pitch-Deck/blob/main/design.md`

This file is the production code reference for generating `.pptx` files. Load it in Phase 4 only.

---

## Setup

```javascript
const pptxgen = require("pptxgenjs");

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_16x9"; // 10" x 5.625" canvas; all coords in inches

  // ... build slides ...

  await pres.writeFile({ fileName: "pitch.pptx" }); // async — must be awaited
})();
```

Install: `npm install pptxgenjs` in the workspace dir before running.

---

## Palette and Typography Constants

```javascript
const C = {
  offwhite: "F0F0F0", // slide background — every slide, never pure white
  white:    "FFFFFF", // card surfaces only
  black:    "0A0A0A", // headlines, primary text
  accent:   "002FA7", // Klein Blue — replace with user's brand hex if provided
  gray:     "888888", // secondary text, captions
  midgray:  "444444", // section labels on neutral slides
};

const SERIF = "Helvetica";    // all headlines
const MONO  = "Courier New";  // labels, tags, card headings, metadata
```

**Critical rule:** never prefix hex values with `#`. PptxGenJS silently corrupts the output file when `#` is included.

---

## Slide Factory

```javascript
function newSlide(pres, logoB64 = null) {
  const s = pres.addSlide();
  s.background = { color: C.offwhite };
  if (logoB64) {
    s.addImage({ data: logoB64, x: 9.2, y: 0.18, w: 0.55, h: 0.56 });
  }
  return s;
}
```

If no logo file provided, skip — do not add a placeholder.

---

## Layout Grid

```
LEFT COLUMN   x: 0.5  to  5.2
RIGHT COLUMN  x: 5.5  to  9.7
Logo          x: 9.2, y: 0.18, w: 0.55, h: 0.56  (top-right)
Section label x: 0.5, y: 0.22                      (top-left, every content slide)
Slide number  x: 8.8, y: 5.35                      (bottom-right)
Card padding  0.20–0.25" from card edge to text
```

---

## Recurring Elements

### Section Label (every content slide)

```javascript
s.addText("YOUR CHALLENGES", {
  x: 0.5, y: 0.22, w: 5, h: 0.26,
  fontSize: 9.5, bold: true,
  color: C.accent,   // key slides (Problem, Market, Team)
  // color: C.midgray, // neutral slides (Process, Traction, Ask)
  fontFace: MONO, charSpacing: 1.5, margin: 0,
});
```

### Slide Number

```javascript
s.addText(`${n} / ${TOTAL}`, {
  x: 8.8, y: 5.35, w: 1.0, h: 0.2,
  fontSize: 8, color: C.gray, fontFace: MONO,
  align: "right", margin: 0,
});
```

---

## Card Helper — THE SHADOW GOTCHA

**Never reuse a shadow object.** PptxGenJS mutates the options object in-place during `addShape`. Passing the same shadow reference to multiple calls corrupts later cards. Always inline the object literal:

```javascript
function card(pres, s, x, y, w, h) {
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h,
    fill: { color: "FFFFFF" },
    line: { color: "E8E8E8", width: 1 },
    rectRadius: 0.12,
    // inline the shadow literal every single call — never extract to a const
    shadow: { type: "outer", color: "000000", blur: 12, offset: 3, angle: 135, opacity: 0.07 },
  });
}
```

Shadow opacity must be <= 0.07. Barely visible is intentional.

---

## Card Patterns

### Numbered Cards (Challenges / Next Steps slides)

```javascript
const items = [
  { n: "01", t: "FIRST PAIN POINT" },
  { n: "02", t: "SECOND PAIN POINT" },
  { n: "03", t: "THIRD PAIN POINT" },
];

items.forEach((item, i) => {
  const cy = 0.62 + i * 1.18;
  card(pres, s, 5.6, cy, 4.15, 1.0);
  s.addText(item.n, {
    x: 5.82, y: cy + 0.1, w: 0.6, h: 0.3,
    fontSize: 9, color: C.gray, fontFace: MONO, margin: 0,
  });
  s.addText(item.t, {
    x: 5.82, y: cy + 0.42, w: 3.7, h: 0.38,
    fontSize: 13, bold: true, color: C.black, fontFace: MONO, margin: 0,
  });
});
```

### Stat Cards (Intro / Cover slides)

```javascript
const stats = [
  { v: "47 clients", l: "served across 3 industries" },
  { v: "3.2x ROI",   l: "average client outcome" },
];

stats.forEach((st, i) => {
  const cy = 0.6 + i * 1.55;
  card(pres, s, 6.3, cy, 3.35, 1.35);
  s.addText(st.v, {
    x: 6.55, y: cy + 0.12, w: 2.9, h: 0.68,
    fontSize: 30, bold: true,
    color: i === 0 ? C.accent : C.black, // accent on the key metric only
    fontFace: SERIF, margin: 0,
  });
  s.addText(st.l, {
    x: 6.55, y: cy + 0.8, w: 2.9, h: 0.3,
    fontSize: 10, color: C.gray, fontFace: MONO, margin: 0,
  });
});
```

### 2x2 Solution Grid (Solutions / Process slides)

```javascript
const solutions = [
  { n: "01", t: "SERVICE NAME", d: "One-line outcome" },
  { n: "02", t: "SERVICE NAME", d: "One-line outcome" },
  { n: "03", t: "SERVICE NAME", d: "One-line outcome" },
  { n: "04", t: "SERVICE NAME", d: "One-line outcome" },
];

solutions.forEach((sol, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const cx = 5.5 + col * 2.2;
  const cy = 0.7 + row * 2.2;
  card(pres, s, cx, cy, 2.0, 2.0);
  s.addText(sol.n, {
    x: cx + 0.15, y: cy + 0.12, w: 0.5, h: 0.28,
    fontSize: 9, color: C.accent, fontFace: MONO, margin: 0,
  });
  s.addText(sol.t, {
    x: cx + 0.15, y: cy + 0.42, w: 1.7, h: 0.35,
    fontSize: 11, bold: true, color: C.black, fontFace: MONO, margin: 0,
  });
  s.addText(sol.d, {
    x: cx + 0.15, y: cy + 0.82, w: 1.7, h: 0.7,
    fontSize: 10, color: C.gray, fontFace: SERIF, margin: 0,
  });
});
```

---

## Typography Reference

| Usage | Font | Size | Bold | Color |
|---|---|---|---|---|
| Slide headline | Helvetica | 52-80pt | yes | black |
| Cover / company name | Helvetica | 80-100pt | yes | black |
| Section label | Courier New | 9.5pt | yes | accent or midgray |
| Card number tag | Courier New | 9-10pt | yes | accent or gray |
| Card heading | Courier New | 12-14pt | yes | black |
| Supporting subtext | Helvetica | 12-14pt | no | gray |
| Stat value | Helvetica | 28-32pt | yes | black or accent |
| Stat label | Courier New | 10pt | no | gray |
| Slide number | Courier New | 8pt | no | gray |
| CTA / email | Courier New | 10pt | no | gray |

Headline length rule: 5-7 words maximum. Shorter = bigger font size.

---

## What to Never Do

| Never | Instead |
|---|---|
| `"#FFFFFF"` with `#` prefix | Bare hex: `"FFFFFF"` |
| `s.background = { color: "FFFFFF" }` | Always `"F0F0F0"` for slides |
| Reuse a shadow object across cards | Inline the literal every call |
| `opacity > 0.10` on shadows | Keep at `0.07` |
| Bullet lists on slides | Numbered white cards |
| Sentences in headlines | 5-7 word billboard statements |
| Dark slide backgrounds | White/offwhite only |

---

## QA Before Delivering

1. File size > 10KB (corrupt .pptx from bad hex or shadow mutation is often < 5KB)
2. Run: `ls -lh ~/Documents/<ProspectName>-pitch/pitch.pptx`
3. Every slide background is `F0F0F0`, not `FFFFFF`
4. No hex values have a `#` prefix anywhere in the script
5. Shadow object is inlined as a literal in every `card()` call
6. `pres.writeFile()` is awaited inside an `async` IIFE
