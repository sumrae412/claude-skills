# Propensity Rubric (Lean v1)

Each candidate parcel is scored 0–100 by summing the weights of every signal that matches. Weights and reason codes are surfaced on every row so a human can audit why a score landed where it did.

## Rubric

| Signal | Weight | Reason code |
|---|---|---|
| Sheriff sale scheduled (auction date set) | 40 | `sheriff_sale:<YYYY-MM-DD>` |
| Tax-delinquent | 5 base + 0.5 per $1k owed (cap 25) | `tax_delinquent:$<amount>` |
| Owner name matches `Estate of` / `Heirs of` / `, Deceased` | 20 | `probate_name_pattern` |
| Absentee owner (mailing state ≠ property state) | 10 | `absentee:<owner_state>` |
| Long tenure (≥20 yrs) AND equity ≥ 60% of est. value | 10 | `long_tenure_high_equity:<years>` |

## Cutoff tiers

| Score | Tier | Action |
|---|---|---|
| `<15` | drop | Not worth a stamp. |
| `15–39` | worth a letter | Include in standard outreach batch. |
| `40–69` | high priority | Pull to the top of the batch. |
| `≥70` | act this week | Likely time-sensitive — sheriff sale on calendar, or stacked signals. Move now. |

## Weight rationale

**Sheriff sale scheduled — 40.** This is the loudest signal in the rubric. A scheduled auction date means the owner has a finite, court-imposed window to either pay, refinance, or sell. A pre-auction letter that offers an alternative to losing the home outright (and the equity in it) is the most likely to be welcomed of any letter in the system. Weighted heavily on purpose: one match alone should clear the "high priority" cutoff.

**Tax-delinquent — 5 + 0.5/$1k (cap 25).** Tax delinquency is a softer signal than a sheriff sale — many owners are years behind without ever facing forced sale — so the floor is modest. The dollar-amount scaler captures urgency: $80k owed is structurally different from $400 owed. Cap at 25 prevents one runaway delinquent from dominating; in combination with other signals it can still push a parcel into the high-priority tier without crowding everything else out.

**Probate name pattern — 20.** "Estate of John Doe" or "Heirs of Mary Smith" in the assessor's owner-name field is a strong public-record signal that the property passed through probate and may be held by family members who don't want it. The weight is meaningful (a single match plus one secondary signal clears the high-priority line) but not as heavy as sheriff sale, because the name pattern can persist on the deed for years after the heirs have already settled into ownership.

**Absentee owner — 10.** Out-of-state owners are statistically more likely to sell than owner-occupiers — distance erodes attachment and amplifies the friction of repairs, tenants, and taxes. A relatively low weight on its own (10 won't clear "worth a letter") but it stacks well with tenure/equity and delinquency. Mailing-state mismatch is the cheap proxy; the heavier "tired landlord" join (multi-property + violations + eviction filings) is deferred to v1.1.

**Long tenure + high equity — 10.** A 25-year owner with most of the value as equity is the classic "ready to downsize / move closer to grandkids" profile — high optionality and minimal financial constraint to a sale. The compound gate (both ≥20 yrs AND ≥60% equity) is deliberate: each leg alone is too weak. Weight is modest on its own but combined with absentee or probate it cleanly hits high-priority.

## Hard filters (applied before scoring)

- Currently listed on Zillow/Redfin → excluded entirely.
- Fails `criteria.yaml` (beds, sqft, lot, year built, price, neighborhood) → excluded.
- LLC owner with >5 properties → flagged `professional_investor` but NOT excluded (a tired landlord is still a candidate).

## What is NOT in this rubric

- No HUD-protected-class fields (race, religion, national origin, sex, disability, familial status, age) — directly or via proxy. Enforced by `references/fair-housing.md` + a unit test in `propensity.py`.
- No divorce / bankruptcy filings — legal but inappropriate for owner-occupier outreach.
- No per-address vacancy (only census-tract aggregates are free).
