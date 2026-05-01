# Impeccable Frontend Design Workflow Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Improve `claude-flow` frontend design development by adding Impeccable-inspired design context, shaping, anti-pattern detection, and review gates without replacing the existing CourierFlow UI rules or `claude-flow` phase model.

**Architecture:** Keep `claude-flow` as the orchestrator. Add a lightweight design-context contract and references, wire those references into Phase 4 UI planning and Phase 6 review, and add a CLI-backed conditional reviewer for `npx impeccable detect` that gracefully skips when unavailable.

**Tech Stack:** Markdown skill references, JSON reviewer registry, Python reviewer-selection tests, shell or Python wrapper for optional Node/npx CLI execution.

**Ruled Out:**
- Vendoring the entire `pbakaus/impeccable` skill bundle - too broad, creates command overlap, and may override local CourierFlow UI standards.
- Replacing Excalidraw visual checkpoints - `claude-flow` already has a mockup/manifest loop; Impeccable should enrich that loop, not replace it.
- Making Impeccable detection a hard dependency - optional tooling must graceful-skip so Phase 6 remains portable.
- Adopting Impeccable aesthetics wholesale - CourierFlow already has locked Inter/Poppins, Bootstrap/Jinja, and design-token rules.

---

## Acceptance Criteria

- UI-affecting `claude-flow` runs load a documented design context before visual planning.
- Phase 4 requires a task-specific design brief for meaningful UI work before mockup generation or implementation planning.
- Phase 6 design review includes measurable Impeccable-style checks: accessibility, performance, theming, responsive behavior, and anti-patterns.
- UI diffs can trigger an `impeccable-detector` reviewer through `reviewer-registry.json`.
- The Impeccable detector exits with a graceful-skip JSON envelope when `npx` or the package is unavailable.
- Existing tests pass, and new tests cover reviewer selection and detector skip/pass behavior.

---

### Task 1: Add Design Context Contract
**Type:** shared_prerequisite
**Depends on:** none

**Files:**
- Create: `contracts/design-context.schema.md`
- Modify: `SKILL.md`
- Test: `scripts/test_workflow_assets.py`

**Step 1: Write the failing asset test**

Add assertions to `scripts/test_workflow_assets.py` that verify:

```python
assert (SKILL_ROOT / "contracts" / "design-context.schema.md").exists()
```

If the existing test file has a centralized list of required assets, add this contract there instead of creating a duplicate test.

**Step 2: Run the test to verify it fails**

Run:

```bash
pytest scripts/test_workflow_assets.py -q
```

Expected: FAIL because `contracts/design-context.schema.md` does not exist.

**Step 3: Create the contract**

Create `contracts/design-context.schema.md` with these sections:

```markdown
# $design_context
<!-- Produced by: Phase 0/Phase 4 UI preflight | Consumed by: Phases 4, 5, 6 -->

## Schema

project_identity:
  product_name: string
  product_scope: string
  register: product | brand

design_system:
  source_files: string[]
  tokens:
    colors: string[]
    typography: string[]
    spacing: string[]
    radii: string[]
  component_patterns: string[]
  centralized_style_rules: string[]

task_design_brief:
  primary_user_action: string
  surface_context: string
  color_strategy: restrained | committed | full_palette | drenched
  theme_scene_sentence: string
  key_states: string[]
  interaction_model: string
  content_requirements: string[]
  anti_goals: string[]

verification:
  required_viewports: string[]
  required_states: string[]
  anti_pattern_checks: string[]
```

Add notes that:
- CourierFlow/Codex project instructions remain authoritative over generic Impeccable advice.
- `DESIGN.md` and `PRODUCT.md` are optional project artifacts, not required dependencies.
- If no design context file exists, agents extract context from `AGENTS.md`, `CLAUDE.md`, design tokens, templates, CSS variables, and adjacent UI.

**Step 4: Document the contract in `SKILL.md`**

In the Phase Output Contracts table in `SKILL.md`, add `$design_context` as an optional UI-only contract:

```markdown
| `$design_context` | `contracts/design-context.schema.md` | Phase 0/4 UI preflight | Phases 4, 5, 6 |
```

Add one sentence below the table:

```markdown
For UI-affecting work, `$design_context` carries the project design system and the task-specific design brief; project-local UI instructions override generic frontend-design guidance.
```

**Step 5: Run the test**

Run:

```bash
pytest scripts/test_workflow_assets.py -q
```

Expected: PASS.

**Step 6: Commit**

```bash
git add contracts/design-context.schema.md SKILL.md scripts/test_workflow_assets.py
git commit -m "docs: add design context contract"
```

---

### Task 2: Add Frontend Design Context Reference
**Type:** shared_prerequisite
**Depends on:** Task 1 (knowledge)

