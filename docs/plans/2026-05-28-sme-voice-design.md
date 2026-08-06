# `sme-voice` skill — design

**Date:** 2026-05-28
**Author:** Summer (with Claude)
**Status:** Approved (pending one storage-path confirmation)
**Sibling skill:** [`writing-voice`](../../writing-voice/SKILL.md) (Summer's personal voice)

## Problem

Summer edits SME (subject-matter expert) scripts for work at DLAI. When she updates a script, the edits need to read as the SME wrote them, not as her or as generic AI prose. `writing-voice` solves the inverse problem (writing as *her*) and explicitly defers SME-preservation work to a not-yet-existing skill — this design fills that gap.

The existing `writing-voice` skill loads a hand-crafted static profile. The new skill must instead **build** a voice profile from samples (because SMEs are different people with different voices) and **apply** it on demand.

## Shape

Two phases, both invoked via the same skill:

### Phase A — Build a profile

**Triggers:** "build a voice profile for [name]", "capture [name]'s voice from these samples", "I'm going to start editing [name]'s scripts", "/sme-voice build [name]"

**Inputs (any mix):**
- Pasted samples in chat
- File paths to scripts/transcripts on disk
- URLs to published material (routes through `web-scraping-efficient` if the page is large)

**Minimum:** 2 samples, ≥500 words total. Below that, the skill refuses and asks for more rather than fabricating axes from thin material.

**Output:** A profile file saved at `~/claude_code/agent-vault/sme-voices/<name-slug>.md` covering the 9 axes (see Profile Template below). The skill echoes the profile back so Summer can correct before it's committed.

### Phase B — Apply a profile

**Triggers:** "edit this in [name]'s voice", "rewrite section X keeping [name]'s style", "add a paragraph here as [name] would write it", "/sme-voice apply [name]". Also auto-applies when Summer is editing a file in a known DLAI-script directory tagged with an SME's name (TBD — depends on her actual script layout).

**Process:**
1. Look for a matching saved profile in `~/claude_code/agent-vault/sme-voices/`
2. If none, fall back to **ad-hoc mode**: extract voice from the current document, flag the missing profile, offer to promote to saved after Summer corrects the draft once
3. Read the SME profile end-to-end
4. Write the requested addition/rewrite
5. Run a **voice-fidelity pass** before returning the draft: diff the draft against the 2-3 exemplar passages on rhythm, register, and signature-phrase usage; flag misses in a short note

### Promotion path

Ad-hoc profiles built mid-edit (Phase B fallback) are kept in memory for the session only. Once Summer corrects the draft once, the skill offers to save the ad-hoc profile as a real one. This avoids creating noisy half-profiles for one-off edits.

## Profile template — 9 axes

Each saved profile is a markdown file with the following sections:

1. **Register** — technical depth, jargon vs plain language, formality. One paragraph.
2. **Sentence rhythm** — average length, short-punchy vs long-flowing, lecture vs conversational. Quote 2 short samples that capture the rhythm.
3. **Pronouns** — primary subject ("we" / "you" / "I" / passive). Note when they switch and why.
4. **Pedagogical moves** — how they introduce concepts, when they hedge, when they assert, how they hand off to examples. The *move sequence* is the load-bearing part.
5. **Signature phrases / vocabulary** — recurring openers, transitions, idioms. List the top 5-10 with frequency notes.
6. **Examples & analogies** — the *kind* they reach for (math, real-world, historical, code, personal anecdote). Not specific examples — the *category preference*.
7. **Hedging patterns** — confident assertions vs careful framing. Where do they soften, where do they commit?
8. **What they never do** — explicit anti-patterns. Never uses emoji. Never says "obviously". Never opens with a question. Etc.
9. **Exemplar passages** — 2-3 quoted samples (100-300 words each) that are the north-star for the voice. These are the diff target for the voice-fidelity pass.

A blank version of this template ships in `references/profile-template.md`.

## Storage

Saved profiles live at `~/claude_code/agent-vault/sme-voices/<name-slug>.md`. The skill reads them via absolute path. Agent-vault is already private, already cross-machine, already cloned everywhere Summer works — no new repo, no new clone step.

**Naming:** `<firstname-lastname>.md` or `<firstname>.md` if unambiguous. The skill checks for ambiguity (multiple Andrews) and asks before saving.

## Shared-communication-principles handling (inverted from `writing-voice`)

`writing-voice` always loads `shared/communication-principles.md` on top of Summer's profile because they reflect *her* writing preferences. SMEs may write differently — their samples are ground truth even when they conflict with Summer's preferred principles.

**Rule:** load `shared/communication-principles.md` *only when* the SME's own samples already follow them. If the SME systematically violates a shared principle (e.g., they love em-dashes, they bury the lede, they open with anecdote), honor the SME register. The skill notes the conflict to Summer in a one-line flag, but doesn't override.

This is the key behavioral inversion vs `writing-voice` and gets named explicitly in `SKILL.md` so it doesn't drift.

## File layout

```
sme-voice/
  SKILL.md                          # router + frontmatter (user-invocable: true)
  references/
    profile-template.md             # blank 9-axis template
    extraction-guide.md             # how to read samples and fill axes (Phase A)
    application-guide.md            # how to apply profile + voice-fidelity pass (Phase B)
```

Saved profiles do NOT live in this repo. They live in `agent-vault`.

## Frontmatter

```yaml
---
name: sme-voice
description: >
  Captures another person's writing voice from samples and applies it when
  ghostwriting or editing in their voice — primarily for SME (subject-matter
  expert) scripts at DeepLearning.AI. Two phases: build a saved voice profile
  from 2+ samples (Phase A), then apply that profile when editing or extending
  the SME's scripts (Phase B). Saved profiles live in ~/claude_code/agent-vault/
  sme-voices/ so they sync across machines.

  Trigger on: "build a voice profile for [name]", "capture [name]'s voice",
  "edit this in [name]'s voice", "rewrite as [name]", "keep [SME's] style",
  or "/sme-voice ...".

  Do NOT use this skill when writing as Summer herself (use writing-voice
  instead), running ToneGuard, or summarizing/analyzing documents.
user-invocable: true
---
```

## Triggering boundary vs `writing-voice`

| Situation | Skill |
|---|---|
| "Write me an email" / "draft this for me" | `writing-voice` |
| "Edit Andrew's L0 script section 3" | `sme-voice` (apply) |
| "Build a voice profile from these 3 samples" | `sme-voice` (build) |
| "Update this script keeping the instructor's voice" | `sme-voice` (apply, ad-hoc if no profile) |
| "Ghostwrite a LinkedIn post as Andrew" | `sme-voice` (apply) |

Both skills update their respective `Do NOT use when…` sections to point at each other.

## Voice-fidelity pass (the diff step)

Before returning any Phase B draft, the skill runs a short structured check:

1. **Rhythm match** — compare sentence-length distribution of the draft vs exemplar passages. Flag if draft is materially shorter or longer.
2. **Register match** — scan for jargon density and formality markers. Flag drift in either direction.
3. **Signature-phrase usage** — list signature phrases used in the draft. Flag if zero, flag if forced/overused.
4. **Never-does check** — grep the draft against the "What they never do" list. Any hit = block, ask Summer.

Output is a 4-line note appended after the draft (or inline as a system comment, TBD in impl). This makes the fidelity check visible to Summer instead of buried in the model's heuristic.

## Anti-overfitting reminder (same as `writing-voice`)

The profile is a source of truth, not a checklist. Three tendencies used naturally beats ten forced in awkwardly. The skill closes each application with:

> "Does this sound like something [name] would actually write — or does it sound like AI trying very hard to imitate them?"

## Open items

1. **DLAI script directory auto-detection** — Phase B's "auto-apply when editing files in known SME directories" is deferred. Need a sample of Summer's actual script repo layout to know what to match on. For v1, skill triggers only on explicit invocation or trigger phrase.
2. **Multi-SME scripts** — some scripts have multiple instructors. v1 punts on this; Summer specifies which SME's voice to use per-edit.
3. **Profile drift** — over time, an SME's voice in production may drift from the saved profile. No auto-refresh in v1; Summer re-runs Phase A when needed.

## Plan

Detailed implementation plan goes in `docs/plans/2026-05-28-sme-voice-impl.md` (next step — `writing-plans` skill).
