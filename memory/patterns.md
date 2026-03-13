# CourierFlow Code Patterns

## Database Setup
- `app/database/__init__.py` exports: `Base`, `GUID`, `JSONEncodedArray`, `get_db`, `init_db`, `engine`, `async_session`, `EncryptedColumn`
- `GUID` is a custom TypeDecorator that works with both PostgreSQL (native UUID) and SQLite (CHAR(36))
- `JSONEncodedArray` handles JSON array storage cross-database
- `get_db` is an async generator yielding `AsyncSession`

## Route Pattern (thin routes)
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth import get_current_active_user  # NOT get_current_user
from app.models.user import User

router = APIRouter(prefix="/something", tags=["something"])

@router.get("/")
async def list_items(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await some_service.list_items(db, current_user.id)
    return templates.TemplateResponse("page.html", {"request": request, "items": result})
```

## Service Pattern (thick services)
- Services receive `db: AsyncSession` and `user_id: UUID` params
- Services do NOT call `db.commit()` - routes own transactions
- Services raise domain exceptions (AppException subclasses)
- User scoping: always filter by `user_id` in queries

## Exception Pattern
```python
# In services - raise domain exceptions
from app.exceptions import ResourceNotFoundException, ValidationException

async def get_item(db, user_id, item_id):
    item = await db.get(Item, item_id)
    if not item or item.user_id != user_id:
        raise ResourceNotFoundException("Item not found")
    return item

# In routes - use HTTP factory functions for direct HTTP errors
from app.exceptions import not_found, bad_request
raise not_found("Item not found")
```

## Naming Conventions
| UI Term | Code/Table | Model Class |
|---------|-----------|-------------|
| Property | `properties` table | `Property` |
| Tenant | `household_members` table | `HouseholdMember` |
| Sequence | `workflow_templates` table | `WorkflowTemplate` |
| Sequence Run | `workflow_instances` table | `WorkflowInstance` |
| Step | `workflow_template_steps` / `workflow_instance_steps` | `WorkflowTemplateStep` / `WorkflowInstanceStep` |

## Synonym Pattern
Many models use SQLAlchemy `synonym()` for backward compat:
```python
from sqlalchemy.orm import synonym
property_id = synonym("household_id")  # property_id is alias for household_id
```

## Template Pattern (Jinja2)
- All pages extend `base.html`
- Use `{% block page_title %}Page Name{% endblock %}` for browser tab title
- Use `.page-content-wrapper` + `.page-header-standard` for consistent layout
- Macro: `{% from 'macros/ui_macros.html' import page_header %}`
- CSS vars: `var(--ds-color-accent)` without fallbacks

## Auth Dependency Chain
Location: `app/services/dependencies.py`
1. `get_current_user_id()` - extracts JWT from header or cookie
2. `get_current_user()` - fetches User from DB
3. `get_current_active_user()` - verifies account is active (USE THIS ONE)

Rate limiting: `Depends(IPRateLimitDependency("endpoint_name"))` for sensitive endpoints

## Middleware Stack (app/main.py, order matters)
1. PerformanceMiddleware - timing headers, cache control, security headers
2. GZipMiddleware - compression
3. CSRF Middleware - state-changing endpoints
4. User Rate Limiter - per-user throttling
5. API Key Rate Limiter - workspace add-on API

## Background Schedulers (registered on startup)
- `workflow_scheduler` - executes steps at scheduled_for times
- `register_email_jobs()` - email delivery
- `register_reminder_jobs()` - reminder delivery
- `register_reply_jobs()` - check for email replies
- `register_archived_task_cleanup_jobs()` - cleanup
- Scheduler manager: `app/tasks/scheduler_manager.py` (APScheduler + PostgreSQL advisory locks)

## CSS Design System
Variables in `app/static/css/design-system/_variables.css`:
- Accent: `--ds-color-accent: #c37a45` (warm gold/brown)
- Background: `--ds-color-bg-primary: #efebe5`
- Font: `--ds-font-family: 'Poppins'`, base size 14px
- Spacing scale: `--ds-space-1` (4px) through `--ds-space-6` (24px)
- Layer order: `@layer design-system, components, pages`

## Key Indexes
- `ix_steps_scheduled_pending` - scheduler query
- `ix_workflow_user_status` - dashboard workflows
- `ix_events_provider_external` - sync lookup (unique partial)
- `ix_clients_user_active` - active clients list
- Trigram indexes on client first/last name for fuzzy search
