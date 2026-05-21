---
name: courierflow-integrations
description: CourierFlow integration guidance for Google Calendar sync/webhooks, Gmail/SMTP, Twilio SMS, OpenAI parsing/content generation, DocuSeal, Google Drive storage, OAuth tokens, retries, rate limits, and provider failure handling. Use when editing external API clients, webhook handlers, calendar import, messaging, AI calls, or document flows.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow Integrations

## Purpose

Keep external services reliable, scoped, and safe. Use this skill for Google
Calendar, Google Drive/Gmail, SMTP, Twilio, OpenAI, DocuSeal, and any provider
that can create side effects outside CourierFlow.

## Load Strategy

1. Read `references/integration-patterns.md` before provider work.
2. Fetch current provider API docs before adding or changing API calls.
3. Pair with `courierflow-security` for OAuth, webhooks, prompt sanitization,
   secrets, or token storage.
4. Pair with `courierflow-api` for route/service boundaries.

## Non-Negotiables

- Use async I/O clients, especially `httpx.AsyncClient`.
- Sanitize AI prompts with `PromptSanitizer`.
- Validate webhook signatures before processing.
- Apply retry/backoff only to retry-safe provider failures.
- Store enough audit metadata to explain provider decisions.
- Never edit existing Google Calendar event dates from CourierFlow.
- No external message sends before landlord confirmation.

## Verification

- Test provider success and failure paths.
- Test idempotency for webhook and scheduler-triggered sends.
- Test prompt sanitization for AI calls.
- For live-only provider behavior, run one canary when available and safe.
