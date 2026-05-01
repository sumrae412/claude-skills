# $design_context
<!-- Produced by: Phase 0/Phase 4 UI preflight | Consumed by: Phases 4, 5, 6 -->

Carries project-local design rules and a task-specific UI brief for
frontend-affecting work. Project instructions remain authoritative: if
`AGENTS.md`, `CLAUDE.md`, or a local design system conflicts with generic
frontend-design guidance, the project-local rule wins.

`DESIGN.md`, `DESIGN.json`, and `PRODUCT.md` are useful inputs when present,
but they are optional. If no dedicated design-context file exists, extract the
context from project instructions, existing tokens, templates, CSS variables,
shared components, adjacent screens, and rendered UI when available.

## Schema

```yaml
project_identity:
  product_name: string
  product_scope: string
  register: product | brand

design_system:
  source_files: string[]
  tokens:
    colors: string[]
    typography: string[]
    spacing: string[]
    radii: string[]
  component_patterns: string[]
  centralized_style_rules: string[]

task_design_brief:
  primary_user_action: string
  surface_context: string
  color_strategy: restrained | committed | full_palette | drenched
  theme_scene_sentence: string
  key_states: string[]
  interaction_model: string
  content_requirements: string[]
  anti_goals: string[]

verification:
  required_viewports: string[]
  required_states: string[]
  anti_pattern_checks: string[]
```

## Field Notes

| Field | Purpose |
|-------|---------|
| `project_identity.product_name` | Product or app name from project docs. |
| `project_identity.product_scope` | One-sentence boundary for what the product is and is not. |
| `project_identity.register` | `product` for task-oriented app UI; `brand` for marketing/editorial surfaces. |
| `design_system.source_files` | Files actually read to derive design rules. |
| `design_system.tokens` | Names and values for colors, type, spacing, and radii that are already established. |
| `design_system.component_patterns` | Existing shared components, macros, templates, or component APIs to reuse. |
| `design_system.centralized_style_rules` | Rules that prevent one-off style drift. |
| `task_design_brief.primary_user_action` | The main thing the user must do or understand on this surface. |
| `task_design_brief.surface_context` | Who is using the surface, where, and under what pressure. |
| `task_design_brief.color_strategy` | Per-surface color commitment, constrained by project tokens. |
| `task_design_brief.theme_scene_sentence` | Concrete ambient-use sentence that justifies light/dark/density decisions. |
| `task_design_brief.key_states` | Default, loading, empty, error, success, disabled, or custom states to implement. |
| `task_design_brief.interaction_model` | How the user moves through the flow and receives feedback. |
| `task_design_brief.content_requirements` | Copy, labels, dynamic data ranges, and overflow risks. |
| `task_design_brief.anti_goals` | Explicit wrong directions and prohibited visual patterns. |
| `verification.required_viewports` | Breakpoints or viewport widths to test. |
| `verification.required_states` | State matrix expected in code and visual checks. |
| `verification.anti_pattern_checks` | Anti-patterns relevant to this project and task. |

## Notes

- Do not synthesize a new brand identity when the project already has one.
- For product UI, earned familiarity is usually a feature. Standard controls,
  predictable grids, and dense scannable information often beat novelty.
- Generic anti-pattern checks are advisory unless they overlap with local hard
  rules, accessibility, responsiveness, or user-flow correctness.
