---
name: deprecation-and-migration
description: Manages deprecation and migration. Use when removing old systems, APIs, features, or skills. Use when migrating consumers from one implementation to another. Use when deciding whether to maintain or sunset existing code.
---

# Deprecation and Migration

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


## Overview

Code is a liability, not an asset. Every line has ongoing maintenance cost — bugs to fix, dependencies to update, security patches to apply, new engineers to onboard. Deprecation is the discipline of removing code that no longer earns its keep. Migration is the process of moving consumers safely from old to new.

Most teams are good at building things. Few are good at removing them. This skill addresses that gap.

## When to Use

- Replacing an old system, API, or library with a new one
- Sunsetting a feature that's no longer needed
- Consolidating duplicate implementations
- Removing dead code that nobody owns but everybody depends on
- Archiving skills or workflows that have been superseded
- Planning the lifecycle of a new system (deprecation planning starts at design time)
- Deciding whether to maintain a legacy system or invest in migration

## Core Principles

### Code Is a Liability

The value of code is the functionality it provides, not the code itself. When the same functionality can be provided with less code, less complexity, or better abstractions — the old code should go.

### Hyrum's Law Makes Removal Hard

With enough users, every observable behavior becomes depended on — including bugs, timing quirks, and undocumented side effects. This is why deprecation requires active migration, not just announcement.

### Deprecation Planning Starts at Design Time

When building something new, ask: "How would we remove this in 3 years?" Systems designed with clean interfaces, feature flags, and minimal surface area are easier to deprecate.

## The Deprecation Decision

Before deprecating anything, answer these questions:

```
1. Does this system still provide unique value?
   → If yes, maintain it. If no, proceed.

2. How many consumers depend on it?
   → Quantify the migration scope.

3. Does a replacement exist?
   → If no, build the replacement first. Don't deprecate without an alternative.

4. What's the migration cost for each consumer?
   → If trivially automated, do it. If manual and high-effort, weigh against maintenance cost.

5. What's the ongoing maintenance cost of NOT deprecating?
   → Security risk, engineer time, opportunity cost of complexity.
```

## Compulsory vs Advisory Deprecation

| Type | When to Use | Mechanism |
|------|-------------|-----------|
| **Advisory** | Migration is optional, old system is stable | Warnings, documentation, nudges. Consumers migrate on their own timeline. |
| **Compulsory** | Old system has security issues, blocks progress, or maintenance cost is unsustainable | Hard deadline. Old system removed by date X. Provide migration tooling. |

**Default to advisory.** Compulsory deprecation requires providing migration tooling, documentation, and support.

## The Migration Process

### Step 1: Build the Replacement

Don't deprecate without a working alternative. The replacement must:

- Cover all critical use cases of the old system
- Have documentation and migration guides
- Be proven in production (not just "theoretically better")

### Step 2: Announce and Document

```markdown
## Deprecation Notice: [System Name]

**Status:** Deprecated as of [date]
**Replacement:** [New System] (see migration guide below)
**Removal date:** [Advisory / hard date]
**Reason:** [Why the old system is being replaced]

### Migration Guide
1. [Step-by-step migration instructions]
2. [With concrete examples]
3. [And verification commands]
```

For skills/workflows in this repo, use the archive pattern:

```yaml
---
name: old-skill
description: ARCHIVED — Use /new-skill instead. [Brief reason for change.]
---

# ARCHIVED

This skill has been replaced by [new-skill], which adds:
- [Key improvement 1]
- [Key improvement 2]
```

### Step 3: Migrate Incrementally

Migrate consumers one at a time, not all at once:

```
1. Identify all touchpoints with the deprecated system
2. Update to use the replacement
3. Verify behavior matches (tests, integration checks)
4. Remove references to the old system
5. Confirm no regressions
```

**The Churn Rule:** If you own the infrastructure being deprecated, you are responsible for migrating your consumers — or providing backward-compatible updates that require no migration. Don't announce deprecation and leave consumers to figure it out.

### Step 4: Remove the Old System

Only after all consumers have migrated:

```
1. Verify zero active usage (metrics, logs, dependency analysis, grep)
2. Remove the code
3. Remove associated tests, documentation, and configuration
4. Remove the deprecation notices
5. Celebrate — removing code is an achievement
```

## Migration Patterns

### Strangler Pattern

Run old and new systems in parallel. Route traffic incrementally from old to new.

```
Phase 1: New system handles 0%, old handles 100%
Phase 2: New system handles 10% (canary)
Phase 3: New system handles 50%
Phase 4: New system handles 100%, old system idle
Phase 5: Remove old system
```

### Adapter Pattern

Create an adapter that translates calls from the old interface to the new implementation:

```python
class LegacyTaskService:
    """Adapter: old interface, new implementation."""
    def __init__(self, new_service: NewTaskService):
        self._new = new_service

    def get_task(self, task_id: int) -> dict:
        task = self._new.find_by_id(str(task_id))
        return self._to_old_format(task)
```

### Feature Flag Migration

Use feature flags to switch consumers one at a time:

```python
def get_task_service(user_id: str) -> TaskService:
    if feature_flags.is_enabled("new-task-service", user_id=user_id):
        return NewTaskService()
    return LegacyTaskService()
```

## Zombie Code

Zombie code is code that nobody owns but everybody depends on. Signs:

- No commits in 6+ months but active consumers exist
- No assigned maintainer
- Failing tests nobody fixes
- Dependencies with known vulnerabilities nobody updates

**Response:** Either assign an owner and maintain it, or deprecate it with a concrete migration plan. Zombie code cannot stay in limbo.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It still works, why remove it?" | Working code that nobody maintains accumulates security debt and complexity. |
| "Someone might need it later" | If needed later, it can be rebuilt. Keeping unused code "just in case" costs more. |
| "The migration is too expensive" | Compare migration cost to 2-3 years of ongoing maintenance. Migration is usually cheaper. |
| "We'll deprecate it after the new system is done" | Deprecation planning starts at design time. Plan now. |
| "Users will migrate on their own" | They won't. Provide tooling, docs, and incentives — or do it yourself (Churn Rule). |

## Out of Scope

This skill does NOT:
- Plan zero-downtime database/service cutover patterns or write rollback runbooks—use `migration-architect`.
- Generate Alembic migration files for schema changes—use `new-migration`.
- Execute the migration code edits across consumers—use `executing-plans` or `claude-flow`.
- Audit deprecated dependencies for CVEs/license risk—use `dependency-auditor`.
- Decide which legacy skills/files are dead—pair with `lint-memory` for memory hygiene or `cleanup` for branch teardown.

## Verification

After completing a deprecation:

- [ ] Replacement is production-proven and covers all critical use cases
- [ ] Migration guide exists with concrete steps and examples
- [ ] All active consumers have been migrated (verified by grep/metrics/logs)
- [ ] Old code, tests, documentation, and configuration are fully removed
- [ ] No references to the deprecated system remain in the codebase
- [ ] Deprecation notices are removed (they served their purpose)