**Files:**
- Create: `references/frontend-design-context.md`
- Modify: `scripts/test_workflow_assets.py`
- Test: `scripts/test_workflow_assets.py`

**Step 1: Write the failing asset test**

Add an assertion:

```python
assert (SKILL_ROOT / "references" / "frontend-design-context.md").exists()
```

**Step 2: Run the test to verify it fails**

Run:

```bash
pytest scripts/test_workflow_assets.py -q
```

Expected: FAIL because the reference does not exist.

**Step 3: Create the reference**

Create `references/frontend-design-context.md` with these headings:

```markdown
# Frontend Design Context

## Purpose
## When To Load
## Source Priority
## Product Register
## Design System Extraction
## Task-Specific Design Brief
## CourierFlow Overrides
## Output Shape
```

The content should adapt the useful Impeccable ideas without copying command mechanics:

- Source priority:
  1. Project instructions: `AGENTS.md`, `CLAUDE.md`, skill-local instructions
  2. Project design docs: `PRODUCT.md`, `DESIGN.md`, `DESIGN.json`
  3. Existing tokens and CSS variables
  4. Shared templates/macros/components
  5. Adjacent rendered UI if a dev server is available
- Register rule:
  - CourierFlow authenticated app/admin/sidebar surfaces are `product`.
  - Marketing or public pages can be `brand`.
- Product UI default:
  - Familiar, dense, task-oriented UI is acceptable.
  - Consistency and clarity beat visual novelty.
- CourierFlow overrides:
  - Preserve centralized Bootstrap/Jinja patterns.
  - Use `base.html`, `macros/ui_macros.html`, and design-system CSS first.
  - Do not hardcode colors.
  - Do not invent one-off page headers.
  - Do not override Inter/Poppins unless project instructions change.
- Design brief fields:
  - primary user action
  - landlord context and urgency
  - screen states
  - interaction model
  - content ranges and overflow risks
  - anti-goals

**Step 4: Run the test**

Run:

```bash
pytest scripts/test_workflow_assets.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add references/frontend-design-context.md scripts/test_workflow_assets.py
git commit -m "docs: add frontend design context reference"
```

---

### Task 3: Wire Design Shaping Into Phase 4
**Type:** value_unit
**Depends on:** Task 1 (data), Task 2 (data)

**Files:**
- Modify: `phases/phase-4-architecture.md`
- Test: `scripts/test_workflow_assets.py`

**Step 1: Add a Phase 4 design preflight section**

In `phases/phase-4-architecture.md`, before the existing visual mockup offer, add a section named:

```markdown
## Step 2.4: Frontend Design Context (UI Features)
```

The guard should match the existing UI signals:

- `--visual`
- task mentions mockup/wireframe/visual review
- `$plan` or expected files touch templates, CSS, JS/TS/TSX, Vue, Svelte, static assets
- the task modifies visible UI behavior or layout

**Step 2: Specify the preflight behavior**

Add instructions:

```markdown
When the guard passes:
1. Load `references/frontend-design-context.md`.
2. Produce `$design_context` using `contracts/design-context.schema.md`.
3. Identify whether the surface is product or brand.
4. Extract project-local design rules before borrowing generic frontend guidance.
5. Create a task-specific design brief before mockups or final plan writing.
```

For CourierFlow-like product UI, explicitly prefer:

- predictable grids
- reusable macros and shared CSS
- complete states
- no decorative reinvention of standard controls
- restrained color unless the surface has a specific reason

**Step 3: Reconcile with existing Step 2.5 and Step 6**

Update Step 2.5 so standalone HTML mockups are optional quick previews, while Step 6 remains the durable Excalidraw state-matrix loop.

Add a rule:

```markdown
If both Step 2.5 and Step 6 run, the Step 2.5 HTML mockup is exploratory only; the Step 6 manifest/mockups are the verification source.
```

**Step 4: Run markdown asset tests**

Run:

```bash
pytest scripts/test_workflow_assets.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add phases/phase-4-architecture.md
git commit -m "docs: add frontend design shaping to phase 4"
```

---

### Task 4: Add Impeccable Detector Runner
**Type:** value_unit
**Depends on:** none

**Files:**
- Create: `scripts/impeccable_detect.sh`
- Create: `scripts/test_impeccable_detect.py`

**Step 1: Write tests for graceful skip**

Create `scripts/test_impeccable_detect.py`.

Use `subprocess.run` to execute the script with an environment that forces skip behavior:

