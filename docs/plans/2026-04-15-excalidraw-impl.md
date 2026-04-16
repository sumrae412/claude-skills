# Excalidraw Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a general-purpose Excalidraw diagram generation skill with progressive disclosure and a Playwright render-validate pipeline.

**Architecture:** Thin SKILL.md router (~800 tokens) dispatches to lazy-loaded reference files. Render pipeline uses Playwright + Chromium to convert `.excalidraw` JSON → PNG for visual validation.

**Tech Stack:** Markdown (skill files), Python + Playwright (render pipeline), Excalidraw JSON format

**Ruled Out:**
- Monolithic SKILL.md — too much always-resident context (~4K tokens)
- Two-skill split (generation + rendering) — over-engineered for one render script
- Python generator scripts for JSON — adds indirection, harder to debug than hand-crafted JSON

---

### Task 1: Create directory structure
**Type:** shared_prerequisite
**Depends on:** none

**Files:**
- Create: `excalidraw/` directory
- Create: `excalidraw/references/` directory

**Step 1: Create directories**

```bash
mkdir -p excalidraw/references
```

**Step 2: Verify**

```bash
ls -la excalidraw/references/
```
Expected: empty directory exists

---

### Task 2: Write SKILL.md router
**Type:** value_unit
**Depends on:** T1 (build)

**Files:**
- Create: `excalidraw/SKILL.md`

**Step 1: Write the router**

Write `excalidraw/SKILL.md` with this content:

```markdown
---
name: excalidraw
description: Generate Excalidraw diagram JSON files that make visual arguments. Use when the user wants to visualize workflows, architectures, concepts, or any system as a diagram. Produces .excalidraw JSON files with optional PNG rendering for validation.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
  source: "https://github.com/coleam00/excalidraw-diagram-skill"
---

# Excalidraw Diagram Creator

Generate `.excalidraw` JSON files that **argue visually** — shapes and arrangements mirror their underlying concepts, not just label boxes.

## Depth Assessment (Do This First)

**Simple/Conceptual** — abstract shapes, labels, relationships. Use when explaining mental models or the audience doesn't need specifics.

**Comprehensive/Technical** — concrete examples, code snippets, real data formats. Use when diagramming real systems, teaching, or showing how technologies integrate. For technical diagrams, research actual specs/formats before drawing.

## Workflow

### Step 1: Design
Read `references/design-methodology.md`. For each concept, determine what it DOES (not what it IS), then map to a visual pattern. Each major concept should use a different pattern.

### Step 2: Generate JSON
Read `references/json-schema.md`, `references/element-templates.md`, and `references/color-palette.md`.

Build the JSON **one section at a time** — do not generate the entire file in a single pass. For each section:
1. Add elements with descriptive string IDs (e.g., `"trigger_rect"`, `"arrow_fan_left"`)
2. Namespace seeds by section (section 1 uses 100xxx, section 2 uses 200xxx)
3. Update cross-section bindings (`boundElements` arrays) as you go

Wrap in the standard envelope:
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [...],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 },
  "files": {}
}
```

### Step 3: Validate (Render-View-Fix Loop)
Read `references/render_excalidraw.py` for setup instructions, then:

```bash
cd <skill-directory>/references && uv run python render_excalidraw.py <path-to-file.excalidraw>
```

View the output PNG with the Read tool. Check:
1. Does the structure match the conceptual design?
2. No text clipped/overflowing containers
3. No overlapping elements
4. Arrows connect correctly, route cleanly
5. Spacing is consistent, composition balanced

Fix issues in the JSON → re-render → repeat until clean. Typically 2-4 iterations.

**First-time setup:**
```bash
cd <skill-directory>/references && uv sync && uv run playwright install chromium
```

## Quality Checklist

