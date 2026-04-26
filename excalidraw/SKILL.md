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

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


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
2. Namespace the `seed` integer field by section (section 1 uses 100xxx, section 2 uses 200xxx)
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
Read `references/render_excalidraw.py` for setup instructions, then run the command below from the directory containing this SKILL.md file — Claude should resolve the skill's directory from context (plugin cache, repo checkout, etc.):

```bash
# From the directory containing this SKILL.md:
cd references && uv run python render_excalidraw.py <path-to-file.excalidraw>
```

View the output PNG with the Read tool. Check:
1. Does the structure match the conceptual design?
2. No text clipped/overflowing containers
3. No overlapping elements
4. Arrows connect correctly, route cleanly
5. Spacing is consistent, composition balanced

Fix issues in the JSON → re-render → repeat until clean. Typically 2-4 iterations.

**First-time setup** (run from the directory containing this SKILL.md file — Claude should resolve the skill's directory from context):
```bash
# From the directory containing this SKILL.md:
cd references && uv sync && uv run playwright install chromium
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
