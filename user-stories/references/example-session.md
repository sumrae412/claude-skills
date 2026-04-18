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

