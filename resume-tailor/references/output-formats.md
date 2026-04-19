# Output Formats + ATS + Deliverables

Phase 5 produces the final deliverables: tailored resume, keyword coverage report, optional cover letter. No change log — what was changed and why is a conversation artifact, not a file. If the skill itself should behave differently next time, that's a session-learnings update to the skill, not a deliverable.

**Load `templates/README.md` before producing any Phase 5 output.** It captures the user's canonical layout, heading style, date format, and DOCX style source. Every resume and cover letter must follow those conventions unless the user explicitly deviates.

## 0. Output Path Convention (Required)

All Phase 5 deliverables go to `~/Documents/resumes/<Company>/` — one folder per target company. Create the directory if it does not exist (`mkdir -p`).

**File naming inside the folder:**

- `Summer_Rae_Resume_<Company>.md` and `.docx`
- `Summer_Rae_CoverLetter_<Company>.md` and `.docx` (if drafted)
- `Summer_Rae_<Company>_KeywordCoverage.md`
- `jd.md` — **required** (see §0.1)

`<Company>` matches the casing/spelling the user uses (e.g. `AHEAD`, `Anthropic`, `DeepMind`). Strip spaces and punctuation for directory and file names (`Acme Corp` → `AcmeCorp`).

Ask once if the target folder already exists with content that wasn't written this session — otherwise overwrite freely (each session owns its company folder).

## 0.1 `jd.md` — Save the JD Alongside Every Tailored Output (Required)

Every company folder must contain `jd.md` with:

1. The source URL (LinkedIn posting, company careers page, etc.) at the top
2. Date captured (ISO format, e.g. `2026-04-19`)
3. The full JD text as pasted by the user

Write `jd.md` as part of the Phase 5 output set — the same step that writes the resume and cover letter, not after.

**Format:**

```markdown
# <Title> — <Company>

**Source:** <URL>
**Captured:** YYYY-MM-DD

---

<full JD text as pasted>
```

**Input-handling rules:**

- If the user pastes JD text only (no URL): ask for the URL before Phase 5. Do not silently write `jd.md` without the source.
- If the user pastes a URL and the fetch worked: save the fetched text in `jd.md` with the URL at top.
- If the user pastes a URL and the fetch failed: ask the user to paste the text, then save both.

**Why this is required:**

- The tailored resume and cover letter are only legible months later if paired with the JD they were written against. Without the JD, the reframes look arbitrary.
- LinkedIn postings disappear when filled — the URL alone is not durable. The full text must be captured at tailor time.
- When the user asks "why did we lead with X for this role?" later, the JD is the only evidence that answers.
- When the same company reappears, the saved JD lets us diff the new post against the old one.

## 1. Tailored Resume (Markdown, Default)

Markdown is the primary output because it's readable, diff-able, and converts cleanly to DOCX/PDF via downstream tools.

**Use pandoc `custom-style` divs for the name and headline** so the rendered DOCX invokes the template's distinct `Title` and `Subtitle` Word paragraph styles — not generic `Heading 1` + bold body. Without the divs, the name looks identical to section headings like `SKILLS` and the template's visual hierarchy collapses. This is required, not optional.

Structure (template-compliant):

```markdown
::: {custom-style="Title"}
[Name]
:::

::: {custom-style="Subtitle"}
[Headline]
:::

[City] · [email] · [phone] · [portfolio/LinkedIn]

[2–3 sentence summary paragraph, if Phase 4 chose to include one — NO `## Summary` heading; the template has no Summary style]

# SKILLS
[Grouped or flat prose, depending on seniority]

# EXPERIENCE

## [Company], [Location] - [Title]
[MONTH YYYY] - [MONTH YYYY or PRESENT]
- [Bullet 1, highest-confidence, LEAD_WITH applies if relevant]
- [Bullet 2]
- ...

# EDUCATION
[Degree, School, Year]

# [Optional sections: PUBLICATIONS & PRESENTATIONS, AWARDS — ALL CAPS H1, only if Phase 1 flagged them as signal]
```

**Heading rules:**

- Top-level section headings are `# ` (H1) and **ALL CAPS** (`# SKILLS`, `# EXPERIENCE`, `# EDUCATION`). Do not title-case them.
- Role headings are `## ` (H2) in the format `## Company, Location - Title`. No italics, no em-dashes in the heading itself (em-dashes in bullets are fine — but see ATS Tips below).
- No `## Summary` heading. The template has no Summary style; the summary paragraph sits directly under the contact line as body text.
- Dates go on the line immediately after the role heading, in `MONTH YYYY - MONTH YYYY` or `MONTH YYYY - PRESENT` format (three-letter month abbreviations like `FEB 2025` are also acceptable if used consistently).

