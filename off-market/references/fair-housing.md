# Fair Housing Rules

## Forbidden classes (HUD + stricter house policy)

The federal Fair Housing Act (FHA / HUD) protects 7 classes: race, color, religion, national origin, sex, disability, familial status.

We also forbid `age` as a stricter internal policy even though it isn't a federal FHA class (it's covered by ECOA for credit and by some state/local fair-housing laws).

## Enforcement in this skill

- `propensity.py` imports `FORBIDDEN_FIELDS = frozenset({"race", "color", "religion", "national_origin", "sex", "disability", "familial_status", "age"})`.
- A unit test asserts no scoring expression references any forbidden field.
- The skill refuses CLI flags or `criteria.yaml` keys whose name matches a protected class.
- Neighborhood targeting is allowed by polygon / zip / boundary — NEVER by demographic descriptor.

## Why divorce / bankruptcy are excluded

Legal to use (public records), but coming from a family wanting to live there, this kind of outreach is creepy. Investor playbook ≠ owner-occupier playbook. If you ever flip this skill into an investor tool, revisit.
