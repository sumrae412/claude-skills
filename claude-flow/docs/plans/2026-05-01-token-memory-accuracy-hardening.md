# Token, Memory, Learning, and Accuracy Hardening Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task.

**Goal:** Fix the five review findings and make the claude-flow workflow more token-efficient, memory-aware, learnable, and auditable.

**Architecture:** Keep the workflow docs as routers and move mechanical behavior into tested Python helpers. Prefer deterministic scripts for registry learning, memory retrieval, redaction artifacts, outline generation, and RAG injection; phase docs should call those scripts instead of asking the LLM to reconstruct behavior from prose.

**Tech Stack:** Python stdlib for most helpers, existing `pytest` suite, optional `openai`/`numpy` path in `scripts/rag.py`, Markdown phase/reference docs.

**Ruled Out:**
- Broad prompt rewrite — too much churn; fixes should target broken mechanics and stale references.
- Removing RAG outright — it is tested and useful, but needs an explicit workflow entrypoint.
- Replacing forced skill selection with retrieval — current workflow says curated selection shipped; fix evidence docs first, then rerun experiments separately if needed.

---

### Task 1: Make Registry Learning Update Dispatch Counters
**Type:** value_unit
**Depends on:** none

**Files:**
- Modify: `scripts/registry.py`
- Modify: `scripts/test_registry.py`

**Step 1: Write failing tests**

Add tests proving `compact_events()` increments `dispatches`, preserves/sets `last_updated`, and creates usable unknown-agent entries:

```python
def test_compact_events_increments_dispatch_count_and_timestamp(tmp_path):
    registry_path = tmp_path / "registry.json"
    events_path = tmp_path / "events.jsonl"
    registry_path.write_text(json.dumps({
        "schema_version": 2,
        "agents": {"reviewer:slow": {
            "prior": {"alpha": 1.0, "beta": 1.0},
            "dispatches": 14,
            "findings_produced": 0,
            "findings_used": 0,
            "findings_used_rate": 0.0,
            "missed_context_count": 0,
            "last_dispatched": None,
            "last_updated": None,
        }},
    }))
    events_path.write_text(json.dumps({
        "agent": "reviewer:slow",
        "success": False,
        "timestamp": "2026-05-01T12:00:00+00:00",
    }) + "\n")

    compact_events(registry_path, events_path)

    data = json.loads(registry_path.read_text())
    agent = data["agents"]["reviewer:slow"]
    assert agent["prior"] == {"alpha": 1.0, "beta": 2.0}
    assert agent["dispatches"] == 15
    assert agent["last_updated"] == "2026-05-01T12:00:00+00:00"
    assert events_path.read_text() == ""
```

Run: `python3 -m pytest scripts/test_registry.py -q`
Expected: FAIL before implementation.

**Step 2: Implement minimal registry compaction**

In `compact_events()`, after `bayesian_update()`:

```python
agent = agents[key]
agent["prior"] = bayesian_update(agent["prior"], ev["success"])
agent["dispatches"] = int(agent.get("dispatches", 0)) + 1
timestamp = ev.get("timestamp")
if timestamp:
    agent["last_updated"] = timestamp
    agent.setdefault("last_dispatched", timestamp)
```

If events include optional counters, accumulate them defensively:

```python
for field in ("findings_produced", "findings_used", "missed_context_count"):
    if field in ev:
        agent[field] = int(agent.get(field, 0)) + int(ev[field])
produced = int(agent.get("findings_produced", 0))
used = int(agent.get("findings_used", 0))
agent["findings_used_rate"] = (used / produced) if produced else 0.0
```

**Step 3: Verify**

Run:

```bash
python3 -m pytest scripts/test_registry.py -q
python3 -m pytest scripts/test_moe_router.py -q
```

Expected: PASS.

---

### Task 2: Add the Missing Repo Outline Helper
**Type:** value_unit
**Depends on:** none

**Files:**
- Create: `scripts/generate_repo_outline.py`
- Create: `scripts/test_generate_repo_outline.py`
- Modify: `phases/phase-2-exploration.md`

