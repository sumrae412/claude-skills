# Reviewer Registry Schema

Reference documentation for `reviewer-registry.json` — the declarative config
that drives Phase 6's cascading review. This file is documentation; the runtime
parser is `scripts/select_reviewers.py`.

The bundled default registry ships with this skill at
`claude-flow/reviewer-registry.json`. Effective runtime order is:

1. bundled default
2. `~/.claude/reviewer-registry.json` override
3. project `.claude/reviewer-registry.json` override

## Top-level shape

```json
{
  "version": "1.0",
  "description": "...",
  "reviewers": [ { ...entry... }, ... ]
}
```

## Entry shape

Two flavors of entry coexist: **agent-dispatched** (the default — a subagent runs the review) and **CLI-backed** (a shell script runs the review, useful for non-Anthropic models or external tools).

### Common fields (all entries)

| Field | Type | Required | Meaning |
|---|---|---|---|
| `id` | string | yes | Unique identifier, kebab-case. Used in logs and as the reviewer reference in Phase 6 output. |
| `tier` | `"always"` \| `"conditional"` | yes | `always`: runs every review pass. `conditional`: runs only if `file_patterns` match the diff. |
| `cascade_tier` | integer | yes | Phase 6 dispatch bucket (1-5). **Tier 1 is reserved for the broad first-pass sweep (CodeRabbit) that enables early-exit. New `always` reviewers go at Tier ≥ 2.** |
| `min_budget` | `"low"` \| `"medium"` \| `"high"` | no | Smallest review budget that may run this reviewer. Default `low`. |
| `description` | string | yes | One-line summary for humans. |
| `model` | string | no | Model identifier for observability. Not runtime-consumed for CLI-backed entries. |

### Agent-dispatched fields

Use when the reviewer is a Claude subagent invoked via the Task tool.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `subagent_type` | string | yes | Agent type passed to the Task tool (e.g. `coderabbit:code-reviewer`, `security-reviewer`). |
| `file_patterns` | `[string]` | if `tier == "conditional"` | Glob patterns (e.g. `alembic/**/*.py`). |
| `content_pattern` | string | no | Regex for file contents; combined with `threshold` to require N matches. |
| `threshold` | integer | no | Minimum `content_pattern` match count to trigger the reviewer. Default `0`. |

### CLI-backed fields

Use when the reviewer is a shell script that shells out to an external tool (non-Anthropic model, linter, security scanner). Established by `curmudgeon-review` in this schema.

| Field | Type | Required | Meaning |
|---|---|---|---|
| `runner` | string | yes | Runner kind, used for dispatch routing (`"codex-cli"` today; future: `"gemini-cli"`, `"semgrep-cli"`, etc.). |
| `runner_script` | string (repo-relative path) | yes | Path to the script Phase 6 invokes with the diff file as `$1`. |

`runner_script` is resolved relative to the registry file that declared the
entry. The selector emits `resolved_runner_script` so dispatchers do not have to
reconstruct that path.

The runner script's contract:

1. **Input:** a single argv — the path to a unified-diff file.
2. **Output (stdout):** a single JSON object `{"reviewer": "<id>", "findings": [{"file":str, "line":int, "severity":"HIGH"|"MEDIUM"|"LOW", "title":str, "rationale":str}, ...]}`.
3. **Graceful skip:** if the external CLI or a required input is missing, emit the **skip envelope** on stdout and exit 0:
   ```json
   {"reviewer": "<id>", "findings": [], "skipped": true, "reason": "<one-line explanation>"}
   ```
   Do NOT exit non-zero; Phase 6 treats non-zero as a real failure.
4. **Stderr:** human-readable warnings (e.g. "curmudgeon: codex CLI not found"). Not parsed by Phase 6.

### Skip envelope: canonical branches

Reference implementation (`scripts/curmudgeon_review.sh`) emits skip envelopes from three branches:

| Branch | Reason string | When |
|---|---|---|
| Missing external CLI | `"<cli> CLI not installed"` | `command -v <cli>` fails |
| Missing input file | `"diff file not found"` | `[ ! -f "$1" ]` |
| Malformed external output | `"malformed output from <cli>"` | External emits non-JSON or unexpected shape |

Future CLI-backed runners should emit the envelope from the same three branches at minimum.

## Budget filtering

The selector computes a `review_budget` (`low`, `medium`, `high`) from workflow
path plus diff signals, unless the caller passes an explicit override.

Reviewers whose `min_budget` exceeds the selected budget are omitted and
reported under `budget_skipped`. This keeps Phase 6 proportional to change
risk instead of paying the full review tax on every contained diff.

## Early-exit invariant

