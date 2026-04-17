# Output Formats + ATS + Deliverables

Phase 5 produces the final deliverables. Four parts — tailored resume, change log, keyword coverage report, optional cover letter.

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
  ± "Product Manager" → "Product Manager specializing in 0→1 B2B SaaS"
  Why: JD weights 0→1 product discovery at 0.4 (LEAD_WITH). Option A (function-forward) chosen per Phase 4.

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
  ✓ "0 to 1"                   — summary, bullet 1 of Acme ("0→1")
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

Offered, not default. If the user says yes:

- 3–4 short paragraphs; not a resume rehash.
- Paragraph 1: one-sentence hook — why this role, why now.
- Paragraph 2: the single strongest claim from the resume's `LEAD_WITH` area, told as a mini-story.
- Paragraph 3: address any gap/pivot/short tenure the resume deferred (per Phase 4 gap plan).
- Paragraph 4: one concrete thing that excites about the company — not "your mission".

Draft in the user's voice using Phase 1 culture signals and Phase 4 narrative arc. Get explicit sign-off — cover letters are much more voice-sensitive than resumes.

## 5. Format Conversion (Optional)

- **DOCX:** invoke `anthropic-skills:docx` with the final markdown. Handles styling, hyperlinks, and file write.
- **PDF:** convert from DOCX (Word, Pages, LibreOffice) OR render markdown via pandoc. Avoid PDF as primary source — ATS parses PDF unreliably. Submit DOCX when allowed; PDF only when required.
- **Plain text:** for pasting into LinkedIn or ATS forms, generate a plain-text version stripped of markdown syntax.

Never offer HTML, LaTeX, or heavily-designed templates as default. They fail ATS parsers.

## ATS Tips

- Keywords must appear **in the bullet prose**, not just in a skills list. ATS-modern scanners weight context, not keyword density.
- Do not use tables, text boxes, headers/footers, or multi-column layouts in DOCX. Single column, standard headings.
- Standard section names (`Experience`, not "Where I've Been"). ATS looks for headers.
- Dates in `MMM YYYY` or `YYYY`, consistently.
- Font: system defaults (Calibri, Arial, Georgia). Don't embed custom fonts.
- File name: `Firstname_Lastname_Resume_CompanyName.docx`. ATS sometimes surfaces filename.

## Deliverables Checklist

Before wrapping up:

- [ ] Tailored resume (markdown)
- [ ] Change log with rationale per change
- [ ] Keyword coverage report
- [ ] DOCX version (if requested)
- [ ] Cover letter draft (if requested)
- [ ] User has signed off on each artifact or flagged what to revise
