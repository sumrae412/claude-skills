---
name: html-spec
description: Use when authoring an implementation plan, PRD, design doc, or brainstorm artifact that would beat its Markdown equivalent by inlining visual mockups, interactive elements, or component examples — i.e., specs where a long flat-text outline would lose human engagement. Triggers on "draft an HTML spec", "plan in HTML", "PRD with mockups", "visual implementation plan", "spec with mockups", "design system file", "living design system", "build a throwaway editor for this plan", "micro-UI to edit my plan", "interactive plan", "spec I can click through", or any planning/scoping/brainstorm request where mockups + descriptions + risk callouts in one document would beat a text outline. Composes with [`writing-plans`](../writing-plans/SKILL.md) (HTML output variant), [`prd`](../prd/SKILL.md) (HTML output variant), [`claude-flow`](../claude-flow/SKILL.md) Phase 4 (visual design-doc mode), and [`excalidraw-canvas`](../excalidraw-canvas/SKILL.md) (Excalidraw for whiteboard-style diagrams; html-spec for full single-page artifacts with mockups + copy + risk + code). Pattern originates from Thariq Shihipar's HTML-as-spec workflow at Anthropic ([source](https://www.chatprd.ai/how-i-ai/claude-code-anthropic-thariq-shihipar-on-replacing-markdown-with-html)).
user-invocable: true
metadata:
  hermes:
    tags: [planning, specs, prd, html, visual, design-system, brainstorming]
    related_skills: [writing-plans, prd, claude-flow, excalidraw-canvas]
---

# HTML Spec

## What this produces

