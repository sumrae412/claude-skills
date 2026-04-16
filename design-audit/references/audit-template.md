# Audit Output Template

Use this structure when presenting findings.

```
DESIGN AUDIT RESULTS

Overall Assessment: [1-2 sentences on the current state]

────────────────────────────────────────────

PHASE 1 — Critical
(Hierarchy, usability, responsiveness, consistency issues that actively hurt UX)

- [Screen/Component]: [What's wrong] -> [What it should be] -> [Why this matters]
- [Screen/Component]: [What's wrong] -> [What it should be] -> [Why this matters]

Review: [Why these are highest priority]

────────────────────────────────────────────

PHASE 2 — Refinement
(Spacing, typography, color, alignment, iconography that elevate the experience)

- [Screen/Component]: [What's wrong] -> [What it should be] -> [Why this matters]
- [Screen/Component]: [What's wrong] -> [What it should be] -> [Why this matters]

Review: [Why this sequencing]

────────────────────────────────────────────

PHASE 3 — Polish
(Micro-interactions, transitions, empty/loading/error states, dark mode)

- [Screen/Component]: [What's wrong] -> [What it should be] -> [Why this matters]
- [Screen/Component]: [What's wrong] -> [What it should be] -> [Why this matters]

Review: [Expected cumulative impact]

────────────────────────────────────────────

DESIGN SYSTEM UPDATES REQUIRED

- [New tokens, colors, spacing values, typography changes, or component additions]
- These must be approved and added to design system before implementation

────────────────────────────────────────────

IMPLEMENTATION NOTES

Precision standard — a build agent must execute without design interpretation:

BAD:  "Make the cards feel softer"
GOOD: "CardComponent border-radius: 8px -> 12px per token border-radius-lg"

BAD:  "Improve the spacing"
GOOD: "DashboardHeader margin-bottom: 16px -> 24px (spacing-lg)"

BAD:  "The button needs more contrast"
GOOD: "PrimaryButton background: #6B7280 -> #2563EB (color-brand-primary).
       Contrast ratio: 3.8:1 -> 8.6:1 (WCAG AAA)"
```

## Rules

1. Every finding: **what's wrong -> what it should be -> why it matters**
2. Implementation notes reference design system tokens, not raw values
3. If a new token is needed, list it in DESIGN SYSTEM UPDATES first
4. No vague language. No "feels" without a measurable change.
5. Phase assignment:
   - Phase 1: Actively hurts usability or breaks consistency
   - Phase 2: Below professional standard but functional
   - Phase 3: Functional but not yet premium
