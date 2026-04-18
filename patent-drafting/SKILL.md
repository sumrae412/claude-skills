---
name: patent-drafting
description: Draft US provisional patent applications — specification, Application Data Sheet (37 CFR §1.76), drawings, and USPTO Patent Center filing checklist. Triggers on "draft a provisional", "patent application", "provisional patent", "file a patent", "ADS", "Application Data Sheet", "micro entity cert", "patent drawings", or when a user wants to capture an invention's priority date.
---

# Patent Drafting — US Provisional Application Workflow

Produces an attorney-review-ready provisional patent application for software inventions: specification with Alice §101 framing, Application Data Sheet per 37 CFR §1.76, black-and-white line drawings, and a USPTO Patent Center filing checklist. Not a substitute for a patent attorney — pressure-tests the spec against §112(a) written-description and §101 eligibility, but claim strategy and final-form filing should go through a registered practitioner.

## Mission

Software founders underutilize provisional applications because the bibliographic forms are opaque and the specification standards are unclear. This skill produces a complete filing package quickly enough that a founder can lock in a priority date within a few hours, then hand a polished draft to an attorney for claim work before the 12-month non-provisional deadline.

## Scope

**In scope:**
- US provisional applications under 35 U.S.C. §111(b)
- Software / computer-implemented inventions
- Solo inventor filings (pro se) and inventor-assignee filings (entity-applicant)
- Micro and small entity status
- Specification, ADS (PTO/AIA/14 equivalent), drawings (SVG-based), filing checklist

**Not in scope:**
- Non-provisional drafting with formal claims
- Patent prosecution (office-action responses)
- Foreign filings (PCT, EPO, etc.)
- Patent validity analysis or freedom-to-operate opinions
- Legal advice — always route through a registered US patent practitioner

## Sensitive-content handling (READ FIRST)

Patent drafts contain personally-identifying information (inventor address, phone, entity registration details) and unpublished invention disclosures. They must not live in a project's git repository. **Default storage location:** `~/Documents/patents/<project-name>/`. If the user is inside a project repo, (a) never write draft files under the project's working tree, (b) add `docs/patent/`, `patents/`, and `**/patent-drafts/` to the project's `.gitignore` as a safety net. See the user's global CLAUDE.md "Sensitive content" section.

If the user has an existing patent skill invocation on a repo branch, audit for leakage before proceeding: run `git log --all --oneline | grep -iE "patent|provisional"` and `git ls-files | grep -iE "patent"`. Any hits require remediation (branch rebase to drop, reflog expire, aggressive gc) before producing new drafts.

## Before Starting — Required Inputs

Ask the user for, in order:

1. **Invention domain + brief description** (2–3 sentences): what the invention does and what problem it solves. This is the raw material the specification is built from.
2. **Inventor(s)** — full legal name(s), residence city/state/country, citizenship, mailing address, phone, email. Multiple inventors: collect all.
3. **Applicant** — either the inventor(s) pro se (simpler for provisionals) or a juristic entity (LLC / corporation) via assignment.
   - Filing pro se is simpler: no assignment document required, no entity good-standing check, no §3.73(c) statement. The inventor can still assign to the entity later before the non-provisional.
   - Filing as entity-applicant is appropriate when ownership must be established early (investor diligence, cap-table-linked IP, M&A prep).
4. **Entity status** — micro (§1.29(a), income-based, ≤$241,830 gross income for 2025 — verify current figure at uspto.gov), small (§1.27), or large.
5. **Disclosure chronology** — specifically the first non-private disclosure date (public website launch, blog post, public repo commit, non-NDA pitch, product demo). This starts the 12-month §102(b)(1)(A) grace period.
6. **Codebase location** (if software) — the skill will explore the code to extract concrete technical details for the specification.

If any piece is missing, ask once. Do not fabricate an inventor or applicant.

---

## Phase 1 — Codebase Exploration (for software inventions)

Before drafting, dispatch an explorer subagent to map the architecture. Goal: extract concrete technical detail that survives Alice §101 review. Target outputs:

