---
name: resume-tailor
description: Tailor an existing resume to a specific job description with visible confidence scoring, structured reframing, and positioning help. Triggers on "tailor my resume", "update my resume for this job", "resume to job", "match resume to JD", "help me apply to", "resume keywords", "ATS alignment", "position my experience", "reframe my resume", or pasting a JD alongside a resume.
---

# Resume Tailor — JD-Driven Resume Tailoring + Positioning

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


Walks the user through a phased resume-tailoring session: JD analysis → matching pass with confidence scores → optional gap discovery → positioning pass → output. Truth-preserving — the skill selects, emphasizes, and reframes existing experience; it never fabricates.

## Mission

A person's ability to get a job should be based on their actual experience, not on their resume-writing skills. This skill closes that gap by making alignment auditable (visible scores), bringing out undocumented experience (branching interview), and calibrating tone/level to the target role — without inventing anything.

## Before Starting

Ask the user for:

1. **Resume source** — path to their canonical resume (markdown preferred; DOCX/PDF fine, converted in-memory) OR pasted text.
2. **Job description** — URL, file path, or pasted text. If it is a LinkedIn URL, prefer `tools/jd-prep/jd_prep.py` to capture `jd.md`. If it is another URL, fetch it with the host's available web tool. If fetch fails, ask the user to paste the JD text and keep the URL for `jd.md`.
3. **Target outcome** — "drop-in replacement bullets", "full rewrite", or "just show me gaps". Default: tailored resume + keyword coverage report. Cover letters are opt-in only — see Phase 5 §4 and Principle 8. Do not offer one unless the user has explicitly asked.

If any piece is missing, ask once. Don't proceed with half the inputs.

**If no resume exists yet:** offer to run Phase 3 (discovery) first to generate source bullets from scratch, then return to Phase 1 with the drafted material as the "resume".

**If the user pastes multiple JDs:** pick one and defer the others. This skill is one-JD-at-a-time by design (see Principle 4). Say so and let the user choose.

---

## Phase 1 — JD Analysis

Produce a **structured job profile** before touching the resume. Output format, action codes, and extraction heuristics live in `references/jd-analysis.md` — load it now. Also load `references/role-archetypes.md` so the JD is classified into the right resume-story type before weights and bullet rewrites begin.

Output to user (checkpoint) — **in this order**:

1. **JD recap** — title, company, seniority, comp, work mode, industry. Then a **bulleted 3-6 line summary of what the role actually does** (responsibilities + must-haves in plain language, not JD-parroted). This anchors the user in the JD before they evaluate weights.
2. Weighted focus areas (weights sum to 1.0) — tied explicitly to JD recap items so the user can see *why* each area got its weight
3. Must-have keywords vs. nice-to-haves (ATS tier)
4. Seniority signals + scope signals (team size, ownership, budget)
5. Cultural signals (what kind of operator do they want?)
6. Archetype selected + resume story to foreground + what to downplay
7. Action-code plan per focus area: `LEAD_WITH` / `EMPHASIZE` / `QUANTIFY` / `DOWNPLAY`

**Rationale for JD-first ordering:** Users often can't evaluate whether a weight is right without re-anchoring in the JD content. Placing the JD recap immediately above the weights means the user sees the *evidence* and the *derived profile* together, without scrolling back to the JD file.

Ask: *"Does this profile match how you read the role? Anything I over- or under-weighted?"* Wait for confirmation before Phase 2.

---

## Phase 2 — Matching Pass

For each bullet and role in the resume, assign a confidence band vs. the JD profile and propose a reframe if appropriate. Rubric + four reframing strategies are in `references/matching-rubric.md` — load it. Also load `shared/communication-principles.md` — reframed bullets must lead with the conclusion, stay in plain language, and serve the reader (hiring manager / ATS), not the author. If the target role is Head/VP/executive level, also load `references/executive-bullets.md` so bullet rewrites surface decisions, tradeoffs, governance, and leverage rather than just implementation.

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

Always runs. This is where the skill's second promise lives. Covers headline/summary, narrative arc, level calibration, and gap handling. Load `references/positioning.md`, `shared/communication-principles.md`, `references/writing-quality.md`, `references/headline-library.md`, and `references/summary-patterns.md` — the "I help" framing (principle 6) applies directly to headlines and summaries; audience-centered focus (principle 1) drives the narrative arc; the headline and summary libraries keep the prose specific instead of generic.

Output to user (checkpoint):

- Headline options (2–3) at different angles, with the framing choice shown
- Narrative arc — current vs. target, with the delta named
- Level calibration — is the language at, above, or below target seniority? Evidence required.
- Gap handling plan — per visible gap: resume / cover letter / interview

Ask: *"Which headline angle? Does the narrative match how you want to be perceived?"*

---

## Phase 5 — Output

Final deliverables. Format details, ATS tips, and optional DOCX export are in `references/output-formats.md`. **Load `references/templates/README.md`, `references/writing-quality.md`, `references/resume-bullet-bans.md`, and `references/resume-qa.md` now** — the template file captures the user's canonical resume + cover-letter layout, heading style, date format, and DOCX style source; the other references keep the prose specific, ban low-signal bullet patterns, and force a final coherence pass. Every Phase 5 output must follow those conventions unless the user explicitly deviates.

