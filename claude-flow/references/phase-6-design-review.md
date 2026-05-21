# Phase 6 Design Review

Load this reference only when UI-affecting files changed:

- templates
- CSS / SCSS
- HTML
- JS / TS / TSX

## Purpose

Design review tests the live rendered UI, not just the code.

Preferred tooling:

- Claude Preview
- Playwright MCP

Fallback:

- code-only review if the dev server cannot start

## Reviewer

| Agent | `subagent_type` | Focus |
|-------|-----------------|-------|
| Design Reviewer | `general-purpose` | Visual consistency, responsiveness, accessibility, interaction quality |

## Required Checks

1. **Interaction & User Flow**
   - execute the primary user flow
   - test hover / active / disabled states
   - verify destructive confirmations
   - assess perceived performance
2. **Responsiveness**
   - desktop: `1440px`
   - tablet: `768px`
   - mobile: `375px`
   - no overflow, no horizontal scroll, adequate touch targets
3. **Visual Polish**
   - alignment
   - spacing consistency
   - typography hierarchy
   - palette adherence
4. **Accessibility (WCAG 2.1 AA)**
   - keyboard navigation
   - visible focus states
   - Enter / Space activation
   - semantic HTML
   - labels / alt text / contrast
5. **Robustness**
   - invalid inputs
   - content overflow
   - loading / empty / error states

## Scored Design Audit

Score each dimension 0-4. Use concrete evidence from the rendered UI, source
files, or automated detector output.

| Dimension | 0 | 2 | 4 |
|-----------|---|---|---|
| Accessibility | Blocks keyboard or screen-reader use | Partial semantics or contrast gaps | WCAG AA behavior is covered |
| Performance | Obvious jank, layout thrash, or heavy assets | Some unbounded effects or asset issues | Fast interactions and bounded paint work |
| Theming and design-token usage | Hard-coded visual values dominate | Tokens exist but are inconsistently used | Project tokens and shared patterns are followed |
| Responsive behavior | Desktop-only or horizontal scroll | Works with rough touch or overflow edges | Desktop, tablet, and mobile are structurally sound |
| Anti-patterns and design-system drift | Generic AI UI or local-system violations | Minor drift with clear fixes | Distinctive, project-aligned, no material drift |

Report the total as `Design Audit Score: N/20`. A low score is not itself a
blocker; Blocker and High-Priority findings are based on user impact,
accessibility, responsiveness, and project hard-rule violations.

## Drift Classification

For each finding, classify the root cause:

- `missing-token` — the value should exist centrally but does not
- `one-off-implementation` — a shared macro/component/pattern exists but was
  bypassed
- `conceptual-misalignment` — the flow, information architecture, or hierarchy
  does not match neighboring features
- `state-gap` — a required loading, empty, error, success, disabled, hover,
  focus, or active state is missing
- `accessibility-gap` — semantics, labels, focus, keyboard behavior, or
  contrast are insufficient

Use the classification to choose the fix: add/reuse a token, swap to the shared
pattern, rework the flow, add the missing state, or fix the accessibility
contract. Do not patch symptoms when the root cause is design-system drift.

## Impeccable Detector

If `impeccable-detector` was selected by the reviewer registry, run its
resolved runner script against the changed UI paths. Treat findings as
advisory unless they overlap with project hard rules, WCAG AA, broken
responsiveness, or visible user-flow regressions.

Project-local UI rules outrank generic anti-pattern rules. For CourierFlow,
centralized Jinja/Bootstrap patterns, design-system variables, page-header
standards, and established typography rules are authoritative.

## Triage

Use:

- `[Blocker]`
- `[High-Priority]`
- `[Medium-Priority]`
- `[Nitpick]`

Blocker and High-Priority findings enter the same recheck loop as code-review
findings.
