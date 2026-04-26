# Project Bootstrap

Load this reference only when:

- `.claude/hooks.json` is missing, or
- project-scoped `MEMORY.md` is missing

Keep it out of the default hot path for projects that are already bootstrapped.

## Memory Bootstrap

Check in this order:

1. `$PROJECT/.claude/memory/MEMORY.md`
2. `$PROJECT/MEMORY.md`

If neither exists:

1. Choose the memory directory:
   - prefer `$PROJECT/.claude/memory/` if `.claude/` exists
   - otherwise use `$PROJECT/`
2. Create `MEMORY.md`:

```markdown
# Project Memory

<!-- Index of memory files. Each entry: - [Title](file.md) — one-line description -->
<!-- Keep entries under 150 chars. Content goes in individual files, not here. -->
```

3. Announce:
   `Created MEMORY.md for cross-session context — I'll populate it as I learn about the project.`

## Hook Bootstrap

Auto-generates project hooks once, then stays out of the way.

### Step 1: Detect Stack

Use `references/hook-templates.md` for signal files and tags.

Typical tags:

- `python`
- `alembic`
- `ruff`
- `has-env`
- `service-layer`
- `server-templates`

### Step 2: Generate `.claude/hooks.json`

Tier 1 hooks are always included:

- session context
- pre-compaction transcript backup
- post-commit memory update
- worktree guard
- credential leak scanner

Tier 2 hooks are conditional on stack tags:

- `.env` blocker
- linter-on-save
- service-layer safety guards
- UI skill reminders

### Credential Leak Scanner

Allowlist:

- `PATH`, `HOME`, `USER`, `SHELL`, `TERM`, `LANG`, `LC_*`
- `BUILD_ENV`, `NODE_ENV`, `PYTHON_VERSION`
- `CI`, `GITHUB_ACTIONS`

Block from AI context:

- `*_TOKEN`, `*_SECRET`, `*_KEY`, `*_PASSWORD`, `*_CREDENTIAL`
- `AWS_*`, `STRIPE_*`, `OPENAI_*`, `ANTHROPIC_*`
- `DATABASE_URL`, `REDIS_URL`

Implementation requirement:

- scrub process environment before spawning subagents or subprocesses
- log `[REDACTED]` for blocked variables

### Step 3: Generate Hook Scripts + Config

1. Copy parameterized scripts into `$PROJECT/scripts/hooks/`
2. Generate `scripts/hooks/hook-config.sh` with:
   - detected file categories
   - skill suggestions
   - linter command and glob
3. `chmod +x` the generated scripts

### Step 4: Confirm

Output a short table of generated hooks and ask the user to review
`hooks.json` before continuing.
