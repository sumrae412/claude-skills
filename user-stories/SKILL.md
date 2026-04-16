---
name: user-stories
description: Generate detailed, Playwright-testable user stories by exploring an existing codebase and asking targeted questions. Crawls routes, templates, and models, synthesizes context from docs, then produces acceptance criteria ready for test conversion. Use when creating user stories, acceptance criteria, or test specs for a web application. Pairs with the `playwright-test` skill for test execution.
---

# User Story Generator - Test-Ready Stories from Codebase Analysis

Generate detailed, Playwright-testable user stories by exploring the codebase and asking targeted questions. This skill crawls the project to understand existing features, then collaboratively builds comprehensive user stories with acceptance criteria.

## How This Works

1. **Read all documentation first** - README, CLAUDE.md, docs/*.md, design specs, architecture docs
2. **Explore the codebase** - Analyze routes, templates, models, and services
3. **Synthesize context** - Combine doc insights with code discoveries
4. **Ask targeted questions** - One at a time, referencing what you learned
5. **Generate user stories** - With detailed acceptance criteria
6. **Output Playwright-ready specs** - Stories structured for easy test conversion

**IMPORTANT:** Always read existing documentation before scanning code. Docs provide crucial context about why things are built a certain way, what the vision is, and what constraints exist.

## Phase 1: Codebase & Documentation Exploration

When invoked, FIRST explore documentation AND codebase before asking questions:

### Step 1: Read Existing Documentation
Search for and read any existing documentation to understand the app's purpose, architecture, and design decisions:

```
1. README.md, README.txt - Project overview
2. CLAUDE.md - AI assistant context and project rules
3. docs/**/*.md - All documentation files
4. docs/architecture*.md - System architecture
5. docs/design*.md - Design documents
6. docs/*requirements*.md - Requirements docs
7. docs/*spec*.md - Specifications
8. docs/api*.md - API documentation
9. CONTRIBUTING.md - Development guidelines
10. CHANGELOG.md - Feature history
11. Any .md files in root directory
```

**Documentation Discovery Commands:**
```bash
# Find all markdown documentation
find . -name "*.md" -type f | grep -v node_modules | grep -v venv

# Check for docs folder
ls -la docs/ 2>/dev/null

# Check for design/architecture docs
find . -name "*design*" -o -name "*architecture*" -o -name "*spec*" | grep -v node_modules
```

### Step 2: Scan Codebase Structure
After reading docs, explore the code:

```
1. Scan routes/endpoints to understand available features
2. Scan templates to understand UI pages and flows
3. Scan models to understand data structures
4. Identify key user workflows
5. Note authentication/authorization patterns
6. Check existing tests for behavior expectations
```

### Files to Explore

**Documentation (read first):**
- `README.md` - Project overview and setup
- `CLAUDE.md` - Project context and conventions
- `docs/**/*.md` - All documentation
- `docs/architecture*.md` - System design
- `docs/design*.md` - Feature designs
- `docs/*workflow*.md` - Workflow documentation
- `docs/*api*.md` - API specs
- `*.md` in root - Any other documentation

**Code (scan after docs):**
- `app/routes/*.py` - All API endpoints and page routes
- `app/templates/**/*.html` - UI pages and components
- `app/models/*.py` - Data models and relationships
- `app/services/*.py` - Business logic
- `tests/` - Existing test patterns and expected behaviors

## Phase 2: Feature Discovery Questions

After exploration, present findings and ask ONE question at a time:

### Opening
---
**User Story Discovery Session**

**Documentation Found:**
- [List any docs found: README, CLAUDE.md, design docs, etc.]
- [Note key insights from documentation]

**Key Context from Docs:**
- [App purpose/description from README]
- [Architecture notes if found]
- [Relevant design decisions]
- [Existing requirements or specs]

**Feature Areas Discovered:**

1. **[Feature Area 1]** - [brief description + any doc references]
2. **[Feature Area 2]** - [brief description + any doc references]
3. **[Feature Area 3]** - [brief description + any doc references]
...

**First question:** Which feature area would you like to create user stories for? Or describe a new feature you're planning to add.

---

### Discovery Questions (ask one at a time)

**User Context:**
- Who is the primary user for this feature?
- What is their role/permission level?
- What are they trying to accomplish?
- What's their starting point (which page, what state)?

**Happy Path:**
- What's the main success scenario?
- What steps do they take?
- What do they see at each step?
- What's the end state?

**Edge Cases:**
- What if they're not logged in?
- What if they don't have permission?
- What if required data is missing?
- What if the operation fails?
- What if they cancel midway?

**Validation:**
- What inputs are required?
- What are the validation rules?
- What error messages should appear?
- What are the field constraints?

**Visual/UX:**
- What loading states should appear?
- What success/error feedback is shown?
- Are there confirmation dialogs?
- What navigation happens after completion?

**Data:**
- What data is created/modified?
- What related data is affected?
- Are there audit/history requirements?
- What should happen to related records?

## Writing Rules

Before generating stories, apply these rules uniformly:

- **Cover all major user-facing flows** — no skipping auth, error paths, or edge states.
- **Consistent structure** — every story uses the template below; no deviation.
- **Strict Gherkin for acceptance criteria** — `Given` / `When` / `Then` / `And` only. No prose paragraphs, no mixed narrative + bullets.
- **Every step references observable UI behavior** — something a test runner can assert (visible text, element state, URL change, DOM attribute).
- **Ban vague language** — no "works correctly", "loads successfully", "behaves as expected", "is displayed properly". If a criterion can't name what's observable, rewrite it until it can.
- **Prefer testable anchors** — reference accessible labels (`aria-label`, role), visible text, or stable selectors that a Playwright test could target. Avoid brittle anchors (nth-child, auto-generated class names).
- **No implementation details** — stories describe user-visible behavior, not code, endpoints, or internal state transitions.

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

## Session Rules

1. **Read docs first** - Always read README, CLAUDE.md, and docs/ before anything else
2. **Then explore code** - Scan routes, models, templates, services
3. **Synthesize both** - Combine documentation insights with code discoveries
4. **One question at a time** - Wait for answer before proceeding
5. **Be specific** - Reference actual pages, buttons, fields from codebase AND docs
6. **Validate understanding** - Summarize after every 4-5 questions
7. **Think like a tester** - Ask about edge cases, errors, boundaries
8. **Cite sources** - Reference specific files, docs, routes when discussing features

## Question Patterns

### For New Features
- "What triggers this workflow?"
- "What data does the user need to provide?"
- "What happens if they provide invalid data?"
- "What confirmation does the user receive?"
- "Can they undo or cancel this action?"

### For Existing Features
- "I see [feature] exists at [route]. Is this working as expected?"
- "The current flow is [X]. Should it stay this way?"
- "I notice [edge case] isn't handled. What should happen?"
- "There's no validation for [field]. What rules should apply?"

### For Complex Workflows
- "Let's walk through step by step. After [step 1], what happens?"
- "If they abandon at [step], what state is preserved?"
- "Can they go back to [previous step]?"
- "What notifications/emails are triggered?"

## Ending the Session

When stories are complete, offer:

> We've defined [X] user stories with [Y] acceptance criteria. Would you like me to:
> 1. Save all stories to a markdown file
> 2. Generate Playwright test templates
> 3. Create a test plan document
> 4. All of the above

## Output Files

### User Stories Document
Save to: `docs/user-stories/[feature-name].md`

### Playwright Tests
Save to: `tests/e2e/[feature-name].spec.ts`

### Test Plan
Save to: `docs/test-plans/[feature-name]-test-plan.md`

## Example Session

```
User: /user-stories

Claude: [Reading documentation...]

Found and analyzed:
- README.md - Project overview
- CLAUDE.md - Development guidelines, architecture notes
- docs/workflow_overhaul.md - Workflow builder v7.0 requirements
- docs/INTEGRATION_DEVELOPMENT.md - Integration patterns

[Scanning codebase...]

**Documentation Summary:**
- This is a workflow automation platform for managing contacts, tasks, and automated communication sequences
- CLAUDE.md notes: Household-centric design, async-first, service layer pattern
- Workflow builder is being overhauled (v7.0) with timeline-based UI

**Feature Areas Discovered:**

1. **Authentication** - Login, registration, password reset, 2FA
2. **Contacts/Households** - CRUD, search, import, merge (household-centric per CLAUDE.md)
3. **Tasks** - Create, assign, complete, recurring tasks
4. **Workflows** - Template builder, assignments, execution (v7.0 overhaul in progress)
5. **Communications** - Email, SMS, templates
6. **Chat/AI** - AI assistant, queries, actions

Which feature area would you like to create user stories for?

User: Let's do task creation

Claude: Great choice. From the docs I see tasks are part of the core workflow system.

Code locations found:
- Routes: `app/routes/tasks.py`
- Models: `app/models/task.py`
- Service: `app/services/task_service.py`
- Templates: `app/templates/tasks/`

From the model, tasks have: title, description, due_date, priority, status, assigned_to, household_id.

Per CLAUDE.md, the architecture is "household-centric" - tasks belong to households.

**Question 1:** Who typically creates tasks - just the main user, or can team members also create them?

User: Both the main user and team members with appropriate permissions

Claude: Got it - role-based task creation. I see there's a Team model with role-based permissions mentioned in CLAUDE.md.

**Question 2:** When creating a task, which fields are required vs optional?

[...continues until complete...]
```

## Tips for Best Results

- Be specific about user roles and permissions
- Describe what success looks like visually
- Think about what could go wrong
- Consider mobile vs desktop if relevant
- Mention any time-sensitive aspects
- Share examples of similar features you like
