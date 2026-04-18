## Trigger System

### Step 1: Get the Diff

```bash
git diff origin/main...HEAD --name-only
```

Capture the list of changed files. This drives both the minimal core checks and the deep-dive trigger matching.

### Step 2: Run Minimal Core (Always)

These three checks run on every invocation regardless of which files changed.

#### C1: Secrets in Code

Grep the diff for hardcoded secrets:

```bash
# General credential assignments (catches custom keys, passwords, secrets)
git diff origin/main...HEAD -U0 | grep -iE "(api_key|api_secret|password|secret_key|private_key|token)\s*=\s*['\"][^'\"]{8,}"

# Known-format tokens (AWS, Stripe, GitHub, GitLab)
git diff origin/main...HEAD -U0 | grep -E 'AKIA[0-9A-Z]{16}|sk-[a-zA-Z0-9\-]{20,}|pk_live_|ghp_[a-zA-Z0-9]{36}|glpat-[a-zA-Z0-9\-]{20}'
```

Also check for committed `.env` files:

```bash
git diff origin/main...HEAD --name-only | grep -i '\.env'
```

Look for generic credential assignments (`API_KEY = "..."`, `password = "..."`) as well as known-format tokens: AWS access keys (`AKIA[0-9A-Z]{16}`), Stripe keys (`sk-`, `pk_live_`), GitHub tokens (`ghp_`), and GitLab tokens (`glpat-`).

- **Score: 100** — any match is a critical finding.

#### C2: HTTPS / TLS Enforcement

Grep changed files for plaintext HTTP URLs (excluding localhost, 127.0.0.1, XML schemas, and W3 references):

```bash
git diff origin/main...HEAD | grep -E 'http://' | grep -vE 'localhost|127\.0\.0\.1|schemas|w3\.org|example\.com'
```

Check for HSTS header configuration:

```bash
git diff origin/main...HEAD --name-only | xargs grep -l 'Strict-Transport-Security' /dev/null 2>/dev/null
```

If no matches in changed files, fall back to a project-wide check to confirm HSTS exists somewhere:

```bash
grep -riE 'Strict-Transport-Security' --include='*.py' --include='*.js' --include='*.ts' --include='*.yaml' --include='*.yml' 2>/dev/null
```

- **Score: 75** — plaintext `http://` URLs found in non-exempt contexts.
- **Score: 60** — no HSTS header configured anywhere in the project.

#### C3: Security Event Logging

Find new route or endpoint definitions in the diff and cross-reference against logging calls:

```bash
# Find new endpoints
git diff origin/main...HEAD | grep -E '^\+.*(\.route|\.get|\.post|\.put|\.patch|\.delete|@app\.|@router\.|app\.(use|all))\b'

# Cross-reference against logging in the same files
git diff origin/main...HEAD --name-only | xargs grep -lE '(logger\.|logging\.|console\.log|audit_log|log\.info|log\.warn|log\.error)' 2>/dev/null
```

- **Score: 80** — new endpoints found that lack audit logging in the same file.

#### C4: CI Workflow Companion Artifacts

Any workflow that runs a deterministic install (`npm ci`, `yarn install --frozen-lockfile`, `pnpm install --frozen-lockfile`, `poetry install --no-update`, `pip install -r *.lock`) must have the corresponding lock file committed in the working directory it targets. Workflows shipped without the lock file chronically fail every PR silently until someone traces the failure.

```bash
# For each workflow, find deterministic-install commands and verify lockfile sibling
for wf in .github/workflows/*.yml .github/workflows/*.yaml; do
  [ -f "$wf" ] || continue
  grep -qE 'npm ci|yarn install --frozen|pnpm install --frozen|poetry install --no-update|pip install -r [^ ]*\.lock' "$wf" || continue
  wd=$(grep -oE 'working-directory:\s*\S+' "$wf" | awk '{print $2}' | head -1)
  wd="${wd:-.}"
  found=0
  for lock in package-lock.json yarn.lock pnpm-lock.yaml poetry.lock; do
    [ -f "$wd/$lock" ] && found=1 && break
  done
  [ "$found" -eq 0 ] && echo "FAIL: $wf runs deterministic install in $wd but no lock file found"
done
```

