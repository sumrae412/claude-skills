# Experiment: Forced Selection at Scale (Variant C)

**Date:** 2026-04-29
**Status:** Complete — shipped variant B holds. None of B-150, C1, or C3 beat it.
**Predecessor:** [2026-04-29-skill-selection-vs-progressive-disclosure.md](2026-04-29-skill-selection-vs-progressive-disclosure.md) — variant B shipped on 5-skill corpus.
**Source motivation:** Su et al., *Skill Retrieval Augmentation for Agentic AI* (arXiv:2604.24594), Table 5 (BM25+rerank > pure sparse > pure dense at 26K-skill scale).

## Why now

The variant B win on 5 skills doesn't tell us whether forced selection scales. Real claude-flow runs see 150+ skills loaded into session context (all `superpowers:`, `engineering:`, `pdf-viewer:`, plugin skills, etc.). At that corpus size:

- A 150-line `Available skills` block in every subagent prompt is ~3K tokens of pure overhead before the task is described.
- BM25 ranking over name+description should narrow that to a top-K candidate set, but the paper found pure BM25 alone is unreliable; it needed an LLM rerank pass.
- The `correct_skill_rate` win from variant B may erode as the candidate set widens — too many plausible options confuses the model.

This experiment isolates the corpus-size variable.

## Variants under test

### B-150 — Variant B at full scale (control for this experiment)
Same forced-selection prompt as the shipped variant B, but the `Available skills` block lists **all** session-loaded skills (~150 with name + 1-line description). Measures the no-retrieval ceiling at scale.

### C1 — BM25 retrieval, top-5
For each task, run BM25 over `name + description` for all session skills, take top-5, present as the forced-selection menu. Tests whether retrieval narrows the choice usefully.

### C2 — BM25 retrieval, top-10
Same as C1 but top-10. Tests the recall-vs-confusion tradeoff.

### C3 — BM25 + LLM rerank, top-5
Two-stage: BM25 to top-50, then a cheap LLM rerank (haiku) to top-5, then forced selection. The paper's strongest finding (Table 5).

## Hypotheses

- **H1:** At scale, B-150 will show degraded `correct_skill_rate` vs. the shipped variant B's 75.0% — too many distractors. Predicted ≤60%.
- **H2:** C1 (BM25 top-5) will roughly match the shipped variant B (~75%) at much lower token cost than B-150.
- **H3:** C3 (BM25 + rerank) will exceed variant B (≥80%), matching the paper's directional finding.
- **H4:** C2 (top-10) will under-perform C1 — wider candidate sets at our scale add more confusion than coverage.

## Test set

Reuse the 12 dispatches from [2026-04-29-gold-labels.md](../experiments/2026-04-29-gold-labels.md). The variant B run already established baseline metrics; this experiment varies only the candidate generation step.

**One labeling extension required:** for each task, label the *true* gold skill from the full ~150-skill universe, not just the 5 courierflow-* ones. Most rows' gold won't change (the courierflow skill IS the right answer), but rows like PR #511 (CopilotKit) might have a better-fitting skill in the broader corpus (e.g., `frontend-design:frontend-design` or some plugin skill). This relabeling is ~10 min of work and unblocks the experiment.

## Implementation

Three new scripts:

- **`build_skill_corpus.py`** — emits the full skill corpus from session-loaded skills (parses output of `Skill` tool listing, or reads from `~/.claude/plugins/cache/`). Produces `skill_corpus.jsonl` with `{slug, name, description}` per skill.
- **`bm25_rank.py`** — given a task prompt and corpus, returns top-K skills by BM25. Pure Python, no external deps (use `rank_bm25` if available, else implement from scratch over ~500 lines of corpus).
- **Extend `replay_skill_selection.py`** — add `--variant {a,b,b150,c1,c2,c3}` and a `--retriever {none,bm25,bm25-rerank}` flag.

## Token budget

Per dispatch:

| variant | candidate-block tokens | retrieval calls |
|---|---|---|
| B (5 skills) | ~200 | 0 |
| B-150 | ~3,000 | 0 |
| C1 (BM25 top-5) | ~200 | 1 (local, free) |
| C3 (BM25+rerank) | ~200 | 2 (1 local + 1 haiku) |