```python
def test_impeccable_detect_forced_skip_outputs_json(tmp_path):
    env = os.environ.copy()
    env["IMPECCABLE_FORCE_UNAVAILABLE"] = "1"
    result = subprocess.run(
        ["bash", "scripts/impeccable_detect.sh", "--json", str(tmp_path)],
        cwd=SKILL_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["reviewer"] == "impeccable-detector"
    assert payload["skipped"] is True
    assert payload["findings"] == []
```

Add a second test for missing path or empty args if useful, but keep scope tight.

**Step 2: Run the test to verify it fails**

Run:

```bash
pytest scripts/test_impeccable_detect.py -q
```

Expected: FAIL because `scripts/impeccable_detect.sh` does not exist.

**Step 3: Implement the runner**

Create `scripts/impeccable_detect.sh`.

Behavior:

- `set -u`, but avoid `set -e` around the detector command because exit code `2` means findings.
- If `IMPECCABLE_FORCE_UNAVAILABLE=1`, print:

```json
{"reviewer":"impeccable-detector","findings":[],"skipped":true,"reason":"impeccable forced unavailable"}
```

- If `npx` is missing, print a skip envelope with reason `npx not available`.
- Otherwise run:

```bash
npx --yes impeccable detect --fast --json "$@"
```

- Normalize exit codes:
  - `0`: pass through JSON if valid, or wrap stdout in a pass envelope.
  - `2`: pass through findings and exit `1` only if Phase 6 should treat findings as reviewer findings. Prefer exit `0` plus JSON findings if existing CLI-backed reviewers expect advisory output.
  - any other exit: print skip envelope with stderr in `reason`, exit `0`.

Keep the output shape compatible with other reviewer JSON:

```json
{
  "reviewer": "impeccable-detector",
  "findings": [],
  "skipped": false,
  "reason": ""
}
```

**Step 4: Run tests**

Run:

```bash
pytest scripts/test_impeccable_detect.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add scripts/impeccable_detect.sh scripts/test_impeccable_detect.py
git commit -m "test: add impeccable detector runner"
```

---

### Task 5: Register Conditional Impeccable Reviewer
**Type:** value_unit
**Depends on:** Task 4 (data)

**Files:**
- Modify: `reviewer-registry.json`
- Modify: `scripts/test_select_reviewers.py`
- Test: `scripts/test_select_reviewers.py`

**Step 1: Write reviewer-selection tests**

In `scripts/test_select_reviewers.py`, add coverage that:

- a UI file such as `app/templates/dashboard.html` selects `impeccable-detector`
- a backend-only file such as `app/services/calendar.py` does not select it

Use the existing helper patterns in the file. The assertion should inspect `conditional_matched` or `by_tier`, whichever the current tests already use.

**Step 2: Run the test to verify it fails**

Run:

```bash
pytest scripts/test_select_reviewers.py -q
```

Expected: FAIL because `impeccable-detector` is not registered.

**Step 3: Add registry entry**

Add this reviewer to `reviewer-registry.json`:

```json
{
  "id": "impeccable-detector",
  "tier": "conditional",
  "cascade_tier": 3,
  "min_budget": "medium",
  "file_patterns": [
    "**/*.html",
    "**/*.css",
    "**/*.scss",
    "**/*.js",
    "**/*.ts",
    "**/*.tsx",
    "**/*.vue",
    "**/*.svelte",
    "**/templates/**",
    "**/static/**"
  ],
  "runner": "shell",
  "runner_script": "scripts/impeccable_detect.sh",
  "description": "Optional Impeccable CLI anti-pattern and frontend design-quality detector"
}
```

Do not modify `scripts/select_reviewers.py` unless tests reveal the existing pattern matching cannot support this reviewer. UI files already raise review budget to `medium`, which matches this reviewer.

**Step 4: Run tests**

Run:

```bash
pytest scripts/test_select_reviewers.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add reviewer-registry.json scripts/test_select_reviewers.py
git commit -m "feat: register impeccable frontend reviewer"
```

---

### Task 6: Upgrade Phase 6 Design Review Rubric
**Type:** value_unit
**Depends on:** Task 2 (knowledge), Task 5 (knowledge)

**Files:**
- Modify: `references/phase-6-design-review.md`
- Test: `scripts/test_workflow_assets.py`

**Step 1: Extend the review dimensions**

In `references/phase-6-design-review.md`, add an Impeccable-inspired scoring table:

```markdown
## Scored Design Audit

Score each dimension 0-4:

1. Accessibility
2. Performance
3. Theming and design-token usage
4. Responsive behavior
5. Anti-patterns and design-system drift
```

Keep the existing required checks. This is an addition, not a replacement.

**Step 2: Add design drift classification**

Add a section:

```markdown
## Drift Classification

For each finding, classify root cause:
- `missing-token`
- `one-off-implementation`
- `conceptual-misalignment`
- `state-gap`
- `accessibility-gap`
```

Add guidance:

