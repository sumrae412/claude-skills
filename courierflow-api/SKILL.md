---
name: courierflow-api
description: Routes, services, error handling, async patterns. Load when working on app/routes/*, app/services/*, or API endpoints.
---

# CourierFlow API Patterns

## Architecture Principles

1. **Service layer owns business logic** — Routes are thin (validate input, call service, return response)
2. **Async-first** — All database and I/O operations use `async`/`await`
3. **Use `httpx.AsyncClient`** — Not `requests`

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

## Route-to-Template Gotcha

Route URLs, handler names, and template filenames do not always match:

| URL | Route File | Handler | Template |
|-----|-----------|---------|----------|
| `/home` | `landing.py` | `home_page` | `dashboard.html` |

**Always check the route handler** before editing templates:
```bash
grep -r '"/home"' app/routes/
```

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
