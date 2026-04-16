# Design Methodology

How to translate concepts into visual structure before writing any JSON. For each concept, determine what it **DOES** (not what it IS), then map it to a visual pattern. Each major concept in a multi-concept diagram should use a different pattern.

---

## 1. Visual Pattern Library

### Fan-Out (One-to-Many)
Central element with arrows radiating to multiple targets. Use for: sources, PRDs, root causes, central hubs.
```
        ○
       ↗
  □ → ○
       ↘
        ○
```

### Convergence (Many-to-One)
Multiple inputs merging through arrows to single output. Use for: aggregation, funnels, synthesis.
```
  ○ ↘
  ○ → □
  ○ ↗
```

### Tree (Hierarchy)
Parent-child branching with connecting lines and free-floating text (no boxes needed). Use for: file systems, org charts, taxonomies.
```
  label
  ├── label
  │   ├── label
  │   └── label
  └── label
```
Use `line` elements for the trunk and branches, free-floating text for labels.

### Timeline
Horizontal or vertical line with small dots (10-20px ellipses) at intervals, free-floating labels beside each dot. Use for: sequences, lifecycles, protocols.
```
  ●─── Label 1
  │
  ●─── Label 2
  │
  ●─── Label 3
```

### Spiral/Cycle (Continuous Loop)
Elements in sequence with arrow returning to start. Use for: feedback loops, iterative processes, evolution.
```
  □ → □
  ↑     ↓
  □ ← □
```

### Assembly Line (Transformation)
Input → Process Box → Output with clear before/after. Use for: transformations, processing, conversion.
```
  ○○○ → [PROCESS] → □□□
  chaos              order
```

### Side-by-Side (Comparison)
Two parallel structures with visual contrast. Use for: before/after, options, trade-offs.

### Gap/Break (Separation)
Visual whitespace or barrier between sections. Use for: phase changes, context resets, boundaries.

### Cloud (Abstract State)
Overlapping ellipses with varied sizes. Use for: context, memory, conversations, mental states.

---

## 2. Concept-to-Pattern Mapping

| If the concept... | Use this pattern |
|---|---|
| Spawns multiple outputs | Fan-out |
| Combines inputs into one | Convergence |
| Has hierarchy/nesting | Tree (lines + text) |
| Is a sequence of steps | Timeline (line + dots + labels) |
| Loops/improves continuously | Spiral/Cycle |
| Is an abstract state | Cloud (overlapping ellipses) |
| Transforms input to output | Assembly line |
| Compares two things | Side-by-side |
| Separates into phases | Gap/Break |

---

## 3. Shape Meaning

Choose a shape based on what it represents — or use no shape at all. Default to no container. Aim for <30% of text elements to be inside containers.

| Concept Type | Shape | Why |
|---|---|---|
| Labels, descriptions | none (free-floating text) | Typography creates hierarchy |
| Section titles | none (free-floating text) | Font size/weight is enough |
| Timeline markers | small ellipse (10-20px) | Visual anchor |
| Start, trigger, input | ellipse | Soft, origin-like |
| End, output, result | ellipse | Completion |
| Decision, condition | diamond | Classic decision symbol |
| Process, action, step | rectangle | Contained action |
| Abstract state | overlapping ellipses | Cloud-like |

---

## 4. Container vs. Free-Floating Text

Not every piece of text needs a shape around it. Default to free-floating; add a container only when it earns its place.

| Use Container When | Use Free-Floating When |
|---|---|
| Focal point of section | Label or description |
| Needs visual grouping | Supporting detail |
| Arrows connect to it | Describes something nearby |
| Shape carries meaning | Section title or annotation |

**The container test**: for each boxed element, ask "Would this work as free-floating text?" If yes, remove the container.

---

## 5. Layout Principles

- **Hierarchy through scale**: Hero 300×150, Primary 180×90, Secondary 120×60, Small 60×40.
- **Whitespace = importance**: the most important element gets 200px+ clearance on all sides.
- **Flow direction**: left→right or top→bottom for sequences, radial for hub-and-spoke.
- **Connections required**: position alone doesn't show relationships — if A relates to B, draw an arrow or line.

---

## 6. Evidence Artifacts (Technical Diagrams)

For technical diagrams, include concrete examples that prove accuracy and let viewers learn. Don't just label boxes — show what things actually look like.

| Artifact Type | When to Use | How to Render |
|---|---|---|
| Code snippets | APIs, integrations | Dark rect + syntax-colored text |
| Data/JSON examples | Schemas, payloads | Dark rect + colored text |
| Event sequences | Protocols, lifecycles | Timeline pattern |
| UI mockups | Showing output | Nested rectangles |

See `color-palette.md` for the specific background/text colors used in evidence artifacts.
