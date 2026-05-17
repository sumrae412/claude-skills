# Cover Letter Review

Local review reference for Phase 5 cover-letter drafting. Load this file before drafting or revising a cover letter so the review rules live inside the `resume-tailor` skill instead of in host memory.

## 0. Input Sources — where voice templates come from

Before drafting, load these in order:

1. **The candidate's canonical structural example** — `~/Documents/resumes/Summer_Rae_CoverLetter.md`. Always load. This is the endorsed paragraph shape, cadence, and voice baseline.
2. **The annotated structural template** — `references/templates/cover-letter-structural-template.md`. Always load alongside the baseline. Captures the 4-paragraph hook → bridge → operational-evidence → close pattern as a skeleton with per-paragraph rules and two paired shapes (Shape A — operational-fit / Shape B — career-arc). The shape pair is selected from the JD signal at draft-start and carried through P1 → P2 → P4.
3. **Voice corpus** — `~/Documents/resumes/_voice-corpus/{originals,successful}/`. Proven-by-interview letters that supplement the baseline when available.

Do NOT read prior letters from per-company folders (`~/Documents/resumes/<company>/cover-letter.md`) as voice templates. Those letters either failed, are in flight, or were endorsed in-session without an interview signal, and pulling voice from them compounds AI cadence over time.

If the voice corpus is empty, that is fine — the canonical baseline (1) is sufficient. See `references/voice-corpus.md` §Bootstrap for how to populate the corpus from interview-signal letters going forward.

## A. Philosophy and Posture

A cover letter is a professional introduction, not a sales pitch or highlight reel. It works when the reader thinks *"I'd like to talk to this person"* — because they sense genuine alignment, not because they were overwhelmed with achievements.

**The goal:** make the reader want to read the resume, not redundantly summarize it. Leave them wanting more.

### Tone

- Lead with **their situation**, not the candidate's accomplishments. Open on what the company is actually trying to solve.
- Connect experience conversationally. *"Your challenge with X reminds me of..."* beats *"I achieved X."*
- Write like a peer-to-peer note, not a pitch deck to investors.
- Confident, not boastful. Let the evidence speak; resist the urge to interpret it for the reader.

### Length and density

- **Aim for ~350 words. Hard limit 400 words.** 3-4 paragraphs.
- Every sentence must add value. If a sentence does not move the reader closer to *"I'd like to talk to this person,"* cut it.
- If a draft lands between 350 and 400, do a tightening pass before shipping — don't ship at the ceiling by default.

### Sentence subjects

- Vary sentence subjects. Most sentences should NOT start with "I" — resume cadence is the failure mode this catches.
- P1 may open with the canonical "I was excited to see..." but subsequent sentences in P1 and all of P2-P4 should rotate subjects (the company, the work, the dataset, the problem, the result, the lesson).
- Diagnostic: if 3+ consecutive sentences in any paragraph start with "I", rewrite.

### Interview defensibility

Every line of the cover letter must be something the candidate can speak to fluently in the interview, without prep. If a phrase, claim, framing, or anecdote would require the candidate to remember *"wait, what did the letter say about that?"* — cut it or rewrite it in language the candidate would naturally use.

The letter is a promissory note redeemed in person. Nothing on it should embarrass the candidate when read aloud back to them by the interviewer. Apply this test in §6 alongside the smart-friend and hiring-manager passes.

## B. Salary Question Handling

When the JD or application asks for salary requirements in the cover letter, handle it in the closing paragraph — never lead with it, never volunteer it unprompted. Two scenarios:

**Scenario 1 — Asked, but no specific range required.** Deflect with negotiable language:

- *"My salary requirements are negotiable based on the responsibilities of the position and the total compensation package."*
- *"I am open to discussing salary as part of the overall compensation package."*

**Scenario 2 — Specific range required.** Do NOT skip the question — failing to address a required field is a screen-out. Research comps first (Levels.fyi, Glassdoor, Ladders, public filings for executive roles) based on title, location, and seniority. Then give a range with flex language attached:

