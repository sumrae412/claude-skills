# Voice Corpus — Two-Tier Cover-Letter Voice Pool

Load this reference whenever drafting a cover letter, reviewing one, or after a successful interview signal. The corpus is what keeps cover-letter voice from drifting into AI-generated cadence over time.

## The Problem This Solves

Reading prior AI-drafted cover letters as voice templates compounds the AI cadence with every new draft. Three letters in, the voice has drifted from the user's authentic prose into a smoothed, generic register — even when each individual letter passed review.

Adapted from the adrasyn cover-letter skill's "originals vs successful" pattern (see `~/Documents/resumes/_voice-corpus/SOURCE.md` after first bootstrap).

## The Two Tiers

```
~/Documents/resumes/_voice-corpus/
├── README.md                     # what's in here, when to read, when to add
├── originals/                    # user-authored letters from before any AI assist
│   └── <date>-<context>.md
└── successful/                   # AI-drafted letters that landed an interview/offer
    └── <YYYY-MM-DD>-<Company>-cover-letter.md
```

**`originals/`** is the gold standard. These are pristine voice samples — the user wrote them solo, no AI involvement. They define what authentic voice sounds like for this user. Treat as read-only.

**`successful/`** is the working pool. A letter is promoted here only after the user reports an interview, screen, or offer for that application. Letters that ship but don't land never enter the corpus.

## Bootstrap (first time)

If `~/Documents/resumes/_voice-corpus/` does not exist when a cover letter is requested:

1. Ask the user: *"Want me to bootstrap a voice corpus? I'll create `~/Documents/resumes/_voice-corpus/{originals,successful}/` and seed `originals/` with a letter you wrote solo (path?). Future drafts will read from there instead of from per-company folders, which prevents AI-voice compounding."*
2. On agreement, create the folders + a one-paragraph `README.md` explaining the tiers + a `SOURCE.md` crediting the adrasyn pattern.
3. If the user names a seed letter, copy (not symlink) it into `originals/` with a date prefix.
4. Proceed with the draft.

If the user declines, proceed without the corpus and surface the AI-voice-compounding risk in the final review pass.

## Read Rules — what counts as a voice template

When drafting a new cover letter and looking for voice cues:

- **READ from:** `originals/*` (preferred), `successful/*` (acceptable, frozen at success-time).
- **DO NOT READ from:** `~/Documents/resumes/<Company>/cover-letter.md` for any company that hasn't been promoted to `successful/`. These letters either failed or are in flight — pulling voice from them compounds AI cadence.
- **DO NOT READ from:** the most recently-modified per-company folder, even if endorsed in this session. "Endorsed by user" ≠ "landed an interview." Endorsement is a fit signal, not a voice signal.

This rule supersedes the older "reuse most recent endorsed letter as STRUCTURAL template" memory (`feedback_cover_letter_reuse_recent_letter_as_template.md`) — that memory pre-dates the voice corpus and remains valid only when no corpus exists.

## Promotion Trigger — when to add to `successful/`

Promote a letter from `<Company>/cover-letter.md` to `_voice-corpus/successful/` when the user reports any of:

- "I got an interview at X"
- "X invited me to a phone screen / first round / on-site"
- "X moved me forward"
- "X made me an offer"
- Any structurally similar signal (recruiter outreach in response to the application, hiring-manager intro email, etc.)

**Do not promote on:**

- Application submitted / received.
- Auto-acknowledgement emails.
- "Application under review" status updates without human contact.
- User endorsement of the letter ("looks good") absent an interview signal.

The bar is *human contact resulting from this application*, not *the letter passed review*.

## Promotion Mechanics

When a promotion signal arrives:

1. Confirm: *"Promoting `~/Documents/resumes/<X>/cover-letter.md` to the voice corpus as `_voice-corpus/successful/<YYYY-MM-DD>-<X>-cover-letter.md`. This freezes the letter at success-time and makes it a voice template for future drafts. OK?"*
2. On confirmation, **copy** (not symlink — symlinks drift if the user later edits the company folder).
3. Append a one-line note to `_voice-corpus/README.md`: `<date> — promoted <Company> (signal: <interview / screen / offer>)`.
4. If the company folder also has a `jd.md`, copy it alongside as `<YYYY-MM-DD>-<X>-jd.md` for context. Do not copy the resume — voice corpus is letter-only.

If a promoted letter later turns into a rejection (interview happened, no offer), the letter stays in `successful/`. The promotion threshold is human contact, not eventual outcome — a letter that opened a door is still a voice signal even if the door later closed.

## Corpus Hygiene

Periodically (every 5-10 promotions, or on user request):

- **Prune the bottom of the pool** if `successful/` exceeds ~15 letters. Drop the oldest non-distinctive letters; keep the ones with strongest voice fingerprint. Surface the proposed cuts before deleting.
- **Audit for drift:** read 3 letters from `successful/` end-to-end. If they sound more like each other than they sound like `originals/`, the pool has converged on AI cadence — stop drawing from `successful/` and re-anchor on `originals/` for the next 3 drafts.
- **Never edit promoted letters.** They are frozen at success-time. If the user wants to update voice, that goes into a new `originals/` entry.

## Drafting Read Order

When the user requests a cover letter and the corpus exists:

1. Read 1-2 files from `originals/` (most recent or most context-relevant) for voice baseline.
2. Read 1-2 files from `successful/` (most recent, or company-similar to target) for what's currently working.
3. Use those 2-4 files as voice anchor. Draft the new letter following the structure rules in `references/cover-letter-review.md` and the patterns in the user's voice memories.
4. Do NOT read prior letters from `~/Documents/resumes/<other-companies>/`.

## Anti-Compounding Diagnostic

Before sign-off on any cover letter draft, run this check:

- Pick 3 distinctive phrases from the new draft.
- Grep `_voice-corpus/successful/` for each.
- If all 3 appear in prior successful letters → the draft is recycling, not authoring. Rewrite those passages.
- If 0 of 3 appear → the draft has no voice continuity with the corpus. Read 1 more `originals/` file and add a connecting cadence.
- The healthy zone is 1-2 phrase echoes (voice continuity) without verbatim recycling.

## Cross-References

- `references/cover-letter-review.md` §"Input Sources" — operational read rule (companion to this file).
- `feedback_cover_letter_reuse_recent_letter_as_template.md` — superseded for users with a corpus; still valid as fallback.
- `feedback_summer_cover_letter_p1_voice.md` and adjacent voice memories — what the corpus is preserving.
