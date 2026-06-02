# Fair Housing Rules

## Forbidden classes (HUD)

Race, color, religion, national origin, sex, disability, familial status, age.

## Enforcement in this skill

- `propensity.py` imports `FORBIDDEN_FIELDS = frozenset({"race", "ethnicity", "religion", "sex", "family_status", "disability", "age", "national_origin"})`.
- A unit test asserts no scoring expression references any forbidden field.
- The skill refuses CLI flags or `criteria.yaml` keys whose name matches a protected class.
- Neighborhood targeting is allowed by polygon / zip / boundary — NEVER by demographic descriptor.

## Why divorce / bankruptcy are excluded

Legal to use (public records), but coming from a family wanting to live there, this kind of outreach is creepy. Investor playbook ≠ owner-occupier playbook. If you ever flip this skill into an investor tool, revisit.
