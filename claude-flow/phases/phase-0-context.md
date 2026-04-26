# Phase 0: Context Loading + Phase 0.5: Hooks Bootstrap

<!-- Loaded: on workflow start | Dropped: after transition to Phase 1 -->

---

## Phase 0 Goals

Load only the context that changes how the workflow should behave:

- project identity and boundaries
- task-scoped skills
- enforcement skills
- bootstrap helpers only when the project actually needs them

Do not initialize the workflow state machine by default. That decision is
path-dependent and is deferred until Phase 1 unless an existing state file is
already present.

## Phase 0: Context Loading

<HARD-GATE>
Load project context before exploration or coding.
</HARD-GATE>

### Step 0: Cheap Workflow-State Check

Check whether `.claude/workflow-state.json` already exists.

- **If it exists:** load `references/workflow-state-lifecycle.md` and decide
  whether to resume or archive.
- **If it does not exist:** do nothing yet. Phase 1 initializes workflow state
  only if the chosen profile in `../workflow-profiles.json` has
  `state_machine: true`.

**Parallel-agent reflog check:** When another agent may be active, run:

```bash
git branch --show-current
git reflog -20
git fetch origin --prune
git log origin/main --oneline -10
```

If HEAD has moved since the last inspection, re-plan from current state.

### Step 1: Load Project Identity

Read the workspace `CLAUDE.md` (or equivalent project identity file) for:

- terminology
- boundaries
- stack
- workflow constraints

### Step 2: Load Core Skill

If the workspace has a core project skill, load it for the trigger matrix and
local conventions.

### Step 3: Classify Task -> Load Contextual Skills

Use the project's trigger matrix to load only the skills relevant to this task:

```text
templates / CSS / HTML?     -> UI skill
routes / services?          -> API skill
models / migrations?        -> data skill
external APIs?              -> integrations skill
git / deploy / PR?          -> git skill
auth / security?            -> security skill
```

Do not bulk-load unrelated skills.

### Step 4: Load Enforcement Skills

Always load:

- `coding-best-practices`

Conditionally load:

- UI work -> `defensive-ui-flows`
- backend work -> `defensive-backend-flows`
- both surfaces -> both

### Step 5: Conditional Tools

| Condition | Action |
|-----------|--------|
| External API work | Prefer MCP. If no MCP exists, invoke `/fetch-api-docs` before coding. |
| Codebase is large or unfamiliar | Use `generate_repo_outline.py` and `repomix --compress` only if they reduce exploration cost. |
| Need symbol precision | Activate Serena and read only the relevant memories. |
| MCP-heavy exploration | Raise `MAX_MCP_OUTPUT_TOKENS` only when needed. |
| Small familiar codebase | Skip all extras. |

Follow the policy from `SKILL.md`:

- MCP first
- CLI second
- direct HTTP only as fallback

### Step 6: Git Check

Verify you are on a feature branch before proceeding.

### Step 7: Optional Bootstrap

Load `references/project-bootstrap.md` only if either of these is true:

- project-scoped `MEMORY.md` is missing
- `.claude/hooks.json` is missing

If `MEMORY.md` is missing, create it using the bootstrap reference.

**State handoff:** transition to Phase 0.5 if hooks are missing; otherwise go to
Phase 1. Canonical transitions live in `../workflow-profiles.json`.

---

## Phase 0.5: Bootstrap Project Hooks (One-Time)

<SKIP-CONDITION>
Skip if `.claude/hooks.json` already exists.
</SKIP-CONDITION>

Load `references/project-bootstrap.md` and perform only the hook bootstrap
portion:

1. detect stack signals using `references/hook-templates.md`
2. generate `.claude/hooks.json`
3. generate hook scripts and `hook-config.sh`
4. confirm the generated hook summary with the user

Keep hook bootstrap details out of the default hot path once the project is
initialized.
