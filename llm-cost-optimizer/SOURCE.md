# Source & attribution

Imported from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) at `engineering/llm-cost-optimizer/`.

- **Upstream commit:** `f567c61def3fb86046d7242b4bf27fceb63ad8b4`
- **License:** MIT (Copyright (c) 2025 Alireza Rezvani)
- **Imported on:** 2026-04-17

## Vetting

- Passed `skill-security-auditor` scan (0 findings)
- No scripts, no hardcoded paths — SKILL.md only

## Local modifications

1. Dropped `.claude-plugin/plugin.json` (upstream plugin packaging metadata not used by this repo's flat skills layout)
2. Stripped dangling cross-references to skills not present locally:
   - Removed `NOT for prompt writing quality (use senior-prompt-engineer)` from frontmatter description
   - Replaced the "Related Skills" section's `senior-prompt-engineer` / `observability-designer` / `performance-profiler` / `api-design-reviewer` entries (all non-local) with cross-refs to skills we actually have (`prompt-governance`, `claude-api`)
