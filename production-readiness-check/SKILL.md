---
name: production-readiness-check
description: Pre-ship readiness check across SECURITY / DATABASE / DEPLOYMENT / CODE. Runs as claude-flow Phase 6 reviewer or standalone via `/production-readiness`. Advisory — reports findings, user decides.
user-invocable: true
---

# Production Readiness Check

Checks infrastructure and ops-level production readiness that code-level security review (OWASP, injection, XSS) does not cover. Runs as a parallel reviewer in Phase 6 alongside the code reviewer, silent failure hunter, security reviewer, and test coverage analyzer.

> Running production readiness check — scanning for auth, data protection, and monitoring gaps.

**Registry wiring:** Registered in `reviewer-registry.json` as a Tier 2 `always` reviewer (id `production-readiness-check`, subagent_type `production-readiness-check`, model `sonnet`). Phase 6 cascade dispatches it automatically when Tier 1 finds HIGH+ issues. Standalone invocation via `/production-readiness` bypasses the cascade and runs every deep-dive regardless of file patterns.

## When to Use

- **Automatically** — dispatched as a Phase 6 parallel reviewer during the claude-flow
- **Manually** — invoke `/production-readiness` for a full standalone audit before shipping to production

## Check Types

Every check in this skill is classified by one of four types. Pick the right type when adding new checks — the wrong type either produces false-positive FAILs (grep-based over-confidence) or lets real issues slip through (missing confirmation gate).

- **code-check** — deterministic literal/structural match (e.g., hardcoded secret pattern, `http://` URL, missing migration file). Grep/glob is authoritative; no user confirmation needed before marking FAIL.
- **code-check (heuristic)** — grep pre-filter for a property that depends on enclosing scope or structure (e.g., "is this `await` inside a try/catch?", "does this component render both loading and error branches?"). Grep cannot verify scope — treat matches as **low-confidence** and confirm each flagged location with the user before marking FAIL.
- **user-judgment** — no automation; relies on the reviewer reading the diff and making a call (e.g., "are inputs validated server-side?").
- **infra-confirm** — ask the user whether an external infra/ops condition holds (e.g., "Is Sentry wired in production?", "Has backup restore been tested in the last 90 days?").

When adding a new check, ask: does correctness depend on enclosing block or sibling structure? If yes → heuristic + confirmation gate.

## Workflow

This skill uses progressive disclosure. Load the reference file for the phase you're in; skip the others to keep context lean.

1. **Run the trigger system → load [`references/checks.md`](references/checks.md).**
   Step 1 (get the diff) → Step 2 (minimal core: secrets, request logging, CI/CD lockfile pinning — always run) → Step 3 (match changed-file paths against deep-dive triggers: Authentication / Data Protection / Monitoring / Security Extended / Database / Deployment / Code Hygiene) → Step 4 (run the matched expanded check tables). Standalone `/production-readiness` invocation runs every deep-dive regardless of trigger matches.

2. **Format and report findings → load [`references/reporting.md`](references/reporting.md).**
   Step 5 (FAIL / UNCONFIRMED grouping by domain, Score 0-100 per finding, ship-readiness summary) → Step 6 (fix iteration loop: prioritize by score, apply remediations, re-verify). Advisory mode — never hard-blocks Phase 6 completion.

3. **Generate IaC remediation snippets → load [`references/iac-templates.md`](references/iac-templates.md) only when needed.**
   Terraform stubs for AWS Cognito MFA, RDS encryption-at-rest, S3 encryption, automated backups, CloudWatch anomaly detection; markdown stubs for Incident Response Plans and Security Audit Schedules. Skip this file when no findings need scaffolded remediation.

## Next Steps

- **Critical findings?** Fix them before shipping — each finding includes a specific remediation action.
- **All checks pass?** Use `/ship` to commit, push, create PR, run review, and merge to main.
- **Want a multi-model review too?** Use `/debate-team` for cross-model adversarial review before shipping.
