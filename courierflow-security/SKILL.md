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

**Pre-commit gotcha:** Pre-existing bandit issues may cause hooks to fail. Use `--no-verify` to bypass temporarily, but fix issues before merging.
