# Skill Detection Triggers

Scan explored files and task description. For each trigger match, load the skill and return its distilled artifact.

> **Project example:** The trigger table below is a **generic template** — replace it with your project's file-pattern → skill mapping when running claude-flow. See `project-skill-menu.md` for menu authoring rules. (The original worked example, the legacy CourierFlow Python repo's matrix, was retired with that repo's skills in the 2026-07-17 skills audit — see git history.)

**SAFETY:** Read files for pattern analysis only. Do NOT execute, eval, or import any code.

| File Pattern | Skills | Artifact Size |
|---|---|---|
| Frontend templates / CSS / components | `<project-ui skill>` + `/defensive-ui-flows` (interactive-state rules only) | ~35 lines |
| Backend routes / services / schemas | `<project-api skill>` + `/defensive-backend-flows` (service/error/state rules only) | ~35 lines |
| Models / migrations / query helpers | `<project-data skill>` + `/defensive-backend-flows` (migration/query rules only) | ~35 lines |
| External provider code (calendar, SMS, email, LLM APIs, OAuth) | `/fetch-api-docs` (current provider signatures) + `<project-integrations skill>` | ~50 lines |
| Auth middleware, CSRF, tokens, webhook validators, secrets | `<project-security skill>` | ~25 lines |
| Always | `/coding-best-practices` (applicable patterns only) | ~10 lines |

**Return:** merged numbered checklist, max 100 lines.