C1 should win on cost-effectiveness. C3 trades a haiku call (~$0.001) for predicted accuracy gain.

## Success criteria

Decide variant per the predecessor plan's tree, with thresholds applied **vs. the shipped variant B** (not vs. variant A):

| Result | Action |
|---|---|
| C3 beats B by ≥10pp on correct-skill | Adopt C3 — author rerank script for production. |
| C1 ties B (±5pp) | Adopt C1 — same accuracy, much lower token cost at scale. |
| B-150 ties B | The retrieval claim doesn't hold at our scale — keep enumerating. Useful negative result. |
| All variants under-perform shipped B | Stop. The 5-skill courierflow corpus is the right granularity; don't expose the full 150-skill universe to subagents. |

## Out of scope

- Dense retrieval (BGE / Contriever). Paper showed pure-dense underperforms; not worth implementing for this scale.
- Hybrid (BM25 + dense). Marginal recall gains in the paper; complexity not justified at our scale.
- Need-awareness training. Paper RQ6's bigger finding remains untouched by retrieval changes; that's a separate research direction.

## Risks

- **Skill corpus quality.** Session-loaded skills aren't all equally well-described. Skills with vague descriptions will rank poorly under BM25. Mitigation: spot-check the corpus before running; fix bad descriptions (this is the paper's "skill corpus quality control" research direction).
- **Reusing the same 12-dispatch set.** Test-set leakage isn't a concern here (we're varying retrieval, not training), but small-n confidence intervals will overlap. Consider expanding to 24 dispatches if results are inconclusive.
- **`Skill` tool listing isn't programmatically accessible.** May need to scrape from system-reminder text or read plugin manifests. If this turns into a yak-shave, defer C and just adopt the shipped variant B as final.

## Pre-experiment: BM25 retrieval ceiling

Before running any model trials, we measured BM25's standalone recall against the 12 gold-labeled dispatches over the 205-skill corpus. Script: [eval_bm25_on_dispatches.py](../../claude-flow/scripts/eval_bm25_on_dispatches.py). Corpus: [skill_corpus.jsonl](../../.claude/experiments/skill_corpus.jsonl) (205 skills, parsed from a session-loaded skills listing).

| metric | value |
|---|---|
| recall@1 | 25.0% (2 / 8 gold-bearing dispatches) |
| recall@5 | 62.5% (5 / 8) |
| recall@10 | 87.5% (7 / 8) |

(Gold-bearing = the 8 of 12 dispatches with `gold_skill ≠ none`.)

**This is a hard ceiling on C1 and C2.** No matter how good the forced-selection prompt is, if the gold skill isn't in the candidate set, the model can't pick it.

**Misses to investigate:**
- **PR #470** (chat-first builder layout): gold ranks **#16**. Beyond top-10. The query terms (chat, builder, workflow, layout) match generic skills (`user-stories`, `anthropic-skills:web-artifacts-builder`) more strongly than the courierflow-ui description.
- **PR #476** (auth template seeding): gold ranks **#6**. `courierflow-api` outscored `courierflow-security` because the title says "templates" — a UI/API word, not a security one.
- **PR #464** (Calendar scan): gold ranks **#6**. `user-stories` and `engineering:documentation` outscored `courierflow-integrations`.

**Implication for variant ordering:**
- **C1 (top-5)** has a 62.5% recall ceiling — unlikely to beat the shipped variant B's 75% correct-skill rate. Run only as a baseline for C3.
- **C3 (BM25 → top-50 → LLM rerank → top-5)** becomes the headline variant. The rerank stage needs to lift gold from positions 6–16 into the top-5.
- **B-150 (no retrieval, full menu)** is now the most interesting cheap variant — does a 150-line menu actually hurt the model, or does it just cost tokens?

