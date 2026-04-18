# Output Templates — Batch Summary, Ranked Table, Handoff Artifacts

## Dedupe Report (Phase 2, Step 1)

Run this BEFORE the ingestion summary. Always report — even when 0 dupes found.

```
## URL Dedupe

Submitted: 13 URLs
Duplicates removed: 2
  - LinkedIn #4401124183 (appeared twice)
  - LinkedIn #4388969098 (appeared twice)
Unique to fetch: 11

Canonical URLs (for reference):
  1. https://www.linkedin.com/jobs/view/4391875424/
  2. https://www.linkedin.com/jobs/view/4400408014/
  …
```

## Batch Summary (Phase 2, Step 2)

```
## JD Ingestion Summary

Unique URLs: 11
Fetched cleanly: 7
Auth-walled (need paste): 3 — LinkedIn #4402280727, #4401999001, #4398112233
Expired / 404: 1 — Lever UUID abc123
JS-rendered failure: 1 — Workday posting for AcmeCo

Please paste the 3 auth-walled JDs (one at a time, I'll confirm before the next).
```

## Ranked Table (Phase 4)

Sort by composite score descending. One row per JD.

```
| #  | Company          | Title                       | Score | Band        | Link                                           | Why fit                                   | Main gap                           | Rec     |
|----|------------------|-----------------------------|-------|-------------|------------------------------------------------|-------------------------------------------|------------------------------------|---------|
| 1  | Enzo Tech Group  | VP of Data and AI           | 82    | STRONG_FIT  | linkedin.com/jobs/view/4402280727              | AI function scale-up + claude_flow proof  | YOE: 12-15 req, 11 candidate       | Go      |
| 2  | HealthWorks      | Director, ML Platform       | 78    | STRETCH★    | boards.greenhouse.io/healthworks/jobs/12345    | Direct domain + team-size match           | No RAG-platform experience         | Go/Ask  |
| 3  | BioForge         | Head of Applied AI          | 71    | STRETCH     | jobs.lever.co/bioforge/uuid-abc                | Biotech domain + production ML            | Title step-up, no prior Head role  | Maybe   |
| 4  | DataCoast        | VP Engineering (AI focus)   | 65    | STRETCH     | datacoast.com/careers/vp-eng                   | Seniority match                           | Engineering lean, not data-native  | Skip    |
| 5  | MegaCorp         | Principal AI Architect      | 48    | WEAK_FIT    | jobs.ashbyhq.com/megacorp/abc                  | Modern AI stack                           | IC track, not leadership           | Skip    |
| 6  | FinFast          | Director of ML              | 72    | NO_GO       | linkedin.com/jobs/view/4398000001              | Skill match is there                      | DEAL-BREAKER: onsite NYC           | No      |

★ = BORDERLINE (within 3 points of a band boundary; user judgment called)
```

**Link column rule:** display host+path (no `https://`, no query params) to keep the table readable. The full URL lives in `jd.md` and `fit-analysis.md`. User can click or copy as needed.

Legend:
- **Rec column values:** `Go` (pursue) · `Go/Ask` (pursue pending user confirmation) · `Maybe` (your call) · `Skip` (don't pursue) · `No` (deal-breaker)

## Per-JD Detail Block (on user drill-down request in Phase 4)

```
### #1 — Enzo Tech Group, VP of Data and AI (Composite 82 / STRONG_FIT)

**Dimension scores:**
- Title/level fit: 70 (Director → VP, one step up)
- YOE fit: 55 (11 yrs candidate vs 12-15 required — 1-4 yrs short)
- Domain fit: 75 (biotech → healthcare advocacy, adjacent)
- Must-have coverage: 90 (5 of 6 with DIRECT/TRANSFERABLE evidence)
- Nice-to-have coverage: 80
- Deal-breaker: PASS

**Why fit:**
- Govini AI org scale-up (15→21) + claude_flow open-source matches "build AI function as durable enterprise capability"
- Production ML governance at Govini + TwinStrand matches "operationalize AI/ML across workflows"

**Main gap:**
- YOE: 11 cumulative vs 12-15+ required. Cover letter must justify.
- No explicit patient-navigation/advocacy domain (biotech-adjacent)

**Recommendation:** Go. Lead resume with claude_flow + Govini 15→21 scale-up. Cover letter frames YOE candidly.

**Red flags to know going in:**
- 200+ applicants already
```

## Per-Company Handoff Directory (Phase 5)

Layout:

```
~/Documents/resumes/
  Enzo/
    jd.md                 # full fetched posting + structured extract
    fit-analysis.md       # Phase 3 score breakdown + Phase 4 notes
    # resume-tailor outputs land here later: resume.md, cover-letter.md, etc.
  HealthWorks/
    jd.md
    fit-analysis.md
```

### jd.md template

```markdown
# Job Description — <Company>, <Title>

**Source:** <source_url>
**Fetched:** <ISO timestamp>
**Method:** <webfetch | paste | variant_url>
**Posted:** <posted_at>
**Applicants:** <applicant_count>

## Summary

- **Company:** …
- **Title:** …
- **Location:** …
- **Seniority:** …
- **Comp:** …

## Required

- …

## Preferred

- …

## Responsibilities

- …

## Culture / Team Signals

- …

---

## Raw posting

<verbatim extracted or pasted text>
```

### fit-analysis.md template

```markdown
# Fit Analysis — <Company>, <Title>

**Date:** <ISO date>
**Composite:** <score> / <band>

## Dimension Scores

| Dimension | Score | Notes |
|---|---|---|
| Title/level fit | N | … |
| YOE fit | N | … |
| Domain fit | N | … |
| Must-have coverage | N | … / total must-haves covered |
| Nice-to-have coverage | N | … |
| Deal-breaker check | PASS/FAIL | … |

## Why fit

- …

## Main gaps

- …

## Recommendation

Go / Stretch-Go / Maybe / Skip / No-Go

## Red flags / context

- …

## Notes for resume-tailor

- Lead bullets / signature projects to emphasize: …
- Cover letter must address: …
- Keywords to weave: …
```

## Handoff Prompt (Phase 5, shown to user)

```
Wrote <N> directories to ~/Documents/resumes/:
  - Enzo/jd.md + fit-analysis.md
  - HealthWorks/jd.md + fit-analysis.md
  - BioForge/jd.md + fit-analysis.md

To draft resume + cover letter for each, invoke `/resume-tailor` and
point it at the directory. Run one at a time — each invocation runs the
full phased flow with review at each checkpoint.

Suggested order (highest-scoring first):
  1. /resume-tailor with ~/Documents/resumes/Enzo/jd.md
     apply at: https://www.linkedin.com/jobs/view/4402280727/
  2. /resume-tailor with ~/Documents/resumes/HealthWorks/jd.md
     apply at: https://boards.greenhouse.io/healthworks/jobs/12345
  3. /resume-tailor with ~/Documents/resumes/BioForge/jd.md
     apply at: https://jobs.lever.co/bioforge/uuid-abc
```

**Every handoff artifact must include the apply URL.** If the source was a paste (no URL), say so explicitly: `apply at: (user-provided paste — no source URL; user knows where to apply)`.

## What NOT to include in outputs

- Personally identifying info for the hiring team beyond what the JD itself lists
- Glassdoor / Blind / backchannel notes — these are user-provided context, not skill outputs
- Any implication the skill has reviewed the company's reputation beyond the JD itself
- Emotional framing ("you'd love this!" / "this is perfect for you!") — the score is the score; enthusiasm is the user's