A single self-contained `.html` file at `docs/specs/<slug>.html` (or the project's analog — `docs/plans/<slug>.html`, `docs/prds/<slug>.html`) that combines mockups, descriptions, risk callouts, code snippets, and design-system fragments in one artifact. The file is human-readable in a browser, machine-readable by Claude on later passes, and editable either directly or via a throwaway micro-UI (Workflow 2).

**Announce at start:** "I'm using the html-spec skill to author the spec as a single-page HTML artifact."

## When to use HTML over Markdown

| Use Markdown | Use HTML |
|---|---|
| Plan fits in one screen of text | Plan exceeds ~1000 lines or has 5+ distinct components |
| Linear sequence of bullets/steps | Multiple UI screens or flows to visualize |
| No mockups needed | Mockups, layouts, or interactive elements would clarify intent |
| Quick decision doc | Long-lived spec that stakeholders will revisit |
| Audience is engineers only | Audience includes PM/designer/non-technical reviewer |

Default to Markdown when in doubt — HTML is the exception, not the rule. The choice is about **human comprehension**, not about what Claude prefers (Claude is fine with either).

## The compute-allocator framing

Per Thariq: "only 1% of tokens [generated] end up in production code. The other 99% are spent on rich, beautiful, sometimes disposable scaffolding: plans, custom interfaces, status updates, design systems." Treat HTML specs as scaffolding investment — they make the 1% that ships *exactly what it needs to be*. If a spec doesn't change a downstream decision, the format choice doesn't matter; Markdown is cheaper. If it does, the extra tokens for HTML mockups and visual context earn their keep.

This skill is the "is the spec worth scaffolding" gate. Three workflows below, used independently or composed.

---

## Workflow 1 — Brainstorm/plan in HTML

**When:** First pass on a multi-screen feature, PRD, or implementation plan where the reader will benefit from inline mockups + descriptions + risk callouts.

**Prompt template:**
```
Create an HTML file at <path/to/spec.html> that visualizes the plan for <feature>.
Include for each major component:
- A mockup or layout sketch (inline SVG, divs with placeholder styling, or
  rendered UI fragments)
- A 2-3 sentence description of intent and scope
- A risk callout (what could go wrong / what we're betting on)
- Code excerpts or interface contracts where relevant
Maximum context, single file, self-contained CSS, no external assets.
I trust you on the visual treatment — make it scannable and engaging.
```

**Key principle:** give constraint + leave room. The "I trust you" framing is load-bearing — under-constrained HTML produces richer artifacts than over-constrained ones, in Thariq's experience.

**Output evidence:** open the file in a browser. The user should be able to skim it in 60 seconds and know what's being proposed. If they can't, the spec is too dense (split it) or the mockups are decorative (replace with diagrams that show real layout).

## Workflow 2 — Throwaway micro-UI for editing

**When:** Part of a plan is hard to edit as raw HTML — a decision table, a state machine, a config tree, a rule set. Editing the HTML directly is slower than building a custom UI to edit it.

**Prompt template:**
```
The <section name> in <spec.html> is hard to edit as raw HTML. Build a
disposable micro-UI as <slug>-editor.html that lets me edit just that
section with input fields / dropdowns / buttons / sliders appropriate to
the data shape. Show me the proposed interface before implementing.
When I'm done editing, the page should export the result as
{Markdown | HTML fragment | JSON | YAML} I can paste back into the spec.
```

**Discipline:**
- The micro-UI is **disposable**. Don't add it to git. Save under `docs/specs/_editors/<slug>-editor.html` and gitignore the `_editors/` dir, OR keep it in `/tmp/` and don't save it at all.
- Export format matches what the spec needs back. Markdown for table cells, HTML fragment for UI mockups, JSON/YAML for config.
- Don't reuse — generate a fresh editor for each editing problem. The "abundance mindset" is that generating a new tool is cheaper than maintaining a reusable one.

## Workflow 3 — Living design system HTML

**When:** A project has visual conventions (color palette, typography, spacing, component patterns) that recur across multiple specs or sessions. The design system file is the single source of truth for Claude + humans + non-technical stakeholders.

**Build steps:**
```
1. Point Claude at the project source:
   "Analyze app/static/css/, app/templates/, and existing UI screenshots
    in docs/. Extract the design DNA — color tokens, typography scale,
    spacing, component patterns, interaction conventions."

2. Generate the artifact:
   "Build docs/design-system.html — a single self-contained page showing:
    - Color palette (swatches with hex + token name + usage notes)
    - Typography scale (real text samples at each size)
    - Spacing scale (visual rulers)
    - Component examples (buttons, cards, modals, tables) with interactive
      knobs for variant exploration
    - Voice/copy conventions if relevant"

3. Use the file as Claude context on future work:
   - Add a reference from CLAUDE.md or the relevant project skill
   - Pass it as a Read in new sessions before UI-shaped work
```

**Maintenance:** the design system HTML drifts. Schedule a quarterly regen — `Re-analyze app/static/css/ and update docs/design-system.html to match`. Treat drift as the cost of the pattern; the artifact is still cheaper than asking "what color is the primary button?" every session.

**Secondary win:** non-technical stakeholders can open the file and see every component without bugging an engineer.

---

## File conventions

| Workflow | Path | Git tracked? |
|---|---|---|
| Plan/PRD in HTML | `docs/plans/YYYY-MM-DD-<slug>.html` or `docs/prds/<slug>.html` | yes |
| Spec artifact | `docs/specs/<slug>.html` | yes |
| Throwaway editor | `docs/specs/_editors/<slug>-editor.html` or `/tmp/` | **no — gitignore** |
| Living design system | `docs/design-system.html` | yes |

For CourierFlow specifically: `docs/plans/` and `docs/prds/` already exist; add `docs/specs/` if a non-plan/non-PRD spec is needed. The `_archived/` rule (Boundary 1) still applies.

## Composition with other skills

- **[`writing-plans`](../writing-plans/SKILL.md):** Default to Markdown. Switch to html-spec when the plan exceeds ~1000 lines or has multiple UI screens. Cross-link from the Markdown plan to the HTML spec (e.g. `See docs/specs/<slug>.html for the visual layout`).
- **[`prd`](../prd/SKILL.md):** PRDs default to Markdown for the `$requirements` contract mapping. Use html-spec for PRDs heavy in user-facing UI — write the contract in Markdown at the top of the file, embed mockups via `<iframe>` or inline below.
- **[`claude-flow`](../claude-flow/SKILL.md) Phase 4 (Architecture):** The Step 2.5 "Offer Visual Mockup" gate is where html-spec triggers. If the executor would otherwise emit ASCII diagrams + bullets, offer to switch the design doc to HTML.
- **[`excalidraw-canvas`](../excalidraw-canvas/SKILL.md):** Excalidraw for whiteboard-style architecture diagrams + free-form sketches. html-spec for full single-page specs (mockups + copy + risk + code in one artifact). They compose — embed Excalidraw exports as SVG inside an html-spec.
- **`superpowers:brainstorming`** (plugin skill — no local path): First brainstorm pass can be HTML if "show me eight different shapes of this feature with mockups" beats "list eight ideas as bullets."

## Anti-patterns

- **Decorative HTML.** Mockups that don't show real layout, color palettes that aren't used downstream, animations on a planning doc. If a visual element doesn't change a reader's mental model, it's noise.
- **HTML for short plans.** A 200-line plan doesn't need HTML. The format earns its keep when the alternative is a 1000+ line Markdown wall.
- **Hand-maintaining the editor.** Workflow 2's micro-UI is disposable. If you find yourself updating it for a second edit pass, regenerate from scratch — that's usually faster and produces a better-fit UI for the new editing problem.
- **External assets in the HTML file.** Self-contained CSS, inline SVG, no `<link>` or `<script src>` to anywhere. The spec must open in a browser with no setup, ideally years from now.

## Source

Workflow patterns derived from:
- Thariq Shihipar (Anthropic, Claude Code team) — [Replacing Markdown with HTML for AI specs](https://www.chatprd.ai/how-i-ai/claude-code-anthropic-thariq-shihipar-on-replacing-markdown-with-html) (May 2026)
- Companion video: [Why this Claude Code engineer uses HTML files as AI specs](https://www.youtube.com/watch?v=Qrpm7E80wQ0)
