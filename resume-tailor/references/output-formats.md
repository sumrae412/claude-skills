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

URL collection is a Phase 5 input-validation step that runs before any file write. `jd.md` is written as part of the Phase 5 output set once the URL is in hand — the same step that writes the resume and cover letter, not after.

**Format:**

```markdown
# <Title> — <Company>

**Source:** <URL>
**Captured:** YYYY-MM-DD
**Outcome:** <optional — `submitted` / `screen` / `interview` / `offer` / `rejected` / `withdrawn`, with date>

---

<full JD text as pasted>
```

**`Outcome:` field (optional, append over time):** when an application gets a human-contact signal (recruiter screen, hiring-manager intro, interview invite, offer, rejection after a real conversation), append a line to the `Outcome:` field with the new status and date. Example:

```markdown
**Outcome:**
- 2026-04-30 submitted
- 2026-05-12 screen invite (recruiter: Maria K.)
- 2026-05-19 first round
- 2026-05-26 rejected after panel
```

The outcome trail makes the per-company folder a forensic record — what was the role, what was the pitch, did it land, and when. It also feeds the voice-corpus promotion trigger (see `references/voice-corpus.md` §"Promotion Trigger") and lets future tailoring sessions weight the candidate's fit-pattern data with real outcomes instead of just self-assessed scores.

**Promotion-only fields (do not pre-populate):** the `Outcome:` field stays absent until something happens. Pre-populating with `submitted` on every save adds noise without signal.

**Recommended fetcher for LinkedIn URLs:** prefer the repo-local `jd-prep` CLI (`tools/jd-prep/jd_prep.py <url>`). It hits LinkedIn's unauthenticated guest endpoint, extracts structured metadata + deduplicated body, and writes `~/Documents/resumes/<Company>/jd.md` directly — satisfying this section's URL-retention rule in one step. Generic web fetch on LinkedIn job pages typically returns auth-walled content. For invocation details, read [tools/jd-prep/README.md](/Users/summerrae/claude_code/claude-skills/tools/jd-prep/README.md).

**Input-handling rules (Phase 5 input validation, before any file write):**

- If the user pastes JD text only (no URL): ask for the URL first. Do not silently write `jd.md` without the source.
- If the user pastes a LinkedIn URL: run `tools/jd-prep/jd_prep.py` first. If it fails, ask the user to paste the text, then save both URL and pasted text.
- If the user pastes a non-LinkedIn URL and the host's web fetch tool works (HTTP 200, non-empty body): save the fetched text in `jd.md` with the URL at top.
- If the user pastes a non-LinkedIn URL and fetch fails (non-200, timeout, empty, or JS-rendered page): ask the user to paste the text, then save both URL and pasted text.

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

**Skills section by seniority:** for executive-targeted resumes, `# SKILLS` should not read like a flat tool dump. Group it by strategic scope first and tools last. Prefer categories such as strategy/systems, production/governance, technical depth (working knowledge), and leadership. The more senior the target role, the less space should go to raw tool enumeration and the more space should go to decision authority, governance, and cross-functional scope.

**Experience bullets by seniority:** for executive-targeted resumes, the bullets should not stop at shipped work. Surface the decision, tradeoff, governance move, failure mode, or leverage mechanism that proves executive judgment. Load `references/executive-bullets.md` when rewriting them.

**Resume bullet bans:** before finalizing any role, load `references/resume-bullet-bans.md` and remove low-signal openers, vague verbs, and tool-pile bullets that down-level the resume.

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

Load `references/writing-quality.md` before drafting. The audit trail can be structured; the letter itself cannot read like a structured report.