- **Score: 90** — workflow invokes `npm ci` (or equivalent) but no lockfile is committed in the referenced `working-directory:`.
- Remediation: generate the lockfile (`npm install --package-lock-only --no-audit`, `poetry lock`, etc.), verify the workflow's install command passes in `--dry-run`, commit both together.

This is Core (not a deep-dive) because the trigger is narrow (`.github/workflows/*.yml` or lockfile-producing `package.json` / `pyproject.toml` in the diff) but very high-signal — every missed instance causes chronic PR failure until manually traced.

### Step 3: Match Deep-Dive Triggers

Compare changed file paths against these patterns. If any match, run the corresponding expanded section.

| File Pattern | Expanded Section |
|---|---|
| `auth/`, `login`, `session`, `jwt`, `token`, `password`, `oauth`, `middleware/auth` | Authentication |
| `models/`, `migrations/`, `schema`, `encrypt`, `pii`, `personal`, `backup`, `gdpr` | Data Protection |
| `logging`, `monitor`, `alert`, `metric`, `sentry`, `datadog`, `grafana`, `prometheus` | Monitoring |
| `routes/`, `api/`, `endpoints/`, `middleware/`, `cors`, `rate_limit`, `limiter` | Security Extended |
| `models/`, `migrations/`, `alembic/`, `schema`, `database`, `db/`, `*.sql` | Database |
| `Dockerfile`, `docker-compose`, `.env.example`, `railway.`, `terraform/`, `deploy/`, `pm2.`, `ecosystem.`, `.github/workflows/`, `systemd/` | Deployment |
| `**/*.js`, `**/*.ts`, `**/*.jsx`, `**/*.tsx`, `**/*.py`, `templates/`, `static/`, `package.json`, `uv.lock`, `poetry.lock` | Code Hygiene |

If no patterns match, skip the deep-dives and proceed to reporting.

**Standalone invocation (`/production-readiness`):** Run ALL deep-dive sections regardless of file patterns — this mode is for pre-ship audits where infra-confirm items (firewall, SSL cert, rollback plan) must be surfaced even when no related files changed.

### Step 4: Run Expanded Checks

Only run the sections triggered in Step 3.

#### Authentication Deep-Dive

| ID | Check | Type | Details |
|---|---|---|---|
| A1 | MFA Available | infra-confirm | Ask: "Is MFA enabled for user-facing auth (e.g., TOTP, WebAuthn)?" If unconfirmed, mark UNCONFIRMED and provide IaC snippet. |
| A2 | Password Policy | code-check | Grep for password length/complexity enforcement. Look for `minlength`, `MIN_PASSWORD_LENGTH`, `passwordStrength`, `zxcvbn`. **Score: 75** if no policy found. |
| A3 | Session Management | code-check | Check for `httpOnly`, `secure`, `sameSite` on cookies. Check session expiry / max-age configuration. **Score: 75** per missing attribute. |
| A4 | JWT Secured | code-check | Verify JWT algorithm is pinned (not `none`). Check secret is from env var. Check for expiry (`exp` claim). **Score: 100** for hardcoded secret, **Score: 85** for algorithm `none` allowed, **Score: 75** for missing `exp` claim. |

#### Data Protection Deep-Dive

| ID | Check | Type | Details |
|---|---|---|---|
| D1 | Encryption at Rest | infra-confirm | Ask: "Is encryption at rest enabled for databases and object stores?" If unconfirmed, mark UNCONFIRMED and provide IaC snippets (RDS + S3). |
| D2 | TLS in Transit | covered-by-core | Covered by C2 above. |
| D3 | PII Anonymization | code-check | Grep for PII field names (`email`, `phone`, `ssn`, `address`, `date_of_birth`) in logs, error messages, and API responses. **Score: 70** for PII in logs, **Score: 80** for PII in API error responses. |
| D4 | Backup & Recovery | infra-confirm | Ask: "Are automated backups configured with tested restore procedures?" If unconfirmed, mark UNCONFIRMED and provide IaC snippet. |

