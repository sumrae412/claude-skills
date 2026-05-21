# CourierFlow Skill Sync Workflow

## Inputs

Required:

- CourierFlow app repository path
- comparison base, usually `origin/main` or the last synced commit/tag

Optional:

- specific changed file list
- specific skill names to refresh

## File Routing

| Changed files | Skill |
| --- | --- |
| `app/templates/**`, `app/static/**`, Vue/workflow builder JS | `courierflow-ui` |
| `app/routes/**`, `app/services/**`, `app/schemas/**` | `courierflow-api` |
| `app/models/**`, `alembic/**`, query helpers | `courierflow-data` |
| Calendar, Twilio, OpenAI, SMTP, Drive, Gmail, DocuSeal clients | `courierflow-integrations` |
| auth, CSRF, webhook validation, prompt sanitizer, file permissions | `courierflow-security` |
| deploy, logs, scheduler incidents, operational runbooks | `courierflow-troubleshooter` |
| `CLAUDE.md`, `AGENTS.md`, skill menu/routing docs | all affected skills |

## Diff Process

```bash
git diff --name-only <base>...HEAD
git diff --stat <base>...HEAD
```

For each changed file group:

1. inspect only the relevant files
2. identify new or changed rules an agent must know
3. update the smallest owning reference
4. update `SKILL.md` description only if trigger conditions changed

## What To Extract

Extract durable rules:

- new architecture boundary
- new command or verification requirement
- new provider behavior
- new security invariant
- new UI centralization pattern
- new recurring bug pattern

Do not extract:

- one-off implementation details
- temporary migration notes
- line-by-line source summaries
- obsolete commands
- details already obvious from file names

## Validation

After edits:

```bash
python3 claude-flow/scripts/lint_workflow.py --json
python3 -m pytest -q claude-flow/scripts
```

If only standalone skills changed and workflow docs did not, run a lightweight
frontmatter/path validation instead.
