# Skill-Standards Rollout Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Institutionalize the 7-pattern skill-quality standard surfaced by the 2026-04-27 audit so every future SKILL.md in this repo passes the same bar without manual review.

**Architecture:** Add a written standard (`docs/skill-standards.md`), a deterministic Python linter (`scripts/lint-skills.py`) that checks each SKILL.md against the 7 patterns, and a pre-commit + CI hook that runs the linter on changed skills. Surface the standard in `MEMORY.md` so future skill authors load it before writing. Upstream propagation to plugin repos (anthropic-skills, superpowers) is explicitly OUT OF SCOPE for this branch — flagged as a follow-up task.

**Tech Stack:** Python 3.11 (stdlib only — `pathlib`, `re`, `sys`, `argparse`, `yaml` via `pyyaml` if frontmatter is non-trivial), pre-commit framework, GitHub Actions.

**Ruled Out:**
- Bash-only linter — regex over YAML frontmatter is fragile; Python with PyYAML is one extra dep but far simpler.
- LLM-based linter — non-deterministic, expensive, slow in CI; the 7 patterns are mechanical enough for regex/AST checks.
- Auto-fixing linter — the audit showed description rewrites need human judgment per skill (not template-fillable). Linter reports; humans edit.
- Splitting standard across multiple docs — one file is easier to keep authoritative.

---

## Task 1: Capture the 7 patterns as `docs/skill-standards.md`
**Type:** value_unit
**Depends on:** none

**Files:**
- Create: `docs/skill-standards.md`

**Step 1: Write the standard**

Create the file with these sections, in order:
1. Why this standard exists (one paragraph — context budget, routing accuracy, output consistency).
2. The 7 patterns, one section each, ~200 words each:
   - P1 Description tells WHEN, not just WHAT
   - P2 Directive tone (imperative verbs, numbered steps)
   - P3 Specify the output format
   - P4 Read-first step where applicable
   - P5 Out-of-Scope section (`## Out of Scope` with 3-5 bullets, each citing an alternative skill)
   - P6 Under 500 lines (use progressive disclosure for longer skills)
   - P7 Description quality: ≥120 chars, ≥3 trigger keywords/quoted phrases
3. "What kills skills" — the failure-pattern checklist from the audit.
4. Authoring checklist (7-line bulleted ready-reference, one per pattern).
5. How to run the linter locally (`python scripts/lint-skills.py [path]`).
6. How to request an exception (commit-message annotation `skip-skill-lint: <reason>` for grandfathered skills, with link to followup issue).

Each pattern section must include: rule, why, good example (cite a real skill from this repo using its filename), bad example (counter-example, anonymized).

**Step 2: Verify file renders cleanly**

Run: `markdownlint docs/skill-standards.md` if available; otherwise spot-check headings render.
Expected: no broken links, all skill citations point to real files in repo.

**Step 3: Commit**

```bash
git add docs/skill-standards.md
git commit -m "docs: add 7-pattern skill-quality standard"
```

---

## Task 2: Build `scripts/lint-skills.py`
**Type:** value_unit
**Depends on:** T1 (knowledge — needs the standard finalized so checks match)

**Files:**
- Create: `scripts/lint-skills.py`
- Create: `tests/test_lint_skills.py`

**Step 1: Write the failing test**

```python
# tests/test_lint_skills.py
import subprocess, textwrap, pathlib

def run_linter(tmp_path, skill_md_content):
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(skill_md_content)
    result = subprocess.run(
        ["python", "scripts/lint-skills.py", str(skill_dir)],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout

def test_passes_clean_skill(tmp_path):
    content = textwrap.dedent("""\
        ---
        name: test-skill
        description: A clearly described skill that triggers on "do X", "do Y", or when the user mentions "Z" — produces structured output. Use when starting a foo. NOT for bar (use other-skill).
        ---
        # Test
        ## Out of Scope
        This skill does NOT:
        - Do bar — use other-skill.
    """)
    code, out = run_linter(tmp_path, content)
    assert code == 0, out

def test_fails_short_description(tmp_path):
    content = "---\nname: x\ndescription: Too short\n---\n# X\n## Out of Scope\n- nope.\n"
    code, out = run_linter(tmp_path, content)
    assert code != 0
    assert "P7" in out or "description" in out.lower()

def test_fails_missing_out_of_scope(tmp_path):
    content = "---\nname: x\ndescription: " + ("trigger word " * 30) + "\n---\n# X\n"
    code, out = run_linter(tmp_path, content)
    assert code != 0
    assert "Out of Scope" in out or "P5" in out

def test_fails_over_500_lines(tmp_path):
    body = "## Out of Scope\n- thing.\n" + ("filler line\n" * 600)
    content = "---\nname: x\ndescription: " + ("trigger " * 30) + "\n---\n# X\n" + body
    code, out = run_linter(tmp_path, content)
    assert code != 0
    assert "P6" in out or "500" in out
```

