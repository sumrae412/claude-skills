## Phase 4: Playwright Test Template

After user story approval, offer to generate a Playwright test template:

```typescript
import { test, expect } from '@playwright/test';

/**
 * US-[ID]: [Title]
 * [User story description]
 */
test.describe('[Feature]: [Story Title]', () => {

  test.beforeEach(async ({ page }) => {
    // Setup: Login, navigate, seed data
  });

  test('AC-1: [Criteria name]', async ({ page }) => {
    // Given [precondition]

    // When [action]

    // Then [assertion]
  });

  test('AC-2: [Criteria name]', async ({ page }) => {
    // Given [precondition]

    // When [action]

    // Then [assertion]
  });

  test('EC-1: [Edge case]', async ({ page }) => {
    // Edge case test
  });

  test('ERR-1: [Error scenario]', async ({ page }) => {
    // Error handling test
  });
});
```

