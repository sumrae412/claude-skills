---
name: resume-tailor
description: Tailor an existing resume to a specific job description with visible confidence scoring, structured reframing, and positioning help. Triggers on "tailor my resume", "update my resume for this job", "resume to job", "match resume to JD", "help me apply to", "resume keywords", "ATS alignment", "position my experience", "reframe my resume", or pasting a JD alongside a resume.
---

# Resume Tailor — JD-Driven Resume Tailoring + Positioning

Walks the user through a phased resume-tailoring session: JD analysis → matching pass with confidence scores → optional gap discovery → positioning pass → output. Truth-preserving — the skill selects, emphasizes, and reframes existing experience; it never fabricates.

## Mission

A person's ability to get a job should be based on their actual experience, not on their resume-writing skills. This skill closes that gap by making alignment auditable (visible scores), bringing out undocumented experience (branching interview), and calibrating tone/level to the target role — without inventing anything.

## Before Starting

Ask the user for:

1. **Resume source** — path to their canonical resume (markdown preferred; DOCX/PDF fine, converted in-memory) OR pasted text.
2. **Job description** — URL, file path, or pasted text. If URL, fetch with WebFetch; fall back to asking the user to paste if fetch fails.
3. **Target outcome** — "drop-in replacement bullets", "full rewrite", "cover-letter draft too", or "just show me gaps". Default: tailored resume + keyword coverage report.

If any piece is missing, ask once. Don't proceed with half the inputs.

**If no resume exists yet:** offer to run Phase 3 (discovery) first to generate source bullets from scratch, then return to Phase 1 with the drafted material as the "resume".

**If the user pastes multiple JDs:** pick one and defer the others. This skill is one-JD-at-a-time by design (see Principle 4). Say so and let the user choose.

---

## Phase 1 — JD Analysis

Produce a **structured job profile** before touching the resume. Output format, action codes, and extraction heuristics live in `references/jd-analysis.md` — load it now.

Output to user (checkpoint) — **in this order**:

1. **JD recap** — title, company, seniority, comp, work mode, industry. Then a **bulleted 3-6 line summary of what the role actually does** (responsibilities + must-haves in plain language, not JD-parroted). This anchors the user in the JD before they evaluate weights.
2. Weighted focus areas (weights sum to 1.0) — tied explicitly to JD recap items so the user can see *why* each area got its weight
3. Must-have keywords vs. nice-to-haves (ATS tier)
4. Seniority signals + scope signals (team size, ownership, budget)
5. Cultural signals (what kind of operator do they want?)
6. Action-code plan per focus area: `LEAD_WITH` / `EMPHASIZE` / `QUANTIFY` / `DOWNPLAY`

**Rationale for JD-first ordering:** Users often can't evaluate whether a weight is right without re-anchoring in the JD content. Placing the JD recap immediately above the weights means the user sees the *evidence* and the *derived profile* together, without scrolling back to the JD file.

Ask: *"Does this profile match how you read the role? Anything I over- or under-weighted?"* Wait for confirmation before Phase 2.

---

## Phase 2 — Matching Pass

For each bullet and role in the resume, assign a confidence band vs. the JD profile and propose a reframe if appropriate. Rubric + four reframing strategies are in `references/matching-rubric.md` — load it. Also load `shared/communication-principles.md` — reframed bullets must lead with the conclusion, stay in plain language, and serve the reader (hiring manager / ATS), not the author.

Output to user (checkpoint):

- Per-bullet table: **Current → Band → Reframed → Strategy used**
- Roll-up counts: # `DIRECT` / `TRANSFERABLE` / `ADJACENT` / `WEAK` / `GAP`
- Proposed reorderings within sections (lead with highest-confidence)

**For resumes >15 bullets:** present results one role at a time and get confirmation before moving to the next role. Dumping 30-bullet tables at once overwhelms the checkpoint.

Ask: *"Which reframes feel true? Any I'm stretching too far? Any bullets you want to remove entirely?"* Apply the user's corrections before Phase 3.

---

## Phase 3 — Gap Discovery (Conditional)

**Skip if:** <3 `GAP`/`WEAK` items AND all must-have keywords have `DIRECT` or `TRANSFERABLE` coverage — *unless the user explicitly asks "what else should I include?" or similar, in which case always run.*

Otherwise, surface the gaps and run a **branching discovery interview** to find undocumented experience. Branch taxonomy (A–E) and question banks are in `references/discovery-interview.md` — load it.

Output to user:

