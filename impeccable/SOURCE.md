# Source: impeccable bundle

- **Author:** pbakaus
- **Repo:** https://github.com/pbakaus/impeccable
- **Commit:** d2ab4ddee6fa63002fae680652b5fbd31735e280
- **License:** Apache-2.0
- **Imported:** 2026-06-24

## Imported sub-skills (28 reference files)

Build: craft, shape, init, document, extract
Evaluate: critique, audit
Refine: polish, bolder, quieter, distill, harden, onboard
Enhance: animate, colorize, typeset, layout, delight, overdrive
Fix: clarify, adapt, optimize
Iterate: live
Register references: brand, product
Design system references: interaction-design, codex
Tooling: hooks

## Adaptations

- Frontmatter added per claude-skills house style
- `{{scripts_path}}`, `{{command_prefix}}`, `{{command_hint}}`, `{{model}}` placeholders resolved
- Internal reference links updated: `reference/` → `references/`
- XML tags (`<codex>`, `<gemini>`) stripped, content preserved
- Added "See also" cross-references to sibling skills
- `allowed-tools: Bash(npx impeccable *)` and `argument-hint` removed (claude-skills convention)

## Dedupe notes

- `impeccable audit` overlaps conceptually with `design-audit` (both do UI quality review) — kept distinct: audit is technical checks (a11y, perf, responsive); design-audit is heuristic UX scoring
- `impeccable polish` overlaps with `design-audit`'s polish phase — kept distinct: polish is final pre-ship pass; design-audit is structured rubric review
- `impeccable layout` overlaps with `fixing-motion-performance` on spacing/rhythm — complementary, not duplicate
