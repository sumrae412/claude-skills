# Cover Letter Review

Local review reference for Phase 5 cover-letter drafting. Load this file before drafting or revising a cover letter so the review rules live inside the `resume-tailor` skill instead of in host memory.

## 0. Input Sources — where voice templates come from

Before drafting, load these in order:

1. **The candidate's canonical structural example** — `~/Documents/resumes/Summer_Rae_CoverLetter.md`. Always load. This is the endorsed paragraph shape, cadence, and voice baseline.
2. **The annotated structural template** — `references/templates/cover-letter-structural-template.md`. Always load alongside the baseline. Captures the 4-paragraph hook → current-edge → prior-leadership-evidence → synthesis-close pattern as a skeleton with per-paragraph rules and named variants (biotech-anchor inversion, seniority alignment, agentic-AI lead).
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

## 6. Final Review Pass

Before sign-off, read:

1. The first sentence of each paragraph by itself.
2. All proper nouns by themselves, cross-checked against the JD and the resume. Catches two failure modes: (a) stale company/role/person names accidentally carried over from another letter, and (b) fresh typos in this letter — recipient firm name, hiring manager's name, the candidate's current employer. Both are interview-killers and resume-screen rejections. (One published experiment had the author address "WXY Architects" when applying to XYZ Architects, and name XYZ as his current employer when it was the role he was applying for — caught only by outside reviewers.)
3. The closing line by itself.
4. The whole letter aloud, asking: *would I send this to a smart friend?* Press-release cadence ("As a passionate strategist with a proven track record of driving impact...") fails this test. Conversational-but-professional passes.
5. Each body paragraph against the **"what can I do for you?" diagnostic.** Every body paragraph should answer that question implicitly. If a paragraph answers "what do I want from you?" instead, rewrite to lead with the company's need (per §1 opening rule).
6. The whole letter from the **hiring manager's perspective.** Read as if you are the hiring manager for this exact role at this exact company. Ask: what raises a question? what makes me want to keep reading? what would make me skip to the next application? Skim-bait paragraphs (predictable openers, generic praise, resume restatement) fail this test even when the §6 step-4 smart-friend test passes — they sound human but waste the reader's time.

The first-sentence pass catches candidate-focused openings. The proper-noun pass catches stale company- or role-specific evidence from another letter. The closing-line pass catches filler. The smart-friend pass catches press-release cadence. The "what can I do for you?" pass catches candidate-centric framing that escaped the §1 first-sentence check. The hiring-manager pass catches skim-bait that survives all of the above by being technically well-written but functionally forgettable.