Phase 6 cascades Tier 1 → Tier 2-4 with an early-exit gate: **if Tier 1 (CodeRabbit) returns no HIGH+ findings, Tiers 2-4 are skipped entirely**. Any `always` reviewer whose cost should be avoided on clean diffs must therefore be at `cascade_tier >= 2`. Keep that invariant covered in `scripts/test_select_reviewers.py`.

## Scored Reviewers (v1.1+)

Reviewers that emit per-criterion numeric scores set:

- `score_threshold` (integer 1-10): scores strictly below this become blocking findings
- `scored_criteria` (array of strings): canonical criterion names the reviewer scores

The Phase 6 aggregator (phase-6-quality.md) reads these fields, iterates the reviewer's
`scores[]` output, and synthesizes one blocking finding per sub-threshold score in the form:
`Adversarial score {N}/10 on {criterion}: {break_case}`.

Sub-threshold findings flow into Phase 5 retry input same as test failures.

Scored reviewers extend their `calibration` block with `"verdict_type": "scored"`. Agreement is computed as `(|judge_score - human_score| <= 2) / n` against a labeled corpus, vs binary reviewers' exact-match agreement.

### Calibration block fields (scored reviewers)

The `calibration` block on a scored reviewer entry carries:

| Field | Type | Set by | Meaning |
|---|---|---|---|
| `verdict_type` | `"scored"` | author | Marks the reviewer as scored vs binary. Drives which agreement formula the calibration script uses. |
| `min_agreement` | float (0.0-1.0) | author | Pass threshold. Calibration runs below this should not record a passing value into `last_agreement`. |
| `sample_size` | integer | author | Target corpus size. The labeled corpus under `tests/fixtures/<reviewer>/calibration_corpus/` should have at least this many cases. |
| `last_calibrated` | ISO date string \| null | calibration script | Date of the most recent successful calibration run. `null` until the first run. |
| `last_agreement` | float \| null | calibration script | Overall agreement value from the most recent successful run, rounded to 4 decimals. `null` until the first run. |
| `note` | string | author | Free-form description of the agreement formula or any reviewer-specific quirks. |

`last_calibrated` and `last_agreement` are populated by the per-reviewer calibration script (e.g. `scripts/calibrate_adversarial_breaker.py` in the claude_flow repo) on a successful run — agreement >= `min_agreement`. The script preserves all other fields and the file's existing JSON formatting.

The labeled corpus is the source of truth for "human agreement" — each case has a `diff.patch` (input) and an `expected.json` (per-criterion human-labeled scores in the 1-10 range). See `tests/fixtures/adversarial_breaker/calibration_corpus/README.md` in claude_flow for the canonical layout.

Drift detection (running the live reviewer against a single planted-bug fixture on a cron) is a separate concern from calibration (running against a 20+ case corpus to compute agreement). Both can coexist at different cadences — drift weekly, calibration monthly or on-demand.

### Cross-repo persona resolution

When a reviewer's persona/system-prompt file lives in a different repo than the registry (typical for `general-purpose` agent-backed reviewers under the post-2026-04-16 single-source-of-truth layout), declare BOTH:

- `persona_file` — repo-relative path inside the source repo (e.g. `claude-flow/scripts/adversarial_breaker_persona.txt`)
- `persona_file_root` — install root the path resolves under (e.g. `~/.claude/skills` for the canonical claude-skills install)

Resolved path: `<root>/<persona_file>`. Tests, dispatchers, and runtime consumers all use the same resolution. See MEMORY `cross_repo_persona_resolution.md`.

If the persona file is in the same repo as the registry, omit `persona_file_root` and use a repo-relative `persona_file` only.

## Adding a new reviewer

1. Pick an `id` (kebab-case, domain prefix if extending a family).
2. Decide agent-dispatched vs CLI-backed (default to agent-dispatched; CLI-backed only when the reviewer is not a Claude agent — non-Anthropic models, external linters, security scanners).
3. For CLI-backed: author the runner script per the contract above. Test missing-CLI and missing-input paths at minimum. The bundled `scripts/curmudgeon_review.sh` is the reference skip-first implementation.
4. Add the entry to `claude-flow/reviewer-registry.json` or to a project override.
5. Extend `scripts/test_select_reviewers.py` with an assertion that the new entry is registered and lands in the expected `by_tier` bucket.
6. Document in `phase-6-quality.md`'s Default Reviewers table.

## See also

- `claude-flow/reviewer-registry.json` (bundled default config)
- `scripts/select_reviewers.py` (runtime parser)
- `phases/phase-6-quality.md` (dispatch behavior)
- `scripts/curmudgeon_review.sh` (CLI-backed reference implementation)
