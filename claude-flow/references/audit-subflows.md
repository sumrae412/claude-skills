# Audit Path Subflows

Reference for the audit path (Phase 1 triage option — see `audit_path.md` memory). Loaded on-demand when `$audit_scope` is populated and the user's intent is read-only assessment.

---

## Subflow A: Noisy-Signal Ingestion → Prioritized Checklist

**When to use:** The audit input is a log, CI output, or test run with many small findings (lint warnings, noisy test output, accessibility violations, type errors) and the goal is to turn that firehose into a ranked action list.

**Source:** Zach Kogan's (LaunchDarkly) tech-debt reduction workflow.

### Process

1. **Capture the noisy output** to a single file:

   ```bash
   yarn test 2>&1 | tee audit-inputs/test-noise.log
   # or
   ruff check app/ 2>&1 | tee audit-inputs/lint-noise.log
   # or
   yarn a11y 2>&1 | tee audit-inputs/a11y-noise.log
   ```

2. **Dispatch an analyst subagent** (Sonnet, general-purpose) with:

   - Input: the captured log (path only — let the subagent read it)
   - Prompt shape:

     ```
     Analyze this log file. Categorize findings by type and severity
     (CRITICAL / HIGH / MEDIUM / LOW). For each category, count occurrences
     and list the most common offenders (file:line). Output ONLY a markdown
     checklist, grouped by category, ordered by severity then frequency.
     Do NOT propose fixes — this is the audit pass.
     ```

3. **Write output** to `docs/audits/<YYYY-MM-DD>-<topic>-checklist.md`. Each line is a discrete, addressable task:

   ```markdown
   ## CRITICAL
   - [ ] `app/routes/auth.py:142` — silent except, swallows `KeyError` (3 occurrences across file)

   ## HIGH
   - [ ] `app/services/sync.py:88` — N+1 query pattern in `sync_contacts` loop
   ```

4. **Stop here.** The audit path is read-only. Fixes happen in a separate `/claude-flow` invocation where individual checklist items become $requirements.

### Why separate capture from analysis

Piping `yarn test` output directly to the subagent wastes context on retry-able tool output. Capturing to a file first means:

- Re-runs are free (subagent re-reads the file).
- The log is a durable artifact for the audit report.
- Tool-result clearing (Phase 5 Strategy 1) doesn't drop the evidence.

### Why the "no fixes in this pass" constraint matters

Analysts who propose fixes inline lose prioritization discipline. The audit deliverable is a ranked list of problems. Solutions are a later phase's problem — and often one fix resolves multiple checklist items, which you only see after the whole list is written.

---

## Subflow B: (reserved — codebase-health snapshot)

Future subflow for full-tree audits (complexity, cyclomatic scores, dependency graph). Not yet wired.

---

## Subflow C: Cleanup Audit (multi-dimension, deletion-aware)

**When to use:** `$audit_scope.intent` is "cleanup" / "tech debt" / "dead code" / "consolidate" / "tidy-up". Differs from Subflow A: input is the codebase, not a noisy log; output groups findings by *dimension* and ranks each by *confidence × risk* so that only safe deletions auto-execute.

**Source:** External 8-track cleanup prompt distilled to 3 claude-flow-native additions (deletion safety, AI-artifact dimension, cross-dimension gate).

### Dimensions to scan

Subagents fan out one-per-dimension (skip non-applicable ones — e.g., no circular-deps pass on a flat utility script):

1. **Duplication** — repeated code/types that cause drift.
2. **Unused code** — files, exports, functions, dependencies with no callers.
3. **Circular deps** — import cycles affecting maintainability.
4. **Type/contract weakness** — `any`/`Any`, untyped boundaries, overly broad return types.
5. **Misleading defensive code** — try/except that swallows, fallbacks that mask errors, validation that can't fire (see CLAUDE.md boundary 10 + `gate_on_gate_irony.md`).
6. **Legacy/deprecated paths** — old code marked dead but still imported, feature-flag branches with no live consumer.
7. **AI-generated artifacts** — placeholder stubs, TODO narration, edit-history comments ("// removed X", "// added for Y flow"), restating-what-the-code-does comments. Distinct from `vanity-engineering-review` which targets overengineering.
8. **Dependency hygiene** — unused packages, version-conflict shims, abandoned lockfile entries.