**Step 2: Run tests to verify they fail**

Run: `pytest tests/test_lint_skills.py -v`
Expected: 4 FAIL with "lint-skills.py: No such file"

**Step 3: Implement the linter**

`scripts/lint-skills.py` — single-file Python, stdlib + PyYAML.

Public CLI:
```
lint-skills.py [paths...] [--strict] [--format {text,json}]
```

If no paths given, lints every `*/SKILL.md` under repo root (excluding `node_modules`, `.claude/worktrees`, `docs`, plugin caches).

Per-skill checks (return code 0 = all pass; non-zero = any fail):
- **P1+P7 description quality:**
  - description field present in frontmatter
  - len(description) ≥ 120 chars
  - description contains ≥3 of: quoted phrases (`"..."` or `'...'`), `Use when`, `Triggers`, `Use for`, `/<skill-slug>`, imperative trigger verbs
  - heuristic for "trigger keywords": count quoted phrases + count of `, ` separated items inside any `Triggers:` clause
- **P2 directive tone (advisory):** count imperative verbs at start of `##` body sections; warn (not fail) if ratio of "you can" / "could" exceeds threshold. Advisory only — don't gate.
- **P3 output format (advisory):** body contains at least one of: `## Output`, `## Deliverables`, `## Output Format`, fenced ```` ```...``` ```` block, table with header pipe. Warn if none found.
- **P4 read-first (advisory):** body mentions Read/grep/`git status`/inspect-before-act. Warn if absent in skills that produce code edits.
- **P5 out-of-scope (FAIL):** body contains a heading `## Out of Scope` (or `## When NOT to Use`) AND ≥3 bullets under it.
- **P6 length (FAIL):** body line count <500. Print actual count when fail.
- **frontmatter validity (FAIL):** parses as YAML; has `name` and `description`; `name` matches directory name.

Output format: one block per skill, color-coded if TTY:
```
SKILL: <path> [PASS|FAIL]
  P1+P7: PASS (143 chars, 4 triggers)
  P5:    FAIL — no `## Out of Scope` heading
  P6:    PASS (98 lines)
  ...
```

Strict mode (`--strict`): treat advisories as failures.

JSON mode emits one record per skill for CI consumption.

Honor a per-file pragma `<!-- skip-skill-lint: <reason> -->` near top of SKILL.md to grandfather a skill (with a TODO link).

**Step 4: Run tests to verify they pass**

Run: `pytest tests/test_lint_skills.py -v`
Expected: 4 PASS.

**Step 5: Run the linter on the repo**

Run: `python scripts/lint-skills.py`
Expected: PASS for every custom skill (the audit already brought them up to standard). If any FAIL, fix the skill — do not weaken the linter.

**Step 6: Commit**

```bash
git add scripts/lint-skills.py tests/test_lint_skills.py
git commit -m "feat: add scripts/lint-skills.py with 7-pattern checks"
```

---

## Task 3: Wire lint into pre-commit and CI
**Type:** value_unit
**Depends on:** T2 (build — linter must exist and pass on current repo)

**Files:**
- Modify: `.pre-commit-config.yaml` (create if missing)
- Modify: `.github/workflows/ci.yml` (or create `lint-skills.yml`)

**Step 1: Add pre-commit hook**

Append to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: lint-skills
      name: lint SKILL.md files
      entry: python scripts/lint-skills.py
      language: system
      files: 'SKILL\.md$'
      pass_filenames: true
```

`pass_filenames: true` so the hook only re-checks changed files — keeps commits fast.

**Step 2: Verify pre-commit fires**

Run:
```bash
pre-commit install
echo "" >> brevity/SKILL.md  # trivial change
git add brevity/SKILL.md
pre-commit run --files brevity/SKILL.md
```
Expected: `lint-skills` runs, returns PASS.

Test failure path: temporarily corrupt `brevity/SKILL.md` (delete `## Out of Scope` heading), rerun. Expected: FAIL with P5 message. Restore.

**Step 3: Add CI workflow**

Create or extend `.github/workflows/lint-skills.yml`:

```yaml
name: Lint skills
on:
  pull_request:
    paths:
      - "**/SKILL.md"
      - "scripts/lint-skills.py"
      - ".github/workflows/lint-skills.yml"
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install pyyaml
      - run: python scripts/lint-skills.py --strict --format json
```

**Step 4: Verify CI workflow syntactically**

Run: `actionlint .github/workflows/lint-skills.yml` if installed; otherwise check `yamllint`.
Expected: no errors.

**Step 5: Commit**

```bash
git add .pre-commit-config.yaml .github/workflows/lint-skills.yml
git commit -m "ci: run lint-skills.py on SKILL.md changes"
```

---

