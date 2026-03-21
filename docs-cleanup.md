# Documentation Cleanup

Update all project documentation based on plans created or work completed, then clean up outdated files.

## Purpose

Keep documentation accurate and the docs directory organized by:
1. Updating specs, architecture docs, and requirements with implemented changes
2. Updating REMAINING_WORK.md and status files with completed work
3. Updating CLAUDE.md if architecture or key patterns changed
4. **Verifying plan status against actual codebase** before archiving
5. Archiving completed/superseded plans to docs/archive/
6. Removing duplicate or obsolete documentation

**CRITICAL**: Always verify implementation status by checking the codebase. Plans often show as "Ready" when features are already 80-100% implemented.

---

## Documentation Categories

### Category 1: Specifications (update when features change)
- `docs/CLIENT_PORTAL_SPEC.md` - Client portal features
- `docs/DOCUMENT_MANAGEMENT_SPEC.md` - Document system
- `docs/MAGIC_LINKS_SPECIFICATION.md` - Magic link system
- `docs/CHATBOT_REQUIREMENTS.md` - AI assistant capabilities

### Category 2: Architecture (update when structure changes)
- `docs/ui-design/UI_ARCHITECTURE.md` - Frontend architecture
- `docs/workflow_overhaul.md` - Workflow builder architecture
- `CLAUDE.md` - Overall system architecture and patterns

### Category 3: Status & Tracking (update after completing work)
- `docs/REMAINING_WORK.md` - Master implementation tracker
- `docs/WORKFLOW_BUILDER_STATUS.md` - Workflow builder progress
- `docs/OPTIMIZATION_HISTORY.md` - Performance optimization log

### Category 4: Roadmaps (update when priorities change)
- `docs/INTEGRATIONS_ROADMAP.md` - Integration priorities
- `docs/DATABASE_OPTIMIZATION_ROADMAP.md` - DB optimization plans

### Category 5: Implementation Plans (archive when complete)
- `docs/IMPLEMENTATION_PLAN_V2.md` - Current implementation plan
- `docs/CHATBOT_OPTIMIZATION_PLAN.md` - Chatbot improvements
- `docs/archive/*_PLAN.md` - Archived plans

### Category 6: Guides (update when features/APIs change)
- `docs/user-guides/*.md` - End-user documentation
- `docs/api/*.md` - API documentation
- `docs/deployment/*.md` - Deployment guides

---

## Workflow

### Step 1: Gather Session Context

Understand what was accomplished or planned this session:

```bash
# Check current changes
git status

# Check recent commits
git log --oneline -10 2>/dev/null || echo "No recent commits"

# Find recently modified docs
find docs -name "*.md" -mtime -1 2>/dev/null | head -20
```

Also review the conversation history for:
- Features implemented or modified
- Architecture decisions made
- New components or services added
- Bug fixes that changed behavior
- Plans that were created or executed

### Step 2: Identify Documentation to Update

Based on what was done, determine which docs need updates:

| If you did this... | Update these docs... |
|-------------------|---------------------|
| Implemented a feature | Spec file, REMAINING_WORK.md, relevant guides |
| Changed architecture | UI_ARCHITECTURE.md or CLAUDE.md |
| Added/modified API | docs/api/*.md, CLAUDE.md (if new patterns) |
| Completed a plan item | REMAINING_WORK.md, archive plan if fully done |
| Added integration | INTEGRATIONS_ROADMAP.md, CLAUDE.md |
| Performance optimization | OPTIMIZATION_HISTORY.md, DATABASE_OPTIMIZATION_ROADMAP.md |
| Changed workflow builder | WORKFLOW_BUILDER_STATUS.md, workflow_overhaul.md |
| Created a new plan | REMAINING_WORK.md (reference it) |

### Step 3: Update Specifications

For each relevant spec file, update to reflect current implementation:

1. Read the spec file
2. Compare against actual implementation in codebase
3. Update sections that are now implemented:
   - Mark features as "Implemented" or "Complete"
   - Add implementation details (file paths, API endpoints)
   - Remove or note deprecated approaches
4. Add "Last Updated" date

**Spec update format:**
```markdown
### Feature Name
**Status**: Implemented (2026-01-25)
**Location**: `app/services/feature_service.py`

[Updated description reflecting actual implementation]
```

### Step 4: Update Architecture Docs

If architecture changed, update the relevant docs:

**For UI_ARCHITECTURE.md:**
- New components added
- Component relationships changed
- State management updates
- New patterns introduced

**For CLAUDE.md:**
- New key files added
- Architecture patterns changed
- New services or models
- Updated data model relationships
- New environment variables

**For workflow_overhaul.md:**
- Workflow builder components
- Step types added
- API changes

### Step 5: Update Status & Tracking Files

**REMAINING_WORK.md updates:**
1. Mark completed items with `[x]`
2. Add completion dates for phases/milestones
3. Update phase status (COMPLETE, PARTIALLY COMPLETE, etc.)
4. Add any new work items discovered
5. Update "Last Updated" date

```markdown
### Phase X: Name (Weeks N-M) - COMPLETE
- [x] Task completed (2026-01-25)
- [x] Another task
- [ ] Still pending task
```

**WORKFLOW_BUILDER_STATUS.md updates:**
- Component completion status
- Feature implementation status
- Known issues resolved

**OPTIMIZATION_HISTORY.md updates:**
- Add new optimizations with date
- Document performance improvements
- Note techniques used

### Step 6: Update Roadmaps

If priorities changed or items were completed:

**INTEGRATIONS_ROADMAP.md:**
- Mark completed integrations
- Update priority order if changed
- Add new integration requirements

**DATABASE_OPTIMIZATION_ROADMAP.md:**
- Mark completed optimizations
- Update metrics achieved
- Add new optimization targets

### Step 7: Update Guides (if features changed)

If user-facing features changed, update relevant guides:
- `docs/user-guides/` - End-user documentation
- `docs/api/` - API documentation
- `docs/WORKFLOW_BUILDER_GUIDE.md` - Workflow builder usage

### Step 8: Verify Plan Status Against Codebase

**CRITICAL**: Before archiving any plan, verify its actual implementation status by checking the codebase. Plans often claim features are "ready to implement" when they're already fully or partially implemented.

**Use the Task tool with Explore agent** to verify each active plan:

```
For each plan in docs/plans/:
1. Read the plan's implementation steps
2. Use Task tool (subagent_type=Explore) to check if each component exists:
   - Schema files mentioned → Do they exist?
   - Service methods mentioned → Are they implemented?
   - API routes mentioned → Do the endpoints exist?
   - Templates mentioned → Are they created?
   - Tests mentioned → Do they pass?
3. Categorize the plan:
   - 100% Complete → Archive immediately
   - 90%+ Complete → Document remaining tasks, then archive
   - 50-90% Complete → Update plan with "Remaining Tasks" section
   - <50% Complete → Keep as active plan
```

**Example verification prompt for Task tool:**
```
Check what exists for [Plan Name]:
1. Does `app/schemas/[expected_file].py` exist?
2. Does `[ServiceName].[method_name]` method exist in `app/services/[file].py`?
3. Does `/api/[endpoint]` route exist in `app/routes/[file].py`?
4. Does `app/templates/components/[component].html` exist?
5. Do tests exist in `tests/api/test_[feature].py`?
Report which exist and which are missing.
```

**Update REMAINING_WORK.md with verified status:**
- Move fully implemented plans to "Fully Implemented (Ready to Archive)"
- Add "Remaining Tasks" section with specific file:line locations for partial implementations
- Remove incorrect "Ready" status from plans that are actually complete

### Step 9: Archive Verified-Complete Plans

For plans that are fully COMPLETED or SUPERSEDED (verified against codebase in Step 8):

```bash
# Create archive directory if needed
mkdir -p docs/archive/plans

# Move completed plan
git mv docs/plans/OLD_PLAN.md docs/archive/plans/OLD_PLAN.md
```

Add archive header to moved file:
```markdown
> **ARCHIVED**: 2026-01-25
> **Reason**: Fully implemented / Superseded by [NEW_PLAN.md]
> **Original Location**: docs/plans/OLD_PLAN.md
> **Verified**: Codebase check confirmed all components exist
```

### Step 10: Clean Up

**Find and handle:**
```bash
# Empty or stub files
find docs -name "*.md" -size -100c

# Potential duplicates
ls docs/*.md | sort

# Orphaned files (not referenced anywhere)
for f in docs/*.md; do
  name=$(basename "$f")
  if ! grep -r "$name" docs/ CLAUDE.md --include="*.md" -q 2>/dev/null; then
    echo "Potentially orphaned: $f"
  fi
done
```

**Verify links in CLAUDE.md:**
```bash
grep -oE '\./[^)]+\.md|\[.+\]\([^)]+\.md\)' CLAUDE.md | while read link; do
  path=$(echo "$link" | grep -oE '[^(]+\.md' | head -1)
  if [ ! -f "docs/$path" ] && [ ! -f "$path" ]; then
    echo "Broken link: $path"
  fi
done
```

### Step 11: Generate Summary

Provide a cleanup summary:

```markdown
## Documentation Cleanup Summary

**Date**: YYYY-MM-DD
**Session Context**: [Brief description of work done]

### Documents Updated

#### Specifications
- `docs/SPEC_NAME.md` - [What was updated]

#### Architecture
- `CLAUDE.md` - [What was updated]
- `docs/ui-design/UI_ARCHITECTURE.md` - [What was updated]

#### Status & Tracking
- `docs/REMAINING_WORK.md` - Marked X items complete, added Y new items
- `docs/WORKFLOW_BUILDER_STATUS.md` - [What was updated]

#### Roadmaps
- `docs/INTEGRATIONS_ROADMAP.md` - [What was updated]

#### Guides
- `docs/user-guides/X.md` - [What was updated]

### Files Archived
- `docs/archive/OLD_PLAN.md` - Reason: [completed/superseded]

### Files Deleted
- [None / List with reasons]

### New Documentation Created
- [None / List new files]

### Remaining Active Plans
- `docs/IMPLEMENTATION_PLAN_V2.md` - Phase X in progress
- `docs/CHATBOT_OPTIMIZATION_PLAN.md` - Stages 5-8 pending
```

---

## Decision Guidelines

### When to Update vs Create New

**Update existing doc when:**
- Adding implementation details to a spec
- Marking items complete
- Fixing outdated information
- Adding new sections to existing categories

**Create new doc when:**
- Entirely new feature area
- New architectural component
- User requests a new plan

### When to Archive vs Delete

**Archive** (move to docs/archive/) — **ONLY after codebase verification**:
- Completed implementation plans (verified 100% implemented)
- Superseded plans (contain useful history)
- Deferred feature plans (might revisit)

**Keep as active** (update remaining tasks):
- Plans showing 50-99% implementation
- Plans with specific bugs or wiring issues remaining

**Delete** (with user confirmation):
- Exact duplicates
- Empty/placeholder files
- Temporary drafts never completed
- Files with completely outdated info that has no historical value

### Files to Never Delete Without Asking

- CLAUDE.md
- docs/REMAINING_WORK.md
- Any file in docs/user-guides/
- Any file in docs/api/
- Any file in docs/deployment/
- Active specification files

---

## Quick Reference: File Purposes

| File | Purpose | Update When |
|------|---------|-------------|
| `CLAUDE.md` | AI assistant instructions, architecture | Architecture/patterns change |
| `REMAINING_WORK.md` | Master task tracker | Any work completed |
| `*_SPEC.md` | Feature specifications | Features implemented/changed |
| `*_REQUIREMENTS.md` | Feature requirements | Requirements met/changed |
| `UI_ARCHITECTURE.md` | Frontend structure | UI components change |
| `*_STATUS.md` | Implementation progress | Progress made |
| `*_ROADMAP.md` | Future plans | Priorities change |
| `*_PLAN.md` | Implementation plans | Plan executed (then archive) |
| `*_GUIDE.md` | How-to documentation | Features change |
| `OPTIMIZATION_HISTORY.md` | Performance log | Optimizations done |
