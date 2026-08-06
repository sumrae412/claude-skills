# Phase 2 — Datasets

A dataset is a list of `{input, reference?, metadata}` examples. The
reference is optional but unlocks code-based evaluators.

## Sourcing

In rough order of value:

1. **Production traces** — real user inputs are the highest-signal
   source. Sample across time, user cohort, and outcome (errors,
   thumbs-down, long sessions). Don't only take the failures or only
   the successes.
2. **Curated edge cases** — adversarial inputs the team knows are hard
   (jailbreaks, ambiguous queries, multilingual, very long context,
   empty context).
3. **Hand-written examples** — for new features with no traces yet.
   Write 20–50 to start; replace with prod traces as they accumulate.
4. **Synthetic generation** — useful for stress-testing coverage, but
   never the *only* source. Synthetic data inherits the bias of the
   generator model.
5. **Generative benchmarking from your own corpus** — use an LLM to
   generate a representative eval dataset from your *own* documents,
   traces, or knowledge base instead of relying on generic public
   benchmarks (which are often too clean, may be in training data, and
   don't generalize to your production distribution). Key technique:
   **Distinct Query Generation** — feed the ground-truth queries to
   the generator as *negative examples* so generated queries are
   genuinely unseen. Naive generation without this step reproduces
   ground-truth queries verbatim, defeating the purpose. Validation
   finding: public-benchmark model rankings don't always hold on a
   production corpus, so a domain-generated set is the trustworthy
   signal for your deployment. Source:
   [Chroma Generative Benchmarking](https://www.trychroma.com/research/generative-benchmarking).
6. **Weaker-model failure mining** — run your prompts through a weaker,
   cheaper model; its organic mistakes resemble real production
   failures better than hand-crafted defects. Curate like any synthetic
   batch — a small model's error *distribution* is not ground truth.

No source is neutral: support queues skew to failures, common requests
skew easy, synthetic skews to what the generator prompt emphasized.
Record `metadata.source` (schema below) and read scores per-source.
For synthetic batches, vary situation × information quality (detailed /
vague / conflicting) × phrasing (full sentences / shorthand / typos /
second-language), then curate hard: drop duplicates, nothing-new cases,
and one-line-fix cases; keep lasting-problem cases. Full checklist:
`../references/error-analysis-and-test-sets.md`.

## Size

| Use case                          | Target size      |
| --------------------------------- | ---------------- |
| Smoke (CI on every PR)            | 20–50            |
| Regression gate (CI nightly)      | 200–500          |
| Pre-release / model swap decision | 500–2000         |
| Statistical claim ("X is better") | power-analyzed, usually 300+ per arm |

Below N≈30 the noise on LLM-judge scores swamps real differences.

## Failure-mode coverage, not just count

For each failure mode named in Phase 1, ensure the dataset contains
examples that should trigger it. Track coverage explicitly:

```
failure_mode               examples
api_hallucination          42
multi-domain_routing       28
empty_context              15
long_context (>50k tokens) 12
multilingual               20
```

A 500-example dataset that's all easy paraphrase questions is worse
than a 100-example dataset with deliberate coverage.

## Splits

- **train** — for tuning prompts / iterating. The model sees this set.
- **dev / val** — for picking between candidates during iteration.
- **test** — held out. Touched only at decision points (ship / no
  ship). If you tune on test, you no longer have a test set.

For small features one split is fine; record in the dataset
metadata which examples were used for tuning vs. decision so the
distinction survives later when you re-split.

## Versioning

Datasets change. Without versioning, "score went up" is unfalsifiable.

- Track inserts / updates / deletes (Phoenix, Braintrust, LangSmith
  all do this; in a hand-rolled harness, commit the dataset to git or
  hash the file and store the hash with each result).
- When you add examples, re-run the prior best candidate to update the
  baseline. Don't compare new-dataset scores to old-dataset scores.

## Schema

Minimum viable example:

```json
{
  "id": "stable-uuid",
  "input": { ... },
  "reference": { ... },
  "metadata": {
    "failure_mode": "api_hallucination",
    "source": "prod_trace",
    "trace_id": "...",
    "added_at": "2026-05-20"
  }
}
```

`reference` is optional — present it when ground truth exists (the
key that unlocks code-based evaluators), omit it otherwise.

Stable IDs matter — they let you join across runs to see *which*
examples regressed, not just that the mean dropped.

## Training-data contamination

If your task model is (or will be) fine-tuned on production data
that overlaps with the prod traces you're sampling into your golden
or calibration sets, you've contaminated your hold-out — the model
has already seen the test cases. Either:

- **Deduplicate eval data against training data** at ingestion
  (content hash, near-duplicate detection, or source-id matching).
- **Sample only from a time window the model has never trained on**
  (e.g., post-cutoff traffic), and freeze the cutoff in the dataset
  metadata.
- **Flag the eval set as potentially contaminated** and treat
  scores as upper bounds, not unbiased estimates.

The same applies to embedding-based evaluators using a fine-tuned
embedding model.

## Adding from failures (closing the loop)

Every interesting failure in a real run is dataset material. Wire a
one-click "add to dataset" path from your trace viewer. A static
dataset stops representing prod within months — the loop is what
keeps it honest.

## Failure funnels — find the highest-loss stage first

An agent's pipeline has sequential stages (retrieve → reason → format
→ respond). Map the error/dropout rate at each stage like a conversion
funnel to identify where most failures originate.

**Why it matters:** if retrieval fails 30% of the time, fixing the
reasoning step won't help those 30% — they arrive at reasoning already
broken. Fix the upstream stage first; downstream fixes are wasted until
upstream is solid.

**How to apply:** for each stage, track "fraction of inputs that arrive
correct AND leave correct." Compute the cumulative loss:

```
stage          inputs correct  outputs correct  stage loss
retrieval      100%            70%              30%   ← fix this first
reasoning       70%            63%               7%
formatting      63%            61%               2%
```

This is a dataset-design concern: your test set must include examples
that exercise each stage independently so you can localize failure. See
`references/eval-philosophy.md` for the orthogonalization principle
(each knob affects one thing); failure funnels are its applied form for
pipeline agents.

## Two-arm datasets (evaluating a change, not a system)

When the thing under test is a *change* — a new skill, prompt, model, or
tool description — you don't just need tasks, you need the **same tasks
run through two arms** (treatment vs baseline / previous version) so the
delta is measurable. The dataset shape, the with/without harness, the
cost-vs-quality delta table, and the disable-and-retest deprecation
check live in `references/skill-and-prompt-baseline-evals.md`.
