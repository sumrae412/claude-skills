# Primary Research Playbook

Cheap primary research that can overturn the plan — survey design,
willingness-to-pay elicitation, and the single break-even variable.

Load during Phase 1 when the idea's core risk is *"will a person pay
recurring money for this"* and desk research alone can't settle it.
Skip when the gating risk is technical feasibility, regulatory approval,
or enterprise sales-cycle length — see **Fit** at the bottom.

## 0. Pre-register the kill number — before any research runs

Write down, in advance, the result that would produce a **No-Go**. A
specific number, not a posture.

> "If median stated WTP lands under $15/month, this is a No-Go."

Research designed after the hypothesis confirms it. A criterion written
only once the data is back is not a test — it is a rationalisation with
a chart. If no kill number was recorded before the evidence arrived,
label the verdict `confirmatory — not falsified` in Phase 7 output and
discount it accordingly.

This is the single highest-leverage step in the playbook. Everything
below is worth less without it.

## 1. Desktop research — look for adjacent-market proof

Two questions, not one:

- **Does money already move in this category?** Spend flowing to a
  different buyer (enterprise, clinical, B2B) is stronger evidence than a
  consumer TAM projection, because it is observed rather than forecast.
  Name the incumbent channel and roughly what it captures.
- **Has anyone been paid to exit here?** One acquisition or one durable
  profitable operator is existence-proof that the category can support a
  business. Absence is not disproof, but it changes the burden.

The useful shape of this finding is *"the money is already here, just not
flowing to this buyer"* — which reframes the question from "is there a
market" to "can this buyer be reached profitably."

**Every number carries a source or the inline label `unverified`.** No
exceptions, applied before the memo ships rather than when someone asks.
An unsourced multiple ("returned ~25x to early investors") laundered into
a deck is how a validation exercise starts lying to its own author.

## 2. Cheap primary survey

A small survey is not a substitute for customer interviews. It is a
cheap instrument for finding out whether the thing you believe is
*widely* believed, and for producing a number you can be wrong about.

### Design

- **Screen hard.** Qualify on the behaviour that defines the buyer
  (bought the adjacent product in the past year, visited the relevant
  professional in the past year). A screened n=100 beats an unscreened
  n=500.
- **Budget honestly.** Panel responses run roughly $1-2 each; a screened
  100-response survey is on the order of $150. This is cheap enough to
  run before the idea deserves it, which is the point.
- **Three question types, all three required:**

| Type | Asks | Catches |
|---|---|---|
| Problem intensity | "My [X] could be failing right now and I wouldn't know" — agree/disagree | Whether the pain is felt, not just describable |
| WTP as a **number** | "What would you pay per month?" — open or laddered bands | The gap between "yes I'd pay" and what they'd actually pay |
| The overturning question | One question whose answer could move the business model | Whether the plan survives contact |

### Ask willingness-to-pay as a number, never yes/no

A yes/no WTP question answers a different and less useful question.
Worked example: 46% said they would pay for the service, which reads as
validation — but the median number they named was **$12/month**, and only
24% would go to $25+. The binary version of that question would have
shipped a business built on a price point most of the market rejects.

Elicit the number. Report the **median**, the share above your intended
price, and the share above the price you would need if costs run high.

### Segment WTP by behaviour, not demographics

Cross-tab willingness to pay against what respondents *already buy*, not
against age or income. In the worked example, overall WTP was thin, but
61% of respondents who already bought the adjacent product would pay
$20+/month — a different business than the headline number implied.

Behaviour predicts revenue. Demographics predict very little, and
segmenting on them is how a survey produces a persona nobody can find.

### Write one question that can overturn the plan — then let it

Include at least one question whose answer you would not like. In the
worked example the question was *where* the buyer would tolerate the
service being delivered; 63% would only accept it through the
professional they already trusted, which killed the direct-to-consumer
model outright and replaced it with a channel play.

A survey that cannot produce a result you don't want is not testing
anything. When the overturning question fires, the plan changes — that
is the instrument working, not the research failing.

### Separate problem intensity from willingness to pay

Track them as two distinct findings and watch for divergence. In the
worked example, 71% reported the fear and only 24% would pay $25+. Fear
is not a budget line. High intensity plus low WTP is a real and common
result; it usually means the problem is genuine but the buyer expects
someone else to pay for it — which is a channel and business-model
finding, not a reason to discard the idea.

### Report the sample honestly

A self-selected panel of 100 does not support percentages quoted to the
decimal. Report as ranges, and put the selection bias in the same
sentence as the headline:

> "Roughly 40-50% of screened respondents (n=100, self-selected panel)
> said they would pay; median named price $12/month."

**Stated WTP is a ceiling, not an estimate.** People are more generous
with hypothetical money than real money. Treat the number as directional,
never as a revenue forecast, and never model conversion at the stated
rate.

## 3. Name the number that decides it

Every business has one variable that, if it lands wrong, invalidates the
plan regardless of how the rest of the analysis scored. Find it, name it,
and settle it before anything downstream gets built.

> "If all-in cost to serve exceeds ~$70 per unit, the $299 price point
> collapses and you are forced to $399+, where the survey says most of
> the market falls away. Get the supply contract right before you get the
> logo right."

Requirements:

- It is a **number with a threshold**, not a risk category.
- Crossing the threshold changes the verdict, not just the plan.
- It names the cheapest experiment that would settle it.

This upgrades Phase 1's "CAC / CLV logic when possible" from a
nice-to-have into a gate. Where CAC and LTV are the relevant variables:

- **CAC** — state the target and the expected paid-channel drift at
  scale. High-intent audiences are high-intent for your competitors too;
  early organic CAC is not the number you will pay later.
- **LTV** — must carry a churn assumption sourced from a comparable
  business. An unstated "customer stays five years" default is the most
  common way an LTV figure becomes fiction. Absent real data, show two
  scenarios (conservative and generous) rather than one number.

## 4. Size competitors as threats, not as a list

For each named competitor state **what they would have to change to
compete directly**: nothing, a repricing, a new feature, or a new
capability. A competitor who would have to do nothing is a different
finding than one who would need to rebuild.

A list without a threat-size column is a bibliography, not competitive
analysis.

## Fit

**Fits:** consumer and prosumer ideas where the core risk is *"will a
person pay recurring money for this"* — the playbook is built around a
survey instrument and a subscription economics model.

**Misleads for:**

- **B2B / enterprise** — the survey respondent is not the buyer, and the
  real risk is sales-cycle length and procurement, not stated WTP.
- **Regulated or infrastructure businesses** — the gating question is
  compliance, licensing, or capacity, and a clean demand read tells you
  nothing about whether you are allowed to operate.
- **Pre-product technical bets** — a Go here can still be a No-Go on
  "can we build it." Feasibility is a separate gate this playbook does
  not test.

When the idea sits in one of those classes, run Phases 1-5 normally and
skip this file rather than producing a confident number about the wrong
risk.
