# Railway Deployment

Deploy the application to Railway production environment.

## Railway Project Details

| Setting | Value |
|---------|-------|
| **Platform** | Railway |
| **Web URL** | Set via `APP_URL` env var |

## Full Deployment Sequence

Follow these steps in order. Do NOT skip ahead — each step must pass before proceeding.

### 1. Write & Run Tests (if code was changed)

If this deployment includes code changes (bug fixes, features, refactors):

1. **Create tests** for the changes in the appropriate test file:
   - Service logic → `tests/test_<service_name>.py` or relevant integration test file
   - API endpoints → `tests/test_<feature>_api.py` or `tests/test_ai_enhancements.py`
   - Integration/data flow → `tests/test_task_unification_integration.py` (for cross-service data)
   - Follow existing patterns in the test suite (fixtures, mocking style, class grouping)

2. **Run the tests** and verify they pass:
   ```bash
   pytest tests/<test_file>.py -v --no-cov -x
   ```

3. **Fix any failures** before proceeding. Re-run until green.

4. **Run related test suites** to check for regressions:
   ```bash
   pytest tests/test_ai_enhancements.py tests/test_task_unification_integration.py -v --no-cov
   ```

### 2. Update Documentation

If the changes are non-trivial:
- Update `docs/REMAINING_WORK.md` with bug fix notes or feature additions
- Update `CLAUDE.md` if architecture or patterns changed

### 3. Pre-Deployment Validation (REQUIRED)

Run the `/pre-deploy` skill to validate the codebase. This runs:
- Critical alignment tests
- Pre-deployment validation script
- Quick CI checks

**Manual check:** If `requirements.txt` was modified, run `pip install --dry-run -r requirements.txt` locally to verify dependency resolution succeeds. Pip conflicts are not caught by `quick_ci.sh` but will fail the Railway build.

### 4. Deploy to Railway

```bash
railway up
```

### 5. Verify Deployment

```bash
# Check logs for errors
railway logs

# Or check recent logs
railway logs --num 100
```

## Additional Commands

```bash
# Run a one-off command in Railway
railway run alembic upgrade head

# Open the app in browser
railway open

# Check service status
railway status

# View environment variables
railway variables
```

## Rollback (if needed)

```bash
# List recent deployments
railway deployments

# Rollback to a previous deployment via the Railway dashboard
# Railway supports instant rollbacks from the dashboard UI
```

## Post-Deployment Verification

1. Visit the web URL and verify the app loads
2. Check the logs for any startup errors
3. Test critical functionality (login, dashboard, workflows)

## Debugging "Code Not Updating"

If deployed code does not match the repo after push:
1. **Check build status** — Use Railway MCP `list-deployments` tool or `railway logs --build` to see if recent builds FAILED.
2. **Railway serves last success** — Failed builds do not replace the running deployment. "Redeploy" re-serves the old image.
3. **Common cause: dependency conflicts** — `pip install` failures in `requirements.txt` (version incompatibilities). Check build logs for pip resolution errors.
4. **Fix and push** — Resolve the conflict, push a new commit. Do not rely on the Redeploy button when builds are failing.