- Missing token: add or reuse a design-system variable.
- One-off implementation: replace with existing macro/component.
- Conceptual misalignment: adjust flow/hierarchy, not just CSS.
- State gap: add loading, empty, error, success, disabled, hover, focus, or active state.
- Accessibility gap: fix semantics, labels, focus, contrast, keyboard behavior.

**Step 3: Add CLI reviewer handling**

Add instructions:

```markdown
If `impeccable-detector` was selected, run its resolved runner script against changed UI paths. Treat findings as advisory unless they overlap with CourierFlow hard rules, WCAG AA, broken responsiveness, or visible user-flow regressions.
```

Explicitly say project-local UI rules outrank generic anti-pattern rules.

**Step 4: Run asset test**

Run:

```bash
pytest scripts/test_workflow_assets.py -q
```

Expected: PASS.

**Step 5: Commit**

```bash
git add references/phase-6-design-review.md
git commit -m "docs: add impeccable design review rubric"
```

---

### Task 7: Add Phase 5 UI Implementation Guidance
**Type:** value_unit
**Depends on:** Task 1 (knowledge), Task 2 (knowledge)

**Files:**
- Modify: `phases/phase-5-implementation.md`
- Test: `scripts/test_workflow_assets.py`

**Step 1: Add UI implementation note**

In `phases/phase-5-implementation.md`, under the UI defensive-pattern area, add:

```markdown
For UI-affecting tasks, carry `$design_context` into implementation dispatches. Implementers must preserve centralized design-system patterns and satisfy the task design brief's required states before polishing visuals.
```

**Step 2: Add subagent prompt guidance**

In the subagent skill-loading section, update `courierflow-ui` wording to mention:

- design-system alignment
- task-specific design brief
- complete UI states
- no one-off styles when central patterns exist

Do not expand the forced-selection menu beyond the existing five skills.

**Step 3: Run asset test**

Run:

```bash
pytest scripts/test_workflow_assets.py -q
```

Expected: PASS.

**Step 4: Commit**

```bash
git add phases/phase-5-implementation.md
git commit -m "docs: carry design context into ui implementation"
```

---

### Task 8: Verify Full Workflow Assets and Tests
**Type:** value_unit
**Depends on:** Task 3 (build), Task 4 (build), Task 5 (build), Task 6 (build), Task 7 (build)

**Files:**
- Modify: none unless verification finds issues
- Test: `scripts/test_workflow_assets.py`, `scripts/test_select_reviewers.py`, `scripts/test_impeccable_detect.py`

**Step 1: Run targeted tests**

Run:

```bash
pytest scripts/test_workflow_assets.py scripts/test_select_reviewers.py scripts/test_impeccable_detect.py -q
```

Expected: PASS.

**Step 2: Run broader script tests if time allows**

Run:

```bash
pytest scripts -q
```

Expected: PASS. If unrelated pre-existing failures appear, document them with exact test names and keep the targeted tests green.

**Step 3: Run reviewer selector smoke check**

Run:

```bash
printf '%s\n' app/templates/dashboard.html | python3 scripts/select_reviewers.py --workflow-path full
```

Expected:

- `review_budget` is at least `medium`
- `impeccable-detector` appears in `conditional_matched` or `by_tier`

Run:

```bash
printf '%s\n' app/services/calendar.py | python3 scripts/select_reviewers.py --workflow-path full
```

Expected:

- `impeccable-detector` does not appear in matched reviewers

**Step 4: Run detector forced-skip smoke check**

Run:

```bash
IMPECCABLE_FORCE_UNAVAILABLE=1 bash scripts/impeccable_detect.sh --json app/templates
```

Expected: JSON with `"reviewer": "impeccable-detector"` and `"skipped": true`.

**Step 5: Inspect final diff**

Run:

```bash
git diff --stat
git diff --check
```

Expected:

- No whitespace errors.
- Diff only touches the planned files.

**Step 6: Final commit if needed**

If verification required fixes:

```bash
git add <fixed-files>
git commit -m "fix: verify impeccable frontend workflow integration"
```

---

## Parallelization Notes

- Tasks 1 and 2 are shared prerequisites and should run first.
- Task 4 can run in parallel with Tasks 1-3 because it only creates the detector runner and its tests.
- Task 5 depends on Task 4 because it references the runner path.
- Tasks 6 and 7 can run in parallel after Tasks 1 and 2 because they modify different phase references.
- Task 8 must run last.

## Phase 6 Review Expectations

This change touches workflow documentation, reviewer registry behavior, and a new optional CLI runner. Run the normal Phase 6 cascade. UI-specific live browser testing is not required because this repo change does not modify a rendered app UI, but the new design-review instructions and selector behavior must be tested.
