# Binding-Constraint Diagnosis

Which risk actually decides this idea — and whether this stack is the
right instrument for it.

Load at Phase 0, before the kill number is named. Everything downstream
depends on getting this right, and getting it wrong produces a confident
verdict about the wrong risk.

## The problem this solves

Every viability framework pre-supposes its own answer. A demand framework
assumes demand is the risk. A feasibility framework assumes build risk. A
regulatory framework assumes compliance is the gate. Run any of them
against an idea whose real constraint sits elsewhere and it will execute
cleanly, score well, and be wrong.

**This stack is demand-weighted.** Phases 1-5 and the Phase 5.5 pillars
are built to answer *"will someone pay for this?"* That is the right
question for most consumer and prosumer ideas and the wrong one for a
meaningful minority. Name the binding constraint first so you know whether
you are using the right tool, or the right tool plus an extra gate.

## The six constraint classes

Name exactly **one** as primary. Ties mean the diagnosis isn't finished.

| Class | The question it asks | Signal you're here |
|---|---|---|
| **Demand** | Will anyone pay, and enough? | Product is obviously buildable and legal; the only real unknown is the buyer |
| **Epistemic** | Does the knowledge required to build this honestly exist yet? | The product's core promise depends on a body of evidence, data, or research that may not exist at usable quality |
| **Feasibility** | Can we build it at all, with current technology and this team? | Core mechanic depends on an unsolved technical problem, not an unbuilt one |
| **Regulatory** | Are we allowed to operate, and under what conditions? | Licensure, professional-practice rules, or approval sits between the product and its user |
| **Distribution** | Can we reach the buyer at a cost that works? | Demand is well-established by incumbents; nobody has found a profitable channel to this segment |
| **Unit cost** | Can we deliver at a price the market clears? | Demand and channel are both proven; margin is the open question |

### Epistemic is the one most often missed

It looks like feasibility and is not. Feasibility asks *can we build the
thing*; epistemic asks *does anyone know enough for the thing to be
honest*. The tell is that no amount of engineering or vendor spend closes
the gap — because the gap is in the primary literature, not in your
implementation.

**Worked example.** A pet supplement interaction checker: demand tested
strong (high stated problem intensity, an existing supplement-buying
cohort with the highest willingness-to-pay in the sample, reachable breed
communities, and no competitor doing supplement-supplement checking).
Every demand-side pillar would have scored Pass. But veterinary
pharmacology literature reports species-specific supplement-interaction
data as rare, with clinical practice estimating risk from human data.
Licensing a comprehensive database does not fix that — it packages the
same extrapolation. The idea's binding constraint was epistemic, and a
demand-weighted run would have returned Go on a product that cannot make
its core promise honestly.

Ask directly: **is there a body of knowledge this product's core claim
depends on, and does it exist at the quality the claim requires?** If the
answer is no, the demand result is irrelevant — a market that wants
something unbuildable is still a No-Go.

## What to do once it's named

- **Primary constraint is Demand** → run this stack as designed. Load
  [`primary-research-playbook.md`](primary-research-playbook.md) if desk
  research can't settle willingness to pay.
- **Primary constraint is anything else** → say so explicitly in the Phase
  0 output, and add a gate that tests it *before* Phase 1 spends effort on
  market sizing. A demand read is not wrong here, it is just not the
  answer. Note in Phase 7 which constraint the verdict actually tested.
- **Primary constraint is Epistemic, Feasibility, or Regulatory** → that
  gate is cheap and usually decisive. Run it first. A No-Go there saves
  the entire rest of the analysis.

## Order research by expected information per dollar

The stack is already ordered so each stage is cheaper than the one after
it, and each can kill the idea before the expensive one spends. Keep that,
but rank *within* what's available by:

> **(probability this result kills the idea) ÷ (cost to run it)**

Run the highest ratio first. Cost-ordering alone routinely puts a $150
survey ahead of a near-free literature check that was twice as likely to
end the analysis.

In the worked example above, the decisive check cost roughly nothing — a
dozen searches against veterinary pharmacology sources — and had close to
even odds of killing the idea. The survey cost $150 and had perhaps a
one-in-six chance. Cost-ordering gets that backwards.

State the ranking before running anything. Two or three candidate checks
with a rough ratio each is enough; this is a sequencing aid, not a model.

## The No-Go path test

Before any research runs, ask of the plan:

> **What result would stop this, and which stage produces it?**

If no stage in the plan can generate that result, the plan is a case for
the idea, not a test of it. Fix the plan, not the write-up.

This is the architectural version of the kill number. The kill number says
*what* would stop it; this says *whether anything in the plan could ever
find that out*. A study with impeccable reporting hygiene and no route to
No-Go is still not a test.

## Resolving the circularity

Naming a kill number requires knowing which variable binds — which is why
this file runs first. Diagnose the constraint, then set the kill number
**against that constraint**, not against whichever metric is most familiar.

The failure mode is pre-registering a rigorous-feeling threshold on the
wrong axis: a willingness-to-pay kill number on an idea whose real gate is
whether the underlying science exists. That feels disciplined and tests
nothing that matters.

If the constraint diagnosis is genuinely uncertain, say so and pre-register
a kill number for each candidate constraint rather than picking one for
tidiness.
