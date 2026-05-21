# CourierFlow Security Patterns

## User Scoping

Every query for landlord-owned data must include `user_id` directly or through
an already scoped parent. Treat missing scoping as a data leak even if the route
is authenticated.

Check these surfaces carefully:

- dashboard counts
- calendar event resolution
- property and tenant lookup
- workflow template and instance access
- document/file lookup
- background job dequeue and execution

## Protected Routes

- Use `get_current_active_user`.
- Return generic 404 for resources the user cannot access unless the product
  specifically needs a 403.
- Keep service exceptions domain-specific; route layer maps them.

## Webhooks

- Validate Google and Twilio signatures/shared secrets before parsing payloads.
- Fail closed in production when validation material is missing.
- Keep webhook handlers idempotent.
- Do not trust tenant, property, or workflow ids from webhook payloads without
  scoped database verification.

## AI Privacy

- Run `PromptSanitizer` before OpenAI calls.
- Strip emails, phone numbers, full addresses, and direct identifiers.
- Store prompt hash and model metadata, not raw sensitive prompt text.
- Low/medium confidence AI output can assist review, not auto-arm workflow.

## Audit Logs

Audit these actions:

- workflow arming, pausing, resuming, and override
- tenant contact and opt-out changes
- property/unit assignment changes
- document/file operations
- OAuth connection changes
- provider-triggered failures that affect workflow execution

## Secret Handling

- Do not log OAuth tokens, JWTs, refresh tokens, API keys, webhook secrets, or
  signed URLs.
- Do not put provider payloads directly in client-visible errors.
- When adding settings, ensure production missing-secret behavior fails closed
  for security-sensitive paths.
