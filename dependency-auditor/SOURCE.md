# Source & attribution

Imported from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) at `engineering/dependency-auditor/`.

- **Upstream commit:** `f567c61def3fb86046d7242b4bf27fceb63ad8b4`
- **License:** MIT (Copyright (c) Alireza Rezvani)
- **Imported on:** 2026-04-17

## Vetting

- Passed `skill-security-auditor` scan (0 findings; 21 files, 3 scripts, 5 markdown)
- No `.claude-plugin/plugin.json` to strip
- No dangling cross-references to non-local skills
- Python scripts verified as self-contained local CLIs: no network calls, no API keys, no hardcoded paths; `subprocess` imported in `dep_scanner.py` and `upgrade_planner.py` but never invoked (dead import)

## Local modifications

- **Description tightened.** Upstream `description:` was literally the title string (`"Dependency Auditor"`), which did not support skill routing. Rewrote to describe trigger conditions and language coverage. Body content is verbatim from upstream.

SKILL.md, README.md, references, scripts, assets, expected_outputs, test-inventory.json, and test-project are verbatim from upstream.
