# Eval Philosophy

Synthesized from Andrew Ng, Hamel Husain, Eugene Yan, and the "Applied
LLMs" group. Use this when designing an eval *practice*, not when
picking a metric — the phase files cover tactics. This file is the
*why* behind those tactics.

Source: `~/claude_code/Comprehensive_AI_Evaluation_Framework.md`.

---

## Andrew Ng — orthogonalization & the single number

**Orthogonalization.** Each control should affect one aspect of
performance. When a knob affects training fit AND generalization at
once (e.g. early stopping), debugging is exponentially harder. Apply
this when designing evals: one evaluator, one criterion. Mirrors the
"one judge, one criterion" rule in `../SKILL.md`.

**Single optimizing metric, satisficing constraints.** Pick one number
to maximize; everything else is a constraint. "Maximize accuracy
subject to <100ms latency" beats "track accuracy, latency, cost
separately." Multiple co-equal metrics kill decisions — you can't
compare 94%@80ms vs 92%@60ms without a tiebreaker.

**Modern splits.** With 1M+ examples, 98/1/1 train/dev/test is fine.
Dev/test only need enough samples for confident evaluation (~10K).
If you're tuning on "test", it's actually dev — rename it.

---

## Hamel Husain — "Look at the Data™"

**Manually inspect 100 failures before building anything.** This is
the most-repeated lesson from his blog and podcasts. Sampling 100
real failures and categorizing by root cause beats any automated
metric for prioritization.

**Hierarchy of impact** (highest ROI first):

1. Data quality fixes
2. Prompt engineering
3. Model selection
4. Hyperparameter tuning

Each level down requires exponentially more effort for diminishing
returns. Don't reach for fine-tuning when bad labels are the problem.

**LLM-judge reality check.** If you can't manually evaluate 100
examples consistently yourself, don't automate it yet. The judge is
scaling *your* pattern — there has to be a pattern first.

**Common excuses to skip evals** (and why they fail):

- "We'll add evals later" → later never comes
- "Our task is too subjective" → all tasks decompose into measurable parts
- "We don't have test data" → start with 10 examples

Rule of thumb: every hour spent on evals saves ~10 hours of production
debugging.

---

## Eugene Yan — eval as practice, not tool

**Evaluation is a practice, not a tool you install.** Tools amplify
existing process — good or bad. Without discipline they create noise,
not signal.

**Eval-Driven Development (EDD).** Like TDD, but for AI:

1. Write eval criteria *before* building
2. Measure baseline
3. Make changes
4. Verify with evals
5. Nothing ships without eval validation

**Six-step scientific cycle:** Observe → Annotate → Hypothesize →
Experiment → Measure → Iterate. Annotation should aim for ~50/50
positive/negative coverage, with measured inter-annotator agreement
(Cohen's kappa ≥0.6 minimum).

**Long-context Q&A — two orthogonal dimensions:**

- **Faithfulness** (groundedness): does the answer rely only on the
  source? Includes knowing when to say "I don't know." Faithfulness ≠
  correctness — an answer can be generally true but unfaithful to the
  specific document.
- **Helpfulness:** relevance + comprehensiveness + conciseness.

The tension: a faithful answer can be useless. Score both, separately.

---

## Build-Analyze cycle & maturity stages

Less experienced teams over-index on building and under-invest in
analysis. Analysis is what tells you *where* to build next.

| Stage | Eval shape |
|-------|------------|
| Prototype | Manual trace inspection, 10-20 examples |
| Early maturity | End-to-end evals, simple metrics |
| Disciplined | Systematic error analysis, component-level evals |
| Production | Component evals, continuous monitoring, cost/latency optimization |

Optimize cost and latency *after* quality is proven, not before.

---

## How to apply this in a session

- Before picking a metric, ask: what failure mode am I trying to
  detect? (See `../SKILL.md` Session Rules.)
- Before automating judges, ask: have I manually labeled ~100 of
  these? (Hamel's rule.)
- Before adding a second metric, ask: which is optimizing, which is
  satisficing? (Ng's rule.)
- Before declaring an improvement, ask: did I measure a baseline and
  beat the noise floor? (EDD + `phases/phase-4`.)
- Before scaling an eval pipeline, ask: is the process good, or am I
  amplifying a bad one? (Yan's rule.)
