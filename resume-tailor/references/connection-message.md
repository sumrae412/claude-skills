# Connection Message — LinkedIn DM Spec

Load this reference only when the user explicitly requests a connection message ("draft a connection message", "write me a LinkedIn DM for this", "outreach to the recruiter", "DM the hiring manager"). The skill never offers this proactively — see SKILL.md Phase 5 §5.

## Constraint Envelope

- **Length:** ≤300 characters (LinkedIn's hard limit on connection-request notes is 300; DMs to existing connections allow more, but keeping the same envelope makes the artifact reusable across both channels).
- **Tone:** professional but human. Match the candidate's authentic voice from their cover letter / `_voice-corpus/`, not a templated recruiter register.
- **Audience:** the named recipient (recruiter, hiring manager, referrer, or company employee). Address them by name when known. If no name is available, ask the user before drafting.

## Required Inputs

Before drafting, gather:

1. **Recipient name + title** — required. If unknown, ask the user once. If still unknown, draft only the body and prepend a `[Name]` placeholder for the user to fill.
2. **Recipient relationship to the role** — recruiter, hiring manager, future manager, current employee in adjacent function, alumni, or warm referral.
3. **The JD** — already loaded as part of Phase 1.
4. **One specific anchor** — a recent post the recipient wrote, a project the company shipped, a mutual connection, or a JD detail that resonates with the candidate's actual work. *Without an anchor, the message is generic recruiter-spam — refuse to draft and ask for one.*

## Structure (3 beats)

A 300-char message has room for exactly three sentences:

1. **Anchor** — name the specific thing that prompted reaching out. Not "I saw you're hiring" — *what* did you actually see?
2. **Bridge** — one line connecting the anchor to the candidate's actual experience. Not credentials; the *kind of work*.
3. **Ask** — what response would be useful. Default: a 15-min chat. Variants: a referral, a direct application path, or a shared context preview before formal applying.

**Example (recruiter, 280 chars):**

> Hi Maria — saw the Director of Applied AI posting at Acme. The brief on agentic platforms in HIPAA-protected envs maps directly to what I've been running for the last year at Govini. Open to a 15-min chat next week to compare notes on what success looks like in the role?

**Example (hiring manager, 295 chars):**

> Hi Sam — your team's recent post on the multi-agent orchestration patterns you're testing caught my eye. I've been running the same eval framework against tool-call accuracy at Govini and would value 15 min to swap notes, regardless of timing on the open req.

## Anti-Patterns (reject)

- "I'm a passionate professional with X years of experience…" — generic LinkedIn-bio register.
- "I'd love to learn more about your company" — anchor-less, asks the recipient to do work.
- Emojis (most professional recipients screen these out as low-effort).
- Stacked credentials in the opener ("VP of Engineering, ex-FAANG, Stanford MBA…").
- Mention of compensation, visa, or relocation in the first message.
- Comparative put-downs ("unlike most candidates I…").
- Multiple links — one anchor link maximum, and only if it adds context the recipient can't infer.

## Do Not Repeat the Cover Letter

Connection messages are NOT compressed cover letters. The cover letter is for the application; the connection message is for human contact. The right move:

- Cover letter answers *"why am I qualified for this role?"*
- Connection message answers *"why is this person worth 15 minutes of my time?"*

Pulling sentences directly from the cover letter into the DM produces stiff, application-form-ish prose. Draft the DM independently, drawing on the same evidence pool (canonical resume + JD + voice corpus) but with a different governing question.

## Output Path + Format

Save to `~/Documents/resumes/<Company>/connection-message.md`:

```markdown
# Connection Message — <Recipient Name> (<Title>)

**Recipient relationship:** recruiter / hiring manager / employee / referrer
**Channel:** LinkedIn connection request / LinkedIn DM / email
**Anchor:** <one-line description of the specific anchor used>

---

<the message body, ≤300 chars>
```

The metadata block above the `---` lets the user remember context months later (or when revisiting outreach to the same person for a different role).

## Iteration

After drafting, ask:

- *"Does this anchor land for you, or want a different one?"*
- *"Right relationship/tone for [recipient]?"*

Wait for confirmation before saving. Connection messages are higher-stakes than cover letters per character — the recipient sees them outside the formal application context, and tone misfires read as spam.
