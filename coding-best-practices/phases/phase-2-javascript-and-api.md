# Phase 2: JavaScript and API

Load `../docs/javascript-safety.md` and `../docs/api-design.md` before
running this phase. Load `../docs/security.md` if auth or input handling
is involved.

## Goal

Apply frontend safety, API-contract, and route-design standards.

## Always Check

- DOM nodes are null-checked before use
- event handlers accept `event` when needed
- WebSocket clients handle all server message types
- `Promise.all()` is used for parallel independent API calls
- route `name=` is present when `url_for()` matters
- HTTP method and content type match the caller's expectations

## Repo-Specific Gotchas

- Symbol renames often span Python, Jinja, and JS with the same
  attribute names.
- External APIs should use fetched documentation, not memory.
- Path input from users or LLM output must be resolved and contained
  before file access.

## Output

Targeted JS/API review guidance or implementation checklist for the
current change.
