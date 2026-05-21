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

### P1 — Hook + Company-bet bridge

**Job:** open on what makes the role hard, name the company's specific bet, and frame the candidate's track record as the kind of work that bet requires. P1 must answer *"why are you uniquely relevant to THIS role?"* — not *"here is my career arc."*

**Choose ONE P1 shape based on the JD signal.** Both shapes end P1 on the company's bet, not on the candidate.

**Shape A — Intersection-of-problems (preferred for complex / operational / regulated-domain roles):**

```
I was excited to see you post the [ROLE TITLE] role at [COMPANY] because this position sits at the intersection of two problems I have spent my career working on: [PROBLEM 1 — named operationally, e.g. "building trustworthy AI systems in regulated healthcare environments"] and [PROBLEM 2 — named operationally, e.g. "translating emerging AI capabilities into production systems that improve real-world decision making"]. [COMPANY]'s [SPECIFIC BET — the dataset / product / customer / risk the role exists to handle] is exactly that problem at scale.
```

**Shape B — Decade-arc (use only when the candidate's progression itself is the strongest fit signal):**

```
I was excited to see you post the [ROLE TITLE] role because [ARC-FIT REASON — why the candidate's career has been heading toward exactly this kind of work]. After [DECADE-ARC SUMMARY — one sentence naming up to 2 prior employers and what was done at each, demonstrating deliberate progression], I [CURRENT POSITIONING — what the candidate went to their current role to do]. [COMPANY]'s [SPECIFIC NEED, BET, or PROBLEM] is exactly the next layer of that arc.
```

**Rules (both shapes):**

- P1 may open with candidate hook ("I was excited to see..."), per §1 of cover-letter-review.md.
- End P1 on the company's bet, not the candidate. The final clause names the company's specific bet and frames it as the work the candidate is already doing.
- **No chronological employer montage.** Never list 3+ prior employers in P1 in a "At X… Before that, at Y… Earlier, at Z…" cadence — that is resume narration, not positioning. Shape A names no employers in P1. Shape B names up to 2 with a deliberate-progression frame.
- The "specific bet" / "specific need" clause must be grounded in the hiring-risk sentence from Phase 1 (see `references/jd-analysis.md` §"Hiring Risk"). If no hiring-risk sentence exists, do not draft P1 yet — go back to Phase 1.

### P2 — Bridge from company's situation to candidate's evidence

**Job:** make the transition from "what makes this role hard" to "here is the evidence that I have done this kind of work." P2 has two shapes; pair the shape with the P1 shape chosen.

**Shape A — Company-situation deep-dive (paired with P1 Shape A):**

```
[COMPANY]'s opportunity is especially compelling because of [DATASET / SYSTEM / WORKFLOW — named in concrete detail, drawn from the JD or verified company source]. Building [SPECIFIC CAPABILITY the role demands] on top of [DATA SOURCES / WORKFLOWS / CONSTRAINTS] is not simply a [MODELING / ENGINEERING / DESIGN] challenge — it requires [2-3 OPERATIONAL DIMENSIONS the role actually depends on: evaluation discipline, clinician trust, regulatory posture, workflow integration, etc.].
```

**Shape B — Current edge (paired with P1 Shape B):**

```
In my current position at [CURRENT EMPLOYER], I [SCOPE — what the candidate actually does, including who they work alongside if it's a notable name]. [DETAIL — what this work has shown the candidate about the field, the problem class, or the technology — one or two sentences]. [BRIDGE TO SIDE EVIDENCE — in my spare time, I built [PROJECT NAME], an [ONE-LINE DESCRIPTION] that [WHAT IT SOLVES] with [HOW: specific mechanisms, named subcomponents]].
```

**Rules (both shapes):**

- Don't start the paragraph with "I" — open with the prepositional phrase ("In my current position at...") or the company's name ("[COMPANY]'s opportunity is...").
- Shape A names the company's situation in detail before any candidate evidence appears. Skim test: a reader reading only P1 + first sentence of P2 should know what the role's hardest problem is, not where the candidate works now.
- Shape A is preferred for healthcare, regulated, complex-operational, or product-specific roles where the company's situation has multiple distinct operational dimensions worth naming. Shape B is preferred when the candidate's current-edge work is itself the strongest fit signal (e.g. agentic AI roles where DLAI work is directly on-target).
- When using Shape A, the candidate's current-edge work moves into P3's lead sentence or P4's close, not its own paragraph.
- Name notable people the candidate works with directly (e.g. Andrew Ng), only if true and verifiable.

### P3 — Operational evidence (where the candidate has done this kind of work)

**Job:** show the most directly relevant prior tour as an *answer* to the operational dimensions named in P1/P2 — not as a generic leadership credential. P3 evidence is selected by relevance to the hiring risk, not by recency.

**Shape:**

```
In my previous position as [TITLE] at [PRIOR EMPLOYER], I [SCOPE WITH SCALE — led an N-person team, shipped X system to NAMED CLIENT TYPE]. I [GOVERNANCE OWNERSHIP — release decisions, model-quality / bias / fairness / explainability framework — merged into the same sentence as] [EXEC CADENCE — weekly C-suite reporting on model performance, delivery status, and risk posture]. [OPERATIONAL THROUGH-LINE — one sentence naming what the role's hardest part actually was, and why it maps to the company's bet — e.g. "Getting engineering, product, and policy aligned on the same plan was the actual job, and that alignment was the difference between a demo and a system running in a secure production environment."].
```

**Rules:**

- Don't start with "I" — open with the prepositional phrase ("In my previous position as...").
- Merge team-growth + governance + exec-cadence into one tight sentence per the vocabulary-preferences rule. Three separate sentences = corporate filler.
- The operational-through-line sentence is the key new move: it converts P3 from "here is my impressive leadership tour" into "here is how I solved the same operational shape you are now hiring for." It must map directly to the operational dimensions named in P2.
- When the JD is in a regulated/healthcare/biotech domain, P3 may add ONE additional sentence stacking 1-2 earlier employers with regulated-data / publication evidence — but ONLY when those earlier roles are answering the same operational shape as the lead employer. Never a chronological montage; always relevance-ordered.
- Name the *client type* (Department of Defense, healthcare providers, regulated industries) when the prior employer's customer base is itself a credibility signal.
- "the C-suite" — collective noun, never enumerate (CEO, CTO, COO).

### P4 — Pivot-back-to-company + close

**Job:** pivot back to a specific named element of the company's product, vision, or operational challenge (not a generic "stack" of candidate skills), and close on a specific topic the candidate would want to discuss.

**Shape A — Pivot-back close (paired with P1/P2 Shape A):**

```
[OPERATIONAL HOOK — one sentence naming what the candidate's experience is operationally optimized for, e.g. "That operational focus is also what draws me to [COMPANY]'s vision for [NAMED PRODUCT / NAMED INITIATIVE]."]. [SPECIFIC CONNECTION — one sentence tying a named feature in the JD (e.g. clinician-in-the-loop systems, adherence prediction, auditability) to the candidate's understanding of why it matters operationally]. I'd welcome the chance to discuss [SPECIFIC TOPIC — the bet at the center of the role, the year-one priorities, the named problem area].
```

**Shape B — Synthesis close (paired with P1/P2 Shape B):**

```
My experience covers [SYNTHESIS — the stack of things the candidate brings: e.g. exec vision-setting paired with hands-on building, governance wired into release decisions, end-user adoption driven by X]. [EVIDENCE — the proof points underlying the synthesis: named projects, skills portfolio, open-source artifacts that keep delivery reproducible]. I'd welcome the chance to discuss [SPECIFIC TOPIC AT COMPANY — the bet at the center of the role, the year-one priorities, the named problem area].
```

**Rules (both shapes):**

- Do NOT re-list employers from P1 (see memory `feedback_summer_cover_letter_p4_no_redundancy_with_p1`).
- Close on a specific topic, not a vague hope. "I'd welcome the chance to discuss [topic]" is active and specific. "I look forward to hearing from you" is banned (§5 passive closing).
- **No founder-cosplay closers.** Phrases like "these are exactly the bets I want to be running" / "the kind of bets that matter" read as startup-founder cosplay and undermine operational credibility. Close on what would be discussed, not on betting language.
- Shape A is preferred when P2 used Shape A (company-situation deep-dive) — P4 then completes the operational arc by naming the specific product/initiative that draws the candidate to the company.
- If P2/P3 are evidence-dense, P4 may compress to a single-sentence close per the `feedback_cover_letter_single_sentence_p4_close` pattern — preserve the pivot-back-to-company move even when single-sentence.

---

## Shape pairing — pick the same shape across P1/P2/P4

The two shapes (A and B) work as a pair. Shape A is the *operational-fit* arc: lead with the role's operational challenge, deepen into the company's situation, frame evidence as operational answer, close by pivoting back to a named company product. Shape B is the *career-arc* arc: lead with the candidate's deliberate progression, show the current edge, evidence the prior leadership tour, synthesize the stack.

Pick the shape based on the JD signal, not stylistic preference. Use the table:

| JD signal | Use shape |
|---|---|
| Healthcare, biotech, regulated-data, clinical AI, compliance-heavy | A |
| Complex operational AI (governance + workflow integration + cross-functional coordination as primary risk) | A |
| Product-specific role with multiple named operational dimensions (e.g. "Head of X" with platform + team + governance + safety) | A |
| Agentic AI / LLM systems / research-adjacent platform (where current-edge work is the strongest fit) | B |
| Director / VP roles where career progression itself is the credibility signal | B |
| Thin JD with only generic AI-leadership signals | B |

**Never mix shapes** — Shape A P1 followed by Shape B P2 produces the "career-history-in-P1, candidate-current-edge-in-P2" antipattern (the exact failure mode of the Medbridge 2026-05-16 draft). The shape pair is selected once at draft-start and carried through P1 → P2 → P4.

### Anti-pattern: chronological prestige montage in P1

The biotech-anchor variant present in earlier versions of this template (deprecated 2026-05-16) explicitly permitted P1 to lead with a chronological montage of regulated-data employers. That variant produced drafts that read as resume narration instead of positioning, and is replaced by Shape A above. **Never lead P1 with a "At X… Before that, at Y… Earlier, at Z…" cadence**, regardless of how strong the individual employers are. Shape A keeps regulated-data evidence in P3 (relevance-ordered), not P1 (chronological).

## Variants

### When the role is below the candidate's seniority level

Apply §1a Seniority Alignment from `cover-letter-review.md`. Add one sentence in P3 or P4 naming why this *specific* role is a forward step. Confident, not defensive. Applies to either shape pair.

---

## What NOT to template

- Specific company names, recipient names, recent moments. Those are per-application research and must come from the JD, the company site, or user input.
- Specific numbers (team size, system scale, publication names). Those come from the resume.
- Hook variant choice (canonical "I was excited to see..." vs. one of the 3 brainstorm angles in §2). The template defaults to canonical; switch per JD if the canonical hook reads flat.
