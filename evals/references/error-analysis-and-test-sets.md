# Error analysis & test-set construction — data-first practices

Distilled from the DeepLearning.ai evals course, Module 2 (Video 1: "Start
with data, not metrics"; Video 2: test sets and human baselines). First
applied to charley.bot 2026-07-12 — triage + taxonomy record at
[courierflow_beta#668](https://github.com/sumrae412/courierflow_beta/pull/668),
plan in the henry repo `docs/plans/2026-07-12-charley-eval-best-practices-plan.md`.

Load when: standing up evals for a new surface, mining failures from run
artifacts, expanding a dataset, or reviewing an eval plan against best
practice. Overlapping ground already in this skill is pointed to, not
repeated.

## 1. Error-analysis workflow (before inventing metrics)

Move from ad hoc browsing to this loop once you have more traces than you
can read by hand:

1. **Split the workflow's decisions into objective vs subjective.**
   Objective (lookup with a yes/no answer) → write the eval up front,
   clean pass/fail, code-based grader. Subjective (judgment on free-text
   input) → do NOT guess failure modes; run a small set, hand-review,
   build evals around failures you actually found.
2. **Start with 10–20 examples** — enough to see patterns; don't chase
   accurate metrics yet.
3. **Four-field failure record** per failure: input, agent output,
   relevant metadata (model/tier/stop_reason), one line "what went
   wrong."
4. **Name the failure before you fix it.** Label each with a failure
   type (reasoning error, scope violation, unsupported information,
   hallucination, plus domain labels). Fixing mistakes one at a time
   hides the broader pattern; repeated failure types tell you what to
   measure — not generic metrics like "helpfulness."
5. **Triage before labeling** — every failure is infra / grader / task
   first (see SKILL.md Session Rules). Only task failures enter the
   taxonomy. A 0% batch means a broken task, environment, or grader,
   never a bad agent.

The philosophy behind this loop (Hamel's "Look at the Data™", Eugene
Yan's EDD cycle) is in `eval-philosophy.md`; this section is the
operational checklist.

## 2. Test-set construction do's

Sourcing hierarchy, sizes, splits, schema, and the closing-the-loop rule
live in `../phases/phase-2-datasets.md`. On top of those:

- **No source is neutral — read scores per-source.** Support queues and
  bug reports skew toward failures; most-common-requests skew easy;
  synthetic skews toward whatever the generator prompt emphasized. Record
  `metadata.source` on every case (the phase-2 schema has the field) and
  use it deliberately when interpreting a score.
- **Treat every reported failure as an already-labeled example** — it
  arrives with its own ground truth. Turn it into a case within one
  triage cycle, before context evaporates (run artifacts written to temp
  dirs do not survive; persist per-item rows with the baseline).
- **Prioritize by user impact:** build cases first where a failure would
  hurt someone (safety redlines, money, state mutations) before
  tone/quality cases.
- **Cover the ways a single requirement can break**, and write cases
  before building so they guide tools, prompts, and rules — define
  success before behavior exists, or you'll mistake current behavior for
  intended behavior.
- **Curation gates for any generated batch:** drop true duplicates and
  cases that test nothing new; drop cases whose only finding is a
  one-line prompt fix; keep cases that reveal lasting problems. Every
  kept case has a recurring cost (reruns on every change; judgment cases
  need review) — target coverage, not volume.
- **Mining outputs assert; they don't prove.** Any mined claim about
  fixture or dataset contents ("case X contains/lacks Y") must quote the
  file line that proves it before entering a taxonomy or merged doc —
  one unquoted claim cost a correction PR (2026-07-12, Q016,
  [courierflow_beta#671](https://github.com/sumrae412/courierflow_beta/pull/671)).
- **Synthetic diversity axes** — vary along three independent axes
  rather than generating more of the same:
  - *situation* (the scenario itself),
  - *information quality* (detailed / vague / conflicting),
  - *phrasing* (full sentences / shorthand / typos / second-language
    phrasing).
  For user-facing text channels (SMS, chat), shorthand and typos ARE the
  production distribution — treat that axis as required, not optional.
- **Weaker-model failure mining:** run your prompts through a weaker,
  cheaper model; its organic mistakes resemble real production failures
  better than hand-crafted defects. Curate the results like any
  synthetic batch — a small model's error *distribution* is not ground
  truth. (Distinct from judge-model choice in
  `../phases/phase-3-evaluators.md`; this is about the SUT arm.)

## 3. Ambiguity dual-review (task quality, pre-grader)

A good task is unambiguous. Test it: show the task and an output to two
independent reviewers; each answers pass or fail. Disagreement = the task
is ambiguous — inspect the disagreement (ask each to explain), then
revise the task or rubric until explicit criteria resolve it. Run this
on a sample before investing in grader calibration
(`../phases/phase-3-evaluators.md` § Calibration assumes the task itself
is answerable).

Also run dual-review on existing FAILURE CLUSTERS before any
grader-repair work — it localizes grader-vs-task cheaply at zero API
cost (subagent reviewers only). Read both agreement patterns: a
disagreement flags an ambiguous task; unanimous human-PASS/grader-FAIL
flags rubric over-exactness. Validated 2026-07-12 (charley correctness
suite, [courierflow_beta#671](https://github.com/sumrae412/courierflow_beta/pull/671)):
14 contested cases, 13/14 reviewer agreement — the 1 disagreement and
the 4 unanimous PASS/FAIL splits were equally load-bearing, and the
review overturned one merged taxonomy label.

Reference solutions serve the same pre-flight role: a known-good output
proves the task is solvable AND the grader is configured correctly. For
open-ended tasks the reference captures the important constraints, not
one exact answer (an exact-string referral reference fails semantically
correct outputs — loosen to constraint form); for state-changing tasks
it is a state condition.

## 4. Balance and honest reporting

- **Balance toward roughly 50/50 pass/fail** (Eugene Yan — see
  `eval-philosophy.md`) so easy cases don't dominate the metric and hide
  what needs fixing. Applies to *capability* sets; regression/safety
  sets stay one-sided by design (target ~100%) and are reported as such.
- **A balanced set is not a production failure rate.** A 50/50 set
  scoring 60% does not mean 40% of production traffic fails. For
  production reporting use category-level or traffic-weighted metrics;
  keep the balanced-set number for development iteration and label which
  is which in every artifact.
- **Test both directions** — should-act AND should-not-act — or you
  optimize toward an agent that does everything (already a SKILL.md
  guardrail; recorded here because it is a Module 2 core do).

## 5. Human-baseline realism

- Humans are not a clean reference: two humans reviewing the same trace
  disagree more than you'd expect (expert κ often lands around 0.2–0.3),
  and raters miss defects from fatigue.
- Structure annotation: clear rubric, passing AND failing examples,
  edge-case instructions, a disagreement-resolution path.
- Judge an LLM evaluator against the real alternative: the bar is "more
  consistent than a tired, disagreeing human," not perfection — an
  evaluator should be consistent, rubric-aligned, sensitive to important
  failures, and calibrated against reviewed examples
  (`judge-calibration.md` for the cadence; `../phases/phase-3-evaluators.md`
  § Calibration for the mechanics).
- κ limits: affected by label prevalence, and high agreement does not
  prove reviewers are right — it proves they're similar. Same trap as
  cross-provider judge agreement (see SKILL.md Guardrails).
