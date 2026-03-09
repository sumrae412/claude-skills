---
name: quick-ci
description: Run quick CI checks before merge/deploy. Runs ./scripts/quick_ci.sh and reports results. Use before merging PRs or deploying.
---

# Quick CI Check

Run the project's quick CI validation before merging or deploying.

## Steps

1. Run the quick CI script:
   ```bash
   ./scripts/quick_ci.sh
   ```

2. If the user wants thorough testing (or passes `--core`), run with the core flag:
   ```bash
   ./scripts/quick_ci.sh --core
   ```

3. Report results clearly:
   - If all checks pass: confirm safe to merge/deploy
   - If any checks fail: list the failures and suggest fixes

## What It Checks (10 checks, ~20s)

1. Python syntax & imports
2. Deprecated syntax detection
3. Import cycle detection
4. SQLAlchemy relationship validation (critical — #1 production crash cause)
5. Critical lint errors (flake8 E9/F63/F7/F82)
6. Model-migration alignment tests
7. UI state consistency tests
8. Template block name validation
9. Orphaned JavaScript detection
10. UI button handler validation

With `--core` flag: adds full unit/api/integration test suite (~2min).

## When to Use

- Before merging any PR
- Before deploying to production
- After resolving merge conflicts
- When the user asks to validate changes

## Related

- For full validation: `./scripts/validate_all.sh`
- For deployment: use `/pre-deploy` then `/deploy`