- **Subsystem enumeration** — discrete, composable subsystems with boundaries clear enough to claim independently.
- **Concrete technical improvements** per subsystem — what specifically is better vs. a naive implementation? Examples: "eager computation of scheduled_at reduces dispatch query cost from O(N) to O(log N)"; "unique-indexed dedup key gives atomic cross-channel deduplication without app-level check-then-act race".
- **Data-model highlights** — schemas where the structure itself is novel (sticky-override fields, canonical-path invariants, append-only audit logs).
- **Distinguishing features** vs. named categories of prior art — generic IFTTT-style automators, CRMs, transactional-notification services, vertical SaaS, off-the-shelf AI chatbots, etc.

Persist the exploration output — `subsystems`, `concrete_improvements`, `schema_notes`, `distinguishing_features` — and carry it into Phase 2.

---

## Phase 2 — Specification Draft

Produce `provisional-application-draft.md` (final target: ~15–20K words for a moderately complex software system). See `references/specification-template.md` for the full section-by-section template.

**Required sections:**

1. Cover sheet info (title, inventor, citizenship, residence, correspondence, customer number, entity status, docket, applicant)
2. Cross-reference to related applications
3. Statement regarding federally sponsored research
4. Field of the invention
5. Background — prior-art category limitations + specific technical problems the invention solves
6. Summary — subsystems (a), (b), (c)… each with one long sentence enumerating their function
7. Brief description of the drawings — one bullet per figure
8. Detailed description — one numbered section per subsystem, with concrete schemas, pseudocode, algorithms, and data-flow detail
9. Distinguishing features over prior art — organized by prior-art category
10. Concrete technical improvements (for §101 / Alice framing) — numbered list; this is the single most important section for software subject-matter eligibility
11. Non-limiting aspects — numbered claim-style paragraphs (target: 60–120+) providing claim optionality for the non-provisional
12. Data schema appendix — illustrative table definitions in PostgreSQL (or target DB) dialect
13. Glossary — every non-obvious term defined, precluding narrow later claim construction
14. General remarks on scope — boilerplate broadening language
15. Priority-date chronology — for attorney review (conception date, first disclosure, statutory bar, recommended internal deadline, foreign-filing implications)
16. Drawings to be prepared — per-figure brief for the draftsperson
17. Filing checklist

**Alice §101 framing.** Software inventions survive subject-matter-eligibility review when the specification emphasizes *concrete technical improvements*, not abstract business processes. For each subsystem, frame the claim in terms of: (a) what technical problem it solves, (b) what technical mechanism it uses, (c) what measurable improvement results (latency, correctness, privacy, reliability). Avoid marketing language. Examples: "Single-statement insert-or-update-on-expiry semantics gives exactly-once-within-expiry processing of duplicate webhook emissions"; "Eager materialization of scheduled times combined with a covering index reduces dispatch cost from O(N·M) to O(log N)".

---

## Phase 3 — Application Data Sheet

Produce `application-data-sheet.md` mirroring USPTO form PTO/AIA/14 per 37 CFR §1.76. See `references/ads-template.md` for the full section layout.

**Required sections:**

I. Title of invention
II. Application information (type, subject matter, drawing sheet count, entity status)
III. Inventor information (one block per inventor: name, residence, citizenship, mailing address)
IV. Correspondence information (customer number OR full address + email)
V. Domestic benefit / national stage (usually "None" for a first-filed provisional)
VI. Foreign priority information (usually "None")
VII. Applicant information (if separate from inventor — e.g., LLC via assignment under §1.46(b); omit if inventor is applicant under §1.46(a))
VIII. Micro-entity certification (four §1.29(a) conditions, if claimed)
IX. Representative information (patent attorney/agent, if engaged)
X. Assignee information (if assignment executed)
XI. Disclosure chronology (supplemental — not on the USPTO form, but useful as attorney reference)
XII. Signature block

