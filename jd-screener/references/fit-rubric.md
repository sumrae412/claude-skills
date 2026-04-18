# Fit Rubric — Profile Schema + Scoring

## Profile Schema

```yaml
candidate_profile:
  name: "…"
  current_role:
    title: "…"
    company: "…"
    start: "YYYY-MM"
  career_arc:
    - { title, company, start, end, team_size, scope_notes }
  tenure:
    total_career_years: N
    leadership_years: N          # strict: years in direct DS/mgmt leadership
    total_management_years: N    # inclusive of early-career non-domain mgmt
  education:
    - { degree, school, year }
  signature_projects:
    - { name, description, url_if_public, relevance_keywords }
  publications_speaking:
    - "…"
  keyword_coverage:
    strong: [ "RAG", "LLM", "data governance", … ]
    working: [ "…" ]             # can speak to, not deep
    none: [ "…" ]                # explicit gaps

search_preferences:
  comp_floor: 325000
  comp_target: 400000
  work_mode: remote              # remote | hybrid | onsite | flexible
  locations_ok: [ "US-anywhere" ]
  level_range: [ director, vp, exec ]
  domain_prefs: [ healthcare, biotech, AI/ML-tools ]
  domain_excludes: [ defense-primary, adtech ]
  deal_breakers:
    - "Onsite 5 days a week"
    - "Salary <$300K"
    - "Requires security clearance candidate doesn't hold"
```

**Rules:**

- Tenure numbers are defensible against a LinkedIn check. Stretched tenure is a NO_GO risk at screening, not a scoring advantage.
- `keyword_coverage` is pre-declared at Phase 1; Phase 3 matches JD must-haves against this list, not against a fresh re-read of the resume.
- `deal_breakers` are binary. One hit = NO_GO. Do not weight around them.

---

## Scoring (Phase 3)

Compute each dimension independently, then combine. Round all scores to the nearest 5%.

### 1. Title / Level Fit

| Situation | Score |
|---|---|
| JD title matches a title the candidate has held or is currently in | 90–100 |
| JD title is one level up from current (e.g., Director → VP) | 65–80 |
| JD title is two levels up (e.g., Director → C-suite) | 30–50 |
| JD title is one level down from current | 75–85 (fine for non-growth pivots) |
| JD title is two+ levels down | 40–60 (flag: compensation/status misalignment) |

### 2. YOE Fit

Compare JD required YOE range (e.g., "12–15+") against `candidate_profile.tenure.leadership_years` or the most relevant sub-metric.

| Situation | Score |
|---|---|
| Candidate tenure ≥ JD minimum | 90–100 |
| Candidate tenure within 1–2 years of minimum | 70–85 (stretch) |
| Candidate tenure 3–5 years short | 40–60 (big stretch; cover letter must justify) |
| Candidate tenure 6+ years short | 15–35 (reach) |
| Candidate tenure exceeds max by >5 years | 70–85 (flag: possible overqualification) |

### 3. Domain Fit

| Situation | Score |
|---|---|
| Same industry + same vertical (e.g., healthcare + patient-facing SaaS) | 90–100 |
| Same industry, adjacent vertical (e.g., biotech → healthcare advocacy) | 65–80 |
| Adjacent industry, same function (e.g., fintech ML lead → healthcare ML lead) | 50–70 |
| Unrelated industry, function is portable | 30–50 |
| Unrelated industry, function also unfamiliar | 10–30 |

### 4. Must-Have Coverage

For each JD must-have keyword/requirement, categorize the candidate's evidence:

- **DIRECT**: resume bullet or signature project explicitly covers it → count as 1.0
- **TRANSFERABLE**: same skill in different domain/stack → count as 0.7
- **ADJACENT**: related but not the same skill → count as 0.4
- **GAP**: no evidence → count as 0.0

Score = (sum of weighted matches / count of must-haves) × 100, rounded to 5%.

### 5. Nice-to-Have Coverage

Same math as Must-Have Coverage, on the nice-to-have list. Weight: 40% of Must-Have in composite (nice-to-haves matter less).

### 6. Deal-Breaker Check

Binary. Any deal-breaker from `search_preferences` tripped by the JD = **FAIL → NO_GO** regardless of other dimensions.

Common trips:
- Comp floor: JD's posted band's top < candidate's floor
- Work mode: JD onsite when candidate is remote-only
- Location: JD requires relocation to excluded city
- Domain excludes: JD is in an excluded industry
- Clearance/citizenship requirements candidate doesn't hold

---

## Composite Score

Weighted average:

| Dimension | Weight |
|---|---|
| Title/level fit | 0.15 |
| YOE fit | 0.15 |
| Domain fit | 0.15 |
| Must-have coverage | 0.35 |
| Nice-to-have coverage | 0.10 |
| (Deal-breaker is a gate, not a weighted term) | — |
| **Sum** | **0.90** + 0.10 slack for qualitative override |

The 0.10 slack is for session-specific factors the user flags during Phase 4 (e.g., "this company is in my network", "I've met the hiring manager"). Do NOT auto-apply the slack; ask the user to claim it explicitly per JD.

### Bands

- **STRONG_FIT**: 80–100 composite AND deal-breakers pass
- **STRETCH**: 60–79 composite AND deal-breakers pass
- **WEAK_FIT**: 40–59 composite AND deal-breakers pass
- **NO_GO**: composite <40 OR any deal-breaker tripped

### Band boundary rule

Composites within 3 points of a band boundary (e.g., 78–82 on the STRONG/STRETCH line) are flagged as BORDERLINE. Surface these to the user for manual judgment — the rubric's precision isn't tight enough to decide at the boundary.

---

## What NOT to Score

- **Candidate's interest** — the rubric can't tell if a JD is exciting. That's Phase 4 human judgment.
- **Company quality / culture beyond JD signals** — external research (Glassdoor, Blind, backchannel) is out of scope for this skill. If the user has signals, they bring them to Phase 4.
- **Market competitiveness of the role** — "200 applicants in 48 hours" is a risk flag to surface, not a score input.
- **Candidate's current emotional state** — if the user is in distress, the skill's role is to pause and point to the Professional Help Boundary, not to triage harder.