- *"Based on my level of experience and research of comparable roles, my salary requirements are in the [low]–[high] range, with flexibility based on the overall compensation package."*

Rules:

- Always a range, never a single number — single numbers cap your ceiling for free.
- Never anchor below your researched market floor — anchoring low costs real money in negotiation.
- Never apologize for the range ("I realize this is on the higher end..." kills your own anchor).
- If the JD does NOT ask for salary, do not address it in the letter at all. Volunteering a number unprompted is an unforced negotiation loss.

## 1. Opening Rule

Paragraphs 2-4 must open with the company's need, the role's actual work, or a concrete pain point. Do not open those paragraphs with the candidate's credential.

- Good: "Enterprise AI delivery breaks when orchestration, governance, and adoption are owned separately. At Govini, I led..."
- Weak: "I led enterprise AI delivery at Govini..."

Paragraph 1 may open with candidate positioning, but it still needs to speak directly to the role rather than drift into biography.

## 1a. Seniority Alignment

When the JD's seniority signals sit below the candidate's level (per the YOE cutoff in `references/jd-analysis.md` §"YOE Cutoff" or an explicit titles delta — e.g. Senior IC applying for IC, Director applying for Senior, VP applying for Director), the letter must address **why this specific role** directly. Two failure modes to avoid:

- **Apologizing for the seniority.** Phrases like "even though I have more experience than the listing requires" or "I am happy to take on a hands-on individual contributor role" telegraph anxiety and invite the rejection.
- **Dancing around it.** Pretending the gap isn't visible. The hiring manager already noticed during resume screening; not naming it makes the letter feel evasive.

The clean move: in P3 or P4, name one concrete reason this specific role (not just any role at this level) is a forward step — the domain, the bet, the team, the problem. One sentence. Confident, not defensive. Example: *"This role is a step toward [specific thing the role enables that the candidate wants], which is why a Director title is the right fit even though my last seat was VP."*

## 2. P1 Shape

Use a short hook:

1. Why this role lands.
2. Why the candidate is already doing this kind of work.

Default shape:

```text
I was excited to see you post the [ROLE TITLE] role because [fit statement].
At [employer], I [specific evidence].
```

Avoid:

- Self-introductions like "My name is..."
- Credential stacks in the opener
- Future-tense aspiration language like "the blend I've been building toward"
- Restating the JD back to the reader
- Templated form-letter openers like "I am applying for the [Role] position at [Company]"
- Stacked-noun personal-brand hooks like "As a passionate [X] with a proven track record..."
- Meta-narration about where the listing was found ("I saw your post on LinkedIn", "In response to your job posting on Indeed", "I came across your opening on...") — wastes the first line on information the reader already has

### Hook Variant Brainstorm (when the default feels flat)

If the standard `I was excited to see you post the [ROLE] role because [fit statement]` opener reads generic against this particular JD, brainstorm 3 alternate hooks before committing:

1. **Recent company moment** — a verifiable product launch, public statement, leadership move, or research output. Subject to §4: never invent the moment.
2. **Stated value alignment** — quote one company value or mission line, then immediately ground it in a specific instance from the candidate's record. Skip if the only available connection is generic praise.
3. **Concrete result** — open with a specific outcome the candidate has delivered that maps to the role's primary bet. This is the default shape.

Cap each variant at ~40 words. Pick the one with the strongest evidence behind it, not the cleverest phrasing.

## 3. Bridge Paragraph Test (CAR shape)

For paragraphs 2 and 3, use the **Challenge → Action → Result** shape:

1. **Challenge.** Name the actual problem or capability the role exists to handle.
2. **Action.** Show one concrete thing the candidate did that addresses it.
3. **Result.** Close with the published outcome, named client, scale, or transfer logic.

The Result step requires something concrete: a publication, a system in production, a named user/client, a team size, a measurable change. Generic "led successful initiatives" is not a Result — it is a vague Action.