**Step 1: Write failing tests**

Create tests that build a tiny Python package and assert the helper prints file paths plus class/function signatures without function bodies.

```python
def test_generate_repo_outline_emits_signatures_without_bodies(tmp_path):
    src = tmp_path / "app" / "services" / "tenant.py"
    src.parent.mkdir(parents=True)
    src.write_text(
        "class TenantService:\n"
        "    def create(self, name: str) -> str:\n"
        "        secret = 'body should not appear'\n"
        "        return name\n"
        "async def fetch_tenant(tenant_id: int) -> dict:\n"
        "    return {}\n"
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/generate_repo_outline.py",
            str(src.parent),
            "--max-depth",
            "2",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "tenant.py" in result.stdout
    assert "class TenantService" in result.stdout
    assert "def create(self, name: str) -> str" in result.stdout
    assert "async def fetch_tenant(tenant_id: int) -> dict" in result.stdout
    assert "body should not appear" not in result.stdout
```

Run: `python3 -m pytest scripts/test_generate_repo_outline.py -q`
Expected: FAIL because script is missing.

**Step 2: Implement helper**

Use `argparse`, `ast`, and `pathlib`. Behavior:

- Accept one or more roots.
- Skip `_archived`, `.git`, `.venv`, `venv`, `node_modules`, `__pycache__`.
- Respect `--max-depth` relative to each root.
- For Python files, print imports, top-level classes, functions, async functions, and method signatures.
- For non-Python files, print only the path unless `--include-non-python` is false by default.

Core implementation shape:

```python
def signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    args = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""
    prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
    return f"{prefix} {node.name}({args}){returns}"
```

**Step 3: Update Phase 2 docs**

Change the command to:

```bash
python3 <claude-flow-root>/scripts/generate_repo_outline.py app/services/ --max-depth 2
```

Replace “always run both” with: run `repomix --compress` only when the outline leaves material architecture gaps.

**Step 4: Verify**

Run:

```bash
python3 -m pytest scripts/test_generate_repo_outline.py -q
python3 scripts/generate_repo_outline.py scripts --max-depth 1 | head -80
```

Expected: tests pass and output is compact signatures.

---

### Task 3: Bring Memory Injection Script Up to the Reference Contract
**Type:** value_unit
**Depends on:** none

**Files:**
- Modify: `scripts/match_memory_domains.py`
- Create: `scripts/test_match_memory_domains.py`
- Modify: `references/memory-injection.md`

**Step 1: Write failing tests for direct and expanded memory**

Test these behaviors:

- Direct domain matches still work.
- `## Related` one-hop entries are returned, capped at 3, deterministic by co-citation then slug.
- `knowledge/concepts/*.md` articles are selected by `sources:` overlap with matched domains, capped at 3.
- `.claude/abandoned/*.md` entries are selected only when younger than 30 days when a current date is supplied.

Example test fixture:

```python
def test_related_entries_are_returned_with_direct_matches(tmp_path):
    memory = tmp_path / "memory"
    memory.mkdir()
    (memory / "MEMORY.md").write_text(
        "- [Client sync map](client_sync_map.md) — Keep maps centralized.\n"
        "- [Counts endpoint](counts_endpoint.md) — Use shared counts API.\n"
    )
    (memory / "client_sync_map.md").write_text(
        "# Client sync map\n\n## Related\n- [counts_endpoint] — shared UI/API boundary\n"
    )
    result = run_match(memory, ["app/services/client_service.py"])
    assert any(e["key"] == "client-sync-map" for e in result["matched_entries"])
    assert any(e["key"] == "counts-endpoint" for e in result["related_entries"])
```

Run: `python3 -m pytest scripts/test_match_memory_domains.py -q`
Expected: FAIL before implementation.

**Step 2: Implement deterministic expansion**

Add pure functions:

- `expand_related(memory_dir, matched_entries, limit=3) -> list[dict]`
- `select_compiled_articles(memory_dir, matched_domains, domain_table, limit=3) -> list[dict]`
- `select_abandoned(project_root_or_memory_dir, now, limit=3) -> list[dict]`

