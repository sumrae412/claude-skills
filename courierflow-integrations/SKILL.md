---
name: courierflow-integrations
description: External API patterns — Calendar, Twilio, OpenAI, webhooks. Load when working with external services.
---

# CourierFlow Integrations

## Calendar Sync Rules

| Direction | What Syncs |
|-----------|------------|
| Google → CourierFlow | Event dates, title, description (via webhooks) |
| CourierFlow → Google | Create new events only. **Never edit existing event dates.** |

## Google Calendar API

- **Rate limit:** 1000 queries/100s (sliding window)
- **Circuit breaker:** 3 consecutive failures → 60s cooldown
- **Backoff:** Exponential with jitter on 429/5xx (max 5 retries)

## Calendar Parsing Rules

1. **Title is authoritative** — If title yields confident match, don't override with description
2. **Deterministic first** — Keyword dictionary (case-insensitive) + aliases before AI fallback
3. **Ambiguity** — Multiple matches → `confirmation_status = "pending"`, no auto-arm
4. **Tenant safety** — Never auto-match tenant based on last name only

## AI Guardrails

**PromptSanitizer** (`app/utils/prompt_sanitizer.py`): Mandatory for all AI calls.

- Strips emails, phone numbers, full addresses before sending to LLM
- AI output must include confidence (`high`/`medium`/`low`)
- Only `high` confidence can auto-fill
- Store model name, prompt hash, confidence for audit
- Use cheap models for parsing, capable models for content generation

## Webhook Validation

- Validate signature/shared secret before processing
- Twilio IP whitelist for SMS webhooks

## Dependency Pinning

| Package | Pin | Reason |
|---------|-----|--------|
| `boto3` | `<=1.34.34` | `aioboto3==12.3.0` requires `aiobotocore==2.11.2` which requires `botocore<1.34.35` |

**Before upgrading AWS SDK:** Check full chain `aioboto3` → `aiobotocore` → `botocore` → `boto3`