Do not use abstract filler such as "this is a particular shape of work" or bald "you need X, I did X" cadence.

## 3a. JD Vocabulary Echo

Do not echo the JD's distinctive vocabulary back at the reader verbatim. Lifting the JD's exact phrasing into the letter signals pattern-matching, not understanding — and reads as AI-generated even when the surrounding paragraph is solid.

**Diagnostic:** if a noun phrase or verb construction in the letter is more than 3 consecutive words from the JD, rewrite it. Single shared keywords (e.g. "RAG", "agentic", "GxP") are fine and ATS-helpful; multi-word phrasings are not.

**Replacement strategy — describe the work, don't quote the listing:**

| JD says | Letter should NOT say | Letter SHOULD say |
|---------|----------------------|-------------------|
| "drive cross-functional alignment" | "I drive cross-functional alignment…" | "At Govini, getting eng, product, and policy on the same plan was the actual job." |
| "own the agentic platform roadmap end-to-end" | "I would own the agentic platform roadmap end-to-end" | "I've been running an agentic platform from research through production for the last year." |
| "translate ambiguous business needs into ML systems" | "I translate ambiguous business needs into ML systems" | "Most of what I've shipped started as a vague exec ask and ended as a system in prod." |

The rule is *demonstrate you understand the work, not that you read the listing*. JD vocabulary echo is a special case of the §1 opening rule and the §5 "JD restatement" anti-pattern — it can pass both surface checks while still violating the spirit.

## 4. Company-Specific Claims

Do not claim a specific company priority, product, customer segment, or operating model unless it is verified from the company's own site or another primary source the user provided.

If verification is unavailable:

- keep the paragraph role-specific rather than company-specific, or
- drop the claim.

Generic praise without evidence is filler and should be cut.

## 5. Anti-Patterns

Reject the draft if it contains any of these:

- Candidate-focused paragraph openers in P2-P4
- Comparative put-downs of other candidates
- JD restatement phrases like "your JD emphasizes"
- Resume bullets rewritten as prose with no added context
- Hollow company praise
- Cliches like "hard worker", "team player", "passionate about", "hit the ground running", "results-driven"
- Generic-excitement openers like "I am thrilled to apply...", "I am honored to submit...", "It would be a privilege to..."
- Puffery framings like "I am confident I would be an asset to your team" — these tell the reader what to conclude instead of letting the evidence do the work
- Unsupported superlatives ("master of X", "expert in Y", "superior leadership skills") — claims without a credential, publication, named user, or measurable outcome behind them read as bragging, not confidence
- Bulleted achievement lists inside body paragraphs (cover-letter bodies are prose; bullets belong in the resume)
- Resume-cadence stacking — 3+ consecutive sentences starting with "I" inside one paragraph (see §A Sentence subjects)
- Passive closing lines: "I look forward to hearing from you", "Please feel free to contact me at your convenience", "Thank you for considering my application" as the standalone final sentence. The close must be active and specific — name what you'd talk about, not what you hope happens.
- Em dashes or en dashes

### 5a. LLM-era buzzwords and AI-influencer cadence

Hiring managers in 2024-2026 are increasingly skeptical of bare AI-industry vocabulary used without operational substance. The following phrases read as AI-influencer cosplay even when the candidate's underlying experience is real. Reject if any appear without a concrete operational artifact attached in the same sentence:

