# Application Guide — Phase B

How to apply a saved SME voice profile when ghostwriting or editing in that SME's voice.

## Profile lookup

1. **Slugify the SME name** the same way [`extraction-guide.md`](extraction-guide.md) does: lowercase, hyphens for spaces.
2. **Read** `~/claude_code/agent-vault/sme-voices/<slug>.md` end-to-end. The profile is short and load-bearing — skim costs more than it saves.
3. **If the file doesn't exist**, switch to ad-hoc mode (next section).

## Ad-hoc fallback

When there's no saved profile for the requested SME:

1. **If Summer is editing a current document** authored by the SME — extract voice from that document using the 9-axis template, but skip §9 exemplars (the document IS the exemplar set). Flag the missing profile in one line:

   > "No saved profile for [name] at agent-vault/sme-voices/. Extracting ad-hoc from the current document. Want me to promote this to a saved profile after you correct the draft once?"

2. **If there's no current document either** — STOP and ask Summer to either point at samples (then run Phase A first) or name a different SME with a saved profile.

3. **Do not invent a profile from the SME's reputation.** "Andrew Ng's voice" without samples is fan fiction.

## Shared-communication-principles handling (INVERTED from writing-voice)

This is the key behavioral difference from the sibling `writing-voice` skill.

`writing-voice` always loads [`../../shared/communication-principles.md`](../../shared/communication-principles.md) because it reflects Summer's own preferences. **This skill does not load it by default.**

**Rule:**
- After reading the SME profile (or the ad-hoc source document), check whether the SME's exemplar passages follow the shared principles: lead-with-the-conclusion, plain language, no hollow openers, no em-dashes, etc.
- **If the SME's voice already follows them** → you may load and apply the shared principles on top of the SME profile.
- **If the SME's voice systematically violates them** — SME register wins. Honor the SME profile. Flag the conflict to Summer in a one-line note:

  > "Note: this SME buries the lede / uses em-dashes heavily / opens with anecdote — honoring SME voice over shared principles."

- **Never override the SME voice to enforce a shared principle.** The whole point of the skill is preserving the SME's voice; the shared principles are downstream of that.

## Writing the draft

Standard authoring with the SME profile as source of truth. Two reminders:

- **Mode-match.** If Summer asks for an L0 script edit, mirror script cadence (paragraphs, narration). If she asks for a LinkedIn post in the SME's voice, mirror that mode. The profile captures voice; you adapt to mode.
- **Anti-overfitting.** Three SME tendencies used naturally beats ten forced in awkwardly. The profile is a source of truth, not a checklist.

## Voice-fidelity pass

Run all four checks before returning the draft. Append a 4-line note after the draft body.

### 1. Rhythm match
Compare the draft's sentence-length distribution against the §9 exemplar passages. If draft mean is materially shorter or longer than exemplar mean (>30% deviation), flag.

### 2. Register match
Scan for jargon density and formality markers. Flag drift in either direction:
- Draft uses jargon the SME never uses → flag
- Draft simplifies past the SME's actual register (talks down to the audience) → flag
- Draft is more formal/stiff than the SME → flag

### 3. Signature-phrase usage
List signature phrases (from §5 of the profile) that appear in the draft.
- **Zero used** → flag ("sounds generic — consider adding one of [phrases]")
- **Three or more in a short draft** → flag ("forced/overused — sounds like impersonation")
- **One or two used naturally** → PASS

### 4. Never-does check (grep — BLOCKING)
For each item in the profile's §8 "What they never do" list, grep the draft. **Any hit = BLOCK.** Fix before returning the draft. Do not ship a draft that violates an explicit never-does rule.

### Output format

Append after the draft:

```
---
**Voice-fidelity pass:**
- Rhythm: [PASS / FLAG — note]
- Register: [PASS / FLAG — note]
- Signature phrases used: [list, or "none — consider adding"]
- Never-does check: [PASS / BLOCK — what hit]
```

Keep the notes terse. Theatrical fidelity reports get ignored; informative ones get read.

## Anti-overfitting self-check

Close every Phase B response (after the fidelity note) with:

> Does this sound like something [name] would actually write — or does it sound like AI trying very hard to imitate them?

If it feels forced, revise toward inhabitation, not imitation. Less effort, more naturalness.

## Promoting an ad-hoc profile to saved

After Summer corrects an ad-hoc draft once and the correction lands well, offer:

> "Want me to promote this ad-hoc profile to a saved one at `~/claude_code/agent-vault/sme-voices/<slug>.md`?"

If yes, hand off to [`extraction-guide.md`](extraction-guide.md) § "Promoting an ad-hoc profile". Do not auto-promote without asking — Summer may want to leave the SME ad-hoc if she only edits their work occasionally.
