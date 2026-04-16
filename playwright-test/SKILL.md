# Playwright Test Skill - Interactive E2E Testing from User Stories

Execute comprehensive end-to-end tests using Playwright MCP tools, driven by user stories. This skill provides interactive browser testing with visual verification, screenshots, and detailed reporting.

## Overview

This skill uses the Playwright MCP tools (`browser_navigate`, `browser_snapshot`, `browser_click`, `browser_type`, etc.) to execute real browser tests against the application, validating user stories interactively.

**Target URL:** `your production URL (APP_URL)` (production) or `http://localhost:8000` (local)

## How This Works

1. **Load User Stories** - Read from `tests/e2e/USER_STORIES.md` or use `/user-stories` skill output
2. **Select Test Scope** - Choose feature area or specific user story to test
3. **Execute Tests** - Use Playwright MCP tools to interact with the live site
4. **Capture Evidence** - Take snapshots/screenshots at each step
5. **Report Results** - Provide pass/fail status with detailed findings

## Before Starting

Ask the user:
1. **Target environment**: Production (Heroku) or Local (localhost:8000)?
2. **Test scope**: Full suite, specific feature area, or single user story?
3. **Test credentials**: What email/password to use for authenticated tests?

## Phase 1: Environment Setup

### Step 1: Navigate to Target
```
Use browser_navigate to go to the target URL
- Production: your production URL (APP_URL)
- Local: http://localhost:8000
```

### Step 2: Take Initial Snapshot
```
Use browser_snapshot to capture the page structure
This provides element references (refs) for interactions
```

### Step 3: Verify Site is Accessible
Check the snapshot for:
- Login page elements (if not authenticated)
- Dashboard elements (if authenticated)
- Error messages or maintenance pages

## Phase 2: Authentication (if required)

### Login Flow
1. Navigate to `/auth/login`
2. Take snapshot to find form elements
3. Use `browser_type` to fill email field
4. Use `browser_type` to fill password field
5. Use `browser_click` to submit form
6. Take snapshot to verify dashboard loaded
7. Handle any modals (onboarding, cookie consent)

**Example Login Sequence:**
```
1. browser_navigate: {url: "https://[target]/auth/login"}
2. browser_snapshot: {} -> Get element refs
3. browser_type: {ref: "[email-input-ref]", text: "user@example.com"}
4. browser_type: {ref: "[password-input-ref]", text: "password"}
5. browser_click: {ref: "[submit-button-ref]"}
6. browser_wait_for: {text: "Dashboard"} or {time: 3}
7. browser_snapshot: {} -> Verify login success
```

## Phase 3: Test Execution by Feature Area

### Available Test Suites

| Suite | User Stories | Priority |
|-------|--------------|----------|
| Authentication | US-AUTH-001 to 004 | Critical |
| Client Management | US-CLIENT-001 to 005 | Critical |
| Workflows | US-WF-001 to 006 | Critical |
| Transactions | US-TXN-001 to 004 | High |
| Email | US-EMAIL-001 to 004 | High |
| Teams | US-TEAM-001 to 004 | Medium |
| Calendar | US-CAL-001 to 003 | Medium |
| Analytics | US-ANALYTICS-001 to 002 | Medium |
| Documents | US-DOC-001 to 003 | Medium |
| Navigation | US-NAV-001 to 003 | High |

### Test Execution Pattern

For each acceptance criterion:

1. **Setup**: Navigate to starting page, take snapshot
2. **Action**: Perform the user action using appropriate tool
3. **Verify**: Take snapshot, check for expected elements
4. **Record**: Log pass/fail with evidence

## Phase 4: Individual Test Procedures

### US-AUTH-001: New User Registration
```
Steps:
1. browser_navigate: /auth/login
2. browser_snapshot: Find "Register" or "Sign Up" link
3. browser_click: Register link
4. browser_snapshot: Verify registration form loaded
5. Check for required fields: name, email, password
6. browser_type: Fill test data
7. browser_click: Submit
8. browser_snapshot: Verify success or validation errors
```

### US-AUTH-002: User Login
```
Steps:
1. browser_navigate: /auth/login
2. browser_snapshot: Find login form elements
3. browser_type: Fill email
4. browser_type: Fill password
5. browser_click: Submit
6. browser_wait_for: Dashboard text or URL change
7. browser_snapshot: Verify dashboard loaded
```