- **Bare "frontier AI" / "frontier LLM" / "frontier models"** — must be followed by a specific named system, evaluation framework, shipped artifact, or paper. *"working alongside X on frontier LLM research"* is bare; *"working alongside X on the LLM evaluation framework that gated [named system]'s release"* is anchored.
- **Bare "agentic AI" / "agentic systems" / "agentic workflows"** — must be followed by a named project, governance mechanism, or production constraint. *"agentic-AI research"* is bare; *"agentic orchestration with contract-based handoffs and phase gates that keep multi-agent pipelines reproducible"* is anchored.
- **"next-gen" / "cutting-edge" / "state-of-the-art"** without a named system or benchmark — always cut.
- **"bets I want to be running" / "the bets that matter" / "the right bets"** — startup-founder cosplay. Closes that frame the role as a portfolio of bets read as performative rather than operational. Close on what would be discussed or built, not on betting language.
- **Prestige stacking** — naming 3+ proper nouns (employers, publications, advisors, institutions) inside a single paragraph with no operational through-line. Prestige density asks the reader to *infer* importance; senior writing *demonstrates* it. If a paragraph has more than 2 proper-noun credentials, rewrite so each credential is doing one specific operational job.
- **"the kind of work I have been doing"** / **"exactly the kind of"** / **"this is the work I want to be doing"** — vague affinity claims without naming the work. Replace with the specific operational dimension that maps to the JD.

### 5b. Resume narration in P1

P1 must not be a chronological employer montage. The *"At X, I did Y. Before that, at Z, I did W. Earlier, at V, I first..."* cadence is the strongest single signal that a letter is a resume-in-paragraphs rather than a positioning document. Specific bans for P1:

- More than ONE prior employer named with active-verb evidence before P1 turns to the company's bet.
- The connective tissue *"Before that…"* / *"Earlier…"* / *"Prior to that…"* used inside P1 to chain employers.
- Three or more sentences in P1 whose primary subject is the candidate or a candidate-employer.

P1 may name one employer with one evidence clause when that employer is the strongest single fit signal. Multi-employer evidence belongs in P3 (operational evidence), where it is relevance-ordered — not chronologically chained.

## 6. Final Review Pass

Before sign-off, run BOTH a set of mechanical pre-ship checks (§6.1) AND a hiring-manager perspective review (§6.2). The mechanical checks produce printed evidence — they are not optional vibe-checks. The perspective review runs in a fresh subagent context so it isn't biased by the drafter's own rationalization.

### 6.1. Mechanical pre-ship checks (printed evidence required)

Each check below must produce a one-line printed output. If any check fails, fix the draft and re-run before continuing to §6.2.

**Check 1 — Sentence-subject sequence per paragraph.** For each of P1-P4, print the sequence of sentence subjects as a single line, e.g. *"P1: [company-bet] → [I] → [I] → [I] → [company]"*. Fail conditions:

- Any paragraph has 3+ consecutive sentences whose subject is "I" or "my [employer]" / "my [project]".
- P1 ends on a candidate-subject sentence rather than a company-subject sentence.
- P2-P4 open with "I" as the first-sentence subject.

If any fail condition triggers, the diagnostic itself names the violating paragraph — rewrite that paragraph and re-run the sequence check.

**Check 2 — Proper-noun cross-check.** List every proper noun in the letter and cross-check against the JD and the resume. Catches (a) stale company/role/person names accidentally carried over from another letter, and (b) fresh typos in this letter — recipient firm name, hiring manager's name, the candidate's current employer. Both are interview-killers and resume-screen rejections. (One published experiment had the author address "WXY Architects" when applying to XYZ Architects, and name XYZ as his current employer when it was the role he was applying for — caught only by outside reviewers.)

**Check 3 — Prestige-density count per paragraph.** Count proper-noun credentials (employers, publications, advisors, institutions) in each paragraph. Fail condition: any paragraph has 3+. Per §5a, prestige stacking asks the reader to infer importance instead of demonstrating it. If a paragraph fails, redistribute credentials or cut.

**Check 4 — Hiring-risk anchor presence in P1.** Locate the P1 clause that grounds in the Phase 1 hiring-risk sentence (per `references/templates/cover-letter-structural-template.md` §P1). Print: *"Hiring-risk anchor in P1: [QUOTE the clause]"*. Fail condition: no clause in P1 can be traced to the hiring-risk sentence — the letter is orbiting a generic "AI leadership" frame rather than this role's actual hardest problem.

