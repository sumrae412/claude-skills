## Phase 5: Reporting

### Test Result Format

For each test, report:

```markdown
## [US-ID]: [Title]

**Status**: PASS / FAIL / SKIP

**Steps Executed**:
1. [Step description] - [Result]
2. [Step description] - [Result]
...

**Evidence**:
- Snapshot taken at: [step]
- Screenshot: [if taken]

**Issues Found**:
- [Any issues or observations]

**Notes**:
- [Additional context]
```

### Summary Report

At the end of testing session:

```markdown
# E2E Test Results Summary

**Date**: [timestamp]
**Environment**: [Production/Local]
**Total Tests**: [count]
**Passed**: [count]
**Failed**: [count]
**Skipped**: [count]

## Results by Feature Area

| Feature | Total | Pass | Fail | Skip |
|---------|-------|------|------|------|
| Auth    |   4   |  3   |  1   |  0   |
| Clients |   5   |  5   |  0   |  0   |
| ...     |  ...  | ...  | ...  | ...  |

## Failed Tests

### [US-ID]: [Title]
- **Expected**: [what should happen]
- **Actual**: [what happened]
- **Evidence**: [snapshot/screenshot reference]

## Recommendations

1. [Issues to address]
2. [Suggested fixes]
```