**The ADS is not filed as markdown.** It's a reference for transcribing into Patent Center's interactive form or into the fillable PTO/AIA/14 PDF.

---

## Phase 4 — Drawings (optional but recommended)

Software provisionals can ship text-only — 35 U.S.C. §113 only requires drawings "where necessary for the understanding of the subject matter." A text-only provisional still establishes priority. But drawings broaden what the provisional supports: figures added later to the non-provisional that weren't sketched earlier may not inherit the early priority date.

**Generation approach:** SVG → HTML (one figure per page) → PDF via Chrome headless. Produces USPTO-compliant black-and-white line drawings per 37 CFR §1.84 (black ink on white, 1-inch margins on letter paper, numbered figures).

See `references/drawings-generator.md` for the SVG primitive library and a Python generator template. The script emits one `<svg>` per figure wrapped in letter-sized HTML pages. Chrome headless handles PDF rendering:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
  --print-to-pdf=drawings.pdf file:///absolute/path/to/drawings.html
```

**Typical figure set** (software invention):
- System architecture block diagram
- One flowchart per complex decision pipeline
- Priority-tier or routing resolution (decision tree)
- ER diagram for the core data model
- Timeline for any relative-to-anchor scheduling
- State diagram for each state-machine subsystem (confirmation, channel fallback, circuit breaker)
- Sequence diagram for one or two end-to-end scenarios
- Schema table for each novel persistent entity
- UI views (3–5 primary screens; no more)

Target 15–25 figures for a moderately complex software system.

**Quality note for provisional.** First-draft figures from the Chrome-headless pipeline satisfy USPTO requirements and communicate architecture adequately. For the non-provisional, a patent draftsperson (~$50–150/figure on freelance platforms) polishes line weights, typography, and numbered-reference callouts that tie back to paragraph numbers.

---

## Phase 5 — Filing Checklist

Produce a per-filing checklist covering the following items. Tailor by entity status and applicant type.

**Documents:**
- [ ] Specification PDF finalized
- [ ] ADS data transcribed into Patent Center's interactive form (or PTO/AIA/14 PDF)
- [ ] Drawings PDF prepared
- [ ] PTO/SB/15A (Certification of Micro Entity Status — Gross Income Basis) signed (for micro-entity filings)
- [ ] Inventor-to-LLC assignment executed and recorded *if* filing as entity-applicant

**Patent Center upload:** (patentcenter.uspto.gov)
- All substantive documents go under **Application Part** category:
  - Specification → "Specification"
  - ADS → "Application Data Sheet" (or transcribe directly via Patent Center's interactive form)
  - Drawings → "Drawings-only black and white line drawings"
  - Micro entity cert → "Certification of Micro Entity Status (Gross Income Basis) (SB15A)" — may not appear as an upload option; in that case it's handled as on-screen certification in the fees step

**Fee (2025 figures — verify at filing):**
- Micro entity: $65
- Small entity: $130
- Large entity: $325

**Deadlines:**
- Statutory bar: 12 months from first public disclosure (35 U.S.C. §102(b)(1)(A))
- Internal filing deadline: 1 month before the bar, for attorney review buffer
- Non-provisional filing: within 12 months of provisional filing to claim priority

**Foreign filing:**
- Most non-US jurisdictions apply absolute novelty — prior public disclosure typically forecloses foreign rights
- Canada has a 12-month grace period comparable to US
- Document the foreign-filing decision even if it's "US only"

---

## Filing the Package

The skill outputs are markdown and their derived `.docx` / `.pdf` versions. The user then:

1. Reviews the spec and ADS, resolves any remaining `[FLAG: ...]` placeholders.
2. Optionally sends the package to a patent attorney for §101 / §112(a) review before filing.
3. Uploads to Patent Center as documented in Phase 5.

**Do not file on the user's behalf.** Filing is a legal act; the user (or their attorney) executes it.

---

## Principles

1. **Truth-preserving.** Never fabricate inventor information, applicant details, or prior-art claims. Flag missing data rather than guessing.
2. **Attorney-ready, not attorney-replacing.** Produce drafts at the quality level a patent practitioner can critique and polish, not final-form filings.
3. **Store sensitive content outside the repo.** Default to `~/Documents/patents/<project>/`. Verify there's no leakage into the project's git history.
4. **§101 survival over §112(a) completeness.** A spec that describes the invention exhaustively but fails Alice is worthless. Spend disproportionate care on the "Concrete Technical Improvements" section and on framing each subsystem in technical-improvement language.
5. **Non-limiting aspects are claim optionality.** The more, the better — they're free insurance against narrow later claim construction. Target 60+ aspects for a moderately complex software invention.
6. **Explicit priority chronology.** Always include a priority-date section with the conception date, first public disclosure, statutory bar, and recommended internal deadline. Attorneys care about this first.
7. **Don't automate filing.** The Patent Center upload is a legal act the user (or attorney) must perform. Hand them the checklist; stop there.

---

## Output Conventions

**File naming (under `~/Documents/patents/<project>/`):**

- `provisional-application-draft.md` — specification source
- `provisional-application.docx` — pandoc-generated Word version
- `provisional-application.pdf` — Chrome-headless-rendered PDF (for attorney review and Patent Center upload)
- `application-data-sheet.md` / `.docx` / `.pdf` — ADS reference
- `drawings/generate_drawings.py` — generator script (keep so figures are regeneratable)
- `drawings/drawings.html` — intermediate HTML
- `drawings/drawings.pdf` — final drawing package

**Conversion pipeline:**

```bash
pandoc provisional-application-draft.md -f markdown -t docx --toc --toc-depth=2 \
  --metadata title="Provisional Patent Application" \
  -o provisional-application.docx

