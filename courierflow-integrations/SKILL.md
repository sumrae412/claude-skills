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

## Twilio Webhook Correctness Checklist

Required pattern for every inbound Twilio handler:

1. **Signature body:** Read `params = dict(await request.form())` and pass the FULL dict to `RequestValidator.validate`. Twilio signs all POST fields (AccountSid, ApiVersion, NumMedia, SmsSid, SmsStatus, …); passing a partial dict built from `Form(...)` args 403-rejects every legit production webhook. See memory/gotcha_twilio_signature_full_body.md.
2. **Production fail-closed:** When `settings.twilio_auth_token` is missing AND `settings.is_production`, the validator must return `False`. Never leave a public webhook unauthenticated in prod.
3. **TwiML escaping:** Run `xml.sax.saxutils.escape(reply)` before interpolating into `<Message>{reply}</Message>`. User-controlled text may contain `<`, `&`, or quotes. See memory/gotcha_twiml_xml_escape_user_content.md.
4. **Rate limit:** Async handlers need per-key `asyncio.Lock`; document the per-process scope. See memory/pattern_asyncio_lock_per_key_rate_limit.md.

## Twilio Phone Lookups

Twilio sends inbound numbers in E.164 (`+15551234567`); `Client.phone` stores freeform (`(555) 123-4567`). They will never match. Always normalize to digits AND scope by landlord — same phone can legitimately appear under multiple landlords.

```python
import re
digits = re.sub(r"\D", "", from_number)
stmt = select(Client).where(
    Client.phone_normalized == digits,
    Client.user_id == landlord_id,  # mandatory
)
```

Resolve the landlord by the inbound `to_number` (the Twilio webhook's `To` field) via `User.twilio_phone_number == to_number` before scoping the tenant query. Multi-landlord routing requires this.

## AsyncAnthropic in Webhook Paths

Any `AsyncAnthropic.messages.create(...)` call inside a webhook path must:

- Pass `timeout=<sec>` (SDK default is unbounded; Twilio's 15s deadline will blow up under API slowdown).
- Guard `response.content[0]` before `.text` access — empty content lists and non-text blocks crash the handler.

See memory/pattern_anthropic_timeout_in_webhook.md.

## Integration Data Sync Invariant

Any integration code path that creates a `HouseholdMember` (e.g., `sync_service.py`, `contact_import_service.py`) **must** call `ensure_client_for_member()` (module-level in `app/services/household_service.py`, import directly) after creation. The Tenants page queries `Client` exclusively via `search_clients_grouped` — a member without a corresponding Client is invisible in the UI.

## Column Name Gotcha: `is_primary_contact`

The `HouseholdMember` model uses `is_primary_contact` (not `is_primary`). The shorter name silently fails — SQLAlchemy creates a filter that matches nothing instead of raising an error. Always verify column names against the model definition.

## Dependency Pinning

| Package | Pin | Reason |
|---------|-----|--------|
| `boto3` | `<=1.34.34` | `aioboto3==12.3.0` requires `aiobotocore==2.11.2` which requires `botocore<1.34.35` |

**Before upgrading AWS SDK:** Check full chain `aioboto3` → `aiobotocore` → `botocore` → `boto3`
