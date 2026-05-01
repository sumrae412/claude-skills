# CourierFlow Integration Patterns

## Google Calendar

Direction rules:

- Google -> CourierFlow: event dates, title, description, webhook updates.
- CourierFlow -> Google: create new events only.
- Do not edit existing Google event dates from CourierFlow.

Parsing rules:

- Title is authoritative when it gives a confident match.
- Deterministic parsing runs before AI.
- Multiple plausible matches stay pending.
- Never auto-match tenant by last name only.

Operational rules:

- Use exponential backoff with jitter for 429/5xx.
- Respect the configured circuit breaker.
- Make webhook handling idempotent by provider event id and occurrence.
- Each recurring occurrence gets its own workflow instance.

## Messaging

- Template-level recipient routing is the default.
- Instance-level override is explicit and auditable.
- "Do Not Message" blocks execution unless the landlord confirms an override.
- Email/SMS failures should mark the step failed or retrying and surface in the
  dashboard.

## AI Calls

- `PromptSanitizer` is mandatory.
- Strip emails, phone numbers, and full addresses before sending prompts.
- AI output must include confidence.
- Only high-confidence AI output can prefill fields.
- Store model name, prompt hash, and confidence for audit.
- Use cheap models for parsing and capable models for content generation.

## Files And Documents

- User-owned files live in Google Drive via OAuth access.
- S3/R2 is for internal assets only.
- Document request/send operations require audit logs.
- File failures must not silently unblock workflow execution.

## Provider Failure Checklist

For each provider call, confirm:

- timeout is set
- retry policy is bounded
- 401/403 produces a reconnect or permission message
- 429/5xx uses provider-safe retry
- irreversible side effects have an idempotency key
- exception is wrapped in `ExternalServiceError` or domain-specific equivalent