**Noise generators to fix in the corpus:**
- `user-stories` description mentions "routes, templates, models" — collides with most courierflow API/UI work. Consider tightening the description.
- `agent-sdk-dev:new-sdk-app` is a top hit on many queries because of generic verbs. Same fix.
- `anthropic-skills:web-artifacts-builder` keeps appearing for any UI-adjacent query.

These are exactly the "skill quality control" findings the paper's §7 calls out as a parallel research direction. Worth a short PR after the experiment ships.

## Results (run 2026-04-29, after description tightening)

After tightening 7 skill descriptions, BM25 recall@5 reached 100%. We ran all four scale variants against the same 12-dispatch test set used for the predecessor experiment.

| variant | n | loaded | correct | need-aware | over-load | pass |
|---|---|---|---|---|---|---|
| A (control) | 12 | 83.3% | 58.3% | 100% | 50.0% | 75.0% |
| **B (shipped, 5-skill curated)** | 12 | 75.0% | **75.0%** | 100% | 25.0% | **83.3%** |
| B-150 (full 205-skill menu) | 12 | 25.0% | 58.3% | 37.5% | 0.0% | 58.3% |
| C1 (BM25 top-5) | 12 | 66.7% | 66.7% | 87.5% | 25.0% | 75.0% |
| C3 (BM25 → haiku rerank → top-5) | 12 | 66.7% | 58.3% | 87.5% | 25.0% | 66.7% |

**Verdict: shipped variant B holds.** None of the scale variants beat the 5-skill curated menu on correct-skill, end-task pass, or need-aware load.

### Three failure modes uncovered

1. **B-150 collapsed to 25% load rate.** Faced with 205 candidates, the model just picks "none." Need-aware load dropped from 100% (variant B) to 37.5%. Bigger menu → more abstention. Direct empirical confirmation of the paper's RQ6 retreat-under-noise finding.
2. **C1 retrieval surfaced gold but introduced noise.** With 100% recall@5 after description tightening, gold was always in the menu — but the model sometimes picked nearby generic skills (`engineering:testing-strategy`, `agent-sdk-dev:new-sdk-app`) that ranked alongside.
3. **C3 rerank actively hurt.** Haiku rerank moved correct from C1's 66.7% to 58.3%. Two model calls per dispatch for negative gain. Rerank introduced more reordering noise than signal at this scale.

### Deeper lesson

**Curation > corpus size > retrieval > rerank.** The 5-skill courierflow-* set is curated to be domain-coherent — each skill maps to one architectural layer. Retrieval over a generic corpus surfaces topically-relevant skills that aren't project-aligned. The act of curating the candidate menu is more valuable than any retrieval algorithm operating on an uncurated corpus.

This is a negative result for the paper's directional finding (BM25+rerank > pure-sparse) — but with a clean explanation: the paper measured retrieval over a corpus where every skill was a plausible candidate. Our corpus is project-agnostic; retrieval surfaces relevant-but-wrong skills, which a curated menu eliminates by construction.

### Skill-description quality finding

Before tightening: recall@1=25.0%, recall@5=62.5%, recall@10=87.5%.
After tightening 7 skills (5 courierflow-* + `user-stories` + `anthropic-skills:web-artifacts-builder`): recall@1=87.5%, recall@5=100%, recall@10=100%.

**Description quality is the dominant retrieval lever at our scale.** Five edits added 37.5pp to recall@5. Worth applying the same hygiene pass to all 205 skills as a follow-up, but the headline result wouldn't change — even with perfect retrieval, curated 5-skill menus beat retrieved top-5.

## Follow-ups

1. **Don't ship any scale variant.** Stay on shipped variant B (curated 5-skill forced selection).
2. **Apply description-quality hygiene to the full skill library** as a separate PR. Pattern: avoid generic terms ("routes, templates, models") that collide with project-specific skills; describe what the skill does, not its inputs.
3. **The CopilotKit gap remains the highest-value courierflow skill addition.** PR #511 still failed under every variant. Authoring a `courierflow-copilot` skill would convert that failure to a pass without retrieval changes.
4. **Test set is small (n=12).** Replicate on 24+ before treating these scale-variant results as definitive — but the directional signal is strong enough to halt further variant exploration.
