# Micro-polish Reference

Concrete, checkable values for Phase 3 (Polish) audits. Load on demand — do not keep resident.

Adapted from `jakubkrehel/make-interfaces-feel-better`, 2026-06-26 source read.

---

## Radius

**Concentric radius formula:** `outerRadius = innerRadius + padding`

An inner element's border-radius must be visually concentric with its container's.

Worked example: card with `rounded-xl` (12px) and 8px padding → inner element gets `rounded` (4px).

Exception: if padding > 24px, treat the inner element as a separate surface — do not apply the formula.

---

## Shadow & Elevation

**3-layer shadow** (replaces borders on elevated elements):

```css
box-shadow:
  0px 0px 0px 1px rgba(0,0,0,0.06),
  0px 1px 2px -1px rgba(0,0,0,0.06),
  0px 2px 4px 0px rgba(0,0,0,0.04);
```

Dark mode — replace the top layer with:

```css
0 0 0 1px rgba(255,255,255,0.08)
```

**Image outline:**

```css
outline: 1px solid rgba(0,0,0,0.1);
outline-offset: -1px;
```

Must use pure black/white alpha. Never tinted — tinted outlines read as dirt on the image.

---

## Motion

**Press scale:** `scale(0.96)` on `:active`. Never below `0.95` — anything smaller feels exaggerated.

**Framer Motion spring (production UI):**

```js
{ type: "spring", duration: 0.3, bounce: 0 }
```

`bounce` MUST be `0`. Non-zero bounce reads as playful/toy in production interfaces.

**`AnimatePresence`:** always set `initial={false}` to skip enter-animations on page load.

**Never `transition: all`** — name exact properties only. Example:

```css
/* Bad */
transition: all 0.2s ease;

/* Good */
transition: opacity 0.2s ease, transform 0.2s ease;
```

Use CSS transitions for interactive elements (interruptible by hover/focus); keyframe animations only for one-shot sequences (loading spinners, success bursts).

**Enter animation:** combine `opacity + blur + translateY` with ~100ms stagger between items.

**Exit animation:** softer than enter — use a small fixed `translateY`, shorter duration.

---

## Type

Apply on the root element or a global CSS reset:

```css
-webkit-font-smoothing: antialiased;
```

Heading elements:

```css
text-wrap: balance;
```

Body / paragraph text:

```css
text-wrap: pretty;
```

Any dynamically-updating number (counters, prices, scores):

```css
font-variant-numeric: tabular-nums;
```

---

## Hit Areas

Minimum interactive target: **40 × 40px**.

When the visual element is smaller (an icon button, a small badge), extend the hit area via pseudo-element without affecting layout:

```css
.icon-button {
  position: relative;
}
.icon-button::after {
  content: "";
  position: absolute;
  inset: -8px; /* extend to reach 40px minimum */
}
```