- [ ] Isomorphism: visual structure mirrors conceptual structure
- [ ] Variety: each major concept uses a different visual pattern
- [ ] Connections: every relationship has an arrow or line
- [ ] Hierarchy: important elements are larger/more isolated
- [ ] Container discipline: <30% of text in containers; default to free-floating
- [ ] Text clean: `text` and `originalText` contain only readable words
- [ ] Font: `fontFamily: 3`, `roughness: 0`, `opacity: 100`
- [ ] Colors from palette: all colors pulled from `color-palette.md`
- [ ] Rendered and validated: PNG inspected, no visual defects
- [ ] Evidence artifacts (technical diagrams only): code snippets, real data formats included
```

**Step 2: Verify file exists and token count is reasonable**

```bash
wc -w excalidraw/SKILL.md
```
Expected: ~400-500 words (roughly 600-800 tokens)

---

### Task 3: Write design-methodology.md
**Type:** value_unit
**Depends on:** T1 (build)

**Files:**
- Create: `excalidraw/references/design-methodology.md`

**Step 1: Write the methodology reference**

Write `excalidraw/references/design-methodology.md` cherry-picking from the source repo's SKILL.md. Include these sections:

1. **Visual Pattern Library** — fan-out, convergence, tree, timeline, spiral/cycle, assembly line, side-by-side, gap/break, cloud. Include the ASCII sketches for each.

2. **Concept-to-Pattern Mapping Table:**

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

3. **Shape Meaning Table:**

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

4. **Container vs. Free-Floating Text:**

| Use Container When | Use Free-Floating When |
|---|---|
| Focal point of section | Label or description |
| Needs visual grouping | Supporting detail |
| Arrows connect to it | Describes something nearby |
| Shape carries meaning | Section title or annotation |

5. **Layout Principles:**
- Hierarchy through scale: Hero 300x150, Primary 180x90, Secondary 120x60, Small 60x40
- Whitespace = importance: most important element gets 200px+ clearance
- Flow direction: left→right or top→bottom for sequences, radial for hub-and-spoke

6. **Evidence Artifacts (for technical diagrams):**

| Artifact Type | When to Use | How to Render |
|---|---|---|
| Code snippets | APIs, integrations | Dark rect + syntax-colored text |
| Data/JSON examples | Schemas, payloads | Dark rect + colored text |
| Event sequences | Protocols, lifecycles | Timeline pattern |
| UI mockups | Showing output | Nested rectangles |

**Omit:** verbose bad-vs-good comparisons, multi-zoom architecture, repeated philosophy statements.

**Step 2: Verify**

```bash
wc -w excalidraw/references/design-methodology.md
```
Expected: ~600-900 words

---

### Task 4: Write json-schema.md
**Type:** value_unit
**Depends on:** T1 (build)

**Files:**
- Create: `excalidraw/references/json-schema.md`

**Step 1: Port from source**

Write `excalidraw/references/json-schema.md` with this exact content (ported from source):

```markdown
# Excalidraw JSON Schema

## Element Types

| Type | Use For |
|------|---------|
| `rectangle` | Processes, actions, components |
| `ellipse` | Entry/exit points, external systems |
| `diamond` | Decisions, conditionals |
| `arrow` | Connections between shapes |
| `text` | Labels inside shapes |
| `line` | Non-arrow connections |
| `frame` | Grouping containers |

## Common Properties

All elements share these:

| Property | Type | Description |
|----------|------|-------------|
| `id` | string | Unique identifier |
| `type` | string | Element type |
| `x`, `y` | number | Position in pixels |
| `width`, `height` | number | Size in pixels |
| `strokeColor` | string | Border color (hex) |
| `backgroundColor` | string | Fill color (hex or "transparent") |
| `fillStyle` | string | "solid", "hachure", "cross-hatch" |
| `strokeWidth` | number | 1, 2, or 4 |
| `strokeStyle` | string | "solid", "dashed", "dotted" |
| `roughness` | number | 0 (smooth), 1 (default), 2 (rough) |
| `opacity` | number | 0-100 |
| `seed` | number | Random seed for roughness |

## Text-Specific Properties

| Property | Description |
|----------|-------------|
| `text` | The display text |
| `originalText` | Same as text |
| `fontSize` | Size in pixels (16-20 recommended) |
| `fontFamily` | 3 for monospace (use this) |
| `textAlign` | "left", "center", "right" |
| `verticalAlign` | "top", "middle", "bottom" |
| `containerId` | ID of parent shape |

