# Output Formats + ATS + Deliverables

Phase 5 produces the final deliverables. Four parts — tailored resume, change log, keyword coverage report, optional cover letter.

## 0. Output Path Convention (Required)

All Phase 5 deliverables go to `~/Documents/resumes/<Company>/` — one folder per target company. Create the directory if it does not exist (`mkdir -p`).

**File naming inside the folder:**

- `Summer_Rae_Resume_<Company>.md` and `.docx`
- `Summer_Rae_CoverLetter_<Company>.md` and `.docx` (if drafted)
- `Summer_Rae_<Company>_ChangeLog.md`
- `Summer_Rae_<Company>_KeywordCoverage.md`

`<Company>` matches the casing/spelling the user uses (e.g. `AHEAD`, `Anthropic`, `DeepMind`). Strip spaces and punctuation for directory and file names (`Acme Corp` → `AcmeCorp`).

Ask once if the target folder already exists with content that wasn't written this session — otherwise overwrite freely (each session owns its company folder).

## 1. Tailored Resume (Markdown, Default)

Markdown is the primary output because it's readable, diff-able, and converts cleanly to DOCX/PDF via downstream tools.

Structure:

```markdown
# [Name]

[Headline]

[City] · [email] · [phone] · [portfolio/LinkedIn]

## Summary (optional)
[2–3 sentence summary, if Phase 4 chose to include one]

## Experience

### [Title], [Company] — [Location] (optional)
[Start date] – [End date or Present]
- [Bullet 1, highest-confidence, LEAD_WITH applies if relevant]
- [Bullet 2]
- ...

## Skills (optional, if Phase 1 called for keyword density)
[Grouped or flat, depending on seniority]

## Education
[Degree, School, Year]

## [Optional sections: Projects, Publications, Speaking — only if Phase 1 flagged them as signal]
```

**Ordering rules within a role:**

- Bullet 1: `LEAD_WITH` the highest-weighted focus area for the JD.
- Bullets 2–3: `EMPHASIZE` other high-weight areas.
- Lower-weight or `DOWNPLAY` bullets last.
- 3–5 bullets per role; fewer for older or smaller roles.

**Role ordering:** reverse chronological. Group short or tangentially-relevant roles under "Earlier experience" with title + company + years only.

## 2. Change Log

A line-level diff with rationale. Makes every change auditable.

```
CHANGE LOG — Resume tailored to [Role] at [Company], [Date]

HEADLINE:
  ± "Product Manager" → "Product Manager specializing in 0 to 1 B2B SaaS"
  Why: JD weights 0-to-1 product discovery at 0.4 (LEAD_WITH). Option A (function-forward) chosen per Phase 4.

SUMMARY:
  + Added 2-sentence summary
  Why: Scope signal (cross-functional leadership) + user's eng+PM background warranted framing.

EXPERIENCE — Senior PM, Acme (2022–present):
  ± Bullet 1 reframed (Keyword Alignment):
    Before: Led sprint team to ship onboarding flows
    After:  Led self-serve onboarding redesign, driving 23% activation lift
    Band: TRANSFERABLE 75% → DIRECT 90%
    JD focus: 'B2B SaaS growth' (weight 0.3)

  + New bullet from Phase 3 Branch A (Skill gap — product analytics):
    "Built executive analytics dashboards (Looker) with ~200 weekly viewers..."
    Band: TRANSFERABLE 70%

  − Removed: "Ran weekly team lunches"
    Why: WEAK 20% — no JD signal.

  ↕ Reordered: bullet 4 → bullet 1
    Why: Highest DIRECT band; LEAD_WITH for top focus area.

SECTIONS:
  − Removed "Skills" list (noise; keywords woven into bullets)
  + Added "Projects" section (addresses recency gap on ML)
```

## 3. Keyword Coverage Report

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

## 4. Cover Letter (Optional)

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

