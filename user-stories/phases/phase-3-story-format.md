## Phase 3: User Story Format

Generate stories in this Playwright-optimized format:

```markdown
## US-[ID]: [Title]

**As a** [user type]
**I want to** [action/goal]
**So that** [benefit/value]

### Preconditions
- [ ] User is [logged in / on specific page / has specific data]
- [ ] [Required state exists]

### Steps (Happy Path)
1. User [action] → sees [result]
2. User [action] → sees [result]
3. User [action] → sees [result]
4. System [action] → user sees [result]

### Acceptance Criteria

#### AC-1: [Criteria name]
- **Given** [initial state]
- **When** [action taken]
- **Then** [expected result]
- **And** [additional expectations]

#### AC-2: [Criteria name]
- **Given** [initial state]
- **When** [action taken]
- **Then** [expected result]

### Edge Cases

#### EC-1: [Edge case name]
- **Given** [edge case state]
- **When** [action taken]
- **Then** [expected behavior]

#### EC-2: [Edge case name]
- **Given** [edge case state]
- **When** [action taken]
- **Then** [expected behavior]

### Error Scenarios

#### ERR-1: [Error scenario]
- **Given** [state leading to error]
- **When** [action taken]
- **Then** [error message/behavior]

### Test Data Requirements
- [Data needed to set up test]
- [Specific values or states required]

### Playwright Test Hints
- Page: `[URL or route]`
- Key selectors: `[important elements to target]`
- API calls to mock/intercept: `[endpoints]`
- Wait conditions: `[what to wait for]`
```

