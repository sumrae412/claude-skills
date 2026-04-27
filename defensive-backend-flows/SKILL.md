---
name: defensive-backend-flows
description: Use when writing or reviewing Python backend code that involves error handling, data migrations, service-layer functions, cross-module API calls, or constant definitions
license: MIT
metadata:
  author: summerela
  version: "1.0.0"
---

# Defensive Backend Flows

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


## Overview

Every backend function must answer: **"What happens to the data if this fails halfway?"** If the answer is "nothing visible," you have a bug.

## The Checklist

Before finishing backend code, verify your code against the catalog. The Quick Reference below gives a one-line index of every pattern; load **references/patterns.md** for full bodies with examples and code.

## Quick Reference

| Rule | Symptom | Check |
|------|---------|-------|
| No Silent Swallows | Bug goes unnoticed for weeks | Every `except` logs or re-raises? |
| Catch What You Raise | Unhandled crash instead of fallback | Caller handles ALL exception types? Error-code sets complete? |
| Copy Before Delete | Data loss on deploy | Data copied BEFORE source NULLed/dropped? |
| One Source of Truth | "Fixed it but still wrong" | Constant/scope/config defined in exactly one place? |
| Respect Encapsulation | Double side-effects, brittle coupling | Only calling public API? |
| Verify Imports | `NameError` on first call | Every type/object imported before use? |
| Real DB Semantics | Query works locally, crashes in prod | DISTINCT/JSON/ORDER BY safe for Postgres? |
| Verify Model Attrs | `AttributeError` at runtime | Attribute exists on the model class? |
| Auxiliary Side-Effects | Notification failure aborts core op | Each side-effect wrapped independently? |
| Audit Trail | Action invisible in dashboard | State-changing endpoint creates ActionLog? |
| Error Visibility | Errors hidden from user | Dashboard feed includes ERROR-level logs? |
| Ephemeral Storage | Files vanish after deploy | All file I/O uses persistent storage? |
| Error Leaking | Internal details in HTTP response | Error messages generic, no `str(e)`? |
| String Datetime Compare | Future items filtered out | All datetime comparisons use parsed tz-aware objects? |
| Naive/Aware Datetime Arithmetic | `TypeError: can't subtract offset-naive and offset-aware` | DB datetime normalized to aware before arithmetic with `datetime.now(tz.utc)`? |
| Stale Connection Check | Feature disabled despite connection | Connection state read from owning service, not user column? |
| Cache-Only Primary View | "Only 1 event" when 15 exist | Primary view fetches live source, not just local cache? |
| Post-Conflict Testing | Resolved code breaks behavior | Tests re-run after conflict resolution before push? |
| Split Function Scope | `NameError` on variable from sibling function | Every variable in new function defined locally, as param, or imported? |
| Static Asset Cache-Busting | "Deployed but no visual change" | CSS/JS commit also bumps `?v=` in all loading templates? |
| Subprocess Shell Injection | Command injection vulnerability | Using list args with `shell=False` and timeout? |
| Lock File TOCTOU | Race condition in concurrent ops | Using atomic `O_CREAT | O_EXCL` or proper lock library? |
| Flag Evaluation N+1 | Slow feature flag checks | Batch-loading flags before loop evaluation? |
| Eval Built-in Usage | Security scanner flags, code injection risk | Using `ast.parse()` with explicit node handler? |
| SQL F-String Table Names | SQL injection via dynamic table name | Using allowlist assert + `.replace()` pattern? |
| Transient DB Crash | Operation fails on connection reset | Single-retry loop for `OperationalError`? |
| Can't Clear Nullable Field | User can set but never clear a text field | Explicit `None` → set to `None` branch exists? |
| DB fallback filters | Bare path returns different set than primary | Fallback path applies same filters as primary? Catch only SQLAlchemyError? |
| No BaseHTTPMiddleware | "Session is closed" / greenlet errors | `grep -r "BaseHTTPMiddleware" app/` returns zero? |
| Audit ALL Pattern Instances | Same bug reported twice, different file | Codebase-wide grep for pattern before shipping fix? |
| `scalar_one_or_none` on non-unique col | `MultipleResultsFound` crash months later | WHERE clause backed by unique DB constraint? If no, use `scalars().first()` |
| Test Constraints, Not Shapes | "Tests passed but feature is broken" | Mocked `db.execute` test asserts the bound `Select`? OR has companion integration test? |
| JSON Column Reassignment | `model.field.append(x)` doesn't persist | JSON-column writes reassign (`field = list(field) + [x]`) or use `MutableList`? |
| Phone Lookup Normalization | Twilio E.164 never matches stored phone | Lookup uses `Client.phone_normalized` AND `Client.user_id` scope? |
| State-Machine Exit Transitions | Status stuck in `PENDING_*` forever | Every exit action sets `status` explicitly, not just clears trigger field? |
| Fail-Closed Webhook Validators | Public unauthenticated POST in prod | No-token branch hard-fails when `settings.is_production`? |
| Escape XML/TwiML Substitutions | TwiML hijack via tag injection | AI/user content wrapped in `xml_escape()` before f-string? |
| Context-Aware Sanitizers | "JSON.parse fails at position 1 after sanitize" | Sanitizer is a state-machine walk (tracks in-string vs structural), not a global regex? Fallback path doesn't silently release destructive action on parse failure? |
| Stateful Callback Cleanup | "Feature works once, then wedges until restart" | Every return/raise/early-exit in a function that mutates module-level state clears that state? Prefer `try/finally`. |
| Telemetry Fail-Open | Noisy telemetry bug breaks the critical path it measures | Emit guarded with try/except + env-var opt-out (`REVIEW_LEDGER=0`) + import availability check? Reference: `scripts/plancraft_review.py` `_emit_invocation_record()`. |