- **Audience-centered paragraph openers.** Every body paragraph (P2, P3, P4) must open with the company's need, role pillar, or stated ask — NOT with the candidate's credential. "I did X at Y" openers produce letters that read as a tour of accomplishments instead of a map of fit. Acceptable opener shapes: *"[Role pillar] is [description]. My version of that is…"*, *"[Company-stated challenge]. The closest thing I've shipped is…"*, *"[JD domain] rewards [capability]. At [employer] I [credit]."* P1 may open with candidate positioning, but P2/P3/P4 may not. Also load `shared/communication-principles.md` and `references/cover-letter-review.md` before drafting.
- **Anti-bragging moves on every body paragraph.** When confidence tips into boasting, shift focus toward the work, the team, or the concrete evidence. Use "we" for collective wins when that is the truthful register. Cut editorializing that merely announces importance instead of showing it. See `references/cover-letter-review.md`.
- **No comparative put-downs on other candidates.** Never imply other applicants fall short. Ban: *"not just technical depth"*, *"unlike most candidates"*, *"where others stop, I…"*, *"most teams can't, but I…"*. Describe what the work requires without naming a comparison group. See `references/cover-letter-review.md`.
- **Length:** 250–350 words total.
- **Greeting:** always `Dear Hiring Manager,` unless the user names a specific recipient.
- **Closing:** always `Regards,` followed by the user's name on the next line.
- **Punctuation:** use hyphens only. NO em dashes, NO en dashes — they read as AI-generated.
- **Voice:** sound like a real human wrote it. Plain language. Avoid "thrilled," "passionate," "synergy," "leverage," and other filler. No stacks of adjectives.
- **No sentence-level list writing.** Do not stack three abstract strengths in a row ("strategy, execution, and leadership"). Each paragraph needs a governing idea and one concrete detail that proves it.
- **"various forms" not "in different forms"** — small Summer vocabulary preference (QuillBot 2026-05-03).
- **Truth-preserving:** never fabricate or exaggerate. Every claim must be defensible from the resume or the user's stated experience. Same rule as Phase 2 reframes.
- **Substance:** connect 2–3 specific, measurable achievements from the resume to the employer's stated needs. Not a resume rehash — a targeted bridge between what they need and what the user has done.

### Pre-drafting: map JD to evidence

Before drafting any paragraph, build a two-column map:

- **Left column** — top 3–5 responsibilities or must-haves from the JD, in the JD's own wording.
- **Right column** — one specific achievement from the resume or Phase 2 inventory that directly addresses each.