# PDF via Chrome headless (letter, 1-inch margin, patent-style CSS)
pandoc provisional-application-draft.md -f markdown -t html5 --standalone --toc --toc-depth=2 \
  -H patent-style.css \
  -o provisional-application.html
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless --disable-gpu --no-pdf-header-footer --print-to-pdf-no-header \
  --print-to-pdf=provisional-application.pdf \
  file://$PWD/provisional-application.html
```

See `references/pdf-css.md` for the patent-style CSS.

---

## Lazy-Loaded References

| Reference | Load when |
|---|---|
| `references/specification-template.md` | Drafting Phase 2 — full section layout with §101-framed language and example subsystem descriptions |
| `references/ads-template.md` | Drafting Phase 3 — PTO/AIA/14-equivalent structure with all 12 sections and illustrative content |
| `references/drawings-generator.md` | Phase 4 drawing generation — SVG primitive library, HTML envelope, Chrome-headless invocation |
| `references/pdf-css.md` | Phase 2 / Phase 4 PDF rendering — patent-style CSS (Helvetica body, Menlo code, page-break rules, letter-size) |

Load only when the phase requires it; drop after use.

---

## Failure Modes

| Situation | Handling |
|---|---|
| Inventor asks for claim drafting | Route to patent attorney — this skill produces specifications and non-limiting aspects, not claims |
| First-disclosure date is past the 12-month bar | Flag prominently; filing after the bar forfeits US rights. Foreign rights likely already foreclosed too. Still offer to draft, but the user needs to know the priority is lost |
| Inventor wants to file under an LLC but has no assignment | Default to pro-se filing; note the LLC can take ownership via supplemental ADS and §3.73(c) statement before the non-provisional |
| Inventor has public GitHub repo that may constitute disclosure | Check the repo's public-since date; if before the intended filing, add it to the disclosure chronology |
| Chrome headless unavailable | Fall back to weasyprint or suggest an online markdown-to-PDF converter; do not block the drafting |
| Codebase exploration finds trivial architecture (e.g., a CRUD app with no novel mechanism) | Flag to the user — there may not be patentable subject matter. Still offer to draft, but note that Alice is likely to reject |
| User provides an email with all-caps or obviously test data | Ask to confirm before including in a USPTO-destined document |
