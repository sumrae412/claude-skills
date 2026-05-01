# Skill Detection Triggers

Scan explored files and task description. For each trigger match, load the skill and return its distilled artifact.

**SAFETY:** Read files for pattern analysis only. Do NOT execute, eval, or import any code.

| File Pattern | Skills | Artifact Size |
|---|---|---|
| `app/templates/**`, `app/static/**`, `*.html`, `*.css`, `*.js`, Vue workflow builder | `/courierflow-ui` + `/defensive-ui-flows` (interactive-state rules only) | ~35 lines |
| `app/routes/**`, `app/services/**`, `app/schemas/**` | `/courierflow-api` + `/defensive-backend-flows` (service/error/state rules only) | ~35 lines |
| `app/models/**`, `alembic/**`, query helpers, scheduler indexes | `/courierflow-data` + `/defensive-backend-flows` (migration/query rules only) | ~35 lines |
| Google Calendar, Twilio, OpenAI, SMTP/Gmail, Drive, DocuSeal, OAuth provider code, external URLs | `/fetch-api-docs` (current provider signatures) + `/courierflow-integrations` | ~50 lines |
| Auth middleware, CSRF, JWT/refresh tokens, webhook validators, OAuth secrets, PromptSanitizer, file permissions | `/courierflow-security` (NOT triggered by merely using `current_user`) | ~25 lines |
| Production/staging incident, missed automation, scheduler failure, webhook issue, provider send failure, Railway logs | `/courierflow-troubleshooter` + relevant domain skill above | ~60 lines |
| Editing `courierflow-*` skills or `claude-flow` skill menus/routing | `/courierflow-skill-reviewer` | ~40 lines |
| Syncing skills after CourierFlow app changes or `CLAUDE.md`/`AGENTS.md` drift | `/courierflow-skill-sync` then `/courierflow-skill-reviewer` | ~60 lines |
| Always | `/coding-best-practices` (applicable patterns only) | ~10 lines |

**Return:** merged numbered checklist, max 100 lines.