## Arrow-Specific Properties

| Property | Description |
|----------|-------------|
| `points` | Array of [x, y] coordinates |
| `startBinding` | Connection to start shape |
| `endBinding` | Connection to end shape |
| `startArrowhead` | null, "arrow", "bar", "dot", "triangle" |
| `endArrowhead` | null, "arrow", "bar", "dot", "triangle" |

## Binding Format

\```json
{
  "elementId": "shapeId",
  "focus": 0,
  "gap": 2
}
\```

## Rectangle Roundness

Add for rounded corners:
\```json
"roundness": { "type": 3 }
\```
```

Note: Remove the backslash escapes on the code fences — they're only here to prevent nesting issues in this plan.

**Step 2: Verify**

```bash
wc -w excalidraw/references/json-schema.md
```

---

### Task 5: Write element-templates.md
**Type:** value_unit
**Depends on:** T1 (build)

**Files:**
- Create: `excalidraw/references/element-templates.md`

**Step 1: Port from source**

Write `excalidraw/references/element-templates.md` with the complete JSON templates for each element type, ported from the source repo. Include all six templates:

1. **Free-Floating Text** — `type: "text"`, `containerId: null`, fontSize 20, fontFamily 3
2. **Line** — `type: "line"`, structural (not arrow), points array
3. **Small Marker Dot** — `type: "ellipse"`, 12x12, for timeline markers
4. **Rectangle** — `type: "rectangle"`, with `boundElements` for contained text, `roundness: {"type": 3}`
5. **Text (centered in shape)** — `type: "text"`, `containerId: "elem1"`, textAlign center, verticalAlign middle
6. **Arrow** — `type: "arrow"`, with `startBinding`/`endBinding`, points array

Each template should use placeholder color comments like `"<stroke from palette based on semantic purpose>"` to remind the user to pull from `color-palette.md`.

Include the note at the end: "For curves: use 3+ points in `points` array."

**Step 2: Verify**

```bash
wc -w excalidraw/references/element-templates.md
```

---

### Task 6: Write color-palette.md
**Type:** value_unit
**Depends on:** T1 (build)

**Files:**
- Create: `excalidraw/references/color-palette.md`

**Step 1: Port from source**

Write `excalidraw/references/color-palette.md` with these sections (ported as-is from source):

**Shape Colors (Semantic):**

| Semantic Purpose | Fill | Stroke |
|---|---|---|
| Primary/Neutral | `#3b82f6` | `#1e3a5f` |
| Secondary | `#60a5fa` | `#1e3a5f` |
| Tertiary | `#93c5fd` | `#1e3a5f` |
| Start/Trigger | `#fed7aa` | `#c2410c` |
| End/Success | `#a7f3d0` | `#047857` |
| Warning/Reset | `#fee2e2` | `#dc2626` |
| Decision | `#fef3c7` | `#b45309` |
| AI/LLM | `#ddd6fe` | `#6d28d9` |
| Inactive/Disabled | `#dbeafe` | `#1e40af` (dashed stroke) |
| Error | `#fecaca` | `#b91c1c` |

**Text Colors (Hierarchy):**

| Level | Color | Use For |
|---|---|---|
| Title | `#1e40af` | Section headings |
| Subtitle | `#3b82f6` | Subheadings |
| Body/Detail | `#64748b` | Descriptions, annotations |
| On light fills | `#374151` | Text inside light shapes |
| On dark fills | `#ffffff` | Text inside dark shapes |

**Evidence Artifact Colors:**

| Artifact | Background | Text Color |
|---|---|---|
| Code snippet | `#1e293b` | Syntax-colored |
| JSON/data | `#1e293b` | `#22c55e` |

**Default Stroke & Line Colors:**

| Element | Color |
|---|---|
| Arrows | Source element's stroke color |
| Structural lines | `#1e3a5f` or `#64748b` |
| Marker dots | `#3b82f6` fill |

**Background:** Canvas `#ffffff`

Include the header note: "This is the single source of truth for all colors. To customize for your brand, edit this file."

**Step 2: Verify**

```bash
wc -w excalidraw/references/color-palette.md
```

---