Extend JSON output:

```json
{
  "matched_entries": [],
  "related_entries": [],
  "compiled_articles": [],
  "abandoned_entries": [],
  "skipped": []
}
```

Keep raw formatting in the caller/LLM. The script should return structured entries only.

**Step 3: Update reference docs**

In `references/memory-injection.md`, make the script the source of truth for Steps 3-5b and document the new output keys. Remove any prose that implies the LLM should walk related files or concept files by hand.

**Step 4: Verify**

Run:

```bash
python3 -m pytest scripts/test_match_memory_domains.py -q
python3 -m pytest scripts/test_workflow_assets.py -q
```

Expected: PASS.

---

### Task 4: Preserve Review Redaction Summaries in Phase 6
**Type:** value_unit
**Depends on:** none

**Files:**
- Modify: `phases/phase-6-quality.md`
- Modify: `scripts/test_lint_workflow.py`
- Modify: `scripts/lint_workflow.py` if needed

**Step 1: Add or update workflow lint coverage**

Add a lint test that fails if Phase 6 documents only the raw `scrub_review_payload.py > /tmp/claude-flow-review.diff` pipe and does not mention `orchestrate.py scrub-diff` plus a redactions output.

Run: `python3 -m pytest scripts/test_lint_workflow.py -q`
Expected: FAIL before doc/lint update if guard is implemented.

**Step 2: Update Phase 6 active flow**

Replace the raw pipe with:

```bash
git diff "$REVIEW_BASE_SHA"..HEAD > /tmp/claude-flow-review.raw.diff

python3 <claude-flow-root>/scripts/orchestrate.py scrub-diff \
  /tmp/claude-flow-review.raw.diff \
  --output /tmp/claude-flow-review.diff \
  --redactions-output /tmp/review-redactions.json \
  --json
```

Keep the later `run_manifest.py record-review --redactions-file /tmp/review-redactions.json` command.

**Step 3: Verify**

Run:

```bash
python3 -m pytest scripts/test_scrub_review_payload.py scripts/test_lint_workflow.py -q
python3 scripts/lint_workflow.py --json
```

Expected: PASS and `lint_workflow` remains clean.

---

### Task 5: Restore Missing Experiment Evidence Links
**Type:** value_unit
**Depends on:** none

**Files:**
- Create: `docs/decisions/2026-04-29-ship-forced-selection-phase5.md`
- Create: `docs/plans/2026-04-29-skill-selection-vs-progressive-disclosure.md`
- Create: `docs/plans/2026-04-29-skill-selection-at-scale.md`
- Modify: `SKILL.md` only if references need exact file names instead of globs.
- Modify: `references/workflow-state-lifecycle.md` only if links need correction.

**Step 1: Add compact decision record**

Decision record must include:

- Decision: ship Variant B forced single-skill selection for Phase 5.
- Status/date.
- Evidence summary from the existing scripts and stated experiment result.
- Reproduction commands:

```bash
python3 scripts/replay_skill_selection.py --variant a,b --dry-run
python3 scripts/analyze_skill_selection.py --log .claude/experiments/skill_selection_ab.jsonl
```

- Caveat: raw logs are not bundled unless `.claude/experiments/` exists locally.

**Step 2: Add compact experiment plan docs**

For the A/B plan and scale plan, document:

- Hypothesis.
- Dataset shape.
- Metrics: loaded rate, correct skill, need-aware load, overload, end-task pass.
- Decision threshold.
- Scripts used.
- Known contamination guard: split variant prompt tails.

**Step 3: Verify internal references**

Run:

```bash
test -f docs/decisions/2026-04-29-ship-forced-selection-phase5.md
test -f docs/plans/2026-04-29-skill-selection-vs-progressive-disclosure.md
test -f docs/plans/2026-04-29-skill-selection-at-scale.md
python3 scripts/lint_workflow.py --json
```

Expected: all commands pass.

---

### Task 6: Wire RAG Experience Retrieval Into the Workflow
**Type:** value_unit
**Depends on:** T1 (knowledge)

