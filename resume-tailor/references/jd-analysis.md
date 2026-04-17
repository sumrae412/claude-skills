# JD Analysis — Reference

Parse the job description into a structured profile before touching the resume. Output feeds Phase 2 (matching pass).

## Output Schema

```yaml
role:
  title: "Senior Product Manager"
  seniority: senior          # junior | mid | senior | staff | principal | exec
  scope:
    team_size: "5-15 direct/indirect"
    ownership: "0-to-1 + scale"
    budget: "unspecified"

focus_areas:
  - area: "0-to-1 product discovery"
    weight: 0.4              # weights across all areas must sum to 1.0
    signals: ["shipped 3 products from scratch", "customer interviews", "wrote specs"]
    action: LEAD_WITH
  - area: "B2B SaaS growth"
    weight: 0.3
    signals: ["PLG motion", "self-serve onboarding", "activation metrics"]
    action: EMPHASIZE
  - area: "Technical depth"
    weight: 0.2
    signals: ["works closely with eng", "comfortable with APIs"]
    action: QUANTIFY
  - area: "People management"
    weight: 0.1
    signals: ["mentions managing PMs as a plus"]
    action: DOWNPLAY

keywords:
  must_have: ["product manager", "B2B SaaS", "0 to 1", "customer discovery"]
  nice_to_have: ["PLG", "growth", "metrics", "roadmap"]
  avoid_overuse: ["synergy", "champion", "rockstar"]   # ATS traps / filler

culture_signals:
  - "fast-paced, founder-mode"
  - "owner mentality, high agency"
  - "async-heavy comms"

risk_flags:
  - "no salary band disclosed"    # only surface genuine red flags
```

## Action Codes

Each focus area gets exactly one action code. Phase 2 uses these to decide treatment:

- **LEAD_WITH** — The single most important signal. Top of resume, top of each role's bullets, woven into headline. Reserve for the #1 weighted area only.
- **EMPHASIZE** — Prominent but not lead. Multiple visible bullets, keyword in summary, possibly a dedicated section.
- **QUANTIFY** — The user likely has this but it's buried in qualitative language. Find it and add numbers (team size, scale, revenue, percent, time).
- **DOWNPLAY** — JD mentions it but it's not a differentiator. One brief bullet max; don't over-invest story real-estate.

## Weighting Rules

- Weights are relative importance across areas; they sum to 1.0 so downstream prioritization is principled.
- If the JD is vague, default to `0.4 / 0.3 / 0.2 / 0.1` for 4 areas.
- A single area should rarely exceed 0.5 unless the JD is hyper-focused.

## Extraction Heuristics

- **Must-have keywords:** words that appear in the job title, the first 2 sentences of the description, and any bolded or bulleted "required" list.
- **Nice-to-have:** appears in "bonus" / "plus" / "ideal candidate" sections.
- **Seniority:** combine the title word + years-of-experience range + scope language. When title and scope conflict ("Senior PM" but description sounds junior), surface the tension to the user.
- **Scope signals:** team size, budget, geographic scope, P&L ownership, # of stakeholders. Quote the JD phrases that establish each.
- **Culture signals:** read the "about us" and "how we work" sections. Tone matters — "we move fast" vs. "we believe in sustainable pace" calibrate differently.

## When to Surface Tension

If the JD has internal contradictions (e.g., "senior" title at IC scope + "must manage a team"), name this to the user before Phase 2. It often becomes an interview question; the resume should be tailored to what the role *actually* is, not the title.

## If the JD is Thin

Short listings (a paragraph or two, no "requirements" list) give less signal. In that case:

- Focus on the job title and any named technologies or domains.
- Default to a flatter weight distribution (e.g., `0.35 / 0.3 / 0.2 / 0.15`).
- Tell the user: "This JD is sparse; the profile is lower-confidence. Expect to rely more on the cover letter."