#### Monitoring Deep-Dive

| ID | Check | Type | Details |
|---|---|---|---|
| M1 | Security Logging | covered-by-core | Covered by C3 above. |
| M2 | Anomaly Detection | infra-confirm | Ask: "Are anomaly detection alerts configured (e.g., unusual login patterns, traffic spikes)?" If unconfirmed, mark UNCONFIRMED and provide IaC snippet. |
| M3 | Incident Response Plan | infra-confirm | Check for `docs/incident-response.md`. If missing, mark UNCONFIRMED and provide doc stub. |
| M4 | Security Audit Schedule | infra-confirm | Check for `docs/security-audit-schedule.md`. If missing, mark UNCONFIRMED and provide doc stub. |

#### Security Extended Deep-Dive

| ID | Check | Type | Details |
|---|---|---|---|
| S1 | Route auth audit | code-check | For every new route definition in the diff (`@app.route`, `@router.get\|post\|put\|patch\|delete`, `app.get\|post`, etc.), cross-reference against an auth decorator (`@login_required`, `@jwt_required`, `@require_auth`, `Depends(get_current_user)`, `authenticate`). **Score: 90** per unauthenticated route. Exempt routes explicitly tagged public (`/health`, `/metrics`, `/public/`, `@public`, `@health_check`). |
| S2 | CORS lockdown | code-check | Grep for CORS wildcards: `allow_origins=["*"]`, `Access-Control-Allow-Origin: *`, `origins=["*"]`, `cors(origin: '*')`. **Score: 85** per match — wildcard CORS is prod-unsafe. |
| S3 | Server-side input validation | user-judgment | Ask: "Are user-supplied inputs in changed endpoints validated server-side (schemas, length limits, type coercion)?" UNCONFIRMED if not inspected. Client-side validation is UX, not security. |
| S4 | Rate limiting on auth/sensitive endpoints | code-check | If auth routes (`/login`, `/register`, `/reset-password`, `/api/token`) exist in the diff, grep for rate-limit decorators or middleware (`@limiter.limit`, `slowapi`, `rate_limit`, `RateLimitMiddleware`, `express-rate-limit`). **Score: 75** if auth routes present without rate limiting. |
| S5 | Password hashing algorithm | code-check | If password storage code is touched, grep for strong hashes: `bcrypt`, `argon2`, `passlib`, `scrypt`. Flag weak hashes alone: `md5`, `sha1`, `sha256(password)`. **Score: 100** for weak-hash match on password fields, **Score: 70** if password storage touched without any strong hash import visible. |
| S6 | Logout session invalidation | code-check | For logout endpoints, grep for server-side revocation (`revoke`, `blacklist`, `delete_session`, `session.pop`, `token_blacklist`). **Score: 80** if logout only clears client cookie without server-side cleanup — stolen tokens remain valid. |

#### Database Deep-Dive

| ID | Check | Type | Details |
|---|---|---|---|
| DB1 | Backup restore tested | infra-confirm | Ask: "Has the backup restore procedure been tested end-to-end in the last 90 days?" UNCONFIRMED otherwise. Backups without restore tests are untrusted. |
| DB2 | Parameterized queries | code-check | Grep diff for SQL string concatenation: `execute(f"SELECT`, `execute(".* " + `, `query(f'`, `.format(...)` on SQL strings, `%s` fallback via `%` operator. **Score: 100** per match — injection risk. Use parameterized queries / ORM binds. |
| DB3 | Dev/prod DB separation | infra-confirm | Ask: "Are dev/staging and production databases distinct instances with separate credentials?" UNCONFIRMED if shared. |
| DB4 | Connection pooling configured | code-check | If DB engine configuration is touched, grep for pool settings: `pool_size=`, `QueuePool`, `max_overflow=`, `poolclass=`, external pooler (`PgBouncer`, `RDS Proxy`). **Score: 60** if DB engine configured without explicit pooling. |
| DB5 | Migrations in version control | code-check | If schema-shaped changes appear in diff (`models/`, `schema.sql`, `CREATE TABLE`, `ALTER TABLE`, column adds/drops), verify a corresponding migration file exists in `alembic/versions/`, `migrations/`, or equivalent. **Score: 85** per schema change without migration. No manual DB surgery. |
| DB6 | Non-root DB user | infra-confirm | Ask: "Does the application connect with a non-superuser DB account (limited to the schemas/tables it needs)?" UNCONFIRMED if unsure. Superuser connections magnify SQLi blast radius. |