- Each gap → 2–3 targeted questions
- When the user answers, convert into a candidate bullet at a realistic band
- Any claim that can't be substantiated → flag as a real gap; route to positioning or cover-letter. Never invent.

Then fold new bullets into the matching pass and update the roll-up.

---

## Phase 4 — Positioning

Always runs. This is where the skill's second promise lives. Covers headline/summary, narrative arc, level calibration, and gap handling. Load `references/positioning.md` and `shared/communication-principles.md` — the "I help" framing (principle 6) applies directly to headlines and summaries; audience-centered focus (principle 1) drives the narrative arc.

Output to user (checkpoint):

- Headline options (2–3) at different angles, with the framing choice shown
- Narrative arc — current vs. target, with the delta named
- Level calibration — is the language at, above, or below target seniority? Evidence required.
- Gap handling plan — per visible gap: resume / cover letter / interview

Ask: *"Which headline angle? Does the narrative match how you want to be perceived?"*

---

## Phase 5 — Output

Final deliverables. Format details, ATS tips, and optional DOCX export via `anthropic-skills:docx` in `references/output-formats.md`. **Load `references/templates/README.md` now** — it captures the user's canonical resume + cover-letter layout, heading style, date format, and DOCX style source. Every Phase 5 output must follow those conventions unless the user explicitly deviates.

**Output path:** all files go to `~/Documents/resumes/<Company>/` (one folder per target company). See `references/output-formats.md` §0.

**Required step before any file write:** walk the user through the assembled resume **section by section** (header/summary, each role, tail sections) for approval. See `references/output-formats.md` §3.5. Cover letters get the same treatment paragraph-by-paragraph, and must also clear the anti-patterns checklist (positive framing, no JD restatement, P4 claim verified).

Defaults:

1. **Tailored resume** (markdown, ready to copy-paste or convert)
2. **Keyword coverage report** — must-haves + nice-to-haves hit/missed
3. **(Optional)** Cover letter draft — offered, not default

No change log. What was reframed and why is a conversation artifact, not a deliverable — if the skill itself should behave differently next time, that's a session-learnings update to the skill, not a file for the user.

Offer: *"Want me to convert to DOCX, draft a cover letter, or iterate on any section?"*

**Post-write verification (when this skill's own files are edited):** after any Edit to `references/*.md` or `SKILL.md` in this skill, Read the written file and grep for the inserted anchor text. Do not trust the Edit tool's success signal alone — on hosts where `~/.claude/skills/resume-tailor/` is not a symlink to `claude_code/claude-skills/resume-tailor/`, edits can land in a stale copy while the canonical repo stays clean. Verify in the canonical path at `/Users/summerrae/claude_code/claude-skills/resume-tailor/` (or the host's equivalent).

---

## Principles

1. **Truth-preserving.** Select, emphasize, reframe — never fabricate. A reframe must be defensible from the user's actual experience.
2. **Visible scoring.** Every recommendation shows its confidence band and strategy. No black-box rewrites.
3. **Collaborative, not autopilot.** Every phase ends with a checkpoint. The user edits, vetoes, and corrects before the next phase runs.
4. **Solo-user scope.** One person, one resume, one JD at a time. No batch mode, no library management, no external infra.
5. **Minimum viable dependencies.** Pure markdown by default. Optional DOCX via `anthropic-skills:docx`. No bun/node/React required.
6. **Gap handling is disclosure, not manufacturing.** Visible gaps go to cover letters or discovery prompts — never filled with invented content.
7. **Communication principles apply.** Resumes are author-to-audience writing. Audience-centered focus, lead with the strongest evidence, simple plain-language bullets, no ego residue. Load `shared/communication-principles.md` before Phase 2 matching and Phase 4 positioning — the bullet-level and headline-level decisions are where these principles bite hardest.

## Professional Help Boundary

This skill helps with resume content and positioning for a specific role. It does **not** replace professional help for:

- **Sustained job-search distress, burnout, or imposter-spirals** → therapist or EAP. If the session surfaces acute distress — job-loss anxiety, panic, depressive ideation, or compulsive rewriting driven by anxiety rather than fit — pause the tailoring and say so directly. The resume can wait.
- **Career direction at large** (whether to apply, whether to change fields, longer-term strategy) → licensed career coach.
- **Salary negotiation strategy** → licensed career coach or negotiation specialist.
- **Legal questions** (visa sponsorship, non-competes, discrimination claims, termination disputes) → employment attorney.

When the conversation drifts into any of those, name the limit and suggest the appropriate professional before continuing with resume work.