Pick the two strongest matches for P2 and P3. If fewer than two strong matches exist, the candidate is mis-fit for this role — re-scope before drafting (lower the application's priority, or widen what the user is willing to reframe). Drafting a bridge on a weak match produces the "sounds relevant but leaves no evidence" failure mode called out in the Bridge Shape section.

Diversify the two picks by interview theme — leadership, initiative, execution-under-constraint, problem-solving, cross-functional collaboration, frontier-learning. Two bridges on the same theme (e.g. both "scaled a team") signal narrow range; two on different themes show breadth. If the resume only supports one strong theme, use the single strongest bridge and let P3 carry the company-specific hook instead of forcing a second thin bridge.

### Structure

Roughly 3–4 short paragraphs:

- Paragraph 1 (the hook): one or two sentences on why this role and why now. No preamble, no self-introduction beyond what's functionally necessary. **P1 is positioning, not evidence.** State why the role lands and what the user does about it — do not stack credentials ("fifteen years / past year / worked with X"). Credentials belong in P2/P3 bridges. Keep P1 tight enough that it works as a standalone hook; dumping evidence into it crowds out the reason the reader should keep reading. **Canonical P1 opener template**: *"I was excited to see you post the [ROLE TITLE] role because [thing the candidate has spent the last few years doing that matches]. [One sentence showing how — typically: At [employer] I [did the specific thing]]."* Direct to reader ("you post"), past-tense owned, immediate HOW. This is the default shape for Summer; deviate only with a specific reason. Validate the opener against `references/cover-letter-review.md`. **P1 alternative — "transition you're making" shape (use when JD signals an org pivot or strategic transition):** *"I was excited to see the [ROLE] at [COMPANY]. The shift you're making — [their stated transition] — is exactly the kind of transition I've led across multiple AI organizations: [synthesis line naming the through-line capability]."* Use when the JD foregrounds a strategic pivot (research → product, prototype → production, internal tools → platform). Validated on QuillBot 2026-05-03.
- Paragraph 2 (the strongest bridge): **name the hiring team's actual pain point** — the problem they are trying to solve by filling this role — then show specific evidence of having solved that exact problem, then close with why this makes the candidate a fit. Do NOT open P2 with abstract reframings like *"X is a particular shape of work"*, *"X is the kind of work that asks for Y"*, *"X is a specific pattern"* — these read as AI hedging, not commitment to a named problem. **Demand-then-match, not bald "you need X, I did X".** The you-need/I-did cadence is analytically correct but reads mechanically when the surface language is literal. Keep the logic, reframe the demand as *what the work actually requires* rather than *what you need from a candidate*. Bald version: *"You need someone who can architect enterprise GenAI and ship it. I did that at Govini."* Eloquent version: *"Enterprise GenAI, in my experience, is less about any single component and more about owning every layer under real constraints. At Govini, that's what the work looked like."* Pain-point patterns: *"Most enterprise AI teams can prototype but can't ship…"* (for production-focused JDs), *"Governance inside AI orgs usually shows up too late…"* (for responsible-AI-focused JDs), *"Most platforms survive the first team but can't carry the second…"* (for reusable-framework JDs). Validate the bridge against `references/cover-letter-review.md`.
- Paragraph 3 (the second bridge, optional): second pain or distinctive-asset bridge. Same pain-point-first move as P2, different pillar of the JD. Often the place to land Summer's differentiator (claude_flow, CourierFlow, publications) with a regulated-production grounding credit as the closer. Alternatively — if the user has a gap/pivot/short tenure to address (per Phase 4 gap plan), use this paragraph for that instead.
- Paragraph 4 (the close): one of three shapes, depending on what the user has to work with.
  - **Tie-it-together through-line** (Summer's preferred default when the letter has multiple credentials). Distill the career arc into 3 capabilities that sum up P2 and P3 in one sentence, then deliver a service-framed fit statement (*"That's the combination I'd bring to help [Company] [specific thing they need]"*), then the domain hook if you have one, then soft close. Example from the Builders Capital Exchange letter: *"For more than a decade, I've been building production AI that ships under enterprise constraints, translated for the stakeholders who fund it, and turned into frameworks that outlast any single project. That's the combination I'd bring to help Builders Capital Exchange ship AI that scales across your loan workflows and holds up in production. And because I run a small real-estate investment firm on the side, construction finance isn't abstract to me. I'd welcome the chance to discuss how I can help."* The distilled through-line reads as summary, not as brag, because it's abstracted rather than enumerated. Validate the closing against `references/cover-letter-review.md`.
  - **Company-specific hook** — one concrete, non-generic thing that draws the user to this firm. Not "your mission." Not "your culture." Something the user has actually noticed about the firm, the product, or the role (requires verification from a primary source the user provided or the host can fetch).
  - **Role-need mapping** — name the full shape of the work abstractly (e.g. "vision, execution, governance, adoption"), then map each pillar to a concrete candidate credit. Describes the *kind* of role this is, not the hiring team's stated ask. Use when the user can't produce a verified company-specific hook or when the JD's scope itself is the strongest through-line.
  - **Personal-stake close (healthcare/biopharma roles, only when P1 has NOT already named the medical arc)** — *"Most of my career has been in medical and biotech research — [employer arc]. Healthcare is where I started and where the work has always meant the most."* Validated on Equip 2026-05-03. Do NOT use when P1 already names biotech/HIPAA/drug-target — would duplicate.
  - **Single-sentence P4 close (when P2/P3 are evidence-dense)** — compress P4 to one line: domain-fit + soft close, no body. Pattern: *"[Company] sits at exactly the intersection of [domain A] and [domain B] I'd most want to bring this skillset to, and I'd welcome the opportunity to discuss how I can help."* Validated on SynerG 2026-05-03. Don't use when P2/P3 are thin — P4 then needs to carry real load via the tie-it-together shape.
  - **P4 redundancy rule:** if P1 has already named the domain arc (e.g. "biotech research and drug-target discovery", "HIPAA-regulated production ML"), P4 must NOT re-list the same employer parade as evidence — that's repetition, not synthesis. Use either the **publications-as-evidence** substitute (peer-reviewed papers — medRxiv, PNAS — instead of employer enumeration) or the single-sentence close above.
  - All shapes close with a soft offer to talk. Avoid "I would love the opportunity" filler — shorter is better. *"I'd welcome the chance to discuss how I can help"* is the canonical default.

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

- Load `references/cover-letter-review.md` before drafting or revising. It is the local source for opener tests, anti-patterns, and final review passes.
- **P1 comparative framing** ("rare to find a posting that asks for both") — rewrite to positive-personal ("I was excited to see…"). The hiring team is not the audience for market critique.
- **P1 credential stacking.** P1 sentences stuffed with years, employer names, and stakeholder names ("fifteen years running AI functions for C-suite stakeholders, plus the past year working with Andrew Ng's team") are a P1 failure even when each fact is true. P1 positions; P2/P3 prove. If the hook paragraph carries numbers and named employers, cut them out and push them into the bridge paragraphs where they earn their keep.
- **Aspirational-future framing in P1.** Phrases like "the blend I've been building toward", "the direction I've been working toward", "where I'm heading" read as LLM-generated and weaken owned claims. Prefer completed past tense: "this is exactly where I've spent the last few years" over "the blend I've been building toward." The user has done the thing — say so.
- **Abstracted-away-from-the-posting language.** "A role asking for…" is one step removed; "your role posted for…" / "your posting for…" / "the X role you're hiring for" speaks directly to the reader. Keep P1 second-person-adjacent, not third-person about.
- **Generic nouns where the user has distinctive ones.** "Combination", "intersection", "blend" are invisible; if the user offered a more specific word ("dual-modality", "two-track", "executive-plus-hands-on"), keep it. Don't smooth distinctive vocabulary into interchangeable filler.
- **Any sentence restating the JD back at the reader** ("The JD emphasizes…", "Your posting highlights…", "As described in the role…"). They wrote it; answer the ask instead.
- **Company-specific claims in P4 without verification** — do not infer the company's focus, methodology, or segment from the JD alone. Verify from the company's own site or another primary source the user provided before naming anything specific. If the claim can't be verified, keep P4 generic or drop it.
- **P4 self-focused openers** ("What excites me about working at…", "What drew me to…", "What I'd love about…"). These center the applicant's feelings, not the applicant's match to the role. Flip to audience-centered: lead with the role need (stated abstractly, not as a JD quote) then the candidate's evidence that answers it. Example: *"The full stack of enterprise agentic AI delivery — vision, execution, governance, adoption — is the work I've been running for years. At Govini…"* maps each JD pillar to a concrete credit without saying "your role calls for X." Describes the shape of the work, not the hiring team's stated ask.
- **Dead-weight openers.** "My name is X and I am writing to apply for Y" carries zero information — the reader already has both facts from the application metadata. Open with a specific result, a direct role-to-work map, or a named referral, not a self-introduction.
- **Stacked-noun "what pulled me to apply" hooks.** Sentences of the form *"A [noun phrase], a [noun phrase], and the [expectation/framing] are what pulled me to apply / drew me in"* read as LLM-generated even when every noun is accurate to the JD. Banned at both P1 and P4. If P1's first sentence already positions the fit, do NOT add a second sentence enumerating JD features that caught the candidate's eye.
- **Generic company praise without evidence.** "I've long admired your culture / mission / innovative products" with nothing concrete behind it reads as filler. Either name a specific product, decision, hire, or piece of public writing the candidate actually noticed, or drop the praise. Same verification rule as the P4 company-specific-claim anti-pattern applies.
- **Clichés.** "I am a hard worker," "I think outside the box," "I am a team player," "I am detail-oriented," "I consistently go above and beyond," "results-driven," "dynamic." These occupy space without adding signal. If a claim is true, it will show up in an achievement; if it can only be asserted, cut it.
- **Resume paragraphs.** Rewriting resume bullets into prose does not add information — it removes density. The cover letter's job is context the resume can't carry: why this role, which specific achievements map to which JD needs, what the candidate's distinctive angle is. If a paragraph could be rewritten as resume bullets without loss, it's the wrong content for a letter.
- **One-letter-fits-all.** Swapping only the company name between applications produces detectably generic letters. At minimum, P4 must be specific to the target company; ideally P2 and P3 pick different achievements per JD based on that JD's top needs, not a single "strongest" set that ships everywhere.
- **Wrong length.** Under 200 words reads as effort-minimized. Over 400 rarely gets read end-to-end. The 250–350 target is the band where the reader absorbs the whole thing.
- **"Shape of work" / "kind of work" / "pattern of work" abstractions in bridge openers.** Constructions like *"X is a particular shape of work"*, *"Y is the kind of work that asks for Z"*, *"Z is a specific pattern"* sound profound but commit to naming no actual problem. Replace with a named pain point. See `references/cover-letter-review.md`.
- **Bald "You need X. I did X" mechanical cadence.** The underlying demand-then-match logic is right, but the surface language *"You need someone who can architect enterprise GenAI. I did that at Govini."* reads as mechanical. Rewrite so the demand is described as a feature of the work, not as an instruction to the reader. See `references/cover-letter-review.md`.
- **Comparative put-downs on other candidates.** Any phrasing that implies other applicants fall short — *"not just technical depth"*, *"unlike most candidates"*, *"where others stop, I…"*, *"most teams can't, but I have"* — is banned. Elevation-of-self via demotion-of-others is candidate-focused writing in disguise. Describe what the work requires without naming a comparison group. See `references/cover-letter-review.md`.
- **Restating the JD or quoting it back.** *"Your JD emphasizes X"* / *"The role you describe asks for Y"* / *"Exactly the kind of work this role describes"* / *"Directly addresses the reusable-orchestration ask in this JD"* — all variants of restating the JD back at the reader. They wrote it; answer the ask instead. See `references/cover-letter-review.md`.

### Closing variants

The sign-off (`Regards,`) is fixed. The sentence immediately before it has three acceptable shapes — pick one based on what the candidate can actually back up:

- **Soft offer to talk** (default): *"I'd welcome the chance to talk."* Short, direct, no presumption. Pairs with any P4 shape. Safest choice when no specific next-step context exists.
- **Specific ask**: *"I'd welcome 30 minutes to walk through how the Govini RAG stack maps to your use cases."* Named specificity signals preparation — but only use when the candidate can back up the specificity in the actual call. Generic-specificity ("discuss the role in detail") is worse than the soft offer.
- **Follow-up promise**: *"I'll plan to follow up next week."* Signals initiative but commits the candidate to actually following up. Use sparingly and only when the candidate will do it — unfollowed-up promises damage the next touch.

Avoid: "Thank you for your consideration" as a standalone closer (filler unless paired with a next-step ask); "I look forward to hearing from you" (passive, no ask); "I would love the opportunity" (already banned in Hard Rules filler list).

### Process

Draft in the user's voice using Phase 1 culture signals and Phase 4 narrative arc. Walk the user through **paragraph by paragraph** before writing to a file. Cover letters are more voice-sensitive than resumes — get explicit sign-off on each paragraph.

After each draft, run a prose pass:

- Cut any sentence that could apply to a different company unchanged.
- Replace abstract noun piles with one concrete capability or outcome.
- Vary sentence length so the letter does not thump forward in identical beats.
- Read the first clause of each sentence; if three in a row sound interchangeable, rewrite.

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

Before the final confirmation, load `references/resume-qa.md` and run its section-level, role-level, and document-level checks. If the summary is weaker than the first bullet, cut it. If the skills section is more specific than the experience section, strengthen the experience section before exporting.

## 4. Format Conversion (Optional)

- **DOCX:** use pandoc with `--reference-doc=` pointing at the appropriate template in `templates/` — this inherits the user's fonts, margins, and heading styles on every render. See `templates/README.md` for the exact command. If `pandoc` is unavailable, deliver reviewed markdown and stop there unless the user requests a different conversion path you can actually verify.
- **DOCX via `/tmp/` script:** if generating with a standalone node script that imports `docx-js`, the module is often installed globally. Wrap the call: `NODE_PATH="$(npm root -g)" node /tmp/generate_resume_docx.js`. Without `NODE_PATH`, node can't resolve global packages from scripts outside an npm project and fails with `Cannot find module 'docx'`.
- **PDF:** convert from DOCX (Word, Pages, LibreOffice) OR render markdown via pandoc. Avoid PDF as primary source — ATS parses PDF unreliably. Submit DOCX when allowed; PDF only when required.
- **Plain text:** for pasting into LinkedIn or ATS forms, generate a plain-text version stripped of markdown syntax.

Never offer HTML, LaTeX, or heavily-designed templates as default. They fail ATS parsers.

## ATS Tips

- Keywords must appear **in the bullet prose**, not just in a skills list. ATS-modern scanners weight context, not keyword density.
- **Avoid Unicode glyphs in the resume body.** Arrows (`→`, `⇒`), em-dashes in keyword positions, bullet-point characters, and fancy quotes can fail older ATS parsers and cause keyword mismatches. Write `0 to 1` instead of `0→1`, `A to B` instead of `A→B`, regular hyphens instead of en/em-dashes in keyword-adjacent positions. Reserve Unicode for the coverage report (internal, not parsed by ATS).
- **Decode HTML entities when ingesting source resumes from `.txt` exports or pasted content.** Tools that export resumes via HTML-aware paths can leave entities like `R&amp;D`, `P&amp;L`, `&nbsp;`, `&#39;` in the text. These break ATS keyword matching (`R&amp;D` does not match `R&D`) and look broken to human reviewers. Run a decode pass on any pasted source before treating it as ground truth: `python3 -c "import html,sys; print(html.unescape(sys.stdin.read()))" < source.txt`. Common entities to scan for: `&amp;`, `&nbsp;`, `&#39;`, `&quot;`, `&lt;`, `&gt;`.
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
