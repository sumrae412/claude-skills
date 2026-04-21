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