**Check 5 — Structural diff against canonical baseline.** For each paragraph P1-P4, list (a) which structural move from the canonical baseline at `~/Documents/resumes/Summer_Rae_CoverLetter.md` and (b) which Shape (A vs B from the structural template) was applied. Format:

```
P1: Shape A intersection-of-problems hook + company-bet bridge — matches baseline structural intent (hook → company-bet)
P2: Shape A company-situation deep-dive — DEVIATES from baseline (baseline uses current-edge); reason: JD has 4 distinct operational dimensions worth naming
P3: Shape A operational evidence with through-line — matches baseline
P4: Shape A pivot-back close — matches baseline structural intent (close on company topic)
```

Every paragraph either matches baseline or has an explicit DEVIATES tag with a one-line reason naming the JD signal that justified the deviation. Vague reasons ("different shape needed", "this role is unique") fail the check — name the specific JD signal that triggered the variant. Surface the diff to the user before file-write so they can override.

**Check 6 — Closing-line standalone read.** Read the final sentence alone. Fail conditions: passive closing (§5), founder-cosplay closing (§5a "bets I want to be running"), or generic "I'd welcome the chance to discuss" without naming a specific topic.

**Check 7 — Anti-pattern §5 / §5a / §5b sweep.** Scan the full draft once against the §5 anti-pattern list, the §5a LLM-era buzzword list, and the §5b P1 resume-narration ban. Print: *"§5 hits: [n] — [list]"*. Fail condition: any single hit. (Anti-patterns are reject-on-presence, not score-and-weigh.)

### 6.2. Hiring-manager perspective review (dispatched subagent)

After §6.1 passes, dispatch a fresh subagent via the Agent tool with `model: "sonnet"` and pass ONLY:

- The JD
- The current draft
- The Phase 1 hiring-risk sentence
- The §6.2 prompt below

Do not pass the resume, the canonical baseline, the structural template, or §A philosophy — the reviewer must evaluate the draft cold, as a hiring manager would. Same-context review by the drafting model systematically under-flags problems the drafter has already rationalized.

**§6.2 reviewer prompt:**

```
You are the hiring manager for the role described in [JD]. The candidate sent the cover letter in [DRAFT]. Their Phase 1 hiring-risk sentence is: [HIRING-RISK].

Read the letter the way a hiring manager reads 80+ letters in a screening session: skim P1 first, decide whether to keep reading, then evaluate.

Answer in this order:

1. **After reading P1 only:** would you keep reading? One sentence answer with reason.
2. **What raises a question or makes you want to keep reading?** Quote the specific phrase. Up to 3.
3. **What would make you skip to the next application?** Quote the specific phrase. Up to 3. Special attention to: skim-bait paragraphs, predictable openers, generic AI-leadership framing, prestige stacking without operational substance, founder-cosplay language, resume narration.
4. **Does the letter orbit the hiring risk, or does it orbit "AI leadership in general"?** One sentence.
5. **Verdict — would you grant a screen?** Yes / No / Borderline, with one reason.

Be skim-honest, not generous. The drafter wants the harsh signal, not a confidence boost.
```

The subagent's response is surfaced to the user verbatim. If the verdict is No or Borderline, present the option to revise specific paragraphs before file-write.

### 6.3. Why this two-tier review exists

The first-sentence pass catches candidate-focused openings. The proper-noun pass catches stale company- or role-specific evidence from another letter. The sentence-subject sequence catches I-stacking that the prose-level reviewer would let slide. The structural-diff check catches variant drift (the failure mode where a permissive variant quietly disables the default's safeguards). The prestige-density count catches the LLM-era "infer-from-proper-nouns" failure. The hiring-risk anchor check catches generic-AI-leadership drift. The closing-line pass catches filler. The dispatched hiring-manager review catches skim-bait that survives all the mechanical checks by being technically well-written but functionally forgettable.

Mechanical checks (§6.1) produce evidence. Perspective review (§6.2) produces signal. Both must pass before file-write.
