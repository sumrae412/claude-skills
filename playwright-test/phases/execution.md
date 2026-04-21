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