### Per-finding grading

Each finding must carry both axes:

```yaml
- finding: "app/services/legacy_auth.py — appears unused"
  dimension: unused_code
  confidence: high   # high | medium | low
  risk: low          # low | medium | high
  evidence: "no imports found via grep; no string-based references; not in entry-points"
  dynamic_usage_check: passed   # see checklist below
```

**Auto-implement only:** `confidence: high` AND `risk: low` AND `dynamic_usage_check: passed`. Everything else is flagged in the report for human decision.

### Dynamic-usage checklist (REQUIRED before any deletion finding is graded `risk: low`)

Before claiming code is unused, verify it is NOT referenced by:

- **Reflection / introspection** — `getattr`, `globals()`, `__all__`, `importlib.import_module(name)`
- **String-based lookups** — registry dicts, dispatch tables, plugin discovery, `SKILL.md` frontmatter, `reviewer-registry.json`-style configs
- **Framework conventions** — route handlers found by decorator scan, fixtures by name, Alembic migrations by filename, pytest discovery
- **Hooks / settings** — `~/.claude/settings.json` hook commands, `.pre-commit-config.yaml`, GitHub Actions workflows, package.json scripts
- **Code generation** — templates rendered by Jinja/string interpolation; stubs read by `inject_lookups.py`-style tooling
- **External call sites** — published API consumers, CLI users (`gh`, npm scripts), webhook handlers
- **Migration / compat shims** — explicitly kept for backwards compat (check git log for "compat" / "deprecated" markers)

If ANY check is unverified, downgrade to `risk: medium` and flag for human review. Don't auto-delete.

### Cross-dimension coordination gate

After all dimension subagents return, BEFORE writing the audit report, run a synthesis pass:

1. **Detect overlap.** If two dimensions touch the same file/symbol (e.g., dim 2 says "delete `legacy_auth.py`" and dim 6 says "rip out feature flag `OLD_AUTH`"), they're coupled.
2. **Detect architectural changes.** If findings imply renaming a public API, splitting a module, or changing a contract, that's not a cleanup — it's a refactor.
3. **For coupled or architectural findings:** present a short combined risk assessment FIRST. Block auto-implementation pending user direction. Single-dimension, isolated findings flow through normally.

Output the synthesis as a "## Coordination Notes" section above the per-dimension checklists.

### Report shape

`docs/audits/<YYYY-MM-DD>-cleanup.md`:

```markdown
# Cleanup Audit — <date>

## Coordination Notes
- [ ] FILES `legacy_auth.py` + `OLD_AUTH` flag (dims 2+6): coupled — see combined risk note before either deletion.
- [ ] DIMENSION 4+5 overlap on `app/utils/result.py`: type narrowing changes which exceptions throw.

## Auto-implementable (high-confidence, low-risk)
### Duplication
- [ ] `app/utils/dates.py:42` — `format_date()` duplicate of `format_date()` in `app/helpers/time.py`. Evidence: identical body, both exported. Dynamic check: both grep-discoverable, no string-lookup uses.

### AI-artifacts
- [ ] `app/services/sync.py:88` — comment `// added for the Y flow — handles case from #123` describes history not intent. Safe to remove.

## Flagged for human review (medium+ risk OR medium- confidence)
### Unused code
- [ ] `app/legacy/exporter.py` — no imports found, BUT registered as a CLI subcommand via `pyproject.toml [project.scripts]`. Risk: medium. Recommend deprecation notice + 1 release before removal.

### Type weakness
- [ ] `app/api/webhook.py:14` — `payload: dict[str, Any]`. Boundary type may be legitimate (incoming JSON). Recommend narrowing only after reviewing 3 known callers.
```

### Why this is read-only

Same as Subflow A: the audit deliverable is the prioritized list. Auto-implementation of "high-confidence, low-risk" items is a separate `/claude-flow` invocation where each checked box becomes a `$requirements` entry. Keeps the deletion path through Phase 4/5 verification gates instead of skipping straight to `git rm`.

---

## Related

- `audit_path.md` (memory) — Phase 1 8th triage path, scope → assessment → report flow
- `batch_similar_agents.md` (memory) — fan-out sizing for multi-file audits
- `n_per_entity_fanout.md` (memory) — one-reviewer-per-file for large `$audit_scope.file_count`
