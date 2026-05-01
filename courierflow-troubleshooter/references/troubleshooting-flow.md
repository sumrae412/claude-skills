# CourierFlow Troubleshooting Flow

## 1. Frame The Symptom

Record:

- environment
- timestamp and timezone
- landlord/user id or email if available
- calendar event id or provider id
- workflow instance and step ids
- expected action and observed result

If the report says "nothing happened," check whether it means no event parsed,
no confirmation prompt, no workflow instance, no scheduled step, or no provider
send.

## 2. Check Recent Change Context

Inspect:

- current branch and deploy commit
- recent merges touching the affected surface
- migrations around the failure window
- config/secret changes
- provider status if the failure is external

## 3. Follow The Event Flow

Trace the first missing handoff:

1. Google event/webhook received
2. deterministic parser result
3. AI fallback result if used
4. `CalendarEventMeta` created or updated
5. confirmation status shown to landlord
6. workflow instance created
7. instance steps scheduled
8. scheduler dequeued pending step
9. provider call made
10. step status and dashboard error state updated

## 4. Log Queries To Prefer

Use structured fields when present:

- correlation id
- user id
- calendar event id
- workflow instance id
- step id
- provider
- error code

For Railway, start with recent ERROR/Traceback/5xx lines, then narrow by
timestamp and identifiers. Do not treat absence of an error log as success.

## 5. Database Checks

Read-only checks should answer:

- is the row present and scoped to the user?
- is confirmation pending, confirmed, paused, retrying, failed, or executed?
- are scheduled timestamps in UTC and in the expected order?
- is there exactly one active workflow instance for the calendar event?
- did opt-out, manual override, or conflict warning block execution?

## 6. Provider Checks

- Google: webhook validity, event id, occurrence id, date changes, deletion.
- Twilio: phone normalization, opt-out, TwiML/XML escaping, provider status.
- OpenAI: prompt sanitized, confidence present, audit metadata stored.
- Gmail/SMTP: recipient routing, retry status, provider error visibility.
- Google Drive/DocuSeal: file permission, OAuth connection, signed URL expiry.

## 7. Finish With Evidence

Do not close a diagnosis without:

- exact failing handoff
- one log/database/source reference
- mitigation or explicit "no safe mitigation"
- focused verification step