#### Deployment Deep-Dive

| ID | Check | Type | Details |
|---|---|---|---|
| DP1 | Env vars declared for production | code-check | Grep changed code for `os.getenv`, `os.environ[`, `process.env.*`. Cross-reference each referenced env var against `.env.example` (or equivalent) in the repo. **Score: 70** per env var referenced in code but missing from `.env.example` — deployment-time footgun. |
| DP2 | SSL cert installed and valid | infra-confirm | Ask: "Is the production SSL certificate installed, valid, not expiring in <30 days, and covering all deployed hostnames?" UNCONFIRMED otherwise. |
| DP3 | Firewall (80/443 only public) | infra-confirm | Ask: "Does the production firewall expose only ports 80/443 publicly, with all other ports internal-only?" UNCONFIRMED otherwise. |
| DP4 | Process manager running | infra-confirm | Ask: "Is the app running under a process manager (systemd, PM2, Docker restart policies, Kubernetes) that auto-restarts on crash?" UNCONFIRMED otherwise. |
| DP5 | Rollback plan exists | code-check | Check for `docs/runbooks/rollback.md`, `docs/rollback.md`, `docs/runbooks/`, or equivalent rollback documentation in the repo. **Score: 60** if no rollback runbook exists — every prod system needs a known rollback path. |
| DP6 | Staging test passed | user-judgment | Ask: "Was this change deployed and smoke-tested on staging before production?" UNCONFIRMED if skipped. |

#### Code Hygiene Deep-Dive

| ID | Check | Type | Details |
|---|---|---|---|
| CD1 | No debug logging in prod build | code-check | Grep diff for leftover debug calls: `console.log(`, `console.debug(`, bare `print(` in non-test Python files, `debugger;` in JS. Exclude framework loggers (`logger.info`, `log.debug`, `structlog`). **Score: 60** per leftover debug call. |
| CD2 | Error handling on async operations | code-check (heuristic) | **Heuristic pre-filter** — grep diff for `await ` and `async def` / `async function`; for each hit, check whether the enclosing block contains `try`/`except`/`catch`. Grep cannot verify scope accurately, so treat matches as low-confidence and confirm each flagged location with the user before marking FAIL (e.g., "Function `<name>` contains `await` — is error handling present?"). **Score: 70** per confirmed unguarded await in non-test code. Unhandled promise rejections crash Node processes. |
| CD3 | UI loading and error states | code-check (heuristic) | **Heuristic pre-filter** — for each component/template that fetches data (contains `fetch(`, `axios`, `useQuery`, `useEffect.*fetch`, `{% ... %}` template calls), grep for loading/error branches (`isLoading`, `error`, `{#if error}`, `x-if=`, `{% if error %}`, `<ErrorBoundary>`). Grep cannot verify component structure, so flag matches as low-confidence and confirm with the user (e.g., "`<Component>` fetches data — does it render both loading and error states?"). **Score: 65** per confirmed component missing error or loading branch. |
| CD4 | Pagination on list endpoints | code-check | Grep new list endpoints (routes returning arrays/collections, e.g. `def list_`, `def get_all_`, `return items`, `return query.all()`) for pagination params (`limit`, `offset`, `page`, `cursor`, `page_size`). **Score: 70** per list endpoint without pagination — unbounded queries break under scale. |
| CD5 | Dependency vulnerability audit | code-check | If `package.json` / `package-lock.json` changed: run `npm audit --production --audit-level=high` and report unresolved critical/high issues. If `pyproject.toml` / `uv.lock` / `poetry.lock` changed: run `pip-audit` or `uv pip check`. **Score: 80** per unresolved critical vulnerability. |