**Ordering rules within a role:**

- Bullet 1: `LEAD_WITH` the highest-weighted focus area for the JD.
- Bullets 2–3: `EMPHASIZE` other high-weight areas.
- Lower-weight or `DOWNPLAY` bullets last.
- 3–5 bullets per role; fewer for older or smaller roles.

**Role ordering:** reverse chronological. Group short or tangentially-relevant roles under "Earlier experience" with title + company + years only.

## 2. Keyword Coverage Report

ATS-oriented, binary per keyword.

```
KEYWORD COVERAGE — [Role] at [Company]

MUST-HAVE (4/5):
  ✓ "product manager"          — headline, 3 bullets
  ✓ "B2B SaaS"                 — summary, bullet 2 of Acme
  ✓ "0 to 1"                   — summary, bullet 1 of Acme (rendered as "0 to 1" for ATS safety)
  ✓ "customer discovery"       — bullet 3 of Acme
  ✗ "PLG"                      — missed; nice-to-have in JD but worth adding

NICE-TO-HAVE (2/3):
  ✓ "growth"
  ✓ "metrics"
  ✗ "roadmap"                  — consider adding to Initech bullet 4

NOTES:
  - Must-have coverage: 4/5 (80%).
  - If <80%, Phase 3 discovery should have run — re-check.
  - ATS traps avoided: filler words kept out of bullets.
```

## 3. Cover Letter (Optional)

Offered, not default. If the user says yes, write naturally and persuasively — like a real professional wrote it, not a chatbot.

### Hard rules

- **Length:** 250–350 words total.
- **Greeting:** always `Dear Hiring Manager,` unless the user names a specific recipient.
- **Closing:** always `Regards,` followed by the user's name on the next line.
- **Punctuation:** use hyphens only. NO em dashes, NO en dashes — they read as AI-generated.
- **Voice:** sound like a real human wrote it. Plain language. Avoid "thrilled," "passionate," "synergy," "leverage," and other filler. No stacks of adjectives.
- **Truth-preserving:** never fabricate or exaggerate. Every claim must be defensible from the resume or the user's stated experience. Same rule as Phase 2 reframes.
- **Substance:** connect 2–3 specific, measurable achievements from the resume to the employer's stated needs. Not a resume rehash — a targeted bridge between what they need and what the user has done.

### Structure

Roughly 3–4 short paragraphs:

- Paragraph 1 (the hook): one or two sentences on why this role and why now. No preamble, no self-introduction beyond what's functionally necessary. **P1 is positioning, not evidence.** State why the role lands and what the user does about it — do not stack credentials ("fifteen years / past year / worked with X"). Credentials belong in P2/P3 bridges. Keep P1 tight enough that it works as a standalone hook; dumping evidence into it crowds out the reason the reader should keep reading.
- Paragraph 2 (the strongest bridge): name the JD's top need, then give one specific, measurable thing from the resume that answers it.
- Paragraph 3 (the second bridge, optional): second JD need, second specific answer. Or — if the user has a gap/pivot/short tenure to address (per Phase 4 gap plan), use this paragraph for that instead.
- Paragraph 4 (the close): one of two shapes, depending on what the user has to work with.
  - **Company-specific hook** — one concrete, non-generic thing that draws the user to this firm. Not "your mission." Not "your culture." Something the user has actually noticed about the firm, the product, or the role (requires WebFetch verification — see anti-pattern below).
  - **Role-need mapping** — name the full shape of the work abstractly (e.g. "vision, execution, governance, adoption"), then map each pillar to a concrete candidate credit. Describes the *kind* of role this is, not the hiring team's stated ask. Use when the user can't produce a verified company-specific hook or when the JD's scope itself is the strongest through-line.
  - Both shapes close with a soft offer to talk. Avoid "I would love the opportunity" filler — shorter is better.

### Bridge Shape (Problem → Solution → Impact)

Bridge paragraphs (2 and 3) should hit three beats, in order:

