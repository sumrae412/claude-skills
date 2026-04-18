# Phase 6 — Report

**Purpose:** Aggregate bugs, friction, and coverage. Produce `$eval_report` in Markdown + JSON sidecar.

**Cost:** moderate. Friction clustering uses ~1 LLM call per flow-cluster (typically <10 total).

## Inputs

- `$fidelity_report` — use only `passed_gate == true` transcripts for findings.
- `$eval_transcripts` — raw data (crossed in from Phase 4 via `cell_id`).
- `$persona_pool` — axis positions for clustering, coverage from Phase 2.

## Bug Findings

Scan **passed** transcripts for `outcome in {crash, error}` or non-empty `app_errors[]`.

### Crashes

Aggregate by error signature (exception type + top frame, or HTTP status + endpoint).

- Assign `[B-NN]` — one ID per distinct signature.
- Record: triggering personas, flows, testing styles, representative transcript path, specific repro steps from the transcript.

### Functional bugs

Aggregate `type == functional` entries in `app_errors[]` — app returned an expected-shape response that was wrong (persona-reported, e.g., "the success message said 'canceled'").

Same `[F-NN]` ID scheme.

## UI Snag Findings

Collect `ui_observations[]` from every step of every passed transcript. Also include UI observations from transcripts that later failed (`stuck` / `crash`) if the snag appears upstream of the failure — don't lose the signal to a downstream outcome.

### Two-stage clustering

1. **Group by app area.** Keyword-heuristic classification over the observation text: form / button / label / navigation / error message / modal / table / mobile layout / copy / iconography. Each observation may land in ≥1 area.
2. **Within each area, one LLM call** groups observations into issue clusters (e.g., "labels in the Workflows list are ambiguous", "submit button low contrast on mobile", "stepper progress indicator isn't obvious").

For each cluster, assign `[U-NN]`. Record:

- One-line issue description.
- Representative quote from the persona transcripts (keep it verbatim — it's usable in design reviews).
- Affected persona IDs and flows.
- Inferred severity: **minor** (cosmetic), **moderate** (slows persona), **major** (personas misinterpret the UI and almost did the wrong thing).

### Distinguishing from other findings

- **Crashes / functional bugs** — app did the wrong thing.
- **Friction** — persona gave up.
- **UI snags** — persona noticed and kept going. *"Got through it, but that was annoying."*

## Friction Findings

Group `outcome in {stuck, max_steps}` transcripts by flow, then cluster personas within each flow.

### Clustering

For each flow with ≥3 stuck personas:

1. Cluster by `axis_positions` (simple k-means, k=2–4 by size).
2. For each cluster, one LLM call:
   - What did personas try? Where did they give up? What did they say?
   - Summarize in 2–3 sentences.
3. Name the cluster by its dominant axis signature (e.g., "low trust_in_automation + high portfolio_size").
4. Pick the representative transcript (closest to cluster centroid).
5. Infer a recommended fix — or "investigate further" if the pattern isn't clear.

## Usefulness Assessment

Collect `usefulness_reflection` blocks from every passed transcript.

### Aggregation

1. **Collapse per (persona × flow).** If a persona ran a flow under multiple testing styles, average their ratings and combine their quotes — otherwise the `invalid` habit biases ratings down and obscures the signal.
2. **Reuse Friction Findings' persona clusters** per flow (same axis signatures — don't re-cluster).
3. **Per (flow × cluster)** compute:
   - Mean rating (1–5).
   - `would_use` distribution (yes / no / maybe).
   - 1–2 representative quotes, weighted toward articulate, specific ones (not "it's fine I guess").

### Flagging

- **Low-usefulness clusters** — mean rating <3.0 OR `would_use == no` rate >50%. Surface at top of the section.
- **High-usefulness-but-stuck clusters** — mean rating ≥4.0 AND >50% of transcripts are `stuck`. These are personas who *wanted* to use the app but couldn't — the highest-leverage fix targets. Flag them prominently.

### Interpretation

Low usefulness is often a **product-market-fit signal**, not a bug. A persona cluster rating 2/5 may have no bugs to file — they may simply not be the target segment. Surface this in Recommended Next Steps as *"revisit PMF for <segment>"* rather than *"fix something."*

## Coverage Analysis

Pull from `$persona_pool.coverage_estimate`. Add per-axis table.

Flag:

- Axes where no persona scored >0.8 (high extreme unsampled).
- Axes where no persona scored <0.2 (low extreme unsampled).
- `estimated_support_coverage < 0.8`.
- Excessive Nemotron density in the center (min_pairwise_distance below a threshold).

## Fidelity Gate Summary

Pull from `$fidelity_report.aggregate`:

- Per-task pass rates (5 PersonaGym tasks).
- Refusal rate per persona — flag any >20% and note it's a **Phase 2 issue** (persona prompt), not an app bug.

## Recommended Next Steps

Auto-generate, ordered by impact:

1. **Fixes** — Bug Findings sorted by frequency × severity (crash > functional).
2. **UI redesign targets** — UI Snag clusters with ≥3 affected personas, sorted by inferred severity.
3. **Flows to redesign** — flows where ≥50% of personas got stuck.
4. **Usefulness gaps** — persona clusters with mean usefulness <3.0 or `would_use == no` rate >50%. Split:
   - *Fixable (stuck-but-wanted-it):* treat as UX fixes and fold into item 3.
   - *PMF signal:* this segment may not be the target — revisit audience rather than the product.
5. **Axes to expand next run** — under-sampled extremes, with suggested `pool.tail` increase.
6. **Real-user recruitment profile** — demographics of high-friction OR low-usefulness clusters (what kinds of users to prioritize for actual user testing).

## Output

Write two files (schema: `contracts/eval-report.schema.md`):

- `docs/persona-eval/<app>/YYYY-MM-DD-<run_id>.md` — human-readable.
- `docs/persona-eval/<app>/<run_id>/report.json` — machine-parseable sidecar.

## End of run

Surface to user:

- Report path.
- TL;DR block (copied from the report).
- Offer: "Drill into a specific finding, or re-run with adjusted config (more personas / different axes)?"
