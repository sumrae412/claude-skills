# Project Skill Menu

The Phase 5 forced-selection menu and Phase 0 trigger matrix are project-specific —
the claude-flow workflow itself is generic, but the menu of project skills the
executor selects from must match the host repo's codebase and skill catalog.

The default menu shipped here targets **CourierFlow** (the project this skill set
was authored against). To use claude-flow inside a different project:

1. Copy this file into your project and rewrite the menu/triggers below.
2. Point Phase 5's forced-selection block at your project's menu (replace the
   `Available skills` list in `phases/phase-5-implementation.md` §Subagent Skill
   Loading).
3. Point Phase 0 Step 3's classifier (in `phases/phase-0-context.md`) at your
   project's triggers.
4. Replace `references/skill-triggers.md` with your project's file-pattern table.

A future revision will move the menu into `workflow-profiles.json` as a
`project_skill_menu` field so the phase files stay project-agnostic by default;
until then, the default menu in those two phase files is the
CourierFlow-flavored example.

---

## Default Menu (CourierFlow)

**Phase 5 forced-selection (5 skills, domain-coherent):**

- `courierflow-ui` — Frontend code: Jinja templates, CSS, Vue workflow builder
  pages, dashboards, calendar/sidebar layouts.
- `courierflow-api` — Backend route and service code: FastAPI routes, service
  layer, business logic, request handlers.
- `courierflow-data` — Database layer: SQLAlchemy ORM models, Alembic
  migrations, schema design, eager-loading, Household/HouseholdMember domain.
- `courierflow-integrations` — External services: Google Calendar, Twilio SMS,
  OpenAI, DocuSeal, Gmail, onboarding wizard.
- `courierflow-security` — Auth, registration, login, secrets, permissions,
  session handling, landlord/tenant access.

**Phase 0 trigger matrix (file-pattern → skill):**

```text
templates / CSS / HTML?       -> courierflow-ui
routes / services?            -> courierflow-api
models / migrations?          -> courierflow-data
external APIs / providers?    -> courierflow-integrations
auth / security / webhooks?   -> courierflow-security
prod incident / missed job?   -> courierflow-troubleshooter
skill drift / routing edits?  -> courierflow-skill-sync or reviewer
git / deploy / PR?            -> git skill
```

**Excluded from Phase 5 forced-selection** (use in Phase 0 / maintenance only):
`courierflow-troubleshooter`, `courierflow-skill-sync`,
`courierflow-skill-reviewer`.

---

## Authoring Your Own Menu

Two rules from the 2026-04-29 scale experiment (see
`../docs/plans/2026-04-29-skill-selection-at-scale.md`):

1. **Keep the menu small (≤ 5–6 skills).** A curated short list beat BM25/rerank
   over the full 205-skill catalog. Long menus invite wrong-skill selection.
2. **Make each menu entry domain-coherent.** UI / API / data / integrations /
   security covers most feature work without overlap. Avoid generic skills
   (e.g. "coding-best-practices") in the menu — those load via Phase 0 Step 4.
