---
name: courierflow-api
description: Routes, services, error handling, async patterns. Load when working on app/routes/*, app/services/*, or API endpoints.
---

# CourierFlow API Patterns

## Architecture Principles

1. **Service layer owns business logic** — Routes are thin (validate input, call service, return response)
2. **Async-first** — All database and I/O operations use `async`/`await`
3. **Use `httpx.AsyncClient`** — Not `requests`

## Middleware

Use **pure ASGI middleware** only (class with `__init__(self, app)` and `async def __call__(self, scope, receive, send)`). Do not use `starlette.middleware.base.BaseHTTPMiddleware`: its `call_next()` wraps the response body in an internal task group, which breaks `AsyncSession` lifecycle in FastAPI dependency-injected routes (e.g. AI Insights "Failed to load insights"). When adding or changing middleware, follow the pattern in `PerformanceMiddleware` or `ErrorHandlingMiddleware` in `app/main.py`.

## Error Handling

Services raise domain exceptions; routes convert to HTTP responses:

| Exception | HTTP | When |
|-----------|------|------|
| `NotFoundError` | 404 | Resource doesn't exist or user can't access |
| `ValidationError` | 422 | Invalid input or business rule violation |
| `AuthorizationError` | 403 | User lacks permission |
| `ExternalServiceError` | 502 | Google Calendar API, Twilio, OpenAI failure |
| `ConflictError` | 409 | Duplicate resource or state conflict |

**Rules:**
- Never expose internal error details to clients
- Never silently swallow exceptions (`except SomeError: pass`)
- At minimum, log a warning — silent catches violate "Fail Visible"

## Transaction Boundaries

- **Routes own transactions** — They call `db.commit()`
- **Services use `db.flush()`** — When they need data visible within same transaction
- **Never use `db.commit()` in services**

### Webhook Handlers Own Their Session

The "no `db.commit()` in services" rule applies to request-scoped services where the FastAPI route handler owns the transaction. Webhook handlers (Twilio inbound, DocuSeal callbacks, Stripe webhooks) ARE the route handler — they own their own session via `async with AsyncSessionLocal()` and MUST `await db.commit()` (and `db.rollback()` on error) before returning. The service called from inside still uses `flush()` only.

```python
@router.post("/webhooks/twilio/inbound")
async def twilio_inbound(request: Request, ...):
    if not _validate_twilio_signature(request, params):
        return Response(status_code=403)
    async with AsyncSessionLocal() as db:
        try:
            reply = await get_concierge_service(db).process_inbound_sms(...)
            await db.commit()
        except Exception:
            await db.rollback()
            raise
    return Response(content=twiml(reply), media_type="application/xml")
```

See MEMORY `pattern_webhook_handler_owns_session.md`.

## CopilotKit Action Handlers

CopilotKit action handlers in `app/routes/copilot.py` are route handlers with three distinguishing traits:

- **Auth via ContextVar, not FastAPI DI.** Read the user with `_current_user_id.get()` at the top of the handler and return an error string if `None`. The ContextVar is populated per-request by the `/api/copilot` dispatch layer — handlers can't take `Depends(get_current_user)`.
- **Direct coroutine call, not `.delay()`, for user-blocking ops.** When the action wraps a Celery-backed operation and the user is waiting for the return value (sidebar, `ConfirmationCard`), import the task's async body (`from app.tasks.X import _Y_async`) and `await` it directly. Bypasses the queue; the coroutine opens its own DB session. This is the exception to the external-IO-via-Celery rule — see CLAUDE.md.
- **Deterministic fallback is part of the contract.** The sidebar's guarantee is "every call returns at least one usable result." Fallback must catch raised exceptions, not just `success=False` — `openai_service.chat_completion` raises on timeout / connection / circuit-breaker exhaustion. Wrap the coroutine call in try/except, log the exception, and return the empty sentinel that triggers the default path.

**Testing CopilotKit action handlers:**
- Set `_current_user_id` via `token = _current_user_id.set(uid); try: ...; finally: _current_user_id.reset(token)` — it's a `contextvars.ContextVar`, not a `patch` target.
- Mock external dependencies (`openai_service.is_configured`, `_suggest_workflow_next_step_async`) at the handler's call-site import path, not at the definition site. See MEMORY `gotcha_mock_patch_where_lookedup.md`.
- DB-free handlers (read-only actions that delegate to coroutines opening their own session) don't need a `patched_session_factory` fixture.
- Add an explicit "coroutine raises" test alongside the "returns `success=False`" test — different code paths inside the handler.

See `tests/integration/test_copilot_actions_gap_f.py` for the canonical test shape.

## Route-to-Template Gotcha

Route URLs, handler names, and template filenames do not always match:

| URL | Route File | Handler | Template |
|-----|-----------|---------|----------|
| `/home` | `landing.py` | `home_page` | `dashboard.html` |
| `/workflows/builder` | `workflows.py` | `workflow_builder_page` | `workflows/builder.html` |
| `/workflows/builder/{id}` | `workflows.py` | `workflow_builder_edit_page` | `workflows/builder.html` |

**Builder context variables:** Both builder routes must pass `template_state` (defaults to `"draft"`) for the page header status badge. When adding new template context data to builder routes, update BOTH the new-workflow and edit-workflow handlers.

**Always check the route handler** before editing templates:
```bash
grep -r '"/home"' app/routes/
```

## RORO Pattern (Receive an Object, Return an Object)

Services receive structured input and return structured output — never raw primitives for complex operations:

```python
# GOOD - RORO with Pydantic models
class CreateWorkflowRequest(BaseModel):
    name: str
    event_type: LandlordEventType
    steps: list[StepCreate] = []

class WorkflowResponse(BaseModel):
    model_config = {"from_attributes": True}
    id: UUID
    name: str
    status: WorkflowState

async def create_workflow(
    db: AsyncSession,
    user_id: UUID,
    request: CreateWorkflowRequest,
) -> WorkflowResponse:
    template = WorkflowTemplate(user_id=user_id, **request.model_dump())
    db.add(template)
    await db.flush()
    return WorkflowResponse.model_validate(template)

# BAD - scattered primitives
async def create_workflow(db, user_id, name, event_type, steps=None):
    ...  # Easy to mix up argument order, no validation
```

**When to use RORO:**
- Service functions with 3+ parameters → wrap in a request model
- Functions returning data to routes → use a response model
- Simple lookups (get by ID) → primitives are fine

## Code Style

- Python: flake8/PEP 8, max line length 79
- Type hints on all function parameters and return values
- Docstrings on all public functions and classes
- No unused imports or variables

## Rate Limiting Tiers

| Tier | Endpoints |
|------|-----------|
| Strict | Auth endpoints |
| Moderate | AI endpoints |
| Standard | CRUD operations |
| Relaxed | Read-only endpoints |

## Request Timeouts

- Default: 30s
- AI/bulk operations: 60s

## Webhook Notifications (CI/CD)

CI/CD scripts use async httpx for webhook notifications:

```python
async def send_webhook_notification(
    webhook_url: str,
    payload: Dict[str, Any],
    timeout: int = 10,
) -> bool:
    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            response = await client.post(webhook_url, json=payload)
            return response.status_code < 400
        except httpx.HTTPError:
            return False  # Best-effort, don't fail deployment
```

**Key points:**
- Use `httpx.AsyncClient` (not requests)
- Wrap in try-catch - webhook failure should not abort primary operation
- Configurable timeout with sensible default
