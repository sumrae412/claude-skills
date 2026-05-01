# Frontend Design Context

## Purpose

Use this reference before UI-affecting planning, implementation, or review.
It converts project-local design instructions and existing UI patterns into
`$design_context` so frontend work starts from the product's real identity
instead of generic AI-generated design habits.

## When To Load

Load this reference when a task touches:

- templates, HTML, CSS, SCSS, static frontend assets
- JavaScript, TypeScript, TSX, JSX, Vue, or Svelte UI code
- visible layout, copy, interaction states, responsive behavior, or visual
  hierarchy
- Phase 4 visual checkpoints or Phase 6 design review

Skip for backend-only, migration-only, infrastructure-only, or pure test
changes with no visible UI behavior.

## Source Priority

Read sources in this order and record the files used in
`design_system.source_files`:

1. Project instructions: `AGENTS.md`, `CLAUDE.md`, skill-local instructions,
   and task-specific user requirements.
2. Project design docs: `PRODUCT.md`, `DESIGN.md`, and `DESIGN.json` when
   present.
3. Existing design tokens and CSS variables.
4. Shared templates, macros, components, layout primitives, and app shells.
5. Adjacent rendered UI when a dev server or browser preview is available.

Do not ask the user to create `PRODUCT.md` or `DESIGN.md` as a blocker. If
they are missing, extract the current system from code and rendered surfaces.

## Product Register

Classify the surface before choosing design tactics:

- `product`: authenticated app UI, dashboards, admin surfaces, settings,
  tables, forms, calendars, sidebars, and workflow tools. Design serves task
  completion. Familiarity, consistency, density, and clear feedback are
  usually virtues.
- `brand`: public marketing, editorial, portfolio, campaign, or landing
  surfaces where design is part of the message. Brand surfaces can carry more
  expressive typography, color, motion, and imagery when project rules allow.

CourierFlow's landlord dashboard, web app, setup/admin screens, workflow
builder, and Google Calendar sidebar are product surfaces by default.

## Design System Extraction

Extract the system that exists before proposing changes:

- color variables and semantic roles
- typography variables, heading/body families, and scale
- spacing, radius, border, elevation, and focus patterns
- shared macros, base templates, components, and button/form conventions
- page header, nav, toolbar, table, card, badge, empty-state, and modal
  patterns
- motion duration/easing and reduced-motion behavior when present

Classify any drift you find:

- `missing-token`: the value should exist centrally but does not
- `one-off-implementation`: a shared pattern exists but was bypassed
- `conceptual-misalignment`: the flow or hierarchy does not match neighboring
  features
- `state-gap`: a required loading, empty, error, disabled, hover, focus,
  active, or success state is missing
- `accessibility-gap`: semantics, labels, focus, keyboard behavior, or
  contrast are insufficient

## Task-Specific Design Brief

For meaningful UI work, produce a task-specific brief before code or durable
mockups:

- primary user action: the one thing the user must do or understand
- surface context: who is using it, how often, and under what pressure
- color strategy: restrained, committed, full palette, or drenched, constrained
  by project tokens
- theme scene sentence: concrete physical-use context that justifies theme,
  density, and contrast
- key states: default, loading, empty, error, success, disabled, and custom
  states
- interaction model: clicks, keyboard flow, confirmation, feedback, and
  recovery
- content requirements: labels, microcopy, dynamic ranges, long text, missing
  values, dates, counts, and overflow
- anti-goals: visual directions, components, or UX shapes that would be wrong

Use the brief to drive Excalidraw state-matrix mockups, implementation tasks,
and Phase 6 review.

## CourierFlow Overrides

For CourierFlow-style projects, project rules override generic Impeccable
advice:

- Preserve centralized Bootstrap/Jinja patterns.
- Prefer `base.html`, `macros/ui_macros.html`, and design-system CSS before
  adding new markup or styles.
- Use established page header patterns, title blocks, buttons, badges, color
  variables, and layout wrappers.
- Do not hardcode colors when design-system variables exist.
- Do not create one-off page headers, local button systems, or page-specific
  style vocabularies.
- Do not override the established Inter/Poppins split unless project
  instructions change.
- Keep landlord control, visible failure states, and confirmation paths clear.

Generic anti-pattern rules are useful prompts, not authority. A finding matters
when it violates project rules, accessibility, responsive behavior, state
coverage, or the task's user flow.

## Output Shape

Emit `$design_context` using `contracts/design-context.schema.md`. Keep it
compact enough to pass to Phase 5 implementers and Phase 6 reviewers without
raw transcripts or unrelated visual exploration.