### US-CLIENT-001: View Client List
```
Steps:
1. (Ensure authenticated)
2. browser_navigate: /clients/
3. browser_snapshot: Check for client list or empty state
4. Verify elements: search input, sort dropdown, client cards/rows
5. browser_type: Test search functionality
6. browser_click: Test sort dropdown
```

### US-CLIENT-002: Add New Client
```
Steps:
1. browser_navigate: /clients/add
2. browser_snapshot: Find client type selection
3. browser_click: Select "Buyer" type card
4. browser_snapshot: Verify form fields appeared
5. browser_type: Fill first_name, last_name, email, phone
6. browser_click: Submit button
7. browser_wait_for: Success message or redirect
8. browser_snapshot: Verify client created
```

### US-WF-001: View Workflow Templates
```
Steps:
1. browser_navigate: /workflows/templates OR /automations
2. browser_snapshot: Check for template list
3. Verify: template cards, create button, search/filter
```

### US-NAV-001: Desktop Navigation
```
Steps:
1. browser_navigate: /dashboard
2. browser_snapshot: Check sidebar elements
3. browser_click: Each main nav item
4. browser_snapshot: Verify page loaded
5. Repeat for all navigation items
```

### US-NAV-002: Mobile Navigation
```
Steps:
1. browser_resize: {width: 390, height: 844}
2. browser_navigate: /dashboard
3. browser_snapshot: Find hamburger menu
4. browser_click: Hamburger menu
5. browser_snapshot: Verify mobile menu opened
6. browser_click: Menu items
```

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

## Playwright MCP Tools Reference

### Navigation
- `browser_navigate`: Go to URL
- `browser_navigate_back`: Go back in history

### Inspection
- `browser_snapshot`: Get accessibility tree with element refs (PREFERRED)
- `browser_take_screenshot`: Capture visual screenshot

### Interaction
- `browser_click`: Click element by ref
- `browser_type`: Type text into element
- `browser_fill_form`: Fill multiple form fields
- `browser_select_option`: Select dropdown option
- `browser_hover`: Hover over element
- `browser_press_key`: Press keyboard key

### Waiting
- `browser_wait_for`: Wait for text, text gone, or time

### Utilities
- `browser_resize`: Change viewport size
- `browser_console_messages`: Get console logs
- `browser_network_requests`: Get network activity
- `browser_tabs`: Manage browser tabs
- `browser_evaluate`: Run JavaScript
- `browser_close`: Close browser

## Best Practices

1. **Always take snapshots** before and after interactions
2. **Use refs from snapshots** for accurate element targeting
3. **Wait appropriately** for dynamic content to load
4. **Handle modals** that may block interactions
5. **Test both happy path and edge cases**
6. **Document all findings** with evidence

## Quick Start Commands

### Run Full Test Suite
```
1. Ask for credentials
2. Login to production site
3. Execute all critical path tests
4. Generate summary report
```

### Run Single Feature Tests
```
1. Ask which feature area
2. Run only those user stories
3. Report results
```

### Smoke Test
```
1. Login
2. Navigate to each main section
3. Verify pages load without errors
4. Report any issues
```

## Troubleshooting

### Common Issues

1. **Element not found**: Take fresh snapshot, check element visibility
2. **Login fails**: Verify credentials, check for 2FA requirement
3. **Modal blocking**: Use browser_click to dismiss, or browser_evaluate to close
4. **Timeout**: Increase wait time, check network status
5. **Wrong page**: Use browser_snapshot to verify current URL/content

### Debug Mode

For detailed debugging:
1. Take screenshot at each step
2. Check browser_console_messages for errors
3. Check browser_network_requests for failed API calls
4. Use browser_evaluate to inspect page state

## Session Flow

When user invokes `/playwright-test`:

1. **Greet and configure**:
   > Ready to run E2E tests using Playwright.
   >
   > **Configuration needed:**
   > - Target: Production (Railway) or Local?
   > - Scope: Full suite, feature area, or specific story?
   > - Credentials: Test user email and password?

2. **After configuration**, begin testing systematically
3. **Report results** as tests complete
4. **Provide summary** at end of session

## Integration with User Stories

This skill works best with `/user-stories` skill:

1. Run `/user-stories` to generate or review user stories
2. Run `/playwright-test` to execute those stories as tests
3. Use findings to update stories or fix bugs