**Template-compliant markdown is mandatory.** Resume markdown must use pandoc `custom-style` divs for the name (`::: {custom-style="Title"} ... :::`) and headline (`::: {custom-style="Subtitle"} ... :::`), ALL-CAPS H1 section headers (`# SKILLS`, `# EXPERIENCE`, `# EDUCATION`), plain-text H2 role headings (`## Company, Location - Title`, no italics), and `MONTH YYYY - PRESENT` date lines. Do NOT write the name as `# Name` or add a `## Summary` heading — both break the template's style mapping. Cover letters use the top-block format in `references/templates/README.md` (bold name, city/phone/email, ordinal date, recipient block, `Dear ...`, body, `Regards,`, bold signature name).

**Output path:** all files go to `~/Documents/resumes/<Company>/` (one folder per target company). See `references/output-formats.md` §0.

**Required step before any file write:** walk the user through the assembled resume **section by section** (header/summary, each role, tail sections) for approval. See `references/output-formats.md` §3.5. Cover letters get the same treatment paragraph-by-paragraph, and must also clear the anti-patterns checklist (positive framing, no JD restatement, P4 claim verified).

Defaults:

1. **Tailored resume** (markdown, ready to copy-paste or convert)
2. **Keyword coverage report** — must-haves + nice-to-haves hit/missed
3. **`jd.md`** — source URL + captured date + full JD text. Required in every company folder so the tailored outputs remain legible months later. See `references/output-formats.md` §0.1.
4. **Cover letter draft — opt-in only.** Do NOT offer, pre-announce, or auto-draft a cover letter at the end of Phase 5. Produce resume + keyword coverage + jd.md only. Draft a cover letter exclusively when the user explicitly requests one ("draft a cover letter", "write me a letter for this", etc.). The default closing prompt does NOT mention cover letters — its absence is what prevents an unwanted draft from being produced unprompted.

No change log. What was reframed and why is a conversation artifact, not a deliverable — if the skill itself should behave differently next time, that's a session-learnings update to the skill, not a file for the user.

Offer: *"Want me to convert to DOCX or iterate on any section?"*

**Post-write verification (when this skill's own files are edited):** after any Edit to `references/*.md` or `SKILL.md` in this skill, Read the written file and grep for the inserted anchor text. Do not trust the Edit tool's success signal alone — on hosts where `~/.claude/skills/resume-tailor/` is not a symlink to `claude_code/claude-skills/resume-tailor/`, edits can land in a stale copy while the canonical repo stays clean. Verify in the canonical path at `/Users/summerrae/claude_code/claude-skills/resume-tailor/` (or the host's equivalent).

---

## Principles

1. **Truth-preserving.** Select, emphasize, reframe — never fabricate. A reframe must be defensible from the user's actual experience.
2. **Visible scoring.** Every recommendation shows its confidence band and strategy. No black-box rewrites.
3. **Collaborative, not autopilot.** Every phase ends with a checkpoint. The user edits, vetoes, and corrects before the next phase runs.
4. **Solo-user scope.** One person, one resume, one JD at a time. No batch mode, no library management, no external infra.
5. **Minimum viable dependencies.** Pure markdown by default. Optional DOCX via `pandoc` with the template reference docs in `references/templates/`. If `pandoc` is unavailable, stop at reviewed markdown instead of inventing another render path. No bun/node/React required.
6. **Gap handling is disclosure, not manufacturing.** Visible gaps go to cover letters or discovery prompts — never filled with invented content.
7. **Communication principles apply.** Resumes are author-to-audience writing. Audience-centered focus, lead with the strongest evidence, simple plain-language bullets, no ego residue. Load `shared/communication-principles.md` before Phase 2 matching and Phase 4 positioning — the bullet-level and headline-level decisions are where these principles bite hardest.
8. **Cover letters are opt-in only.** The default Phase 5 deliverable set is resume + keyword coverage + jd.md. Cover letters are produced only on explicit user request — never offered proactively, never pre-announced, never drafted as a "while I'm at it" addition. The closing prompt deliberately omits cover-letter language so the user has to raise it.
9. **Final prose must not sound templated.** Lists and tables are for analysis checkpoints only. Headlines, summaries, and cover letters must read like authored prose with a governing idea, specific evidence, and no buzzword stacking. Load `references/writing-quality.md` before writing them.

## Out of Scope

This skill does NOT:
- Triage/score a batch of JDs against a profile—use `jd-screener` first, then hand winners here one at a time.
- Submit applications, send messages, or interact with employer portals on the user's behalf—the user applies manually.
- Fabricate experience or invent skills/dates/numbers not in the source resume—truth-preserving by design.
- Provide career direction, salary negotiation, or legal advice (visa, non-competes)—engage a licensed coach or employment attorney.
- Offer or auto-draft a cover letter—opt-in only on explicit user request (Principle 8).

## Professional Help Boundary

This skill helps with resume content and positioning for a specific role. It does **not** replace professional help for:

- **Sustained job-search distress, burnout, or imposter-spirals** → therapist or EAP. If the session surfaces acute distress — job-loss anxiety, panic, depressive ideation, or compulsive rewriting driven by anxiety rather than fit — pause the tailoring and say so directly. The resume can wait.
- **Career direction at large** (whether to apply, whether to change fields, longer-term strategy) → licensed career coach.
- **Salary negotiation strategy** → licensed career coach or negotiation specialist.
- **Legal questions** (visa sponsorship, non-competes, discrimination claims, termination disputes) → employment attorney.

When the conversation drifts into any of those, name the limit and suggest the appropriate professional before continuing with resume work.
