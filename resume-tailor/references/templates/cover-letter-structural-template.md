# Cover Letter Structural Template

Extracted from the canonical baseline at `~/Documents/resumes/Summer_Rae_CoverLetter.md`. Load this alongside the baseline letter and `references/cover-letter-review.md` when drafting. The baseline is the **voice** anchor; this file is the **structural** skeleton with annotated placeholders.

The pattern is a 4-paragraph hook → current-edge → prior-leadership-evidence → synthesis-close. Adapt content; preserve shape.

For pandoc layout (top block, sign-off, ordinal date, bold name), see `references/templates/cover-letter-template.md`. For prose rules (350-word soft cap, sentence-subject variety, anti-patterns, etc.), see `references/cover-letter-review.md`.

---

## Layout (per `references/templates/README.md`)

```
**Your Name**

City, ST

(XXX) XXX-XXXX

your.email@example.com

[Ordinal Date — e.g. 16th May 2026]

Dear Hiring Manager,

[P1]

[P2]

[P3]

[P4]

Regards,

**Your Name**
```

---

## Paragraph structure

### P1 — Hook + Arc + Company-fit

**Job:** establish why this role matches the candidate's deliberate career trajectory, and bridge to the company's specific bet.

**Shape:**

```
I was excited to see you post the [ROLE TITLE] role because [ARC-FIT REASON — why the candidate's career has been heading toward exactly this kind of work]. After [DECADE-ARC SUMMARY — one sentence naming 2 prior employers and what was done at each, demonstrating progression], I [CURRENT POSITIONING — what the candidate went to their current role to do]. [COMPANY]'s [SPECIFIC NEED, BET, or PROBLEM the role exists to handle] is exactly the next layer of that arc.
```

**Rules:**

- P1 may open with candidate hook ("I was excited to see..."), per §1 of cover-letter-review.md.
- The decade-arc sentence must show *deliberate progression*, not a list of jobs.
- End P1 on the company, not the candidate — the final clause names the company's specific bet and frames it as the next layer of the arc.

### P2 — Current edge (what the candidate is closest to right now)

**Job:** show what the candidate does *today*, what the current work has taught, and bridge to one piece of supporting evidence (often a side project or published artifact).

**Shape:**

```
In my current position at [CURRENT EMPLOYER], I [SCOPE — what the candidate actually does, including who they work alongside if it's a notable name]. [DETAIL — what this work has shown the candidate about the field, the problem class, or the technology — one or two sentences]. [BRIDGE TO SIDE EVIDENCE — in my spare time, I built [PROJECT NAME], an [ONE-LINE DESCRIPTION] that [WHAT IT SOLVES] with [HOW: specific mechanisms, named subcomponents]].
```

**Rules:**

- Don't start the paragraph with "I" — open with the prepositional phrase ("In my current position at...").
- Name notable people the candidate works with directly (e.g. Andrew Ng), only if true and verifiable.
- The bridge-to-side-evidence move converts a single-employer paragraph into a paragraph that shows the candidate's reach beyond the day job.

### P3 — Prior leadership evidence (where the candidate ran the show)

**Job:** show the most directly relevant prior leadership tour, with scope, governance ownership, and exec-cadence in one tight sentence.

**Shape:**

```
In my previous position as [TITLE] at [PRIOR EMPLOYER], I [SCOPE WITH SCALE — led an N-person team, shipped X system to NAMED CLIENT TYPE]. I [GOVERNANCE OWNERSHIP — release decisions, model-quality / bias / fairness / explainability framework — merged into the same sentence as] [EXEC CADENCE — weekly C-suite reporting on model performance, delivery status, and risk posture].
```

**Rules:**

- Don't start with "I" — open with the prepositional phrase ("In my previous position as...").
- Merge team-growth + governance + exec-cadence into one tight sentence per the vocabulary-preferences rule. Three separate sentences = corporate filler.
- Name the *client type* (Department of Defense, healthcare providers, regulated industries) when the prior employer's customer base is itself a credibility signal.
- "the C-suite" — collective noun, never enumerate (CEO, CTO, COO).

### P4 — Synthesis close

**Job:** synthesize what the candidate brings as a *stack* (not a list of skills), name the evidence behind the stack, and close on a specific topic the candidate would want to discuss with the company.

**Shape:**

```
My experience covers [SYNTHESIS — the stack of things the candidate brings: e.g. exec vision-setting paired with hands-on building, governance wired into release decisions, end-user adoption driven by X]. [EVIDENCE — the proof points underlying the synthesis: named projects, skills portfolio, open-source artifacts that keep delivery reproducible]. I'd welcome the chance to discuss [SPECIFIC TOPIC AT COMPANY — the bet at the center of the role, the year-one priorities, the named problem area].
```

**Rules:**

- Do NOT re-list employers from P1 (see memory `feedback_summer_cover_letter_p4_no_redundancy_with_p1`).
- The synthesis must be 3 things stacked into a single arc — not a 3-item bullet equivalent.
- Close on a specific topic, not a vague hope. "I'd welcome the chance to discuss [topic]" is active and specific. "I look forward to hearing from you" is banned (§5 passive closing).
- If P2/P3 are evidence-dense, P4 may compress to a single-sentence close per the `feedback_cover_letter_single_sentence_p4_close` pattern.

---

## Variants

### When P1 should lead with biotech/healthcare/regulated-data anchor

If the role is in a domain where the candidate's regulated-data history is the strongest claim, invert P1 and P2 from the default shape: put the regulated-data evidence in P1 (with publications/named systems/HIPAA-grade work as the through-line), put the leadership-org evidence in P2, and put the current-edge agentic-AI work in P3. Same P4.

This is the shape used in the Medbridge draft (2026-05-16). Trigger: JD's primary bet is healthcare or biotech ML.

### When the role is below the candidate's seniority level

Apply §1a Seniority Alignment from `cover-letter-review.md`. Add one sentence in P3 or P4 naming why this *specific* role is a forward step. Confident, not defensive.

### When AI/agentic-systems work is the lead claim

Default shape works — current-edge (P2) carries the agentic-AI work, prior-leadership (P3) carries the org-scaling, synthesis (P4) names both.

---

## What NOT to template

- Specific company names, recipient names, recent moments. Those are per-application research and must come from the JD, the company site, or user input.
- Specific numbers (team size, system scale, publication names). Those come from the resume.
- Hook variant choice (canonical "I was excited to see..." vs. one of the 3 brainstorm angles in §2). The template defaults to canonical; switch per JD if the canonical hook reads flat.