**Files:**
- Modify: `scripts/rag.py`
- Modify: `scripts/test_rag.py`
- Modify: `phases/phase-2-exploration.md`
- Modify: `references/dispatch-pipeline.md`

**Step 1: Write failing CLI tests**

Add tests around new CLI parser functions without making network calls:

- `extract` reads an exploration log and writes JSONL chunks.
- `format` reads JSONL chunks and prints a `PRIOR EXPERIENCE` block.
- `query` gracefully skips with a clear message when embeddings or API key are unavailable.

Example:

```python
def test_extract_cli_writes_chunks_jsonl(tmp_path):
    log = tmp_path / "log.json"
    out = tmp_path / "chunks.jsonl"
    log.write_text(json.dumps(SAMPLE_EXPLORATION_LOG))

    assert rag_main(["extract", "--log", str(log), "--out", str(out)]) == 0
    lines = out.read_text().splitlines()
    assert lines
    assert "patterns_found" in lines[0]
```

**Step 2: Implement minimal CLI**

Add subcommands:

```bash
python3 scripts/rag.py extract --log <exploration-log.json> --out <chunks.jsonl>
python3 scripts/rag.py format --chunks <chunks.jsonl> --limit 5
python3 scripts/rag.py query --store .claude/rag --text "<task>" --phase phase-2 --fingerprint '{"languages":["python"]}'
```

Rules:

- `query` returns exit code 0 with empty output if store is missing.
- If `OPENAI_API_KEY` is missing, print a concise skip message to stderr and return 0.
- Never block the main workflow on RAG.

**Step 3: Update Phase 2 prior-knowledge check**

Add RAG as an optional check after MEMORY/PRP:

```bash
python3 <claude-flow-root>/scripts/rag.py query \
  --store .claude/rag \
  --text "<task summary>" \
  --phase phase-2 \
  --fingerprint '<json fingerprint>'
```

Instruction: inject at most 5 chunks and only when output is non-empty.

**Step 4: Verify**

Run:

```bash
python3 -m pytest scripts/test_rag.py -q
python3 scripts/rag.py format --help
```

Expected: PASS.

---

### Task 7: Final Cross-Workflow Verification
**Type:** shared_prerequisite
**Depends on:** T1, T2, T3, T4, T5, T6 (build)

**Files:**
- No new code expected.

**Step 1: Run targeted tests**

```bash
python3 -m pytest \
  scripts/test_registry.py \
  scripts/test_moe_router.py \
  scripts/test_generate_repo_outline.py \
  scripts/test_match_memory_domains.py \
  scripts/test_scrub_review_payload.py \
  scripts/test_lint_workflow.py \
  scripts/test_rag.py \
  -q
```

Expected: PASS.

**Step 2: Run full script suite**

```bash
python3 -m pytest scripts -q
```

Expected: PASS. Current baseline before this plan was `289 passed in 19.42s`.

**Step 3: Run workflow/security linters**

```bash
python3 scripts/lint_workflow.py --json
python3 scripts/lint_skill_metadata.py --skill-root . --json
python3 scripts/lint_skill_security.py --skill-root . --json
```

Expected: all report `"ok": true`.

**Step 4: Manual spot checks**

Run:

```bash
python3 scripts/generate_repo_outline.py scripts --max-depth 1 | head -80
printf "scripts/registry.py\nscripts/rag.py\n" | python3 scripts/match_memory_domains.py /tmp/nonexistent-memory-dir
```

Expected: outline is compact; memory matcher gracefully returns empty matches/skips when no `MEMORY.md` exists.

---

## Execution Notes

- Implement tasks in order unless only documentation tasks are split into a separate commit.
- Recommended commits:
  1. `fix: update registry learning counters`
  2. `feat: add repo outline helper`
  3. `feat: expand deterministic memory injection`
  4. `fix: preserve review redaction summaries`
  5. `docs: restore skill-selection evidence records`
  6. `feat: wire rag retrieval into workflow`
- Keep `_archived/` untouched.
- Do not change the default forced-selection behavior unless a new experiment is run and documented.
