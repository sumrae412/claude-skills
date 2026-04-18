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

