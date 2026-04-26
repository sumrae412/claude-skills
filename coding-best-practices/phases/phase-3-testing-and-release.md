# Phase 3: Testing and Release Discipline

Load `../docs/testing.md` before running this phase. Load
`../docs/security.md` when the change affects auth, secrets, or
externally reachable surfaces.

## Goal

Set the minimum testing and release discipline for the current change.

## Always Check

- tests cover the changed behavior
- async methods use the correct mocking approach
- schema changes have migrations
- high-risk changes have broader regression coverage
- release or CI scripts support dry-run and structured output where
  appropriate

## Repo-Specific Gotchas

- Pydantic `BaseSettings` attributes are not safe to patch directly;
  replace the module-level settings reference.
- Lazy imports inside functions can defeat module-level patching.

## CI / Script Guidance

For operational scripts, prefer:

- usage docstring
- result dataclass
- manager class
- dry-run support
- structured CLI flags
- clear exit codes

## Output

Testing and release checklist sized to the change risk.
