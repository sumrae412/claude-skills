# Source & provenance

This skill was imported from Vercel's open-source agent-skills collection and adapted to the Claude progressive-disclosure skill format.

- **Upstream:** `vercel-labs/skills` → `vercel-react-best-practices`
- **Originally created by:** [@shuding](https://x.com/shuding) at [Vercel](https://vercel.com)
- **License:** MIT (preserved; see frontmatter `license: MIT`)
- **Imported:** 2026-06-17
- **Local landing point:** discovered as orphan noise in a `doc-graph` run over `courierflow_beta/.agents/skills/`; the React-performance content was assessed useful for the React 19 + Vite stack and promoted into the canonical skills repo.

## What was kept

- `SKILL.md` — router/index (adapted: added an "Applicability across stacks" section distinguishing any-React rules from Next/RSC-only rules, since our primary consumer is a Vite SPA, not Next.js).
- `rules/` — all 72 per-rule files verbatim, including `_sections.md` (section metadata) and `_template.md` (authoring template).

## What was dropped on import

- `AGENTS.md` — the upstream Cursor-format compiled monolith (~3.8k lines). Redundant with `rules/` under Claude's progressive-disclosure model and a context-budget risk if ever resident. Regenerable from `rules/` via the upstream `pnpm build`.
- `README.md` — replaced by this file plus `SKILL.md`.
- `src/`, `metadata.json`, `test-cases.json`, `package.json` — upstream build tooling, not needed to consume the knowledge.

## Safety

The `rules/` content is pure markdown guidance (rationale + code examples). A scan for executable/network/prompt-injection patterns at import time returned clean.

## Updating

To pull newer upstream rules, copy the changed files from `vercel-labs/skills` into `rules/`, then update the Quick Reference index in `SKILL.md` if rule names changed. Do not re-introduce `AGENTS.md` or the build tooling.