## Task 4: Surface the standard in MEMORY.md
**Type:** value_unit
**Depends on:** T1 (data — the standard doc must exist for the index entry to point at)

**Files:**
- Create: `~/.claude/projects/-Users-summerrae-repos-claude-skills/memory/skill_standards.md`
- Modify: `~/.claude/projects/-Users-summerrae-repos-claude-skills/memory/MEMORY.md`

**Step 1: Write the memory file**

```markdown
---
name: skill-standards
description: Authoritative 7-pattern checklist for any new SKILL.md authored or edited in this repo
type: feedback
---

All new or edited SKILL.md files in this repo must pass `scripts/lint-skills.py`, which encodes the 7-pattern standard documented at `docs/skill-standards.md`.

**Why:** 2026-04-27 audit found ~12 skills with sub-50-char descriptions and ~40 missing Out-of-Scope sections. Bad descriptions get invoked 3-5x less; missing scope causes wrong-skill routing. Linter is a CI gate on PRs.

**How to apply:**
- Before writing a new skill, read `docs/skill-standards.md`.
- Before committing changes to any `SKILL.md`, run `python scripts/lint-skills.py <path>` locally.
- If a check fails, fix the skill — do not weaken the linter.
- For grandfathered exceptions, add `<!-- skip-skill-lint: <reason> -->` near the top of SKILL.md and open a follow-up issue.
```

**Step 2: Add index entry to MEMORY.md**

Append:
```
- [Skill standards](skill_standards.md) — 7-pattern checklist enforced by scripts/lint-skills.py; required before authoring/editing any SKILL.md
```

**Step 3: Commit (memory lives outside repo — no git step here)**

Memory files are not in the repo. Just write them — done.

---

## Task 5: Document upstream-propagation as follow-up
**Type:** value_unit
**Depends on:** T1 (knowledge — references the standard)

**Files:**
- Create: `docs/skill-standards-upstream-followup.md`
- Modify: `docs/skill-standards.md` (add link)

**Step 1: Write the follow-up doc**

Capture, but DO NOT execute, the upstream propagation:

- **anthropic-skills (Anthropic's official plugin)** — out of scope. Plugin auto-updates would overwrite local edits. Path: open PRs upstream against `anthropics/anthropic-skills` per skill that fails. Track per-skill audit findings in a public issue. Cost: each PR needs the maintainer's review; some skills are intentionally minimal (e.g., `pdf`) and may reject the standard.
- **superpowers** — same risk profile. Out of scope.
- **woz, sentry, claude-code-setup** — vendor-owned. Out of scope; route fixes through their issue trackers if a specific skill is materially broken.

For each upstream skill that fails the local linter today, list:
- Skill name
- Plugin source repo URL (if known) or "unknown — investigate"
- Worst failing pattern (one line)

This list becomes the seed of an "upstream propagation" issue.

**Step 2: Cross-link from the standard**

In `docs/skill-standards.md`, add a "Scope" section:
> This standard governs custom SKILL.md files in `claude-skills/` (this repo). Plugin-installed skills (anthropic-skills, superpowers, woz, sentry, etc.) are out of scope — see `docs/skill-standards-upstream-followup.md`.

**Step 3: Commit**

```bash
git add docs/skill-standards-upstream-followup.md docs/skill-standards.md
git commit -m "docs: scope skill-standards to local skills; capture upstream followup"
```

---

## Verification Gate (run after all tasks)

Before declaring this plan complete, verify:

```bash
# 1. Linter passes on every custom skill
python scripts/lint-skills.py
echo "exit=$?"  # expect 0

# 2. Tests pass
pytest tests/test_lint_skills.py -v

# 3. Pre-commit hook fires on SKILL.md edits
pre-commit run --all-files lint-skills

# 4. CI workflow is valid YAML
yamllint .github/workflows/lint-skills.yml || true

# 5. Memory entry is indexed
grep -q "skill_standards" ~/.claude/projects/-Users-summerrae-repos-claude-skills/memory/MEMORY.md
```

All five must pass.

---

## Out of Scope (this plan)

- Auto-fixing skills that fail the linter — humans edit; linter reports.
- Upstream PRs to anthropic-skills, superpowers, woz, sentry. Captured in T5 as follow-up.
- Splitting any currently-long custom skill below 500 lines (longest is 215 — already passes).
- Building a richer scoring/grading dashboard for skill quality.
- Localizing or translating skill descriptions.
- Per-skill version tracking — out of scope here; covered by `metadata: version` in frontmatter where authors choose to use it.

---

## Execution Handoff

**1. Subagent-Driven (this session)** — fresh subagent per task, review between tasks, fast iteration.

**2. Parallel Session (separate)** — open new session with `superpowers:executing-plans`, batch execution with checkpoints.

Default recommendation: **Option 1**. The plan is small (5 tasks, all docs/script), low-risk, and fits one session.
