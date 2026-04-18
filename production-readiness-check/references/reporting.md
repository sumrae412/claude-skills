## Step 5: Report Findings

**Enforcement mode: advisory.** All findings (FAIL + UNCONFIRMED) are reported to the user with suggested remediation. The user decides what to fix before ship vs. defer. This skill does not hard-block Phase 6 completion — the review-fix-recheck loop treats these findings like any other reviewer output.

Present findings in a table matching the format used by other Phase 6 reviewers. Only report items with score >= 60 or status UNCONFIRMED. Omit PASS items unless they provide useful context. Close with a Ship Readiness Summary so the user can make the final call.

**Output format:**

```markdown
### Production Readiness Check

**Triggered sections:** [list which sections ran, e.g. "Authentication, Monitoring (Data Protection skipped — no matching files)"]

| # | Item | Status | Score | Action |
|---|------|--------|-------|--------|
| 1 | JWT secret from env | PASS | — | — |
| 2 | Session https_only | FAIL | 75 | Fix: set `https_only: True` in session config |
| 3 | MFA enabled | UNCONFIRMED | — | User confirmation needed |
| 4 | Security event logging | FAIL | 80 | Fix: add audit log to new `/api/users` endpoint |
| 5 | Anomaly detection | UNCONFIRMED | — | Generate CloudWatch alarm config? |

**Proposed fix plan:**
1. Set `https_only: True` in `app/config/session.py:14`
2. Add `logger.info("user_action", extra={...})` to `app/routes/users.py:45`
3. Generate `terraform/modules/monitoring/alarms.tf` with anomaly detection config

### Ship Readiness Summary

- **Checks run:** <total items evaluated across triggered sections>
- **PASS:** <n> / **FAIL:** <n> / **UNCONFIRMED:** <n>
- **Critical (score 100):** <n>
- **High (score 75–99):** <n>
- **Medium (score 60–74):** <n>

> Advisory mode — any unresolved FAIL or UNCONFIRMED item is on you. "Can't check every box? You're not ready to ship" is a judgment call, not a hard gate.

Proceed with fixes?
```

Statuses:
- **PASS** — check passed, no action needed
- **FAIL** — code-level issue found, score >= 60
- **UNCONFIRMED** — infra item, needs user confirmation

## Step 6: Fix Iteration

**HARD-GATE: Do NOT apply any fixes until the user explicitly approves.** Present findings, wait for approval, then proceed.

After user approval, apply fixes in this order:

1. **Code fixes** — remove secrets, replace `http://` URLs, add logging, fix session/JWT config, mask PII
2. **IaC snippets** — generate Terraform or config files for infra-confirm items (see templates below)
3. **Doc stubs** — create missing documentation (incident response plan, audit schedule)
4. **Re-verify** — re-run the affected checks to confirm fixes resolved the findings

