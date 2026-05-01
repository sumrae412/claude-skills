---
name: courierflow-troubleshooter
description: Diagnose CourierFlow production and staging issues from logs, failing workflows, scheduler state, Google Calendar webhooks, Twilio/OpenAI/Gmail/Drive failures, Railway deploys, and dashboard-visible error states. Use when the user reports broken automation, missed messages, calendar sync problems, failed jobs, or production errors.
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# CourierFlow Troubleshooter

## Purpose

Diagnose production-like CourierFlow failures without guessing. Start from the
landlord-visible symptom, correlate logs and database state, then identify the
smallest fix or rollback.

## Load Strategy

1. Read `references/troubleshooting-flow.md` for the diagnostic sequence.
2. Pair with the relevant domain skill:
   - UI symptom -> `courierflow-ui`
   - route/service symptom -> `courierflow-api`
   - data/scheduler symptom -> `courierflow-data`
   - provider symptom -> `courierflow-integrations`
   - auth/privacy symptom -> `courierflow-security`
3. Use `investigator` for complex evidence matrices.

## Non-Negotiables

- Capture concrete symptom, timestamp, user, event, and workflow identifiers.
- Check recent deploys and config before changing code.
- Prefer logs and database facts over speculation.
- Do not run destructive production commands.
- Surface whether the landlord can see the failure.

## Output

Return:

- symptom and affected surface
- evidence gathered
- likely cause
- immediate mitigation if safe
- proposed code/config fix
- verification command or canary
