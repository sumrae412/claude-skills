---
name: courierflow-core
description: Core CourierFlow context — product identity, terminology, and boundaries. Always loaded at session start via CLAUDE.md reference.
---

# CourierFlow Core

## Product Identity

**CourierFlow** is a Google Calendar automation tool for small landlords (1–10 units). Landlords create calendar events (move-ins, lease renewals, inspections); CourierFlow detects the event type and fires pre-built communication workflows.

**This is NOT** a generic CRM, virtual assistant, or real estate platform. If a feature doesn't directly serve "landlord creates calendar event → tenants/landlord get the right messages at the right times," it is out of scope.

### Two Front Doors, One Backend

1. **Google Calendar Sidebar** (Workspace Add-on) — Daily interaction point
2. **Web App** — Setup/admin interface

Both share: FastAPI (async), PostgreSQL, SQLAlchemy 2.0, Jinja2/Bootstrap 5.

## Terminology Mapping

| UI Label | Internal Code |
|----------|---------------|
| Property | `Household` |
| Tenant | `HouseholdMember` / `Client` |
| Sequence | `WorkflowTemplate` |
| Sequence Run | `WorkflowInstance` |
| Step | `WorkflowTemplateStep` / `WorkflowInstanceStep` |

## Boundaries — What You Must NOT Do

1. Do not modify `_archived/` files
2. Do not import from `_archived/`
3. Do not add features not in the current task
4. Do not refactor working code unless task requires it
5. Do not skip tests
6. Do not change schema without Alembic migration (`/new-migration`)
7. Do not use `db.commit()` in services — routes own transactions
8. Do not remove type hints or docstrings
9. Do not deploy without `/pre-deploy`
10. Do not deploy without pulling main first
11. Do not commit directly on main — use feature branches

## Trigger Matrix — Load Skills As Needed

| Working On | Load Skill |
|------------|------------|
| `app/templates/*`, CSS, HTML | `/courierflow-ui` |
| `app/routes/*`, `app/services/*` | `/courierflow-api` |
| `app/models/*`, `alembic/*`, schema | `/courierflow-data` |
| Calendar, Twilio, OpenAI, webhooks | `/courierflow-integrations` |
| commit, deploy, PR, branch | `/courierflow-git` |
| auth, JWT, security, compliance | `/courierflow-security` |

## Quick Commands

```bash
# Dev server
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Lint
flake8 app/

# Type check
mypy app/
```

## Key Directories

```
app/
├── routes/          # HTTP endpoints (thin)
├── services/        # Business logic (thick)
├── models/          # SQLAlchemy models
├── templates/       # Jinja2 HTML
├── schemas/         # Pydantic schemas
└── utils/           # Shared utilities
_archived/           # DO NOT TOUCH
```
