# Nemotron-Personas-USA Filter Guide

## Dataset

- HuggingFace: `nvidia/Nemotron-Personas-USA`
- ~100K US-demographic-grounded synthetic personas
- Per-persona fields (typical): `age`, `sex`, `ethnicity`, `location`, `occupation`, `education`, `household_income_bracket`, `marital_status`, `children`, `persona_text` (free-form backstory), plus derived fields.
- License: verify at the dataset page (typically CC-BY-4.0).

## Load

```python
from datasets import load_dataset
ds = load_dataset("nvidia/Nemotron-Personas-USA", split="train")
```

## Segment → field mapping

Segments in `$app_config.segments` are free-form tags. Map each to a boolean rule over Nemotron fields. Extend `SEGMENT_RULES` in `scripts/filter_nemotron.py` as new apps need new segments.

| Segment | Rule |
|---|---|
| `small_landlord_us` | `occupation ∈ {"landlord","property manager","real estate investor"}` OR `persona_text` contains "rental propert(y|ies)" |
| `renter_us_urban` | `persona_text` mentions "rent" AND `location_type == "urban"` |
| `freelance_creative` | `occupation ∈ {"designer","writer","artist","freelancer"}` AND `employment_type == "self-employed"` |
| `retiree_fixed_income` | `age >= 65` AND `household_income_bracket ∈ {"<25k","25-50k"}` |

**Phase 1 must confirm mappings with the user** before writing `$app_config.segments`. Nemotron field names shift across dataset versions — verify against the actual schema of the loaded dataset if a rule matches zero personas.

## Stratified sampling

Within each segment, stratify by:

- **Age bucket** (5 buckets): 18-29, 30-44, 45-59, 60-74, 75+.
- **Location type**: urban, suburban, rural (derive from city population if the field isn't direct).
- **Education**: no-college, some-college, bachelor+, grad.

Goal: avoid Nemotron's natural density clustering (e.g., all personas ending up 35-year-old urban bachelors).

## Axis inference

Nemotron personas don't come labeled with our custom `diversity_axes`. After sampling, Phase 2 Step 2 does one LLM call per persona to map them onto `[0,1]` positions per axis. Include a confidence note; extremely low-confidence positions (<0.3) should be flagged in `generator_metadata` for optional human review.

## Licensing & redistribution

Do not redistribute the full dataset in eval outputs. Transcripts may reference sampled personas by `_nemotron_id` plus a short descriptor; don't copy full `persona_text` into public artifacts unless the license permits.

## Common failure modes

- **Zero matches:** field names differ from your rule. Inspect `ds.features` and adjust `SEGMENT_RULES`.
- **Too few matches after stratification:** reduce stratification dimensions (e.g., drop education) or widen the segment rule.
- **Too-similar personas:** Nemotron densities cluster. Increase `pool.tail` so the two-stage generator fills the edges.