1. **Problem** — name the hiring team's actual challenge in their own words (extracted from the JD).
2. **Solution** — one concrete thing the user has done that addresses it, using resume-verified capability.
3. **Impact** — the measurable result. A percent, dollar, headcount, timeframe, or named outcome.

Skipping Impact is the most common failure mode: the paragraph sounds relevant but leaves the reader without evidence. If the user can't produce a measurable result for a bridge, either pick a different achievement or mark the paragraph as qualitative and lean on scope (team size, stakeholder seniority, org-wide adoption) instead.

### Tone Calibration by Company Type

Read the JD's voice and the company's public writing. Match it. A letter pitched at the wrong register reads as off even when the content is right.

| Company type | Tone | Example phrasing |
|--------------|------|------------------|
| Startup / early-stage | Conversational, direct | "I've spent the last year building exactly this." |
| Corporate / enterprise | Professional, measured | "My experience in enterprise AI delivery aligns closely with the role's stated objectives." |
| Government / public sector | Formal, criteria-driven | "I address each of the key requirements below." |
| Consultancy / advisory | Confident, client-facing | "I bring a track record of translating AI ambition into shipped outcomes for executive stakeholders." |
| Research / academic | Substantive, referential | "My work on [X] intersects directly with the lab's focus on [Y]." |
| Creative / agency | Personality forward | "Your work on [specific thing] is what made me pay attention." |
| Non-profit / mission-driven | Mission-aligned | "I've followed your work on [X] and share the commitment to [Y]." |

### Anti-patterns (reject in review)

- **P1 comparative framing** ("rare to find a posting that asks for both") — rewrite to positive-personal ("I was excited to see…"). The hiring team is not the audience for market critique.
- **P1 credential stacking.** P1 sentences stuffed with years, employer names, and stakeholder names ("fifteen years running AI functions for C-suite stakeholders, plus the past year working with Andrew Ng's team") are a P1 failure even when each fact is true. P1 positions; P2/P3 prove. If the hook paragraph carries numbers and named employers, cut them out and push them into the bridge paragraphs where they earn their keep.
- **Aspirational-future framing in P1.** Phrases like "the blend I've been building toward", "the direction I've been working toward", "where I'm heading" read as LLM-generated and weaken owned claims. Prefer completed past tense: "this is exactly where I've spent the last few years" over "the blend I've been building toward." The user has done the thing — say so.
- **Abstracted-away-from-the-posting language.** "A role asking for…" is one step removed; "your role posted for…" / "your posting for…" / "the X role you're hiring for" speaks directly to the reader. Keep P1 second-person-adjacent, not third-person about.
- **Generic nouns where the user has distinctive ones.** "Combination", "intersection", "blend" are invisible; if the user offered a more specific word ("dual-modality", "two-track", "executive-plus-hands-on"), keep it. Don't smooth distinctive vocabulary into interchangeable filler.
- **Any sentence restating the JD back at the reader** ("The JD emphasizes…", "Your posting highlights…", "As described in the role…"). They wrote it; answer the ask instead.
- **Company-specific claims in P4 without verification** — do not infer the company's focus, methodology, or segment from the JD alone. WebFetch the company's own site (about page, services/products, careers) before naming anything specific. If the claim can't be verified, keep P4 generic or drop it.
- **P4 self-focused openers** ("What excites me about working at…", "What drew me to…", "What I'd love about…"). These center the applicant's feelings, not the applicant's match to the role. Flip to audience-centered: lead with the role need (stated abstractly, not as a JD quote) then the candidate's evidence that answers it. Example: *"The full stack of enterprise agentic AI delivery — vision, execution, governance, adoption — is the work I've been running for years. At Govini…"* maps each JD pillar to a concrete credit without saying "your role calls for X." Describes the shape of the work, not the hiring team's stated ask.

### Process

Draft in the user's voice using Phase 1 culture signals and Phase 4 narrative arc. Walk the user through **paragraph by paragraph** before writing to a file. Cover letters are more voice-sensitive than resumes — get explicit sign-off on each paragraph.

### Iteration

After the first full draft, ask whether the user wants to adjust:

- **Tone** (more formal, more casual, more technical)
- **Which achievements** are highlighted
- **Specific phrasing**
- **Length**

Re-draft. Repeat until the user explicitly signs off before any file write.

## 3.5 Section-by-Section Review (Required Before File Export)