- Paragraph 1 (the hook): one or two sentences on why this role and why now. No preamble, no self-introduction beyond what's functionally necessary.
- Paragraph 2 (the strongest bridge): name the JD's top need, then give one specific, measurable thing from the resume that answers it.
- Paragraph 3 (the second bridge, optional): second JD need, second specific answer. Or — if the user has a gap/pivot/short tenure to address (per Phase 4 gap plan), use this paragraph for that instead.
- Paragraph 4 (the close): one concrete, non-generic thing that draws the user to this specific company. Not "your mission." Not "your culture." Something the user has actually noticed about the firm, the product, or the role.

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
- **Any sentence restating the JD back at the reader** ("The JD emphasizes…", "Your posting highlights…", "As described in the role…"). They wrote it; answer the ask instead.
- **Company-specific claims in P4 without verification** — do not infer the company's focus, methodology, or segment from the JD alone. WebFetch the company's own site (about page, services/products, careers) before naming anything specific. If the claim can't be verified, keep P4 generic or drop it.

### Process

Draft in the user's voice using Phase 1 culture signals and Phase 4 narrative arc. Walk the user through **paragraph by paragraph** before writing to a file. Cover letters are more voice-sensitive than resumes — get explicit sign-off on each paragraph.

### Iteration

After the first full draft, ask whether the user wants to adjust:

- **Tone** (more formal, more casual, more technical)
- **Which achievements** are highlighted
- **Specific phrasing**
- **Length**

Re-draft. Repeat until the user explicitly signs off before any file write.

## 4.5 Section-by-Section Review (Required Before File Export)

Before writing any file (markdown, DOCX, PDF, cover letter), walk the user through the assembled resume **section by section**. Present one section at a time (header/summary, then each role, then education/speaking/skills) and wait for explicit approval or edits before moving to the next.

Why this matters: the Phase 2 and Phase 4 checkpoints validate individual bullets and framing choices, but the *assembled* document reveals problems that only show up in context — duplicated claims across roles, awkward transitions, proportions that feel off, a headline that no longer fits the final narrative. Reviewing in final form catches these before they're baked into a file.

**Procedure:**

1. Show the header + headline + summary together. Ask: *"Header/summary good as-is, or edits?"*
2. For each role, show the full bullet list as it will appear. Ask: *"This role good, or edits?"*
3. Show education, speaking, and any tail sections. Ask: *"Tail sections good, or edits?"*
4. After every section is approved, show the full assembled resume once more and ask: *"Final read — anything to change before I write the file?"*

Only after the final confirmation: write the markdown, generate DOCX, and produce the cover letter. The cover letter gets its own review pass (paragraph-by-paragraph) before file export.

## 5. Format Conversion (Optional)

- **DOCX:** invoke `anthropic-skills:docx` with the final markdown. Handles styling, hyperlinks, and file write.
- **DOCX via `/tmp/` script:** if generating with a standalone node script that imports `docx-js`, the module is often installed globally. Wrap the call: `NODE_PATH="$(npm root -g)" node /tmp/generate_resume_docx.js`. Without `NODE_PATH`, node can't resolve global packages from scripts outside an npm project and fails with `Cannot find module 'docx'`.
- **PDF:** convert from DOCX (Word, Pages, LibreOffice) OR render markdown via pandoc. Avoid PDF as primary source — ATS parses PDF unreliably. Submit DOCX when allowed; PDF only when required.
- **Plain text:** for pasting into LinkedIn or ATS forms, generate a plain-text version stripped of markdown syntax.

Never offer HTML, LaTeX, or heavily-designed templates as default. They fail ATS parsers.

## ATS Tips

- Keywords must appear **in the bullet prose**, not just in a skills list. ATS-modern scanners weight context, not keyword density.
- **Avoid Unicode glyphs in the resume body.** Arrows (`→`, `⇒`), em-dashes in keyword positions, bullet-point characters, and fancy quotes can fail older ATS parsers and cause keyword mismatches. Write `0 to 1` instead of `0→1`, `A to B` instead of `A→B`, regular hyphens instead of en/em-dashes in keyword-adjacent positions. Reserve Unicode for the change log and coverage report (internal, not parsed by ATS).
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
- [ ] Change log with rationale per change
- [ ] Keyword coverage report
- [ ] DOCX version (if requested)
- [ ] Cover letter draft (if requested)
- [ ] User has signed off on each artifact or flagged what to revise
