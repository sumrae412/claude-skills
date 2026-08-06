# JD Analysis — Reference

Parse the job description into a structured profile before touching the resume. Output feeds Phase 2 (matching pass).

## Output Schema

**Phase 1 output order to the user:** JD recap first, then derived profile (weights + keywords + archetype + action codes). The user needs to see the JD content re-surfaced above the weights so they can evaluate fit without scrolling back to the JD file. The recap is plain-English, not YAML.

### 1. JD Recap (shown first, plain-English)

```markdown
## JD Recap

- **Company:** Acme Corp (healthcare AI platform)
- **Title:** Director, Applied AI Engineering
- **Seniority:** Director
- **Comp:** $167K–$268K base
- **Work mode:** Remote with occasional travel
- **Industry:** Healthcare (workers' comp / medical services)

**What the role actually does (plain-English):**
- Lead the team putting AI into production for core product capabilities
- Build document-processing pipelines, LLM orchestration patterns, agentic automation workflows
- Own AI platform strategy + technical direction + standards
- Grow an engineering team across US + Mexico time zones
- Operate inside HIPAA/PHI-protected data environments
```

### 2. Derived Profile (after JD recap)

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

archetype:
  primary: "Platform / Engineering Executive"
  resume_story: "Frame the candidate as the leader who sets technical direction, scales AI platforms, and makes production systems reliable across teams."
  downplay: ["education framing", "isolated prototypes", "tool-list-heavy skills sections"]

risk_flags:
  - "no salary band disclosed"    # only surface genuine red flags
```

### 3. Archetype Check (after derived profile fields)

Load `references/role-archetypes.md` and classify the JD into one primary archetype. Then add three lines to the user-facing checkpoint:

```markdown
## Archetype

- **Archetype selected:** Platform / Engineering Executive
- **Resume story to foreground:** Frame the candidate as the leader who sets technical direction, scales AI platforms, and makes production systems reliable across teams.
- **What to downplay:** education framing, isolated prototypes, tool-list-heavy skills sections
```

This forces the tailoring pass to pick a dominant story before it starts rewriting bullets.

### 4. Hiring Risk (single sentence — required for cover letter drafting)

Produce one sentence answering: *"What is the hardest thing this person has to do, that most candidates with the right keywords can't actually do?"*

Format:

```
Can this person [operationalize / scale / land / govern / unify] [SPECIFIC CAPABILITY] under [SPECIFIC CONSTRAINT — regulatory, technical, organizational, or trust-related] while [SPECIFIC CROSS-FUNCTIONAL PRESSURE — aligning eng/clinicians/exec, integrating into existing workflow, holding the line on quality gates, etc.]?
```

**Examples:**

- *Healthcare AI platform role:* "Can this person operationalize trustworthy healthcare AI systems from messy longitudinal patient data while aligning engineering, clinicians, executives, and compliance on the same release plan?"
- *AI infra role at a frontier lab:* "Can this person ship safety-critical agentic systems at frontier-lab scale while running an evaluation discipline rigorous enough that the org actually trusts the gates?"
- *Director of AI at a defense-tech company:* "Can this person stand up an ML organization that ships into classified production environments without losing the explainability + governance posture the customer demands?"

**Rules:**

- One sentence. If it takes two, the hiring risk isn't sharp enough — tighten.
- Must name a *capability* + a *constraint* + a *cross-functional pressure*. A sentence with only "build X" is too generic to be useful.
- Must be derivable from the JD, not invented. Cite the JD line that motivated each clause if asked.
- This sentence is the antecedent for the cover letter's P1 "specific bet" clause (see `references/templates/cover-letter-structural-template.md` §P1). Without it, cover-letter drafting drifts into resume narration.
- **When the required-quals list reads as boilerplate ("10+ years," "strong executive communication"), derive the hiring risk from the PREFERRED quals instead.** That section is where the hiring manager lists what they wish the ideal candidate already had, which is usually the actual organizational pain the required list is too broad to name. Validated 2026-07-20 (OpenLoop Director of AI Technologies): preferred quals named Amazon Connect, BPO technology, contact-center AI, and workforce management, while the responsibilities included "maintain oversight of AI systems, vendors, and usage across the organization" — together reframing the risk from generic "can she lead AI" to "can she consolidate unowned AI sprawl under one governed platform and prove savings on operations labor."

**Why this is required for cover letters:** the cover-letter draft orbits the hiring risk. Producing it as a Phase 1 artifact (instead of leaving it implicit in the orchestrator's head) means the cover letter has a fixed reference point, the user sees the framing before drafting starts, and "P1 leads with the company's bet" becomes mechanically checkable instead of stylistic.

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

## YOE Cutoff (Honest-Scoping)

When the JD specifies a years-of-experience requirement, compute the *earliest plausible role start year* the resume should show:

```
earliest_start = current_year - (YOE_required + ~3 grace)
```

Roles with start dates earlier than that window become **truncate-or-summarize** candidates in Phase 2:

- Truncate: drop the role entirely if it's not load-bearing for the JD's focus areas.
- Summarize: collapse multiple early-career roles into a single "Earlier roles: [titles], [years]" line at the bottom of EXPERIENCE.

**Why this matters:** a hiring manager reading a 25-year tenure for an 8-YOE role reads it as overqualified or as a candidate who didn't tailor — not as bonus. The grace window (~3 years) avoids cutting roles that are 1-2 years past the literal threshold and still genuinely useful evidence.

**Do not delete the source bullets** from the canonical resume — only from the tailored output. The canonical resume retains every role.

**Example:** JD says "8+ years of experience required". Current year 2026. Earliest plausible start = `2026 - (8 + 3) = 2015`. Roles starting before 2015 are candidates for truncation or summarization in the tailored output.

## When to Surface Tension

If the JD has internal contradictions (e.g., "senior" title at IC scope + "must manage a team"), name this to the user before Phase 2. It often becomes an interview question; the resume should be tailored to what the role *actually* is, not the title.

## If the JD is Thin

Short listings (a paragraph or two, no "requirements" list) give less signal. In that case:

- Focus on the job title and any named technologies or domains.
- Default to a flatter weight distribution (e.g., `0.35 / 0.3 / 0.2 / 0.15`).
- Tell the user: "This JD is sparse; the profile is lower-confidence. Expect to rely more on the cover letter."
