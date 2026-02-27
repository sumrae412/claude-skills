---
name: coding-best-practices
description: Comprehensive coding standards for Python, JavaScript, APIs, testing, and performance. Apply when writing code, reviewing PRs, debugging, or designing systems. Covers SQLAlchemy relationships, async patterns, DOM safety, REST design, and optimization techniques.
user-invocable: false
---

# Coding Best Practices

Apply these principles when writing, reviewing, or debugging code across any project.

## Quick Decision Matrix

| Question | Answer |
|----------|--------|
| Write a test? | **Always**, before implementation |
| Use async/await? | **Always** for I/O operations |
| Create migration? | **Always** when changing DB schema |
| Add type hints? | **Always** on function signatures |
| Use service layer? | **Always** for business logic |
| Cache data? | When frequently accessed, rarely changed |
| Add index? | When queries slow or tables > 1000 rows |
| Add rate limiting? | **Always** for new endpoints |
| Use circuit breaker? | **Always** for external API calls |

## Risk Levels for Changes

- **HIGH** (research first): DB types/migrations, event loops, auth, test fixtures
- **MEDIUM**: API changes, service layer, async additions, integrations
- **LOW**: UI templates, CSS, docs, config

## Core Principles

1. **Simple > Clever** - Readable code beats clever code
2. **Test First** - Write tests before implementation
3. **Fail Fast** - Validate early, provide clear errors
4. **DRY** - Extract repeated patterns (but don't over-abstract)
5. **Single Responsibility** - Each function does one thing well

## Detailed Guidelines

For specific patterns and examples, see:

- [Python Patterns](docs/python-patterns.md) - SQLAlchemy, async, transactions, migrations
- [JavaScript Safety](docs/javascript-safety.md) - DOM, events, WebSocket
- [API Design](docs/api-design.md) - REST, routing, HTTP methods
- [Testing Guide](docs/testing.md) - Test types and when to use them
- [Performance](docs/performance.md) - Caching, circuit breakers, optimization
- [Security](docs/security.md) - OWASP top 10, input validation, secrets

## Pre-Commit Checklist

Before committing code changes:

### Python
- [ ] Type hints on function signatures
- [ ] `AsyncMock` for async method mocking
- [ ] `pattern=` not `regex=` in Pydantic v2
- [ ] Service layer for business logic (not in routes)

### JavaScript
- [ ] DOM elements null-checked before use
- [ ] Event handlers accept `event` parameter
- [ ] WebSocket client handles all server message types
- [ ] `Promise.all()` for parallel API calls

### Database
- [ ] Migration created for schema changes
- [ ] `foreign_keys` and `overlaps` for multiple FKs to same table
- [ ] Indexes on frequently queried columns

### API
- [ ] Route has `name=` parameter for `url_for()`
- [ ] HTTP method matches frontend expectations (PATCH vs PUT)
- [ ] Content-Type matches (JSON vs Form data)
