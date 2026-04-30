# Source & attribution

Imported from [ibelick/ui-skills](https://github.com/ibelick/ui-skills) at `skills/fixing-accessibility/`.

- **Upstream commit:** `df4eb34c5dee830e8e36490d6fde3451c187339b` (2026-02-19)
- **Upstream license:** MIT (Copyright (c) 2025 Julien Thibeaut / ibelick)
- **Imported on:** 2026-04-29

## Vetting

- Passed `skill-security-auditor` scan (0 findings — no scripts, markdown-only)
- No code execution, network calls, dependency declarations, or filesystem writes — pure reference skill

## Why this one (and not the rest of `ui-skills`)

`ibelick/ui-skills` ships four skills (`baseline-ui`, `fixing-accessibility`, `fixing-metadata`, `fixing-motion-performance`). Imported only `fixing-accessibility`:

- **baseline-ui** — hard-coded to React + `motion/react` + Base UI/Radix; CourierFlow uses Jinja + Alpine.js (stack mismatch)
- **fixing-metadata** — SEO/OG/JSON-LD; CourierFlow is auth-walled SaaS, claude-skills/claude_flow ship no public pages (no domain surface)
- **fixing-motion-performance** — minimal animation in either project (low ROI)

`fixing-accessibility` is stack-agnostic — ARIA/keyboard/focus/semantics rules apply to any HTML output (React, Jinja, server-rendered templates).

## Local modifications

- Added a "Framework-agnostic" note in `## how to use` calling out non-React stacks (Jinja, Alpine.js) and pointing to `defensive-ui-flows` for state/feedback patterns
- Added `## related skills` section linking `defensive-ui-flows`, `design-audit`, `design:accessibility-review`, `typography`
- Replaced curly-quote `"click here"` with straight quote (downstream-parser survivability for ATS / plain-text contexts)

SKILL.md body rules and examples are otherwise verbatim from upstream.
