# Source & attribution

Imported from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) at `engineering/prompt-governance/`.

- **Upstream commit:** `f567c61def3fb86046d7242b4bf27fceb63ad8b4`
- **License:** MIT (Copyright (c) 2025 Alireza Rezvani)
- **Imported on:** 2026-04-17

## Vetting

- Passed `skill-security-auditor` scan (0 findings)
- No scripts, no hardcoded paths — SKILL.md only

## Local modifications

1. Dropped `.claude-plugin/plugin.json` (upstream plugin packaging metadata not used by this repo's flat skills layout)
2. Stripped dangling cross-references to skills not present locally:
   - Removed `NOT for writing or improving individual prompts (use senior-prompt-engineer)` from frontmatter description
   - Replaced non-local "Related Skills" entries (`senior-prompt-engineer`, `ci-cd-pipeline-builder`, `observability-designer`) with a pointer to the local `prompt-optimization` skill for adjacent scope