## Red Flags — STOP and Fix

- `except SomeError: pass` with no logging
- A `try/except` that catches fewer types than the callee raises
- An error-code set that doesn't enumerate all permanent/known codes
- A migration that NULLs or DROPs before copying
- Same magic number in two files
- Same scope/config list hardcoded in multiple files
- Calling `obj._method()` from outside `obj`'s module
- A type in a function signature that has no matching `import`
- An object referenced before its late import in a function body
- `DISTINCT` on a table with JSON columns
- `ORDER BY` column not in `SELECT DISTINCT` list
- Accessing `model.attribute` without checking the model definition
- An unwrapped notification/SMS/email call inside a critical operation
- A state-changing endpoint with no `ActionLog` entry
- A dashboard query that filters out ERROR-level logs by default
- Writing files to local disk on a cloud platform (Railway, Heroku)
- Silent fallback to local storage when external storage fails
- `str(e)` or `traceback.format_exc()` in an HTTP response or redirect URL
- `print()` debug statements in production code
- Template file in a directory that doesn't match the route module using it
- CSS variant class that redeclares properties already on the base class
- Datetime comparison using string `>=`/`<=` instead of parsed objects
- Datetime arithmetic between a DB column value and `datetime.now(timezone.utc)` without normalizing timezone awareness
- Connection check using `user.some_token` instead of the token manager
- Primary view reading from local cache when it's the only UI for that data
- Cherry-pick/merge pushed without re-running affected tests
- Variable used in a function that was defined in a different function (split/copy artifact)
- String-quoted type annotation (`"UUID | None"`) without module-level import of the type
- A commit that changes `.css`/`.js` files but doesn't bump `?v=` params in loading templates
- Any use of the eval built-in — replace with `ast.parse()` + purpose-built evaluator
- `text(f"...{variable}...")` in SQL — use allowlist assert + `.replace()` instead
- DB call through dynamic dispatch with no retry for `OperationalError`
- Nullable text field update with only `if value is not None` branch (can't clear)
- A layered DB fallback whose bare path skips filters (status, search) applied in primary path
- `except Exception` in a DB fallback — use `except SQLAlchemyError` so non-DB errors propagate
- `from starlette.middleware.base import BaseHTTPMiddleware` — use pure ASGI middleware instead
- A pattern-class bug fix that only fixes the reported instance without grepping for all occurrences
- `scalar_one_or_none()` on a query filtering by a non-unique column (email, phone, name) — use `scalars().first()` instead
- Mocked `db.execute.return_value` in a test with no companion assertion on the bound `Select` — WHERE clause is invisible
- `.append()` / nested-dict mutation on a `Column(JSON)` value — silent no-op without reassignment or `MutableList`
- `Client.phone == ...` lookup against external (E.164) input — use `Client.phone_normalized` and scope by `user_id`
- Status-enum-driven model where an exit action only clears a trigger field and never reassigns `status`
- Webhook signature validator with a no-token branch that returns `True` unconditionally — must hard-fail in production
- F-string interpolation of AI/user content into XML/TwiML/RSS without `xml.sax.saxutils.escape`

## Pre-flight Construction Smoke (Third-Party SDK Migration)

Before committing to a third-party SDK migration, in a scratch script
verify against the production-pinned versions:

1. The symbol is exported (`from pkg import X` succeeds).
2. The symbol's constructor / wrapper accepts the kwargs you plan to pass.
3. Any wrapping class (e.g. `LangGraphAGUIAgent(graph=create_agent(...))`)
   accepts the resulting object cleanly.

Saves a wasted commit cycle if the SDK shape doesn't match your plan.

**Always `pip install -r requirements.txt` against the venv before
pre-flighting.** Local venv drift is silent — a stale venv (older
pinned version, missing pinned packages) produces false-positive smokes
that let no-op code ship.

## When NOT to Use

- Simple CRUD with no error handling complexity
- Read-only queries with no side effects
- Tests (mocking private methods in tests is acceptable)
