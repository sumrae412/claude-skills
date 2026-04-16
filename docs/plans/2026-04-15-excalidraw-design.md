# Excalidraw Skill Design

**Date:** 2026-04-15
**Source:** [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill)
**Status:** Approved

## Goal

General-purpose skill for generating Excalidraw diagrams from natural language. Produces `.excalidraw` JSON files with a Playwright-based render-validate loop for visual QA.

## Structure

Progressive disclosure — thin router + lazy-loaded references.

```
excalidraw/
├── SKILL.md                          # Router (~800 tokens)
├── references/
│   ├── design-methodology.md         # Visual patterns, shapes, layout
│   ├── json-schema.md                # Excalidraw JSON format spec
│   ├── element-templates.md          # Copy-paste JSON per element type
│   ├── color-palette.md              # Semantic colors (customizable)
│   ├── render_excalidraw.py          # Playwright PNG renderer
│   ├── render_template.html          # Browser rendering template
│   └── pyproject.toml                # Python deps (playwright)
```

## SKILL.md Router (~800 tokens)

Always-resident content:

1. **Frontmatter** — name, description, triggers
2. **Core philosophy** — "Diagrams argue, not display" (brief)
3. **Depth assessment** — simple vs. comprehensive decision criteria
4. **Workflow:**
   - Step 1: Design — Read `design-methodology.md`, map concepts to patterns
   - Step 2: Generate — Read `json-schema.md` + `element-templates.md` + `color-palette.md`, build section-by-section
   - Step 3: Validate — Read `render_excalidraw.py`, render → view → fix loop
5. **Setup** — `uv sync && uv run playwright install chromium`
6. **Quality checklist** — ~10 items (condensed from source's 27)

## Reference Files

### design-methodology.md
Cherry-picked from source SKILL.md:
- Visual pattern library (fan-out, convergence, tree, timeline, spiral, assembly line, side-by-side) with ASCII sketches
- Shape meaning table (concept → shape → rationale)
- Container vs. free-floating text decision table
- Layout principles (scale hierarchy, whitespace, flow direction)
- Evidence artifacts table (code snippets, JSON examples, UI mockups)
- Omitted: verbose comparisons, repeated philosophy, multi-zoom architecture

### json-schema.md
Ported as-is. Element types, common properties, text properties, arrow bindings, rectangle roundness.

### element-templates.md
Ported as-is. JSON templates for: free-floating text, line, marker dot, rectangle, text-in-shape, arrow.

### color-palette.md
Ported as-is. Semantic shape colors, text hierarchy, evidence artifact colors. Customizable per-project.

### Render pipeline
Ported as-is: `render_excalidraw.py`, `render_template.html`, `pyproject.toml`.

## Changes From Source

| Area | Source | This Skill |
|------|--------|------------|
| Structure | Single 4K-token SKILL.md | Router + lazy-loaded references |
| Methodology | Inline | Extracted to design-methodology.md |
| Tone | Repetitive emphasis | Direct, stated once |
| Quality checklist | 27 items | ~10 |
| Multi-zoom | Full section | Dropped |
| Large diagram strategy | Detailed section | Condensed into Step 2 |
| Render path | Hardcoded .claude/skills/ | Relative from skill dir |
