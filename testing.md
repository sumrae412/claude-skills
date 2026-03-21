# Testing Requirements

Standards and patterns for testing CourierFlow code.

## Every PR Must Include

1. **Unit tests** for new service methods (pytest, async)
2. **API tests** for new/modified routes (TestClient)
3. **Migration tests** if schema changes (up + down)

## Coverage Requirements

| Code Type | Minimum Coverage |
|-----------|-----------------|
| New feature code | 80% |
| Critical paths (workflow execution, calendar sync, payments) | 90% |
| Bug fixes | Must include reproducing test |

CI checks coverage on changed files — PRs below threshold are flagged.

## Test Pattern Example

```python
async def test_calculate_step_timestamps(db_session):
    """Eager time calculation: steps get scheduled_for based on event date."""
    template = await create_test_template(db_session, steps=[
        {"action": "EMAIL", "timing": {"type": "RELATIVE_TO_TARGET", "days": -7}},
        {"action": "SMS", "timing": {"type": "RELATIVE_TO_TARGET", "days": -1}},
        {"action": "TASK", "timing": {"type": "RELATIVE_TO_TARGET", "days": 3}},
    ])
    event_date = date(2026, 3, 15)
    instance = await workflow_service.create_instance(
        db_session, template_id=template.id, event_date=event_date
    )
    steps = sorted(instance.steps, key=lambda s: s.scheduled_for)
    assert steps[0].scheduled_for.date() == date(2026, 3, 8)   # -7 days
    assert steps[1].scheduled_for.date() == date(2026, 3, 14)  # -1 day
    assert steps[2].scheduled_for.date() == date(2026, 3, 18)  # +3 days
```

## Commands

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=app --cov-report=html tests/

# Run specific test file
pytest tests/test_workflow_service.py -v

# Run tests matching pattern
pytest -k "test_eager" -v
```

## What NOT to Test

- Archived code in `_archived/`
- Third-party APIs directly (mock them)
- E2E/Playwright tests (use `/playwright-test` skill when needed)
