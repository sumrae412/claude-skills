# CourierFlow Skill Review Checklist

## Structure

- Directory name matches `name`.
- `SKILL.md` exists.
- Frontmatter has `name` and `description`.
- Description is specific, third-person, and under 1024 characters.
- Optional references are one level deep.
- No README/CHANGELOG/installation docs inside the skill folder.

## Trigger Quality

The description should cover:

- user intent: build, fix, review, troubleshoot, sync, secure
- technical context: routes, services, models, migrations, templates, webhooks
- project context: CourierFlow, landlord workflow, calendar automation

Flag vague descriptions like "helps with backend" or descriptions that overlap
without a distinction.

## Scope

Each skill should own one dominant surface:

- UI
- API/service layer
- data/migrations
- integrations
- security
- troubleshooting
- skill maintenance

If a skill owns multiple unrelated surfaces, split it. If two skills duplicate
the same checklist, move shared rules into a shared reference or keep one rule
and cross-link.

## Progressive Disclosure

- `SKILL.md` should explain when and how to use the skill.
- Detailed checklists belong in `references/`.
- Do not paste the whole CourierFlow product constitution into every skill.
- Put volatile commands and provider details in references so they can be
  synced independently.

## CourierFlow Rule Drift

Check against current project instructions for:

- landlord creates calendar event -> confirmed workflow automation scope
- no action without landlord confirmation
- user scoping
- async-first I/O
- routes thin, services thick
- no `db.commit()` in services
- PromptSanitizer for AI
- Google Calendar sync direction rules
- PostgreSQL-first scheduler and locks
- UI design-system centralization

## Phase 5 Selection Quality

For a task title or PR summary, verify the forced menu would select one skill.
If two skills tie, improve descriptions or add a disambiguating example.

Known preferred routing:

- templates, CSS, workflow builder, dashboard -> `courierflow-ui`
- routes, services, request/response behavior -> `courierflow-api`
- models, Alembic, query shape, scheduler indexes -> `courierflow-data`
- Google/Twilio/OpenAI/Drive/Gmail/DocuSeal -> `courierflow-integrations`
- auth, permissions, CSRF, secrets, prompt privacy -> `courierflow-security`
- prod symptom, logs, missed automation -> `courierflow-troubleshooter`