Before writing any file (markdown, DOCX, PDF, cover letter), walk the user through the assembled resume **section by section**. Present one section at a time (header/summary, then each role, then education/speaking/skills) and wait for explicit approval or edits before moving to the next.

Why this matters: the Phase 2 and Phase 4 checkpoints validate individual bullets and framing choices, but the *assembled* document reveals problems that only show up in context — duplicated claims across roles, awkward transitions, proportions that feel off, a headline that no longer fits the final narrative. Reviewing in final form catches these before they're baked into a file.

**Procedure:**

1. Show the header + headline + summary together. Ask: *"Header/summary good as-is, or edits?"*
2. For each role, show the full bullet list as it will appear. Ask: *"This role good, or edits?"*
3. Show education, speaking, and any tail sections. Ask: *"Tail sections good, or edits?"*
4. After every section is approved, show the full assembled resume once more and ask: *"Final read — anything to change before I write the file?"*

Only after the final confirmation: write the markdown, generate DOCX, and produce the cover letter. The cover letter gets its own review pass (paragraph-by-paragraph) before file export.

## 4. Format Conversion (Optional)

- **DOCX:** use pandoc with `--reference-doc=` pointing at the appropriate template in `templates/` — this inherits the user's fonts, margins, and heading styles on every render. See `templates/README.md` for the exact command. Alternative: `anthropic-skills:docx` plugin if template-driven styling is not required.
- **DOCX via `/tmp/` script:** if generating with a standalone node script that imports `docx-js`, the module is often installed globally. Wrap the call: `NODE_PATH="$(npm root -g)" node /tmp/generate_resume_docx.js`. Without `NODE_PATH`, node can't resolve global packages from scripts outside an npm project and fails with `Cannot find module 'docx'`.
- **PDF:** convert from DOCX (Word, Pages, LibreOffice) OR render markdown via pandoc. Avoid PDF as primary source — ATS parses PDF unreliably. Submit DOCX when allowed; PDF only when required.
- **Plain text:** for pasting into LinkedIn or ATS forms, generate a plain-text version stripped of markdown syntax.

Never offer HTML, LaTeX, or heavily-designed templates as default. They fail ATS parsers.

## ATS Tips

- Keywords must appear **in the bullet prose**, not just in a skills list. ATS-modern scanners weight context, not keyword density.
- **Avoid Unicode glyphs in the resume body.** Arrows (`→`, `⇒`), em-dashes in keyword positions, bullet-point characters, and fancy quotes can fail older ATS parsers and cause keyword mismatches. Write `0 to 1` instead of `0→1`, `A to B` instead of `A→B`, regular hyphens instead of en/em-dashes in keyword-adjacent positions. Reserve Unicode for the coverage report (internal, not parsed by ATS).
- Do not use tables, text boxes, headers/footers, or multi-column layouts in DOCX. Single column, standard headings.
- Standard section names (`Experience`, not "Where I've Been"). ATS looks for headers.
- Dates in `MMM YYYY` or `YYYY`, consistently.
- Font: system defaults (Calibri, Arial, Georgia). Don't embed custom fonts.
- File name: `Firstname_Lastname_Resume_CompanyName.docx`. ATS sometimes surfaces filename.
- Spell out acronyms on first use, then abbreviate (`Retrieval-Augmented Generation (RAG)`). ATS keyword scanners match both forms and reviewers skim the expansion.

### What to Omit

These waste line real-estate on a modern resume. Cut them unless a specific JD or region requires otherwise:

- `"References available upon request"` — assumed.
- Objective statements — replaced by the professional summary years ago.
- Every job since high school — cap at last 10–15 years unless earlier roles are directly relevant.
- High school education when the user has a degree.
- Hobbies and interests unless the JD specifically signals cultural fit as a focus.
- Salary expectations — never on the resume.
- Reasons for leaving prior roles.
- Full street address — city and state (or city only, international) are enough.
- Photo, date of birth, nationality — US-market standard (discrimination risk). Override only when the target region/format calls for it.

## Deliverables Checklist

Before wrapping up:

- [ ] Tailored resume (markdown)
- [ ] Keyword coverage report
- [ ] DOCX version (if requested)
- [ ] Cover letter draft (if requested)
- [ ] `jd.md` saved (source URL + captured date + full JD text)
- [ ] User has signed off on each artifact or flagged what to revise
