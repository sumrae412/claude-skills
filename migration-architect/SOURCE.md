# Source & attribution

Imported from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) at `engineering/migration-architect/`.

- **Upstream commit:** `f567c61def3fb86046d7242b4bf27fceb63ad8b4`
- **License:** MIT (Copyright (c) Alireza Rezvani)
- **Imported on:** 2026-04-17

## Vetting

- Passed `skill-security-auditor` scan (0 findings; 24 files, 3 scripts, 5 markdown)
- No `.claude-plugin/plugin.json` to strip
- No dangling cross-references to non-local skills
- Python scripts verified as self-contained local CLIs: no network calls, no API keys, no hardcoded paths, no `subprocess` calls

## Local modifications

- **Description tightened.** Upstream `description:` was literally the title string (`"Migration Architect"`), which did not support skill routing. Rewrote to describe migration patterns and trigger conditions. Body content is verbatim from upstream.

SKILL.md, README.md, references, scripts, assets, and expected_outputs are verbatim from upstream.
