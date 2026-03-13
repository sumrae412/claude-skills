# CourierFlow Codebase Memory

Last surveyed: 2026-03-12

## Quick Reference

- **Product**: Google Calendar automation for small landlords (1-10 units)
- **Stack**: FastAPI (async) + PostgreSQL + SQLAlchemy 2.0 + Jinja2/Bootstrap 5
- **Deploy**: Railway (Dockerfile builder, `$PORT` env var, `railway.toml`)
- **DB module**: `app/database/__init__.py` (not `app/database.py`)
- **Config**: `app/config.py` -> `Settings(BaseSettings)` from pydantic_settings
- **Exceptions**: `app/exceptions.py` -> `AppException` base, factory functions like `not_found()`, `bad_request()`

## Key Gotchas

1. **Model file is `property.py`** not `household.py` - table is `properties`, model is `Property`
2. **`synonym()` aliases**: `property_id = synonym("household_id")` used throughout
3. **`builtin_property`**: Models import `from builtins import property as builtin_property` because `Property` model name conflicts
4. **No `app/core/` directory** - config is at `app/config.py`, database at `app/database/`
5. **Enum values are UPPERCASE** for `WorkflowActionType` (e.g., `EMAIL`, `SMS`, `TASK`)
6. **Tests use SQLite** via `sqlite+aiosqlite:///:memory:` default in Settings

## Data Model Summary

See [models.md](models.md) for full details.

Core chain: `User -> Property -> PropertyUnit -> HouseholdMember`
Event chain: `CalendarEvent -> CalendarEventMeta -> EventTypeMapping -> WorkflowTemplate`
Workflow chain: `WorkflowTemplate -> WorkflowTemplateStep` / `WorkflowInstance -> WorkflowInstanceStep`

## Exception Hierarchy

```
AppException (base)
  ├── ValidationException
  ├── AuthenticationException
  ├── AuthorizationException
  ├── ResourceNotFoundException
  ├── ResourceAlreadyExistsException
  ├── ExternalServiceException (takes service_name)
  ├── DatabaseException
  ├── RateLimitException (takes retry_after)
  ├── WorkflowException
  ├── EmailException
  └── IntegrationException (takes integration_name)
```

HTTP factory functions: `not_found()`, `bad_request()`, `unauthorized()`, `forbidden()`, `internal_error()`, `rate_limited()`

## Key Enums

- `LandlordEventType`: move_in, move_out, lease_renewal, inspection, maintenance, rent_due, lease_end, custom
- `WorkflowInstanceStatus`: pending, active, paused, completed, cancelled, failed, inactive
- `WorkflowStepStatus`: pending, in_progress, completed, skipped, failed, pending_approval, skipped_preference, skipped_frequency
- `WorkflowActionType`: EMAIL, SMS, TASK, WAIT, WEBHOOK, CONDITION, APPROVAL, NOTIFICATION, SEND_DOCUMENT, START_WORKFLOW, etc.
- `StepTimingType`: delay (after previous), relative (to target date), specific (fixed date)
- `StepRecipientType`: TENANT, LANDLORD, BOTH
- `EventConfirmationStatus`: pending, confirmed, rejected
- `WorkflowState`: draft, published, archived

## File Organization

See [file-map.md](file-map.md) for the complete active files list.
