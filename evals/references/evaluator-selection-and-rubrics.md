# Evaluator selection & custom rubric design

Distilled from the DeepLearning.ai evals course, Module 3 (evaluator
selection, code evaluators, LLM-as-judge architecture, custom rubric
design). Companion to `error-analysis-and-test-sets.md` (Module 2 — the
data-first half). The meta-evaluation half of Module 3 — can you trust
the labels your evaluator produces — lives in `judge-calibration.md`
§ "Meta-evaluation".

Load when: choosing what kind of evaluator to build, writing a custom
judge rubric from scratch, or reviewing a rubric someone else wrote.
Mechanics that already live in `../phases/phase-3-evaluators.md`
(judge-prompt template, injection hardening, calibration procedure,
label-space choice) are pointed to, not repeated.

## 1. The decision determines the evaluator

Before writing any evaluation code, name the decision the evaluator has
to make. The decision picks the evaluator type — they are not
interchangeable.

| The decision | Evaluator | Why |
|---|---|---|
| One objectively correct answer (is this product in the catalog? is the price right? does the output match the required schema?) | **Code evaluator** | Deterministic, no model call, no variance |
| Requires judgment (is this helpful? does it answer the question? is the tone right?) | **LLM judge with a pre-built rubric** | Judgment at scale; start from a pre-built evaluator |
| Judgment specific to *your* policies, domain, or constraints | **Custom rubric** | No pre-built evaluator encodes your rules |

The two failure modes are symmetric:

- An LLM judge on an objective question adds cost and variance and buys
  nothing.
- A code evaluator on a judgment question produces brittle rules that
  miss the real failures.

**Try pre-built before custom.** Correctness, groundedness, relevance,
and refusal evaluators ship with most eval platforms and work unmodified
for most agents. Write a custom rubric only when the pre-built set does
not encode the criterion you actually care about. A custom rubric you
did not need is a rubric you now have to calibrate, version, and
maintain.

Worked three-tier stack (customer-service agent over a product
catalog):

1. `product_exists` — **code**: did the agent recommend a real product?
   Checks the agent's claim against the catalog.
2. `correctness` — **LLM judge, pre-built**: did the agent correctly
   answer the customer's question?
3. `policy_compliance` — **custom rubric**: did the agent stay inside its
   policy boundary (answers product and catalog questions only; does not
   invent return windows, refund processes, or contact channels)?

## 2. Code evaluators can check more than format

Code evaluators are the first line of defense: immediate, unambiguous,
and free beyond compute. Anything with a deterministic answer belongs
here, before a model is involved. The check table in
`../phases/phase-3-evaluators.md` lists the common shapes; the one
routinely under-used:

**Query an external source of truth and compare the agent's claim
against it.** When the agent makes a factual claim about *your* data —
product name, price, availability, account balance, tenant record — a
code evaluator can look the ground truth up in the database, catalog, or
API and verify the claim directly. That is groundedness checking with no
judge involved.

The recipe: find the objective question → find the source of truth →
write a function that compares the agent's claim against it.

Distinct from **agent-as-a-judge**
(`../phases/phase-3-evaluators.md` § Agent-as-a-judge), where an LLM
*decides* what to look up. If you already know which lookup settles the
question, write the lookup in code — same grounding, none of the
variance or cost.

## 3. An LLM judge is three swappable parts

A judge is a composition of a **judge model**, a **rubric** (the prompt
that defines the criteria), and **data** (the traces being evaluated).
The three change independently:

- Swap the judge model to improve accuracy.
- Revise the rubric to fix a criterion.
- Add traces to expand coverage.

None of those requires rebuilding the other two — but each invalidates
prior results, so re-calibrate after any of them (see
`../phases/phase-3-evaluators.md` § Calibration, step 5).

**Agent model ≠ judge model, and they optimize for different things.**
The agent model is tuned for speed and cost because it serves real user
requests. The judge model is tuned for accuracy because it decides
whether those responses met your criteria — so don't inherit the agent's
model by default, and pick the judge on measured agreement instead. A
*different provider* reduces the chance that judge and agent share the
same systematic blind spot; that is the mechanism behind the "different
model family" default in SKILL.md § Guardrails.

This does not mean "always reach for the biggest model." A smaller model
is often enough for a judge — it is classifying, not generating — and
`../phases/phase-3-evaluators.md` § Judge model choice is the arbiter:
the calibration set decides, not the price tier. Capability is only the
bottleneck when a stronger judge on the *same* rubric jumps agreement
(`judge-calibration.md` § "When calibration fails", step 3).

### Running the loop

1. Export traces from your agent runs.
2. **Suppress tracing around the evaluation calls.** You want your trace
   log to record agent behavior, not the judge's — un-suppressed judge
   calls pollute the very dataset you sample from next time. (Phoenix
   spells this `suppress_tracing()`; every tracing SDK has an
   equivalent.)