### Task 7: Write render pipeline files
**Type:** value_unit
**Depends on:** T1 (build)

**Files:**
- Create: `excalidraw/references/render_excalidraw.py`
- Create: `excalidraw/references/render_template.html`
- Create: `excalidraw/references/pyproject.toml`

**Step 1: Write pyproject.toml**

```toml
[project]
name = "excalidraw-render"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "playwright>=1.40.0",
]
```

**Step 2: Write render_template.html**

Port verbatim from source. The HTML loads Excalidraw's `exportToSvg` from esm.sh, exposes a `window.renderDiagram(jsonData)` function that renders the diagram as SVG, and signals completion via `window.__renderComplete`.

**Step 3: Write render_excalidraw.py**

Port from source. The script:
1. `validate_excalidraw(data)` — checks `type == "excalidraw"` and non-empty `elements`
2. `compute_bounding_box(elements)` — calculates spatial extent, handling arrows/lines with relative point coordinates
3. `render(input_path, output_path, scale, max_width)` — loads JSON, computes viewport, launches headless Chromium via Playwright, injects diagram data, captures screenshot
4. CLI: accepts `input_file`, optional `--output`, `--scale` (default 2), `--max-width` (default 3000)

**Step 4: Verify files exist**

```bash
ls -la excalidraw/references/
```
Expected: all 7 reference files present

---

### Task 8: Test render pipeline
**Type:** value_unit
**Depends on:** T7 (build)

**Step 1: Install dependencies**

```bash
cd excalidraw/references && uv sync && uv run playwright install chromium
```

**Step 2: Create a minimal test diagram**

Create `/tmp/test-diagram.excalidraw`:
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [
    {
      "type": "rectangle",
      "id": "rect1",
      "x": 100, "y": 100, "width": 180, "height": 90,
      "strokeColor": "#1e3a5f",
      "backgroundColor": "#3b82f6",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "seed": 12345,
      "version": 1,
      "versionNonce": 67890,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": [{"id": "text1", "type": "text"}],
      "link": null,
      "locked": false,
      "roundness": {"type": 3}
    },
    {
      "type": "text",
      "id": "text1",
      "x": 130, "y": 132,
      "width": 120, "height": 25,
      "text": "Hello",
      "originalText": "Hello",
      "fontSize": 20,
      "fontFamily": 3,
      "textAlign": "center",
      "verticalAlign": "middle",
      "strokeColor": "#ffffff",
      "backgroundColor": "transparent",
      "fillStyle": "solid",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 0,
      "opacity": 100,
      "angle": 0,
      "seed": 11111,
      "version": 1,
      "versionNonce": 22222,
      "isDeleted": false,
      "groupIds": [],
      "boundElements": null,
      "link": null,
      "locked": false,
      "containerId": "rect1",
      "lineHeight": 1.25
    }
  ],
  "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
  "files": {}
}
```

**Step 3: Render**

```bash
cd excalidraw/references && uv run python render_excalidraw.py /tmp/test-diagram.excalidraw
```
Expected: PNG file created at `/tmp/test-diagram.png`

**Step 4: View the PNG**

Use the Read tool on `/tmp/test-diagram.png` to verify it shows a blue rounded rectangle with white "Hello" text.

**Step 5: Clean up test file**

```bash
rm /tmp/test-diagram.excalidraw /tmp/test-diagram.png
```

---

### Task 9: Commit
**Type:** value_unit
**Depends on:** T2-T8

**Step 1: Stage and commit**

```bash
git add excalidraw/
git commit -m "feat(excalidraw): add Excalidraw diagram generation skill

Progressive disclosure skill for generating .excalidraw JSON files from
natural language. Includes Playwright render-validate pipeline, semantic
color palette, element templates, and visual pattern library.

Based on coleam00/excalidraw-diagram-skill with condensed methodology
and lazy-loaded reference files.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

---

## Parallelization Notes

- Tasks 2-6 are independent (all depend only on T1) and can be executed in parallel
- Task 7 depends only on T1 and can run in parallel with 2-6
- Task 8 depends on T7 (needs the render script)
- Task 9 depends on all previous tasks
