---
name: courierflow-security
description: Auth, access control, compliance, data privacy. Load when working on auth, JWT, security, or sensitive data.
---

# CourierFlow Security

## Auth & Access Control

- **User scoping enforced** via `UserScopedQuery` pattern
- **All queries must filter by `user_id`**
- **Use `get_current_active_user`** (not `get_current_user`) for protected routes
- **Short JWT expiry** — 15 minutes, use refresh tokens
- **CSRF middleware** on all state-changing endpoints

## UserScopedQuery Pattern

Every database query that returns user data must include:

```python
.where(Model.user_id == current_user.id)
```

## Data Privacy

- **PromptSanitizer default ON** for all AI calls
- **All user files in Google Drive** with OAuth access
- **S3/R2 for internal assets only** — Never store user files there
- **Audit logs** for sensitive actions:
  - Workflow arming
  - Tenant changes
  - File operations

## Compliance & Retention

| Data Type | Retention |
|-----------|-----------|
| Audit logs | 12 months |
| General logs | 90 days |
| AI traces | 90 days |
| Events | 90 days |
| Messages | 90 days |
| Files | Until user deletion or Drive revocation |

Cold storage for data past retention threshold.

## Webhook Security

- Validate signature/shared secret before processing
- Twilio IP whitelist for SMS webhooks

### Webhook Signature Validator Audit Checklist

Every webhook signature validator (grep: `rg -n 'RequestValidator|webhook.*validate|signature' app/routes/`) must confirm BOTH:

- **Fails closed in production:** when the auth token is missing AND `settings.is_production`, return `False`. Never leave a public webhook unauthenticated in prod.
- **Validates against the FULL request body:** `await request.form()` (form-encoded) or `await request.body()` (raw) — not the subset of `Form(...)` args the handler happens to read. Partial dicts rejected legit signed traffic in `twilio_inbound` (caught by CodeRabbit, PR #342).

Known sites to audit: `app/routes/twilio_inbound.py`, `app/routes/sms.py`, any future `/webhooks/*`.

## Secrets Management

- Never commit secrets to git
- Use environment variables
- Check `.env.example` for required vars

## Security Scanning

**GitHub Workflow:** `.github/workflows/security.yml` runs on push to main, PRs, and weekly schedule.

**Manual scan:**
```bash
# Vulnerability scan with severity filtering
python scripts/vulnerability_scan.py --severity-threshold high

# Create GitHub issue for critical vulnerabilities
python scripts/vulnerability_scan.py --severity-threshold critical --create-issue
```

**Severity inference:** pip-audit doesn't provide severity directly. Infer from CVE/GHSA identifiers or use conservative defaults.

**Pre-commit gotcha:** Pre-existing bandit issues may cause hooks to fail. **Fix the root cause** — resolve the bandit finding or add a targeted `# nosec` annotation with justification. Do not use `--no-verify` to bypass fixable code issues, even if pre-existing.
