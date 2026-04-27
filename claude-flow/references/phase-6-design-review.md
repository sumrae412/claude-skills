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

## Triage

Use:

- `[Blocker]`
- `[High-Priority]`
- `[Medium-Priority]`
- `[Nitpick]`

Blocker and High-Priority findings enter the same recheck loop as code-review
findings.