3. Run the judge over the exported set.
4. Log the annotations back alongside the traces.

**Evaluators tell you what failed. Traces show you why.** Use the
evaluator output to find which traces failed, then read those traces to
understand the failure mode. Neither substitutes for the other.

## 4. Five-part rubric anatomy

The rubric *is* the evaluation. Two judges with the same model on the
same response but different rubrics return different verdicts — getting
the rubric right is the whole job. Five parts, one design question each:

**1. Define the judge's role.** *What job is this evaluator doing?*
Name the subject and name the decision. "You are evaluating a customer
service agent response" is too vague to apply a standard. "You are
evaluating whether a Northwind Traders customer service agent correctly
follows its policy about which questions it is permitted to answer"
gives the judge the context to pick the right standard.

**2. State explicit criteria.** *How should it make its decision?*
Concrete and observable, in behavioral language. The judge cannot apply
"handles the topic safely" — it can apply "does not provide a return
window, refund process, or contact channel for returns or shipping
issues." A criterion that can be read two ways will be, inconsistently.
(When a judge flaps on borderline items, tighten the criterion before
touching the model — see `../phases/phase-3-evaluators.md` § Tighten the
spec before collapsing the rubric.)

**3. Provide inputs.** *What information does it need?* Wrap the data
in named XML tags inside a `<data>` block — `<customer_query>`,
`<agent_response>`. Separating instructions from data keeps the judge
from confusing rubric text with the content under evaluation, and is the
same delimiter discipline that hardens the prompt against injection
(`../phases/phase-3-evaluators.md` § Prompt injection hardening).

**4. Add labeled examples.** *What do good and bad look like?* At least
one compliant and one non-compliant, each paired with a one-line reason
naming the criterion it satisfies or violates. Examples are not new
rules — they demonstrate how the stated rules apply to a real case, and
they close the gap between what the rubric says and how the judge reads
it.

**5. Constrain the output.** *How should it report its verdict?*
Binary (`compliant` / `non_compliant`) by default. A third category
("borderline") adds ambiguity without adding diagnostic value; add one
only when there is a genuinely distinct, actionable middle case that
binary labels consistently misclassify. Reasoning first, label last —
see `../phases/phase-3-evaluators.md` § "Ask for the label, not the
reasoning, last" for the ordering, and § "Collapse to binary" for the
calibration-time evidence that tells you when a third class is real.

## 5. The God Evaluator anti-pattern

Do not evaluate multiple dimensions in one rubric. A rubric that scores
helpfulness, accuracy, tone, and policy compliance together cannot tell
you which dimension caused a failing verdict, and you cannot check
whether the judge applied the right criterion.

Build one evaluator per dimension, then **combine verdicts with
programmatic rules** — `correctness AND policy_compliance` — rather than
asking one rubric to hold everything. The combining rule is part of the
eval definition and must be specified alongside the sub-rubrics
(`../phases/phase-3-evaluators.md` § "Aggregation rule matters as much
as sub-judge prompts" — that section is the calibration-time evidence
for why a bad combining rule looks like a bad judge).

Dimensions are genuinely independent in practice: a response can pass
`product_exists` and `correctness` while failing `policy_compliance`
(real product, right answer, but it invented a return window), or pass
`policy_compliance` while failing `correctness` (stayed in bounds,
answered wrong). Each evaluator catches a distinct failure mode. That is
the point of building one per dimension.

## 6. Guardrails vs north-star metrics

Evaluators do two different jobs and both are necessary:

- **Guardrails** block unacceptable behavior — inventing a return
  process, fabricating a product, claiming an out-of-stock item is
  available. They define the floor.
- **North-star metrics** measure how good the agent is at its job —
  correctness, helpfulness, appropriate tone. They define the ceiling
  you are aiming at.

A stack with only guardrails cannot tell you whether the agent is
getting better. A stack with only north-star metrics cannot tell you
whether it is safe to ship. Label each evaluator with which one it is —
the label drives its calibration bar (`../phases/phase-3-evaluators.md`
§ "Calibration regime: measurement vs guardrail") and its CI treatment
(capability vs regression tagging, SKILL.md § Session Rules).

## 7. Common rubric mistakes

- **Vague criteria** — "appropriate response" instead of "does not
  discuss returns or shipping."
- **Too many criteria in one rubric** — the God Evaluator problem above.
- **Never testing the rubric** — writing it and deploying it without
  checking whether its labels agree with carefully reviewed human
  labels. See `judge-calibration.md` § Meta-evaluation.

**Treat eval prompts like code.** A rubric is a program: it has bugs, it
needs tests, and it needs maintenance. Version it, test it against
labeled examples before deploying, and when you change it, change one
thing at a time and measure what moved.
