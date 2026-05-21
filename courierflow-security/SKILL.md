---
name: courierflow-security
description: CourierFlow security guidance for authentication, authorization, user scoping, CSRF, JWT/refresh tokens, OAuth secrets, webhook validation, tenant privacy, prompt sanitization, audit logs, and landlord/tenant access boundaries. Use when editing auth routes, permission checks, webhooks, AI prompts, file access, or sensitive state changes.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow Security

## Purpose

Keep landlord and tenant data isolated, auditable, and safe across web app,
Google Calendar add-on, background jobs, and provider webhooks.

## Load Strategy

1. Read `references/security-patterns.md` before auth, webhook, secret, AI, or
   file-access work.
2. Pair with `courierflow-api` for protected routes and services.
3. Pair with `courierflow-integrations` for OAuth/provider calls.

## Non-Negotiables

- Use `get_current_active_user` for protected routes.
- Scope user data by `user_id`.
- Validate CSRF on state-changing endpoints.
- Validate webhook signatures or shared secrets before processing.
- Never send tenant PII to AI without `PromptSanitizer`.
- Audit sensitive actions.
- Never expose internal error details to clients.

## Verification

- Test wrong-user access.
- Test unauthenticated and inactive-user paths.
- Test webhook validator fail-closed behavior.
- Test prompt sanitization and file permission boundaries when touched.
