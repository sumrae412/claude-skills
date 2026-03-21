# Pre-Deployment Validation

Run all validation checks before deploying to production.

## Command

```bash
./scripts/quick_ci.sh --core
```

This single command runs:
- Python syntax & imports
- Deprecated syntax detection
- Import cycle detection
- SQLAlchemy relationship validation (pre_deployment_validation.py)
- Critical lint errors
- Model-migration alignment tests
- UI state consistency tests
- Template block name validation
- Orphaned JavaScript detection
- UI button handler validation
- Full unit/api/integration test suite (~2min)

## On Failure

- If validation fails: Run `python -c "from sqlalchemy.orm import configure_mappers; configure_mappers()"` to see detailed SQLAlchemy errors
- If tests fail: Review the specific failures and fix before deploying
- For full validation: `./scripts/validate_all.sh`

## Success Criteria

All checks must pass with no errors before deployment is safe.
