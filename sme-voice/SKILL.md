---
name: sme-voice
description: "Captures another person's writing voice from samples and applies it when ghostwriting or editing in their voice — primarily for SME (subject-matter expert) scripts at DeepLearning.AI. Phase A builds a saved voice profile from samples; Phase B applies it when editing or extending the SME's scripts. Profiles live in ~/claude_code/agent-vault/sme-voices/ to sync across machines. Trigger on 'capture [name]'s voice', 'edit this in [name]'s voice', 'ghostwrite as [name]', or '/sme-voice'. NOT for writing as Summer herself (use writing-voice), ToneGuard analysis, or summarizing/analyzing documents."
user-invocable: true
---

# SME Voice

Capture and apply another person's writing voice — the inverse of [`writing-voice`](../writing-voice/SKILL.md), which writes as Summer.

## Role Contract

You are the SME voice profiler and ghostwriting adapter. Your role is to infer
another person's writing patterns from evidence, preserve that person's register,
and avoid replacing their voice with Summer's defaults.

## Scope

Use this skill to build reusable SME voice profiles from samples or to apply an
existing profile while editing, extending, or ghostwriting. Return the saved
profile path, revised draft, or voice-fidelity notes required by the active
phase.

## What this skill does

Two phases, same skill:

- **Phase A — Build** a saved voice profile from 2+ samples of the SME's writing.
- **Phase B — Apply** the saved profile when editing or ghostwriting in that SME's voice.

Saved profiles live at `~/claude_code/agent-vault/sme-voices/<slug>.md` (private repo, syncs across machines).

## Phase detection

Match Summer's request to the right phase:

| Request shape | Phase |
|---|---|
| "build a voice profile for [name]", "capture [name]'s voice", "I'm going to start editing [name]'s scripts" | **A — Build** |
| "edit this in [name]'s voice", "rewrite section X keeping [name]'s style", "add a paragraph as [name] would", "ghostwrite as [name]" | **B — Apply** |
| `/sme-voice build [name]` | **A** |
| `/sme-voice apply [name]` | **B** |
| `/sme-voice [name]` (ambiguous) | Ask which one |

If Phase B is requested but no saved profile exists, the skill auto-falls-back to ad-hoc mode (extract voice from the current document). See application-guide.

## Phase A — Build

Read [`references/extraction-guide.md`](references/extraction-guide.md). It walks through:
- 2-sample / 500-word minimum (refuse below this; don't fabricate)
- Reading samples end-to-end
- Filling each of the 9 axes with evidence
- Echoing the profile to Summer for correction
- Slugifying the name and saving to `~/claude_code/agent-vault/sme-voices/`
- Committing in the agent-vault repo

The blank template lives at [`references/profile-template.md`](references/profile-template.md).

## Phase B — Apply

Read [`references/application-guide.md`](references/application-guide.md). It walks through:
- Profile lookup (or ad-hoc fallback)
- The **inverted shared-principles rule** (SME register wins when in conflict with `shared/communication-principles.md`)
- Writing the draft mode-matched to the request
- The **voice-fidelity pass** (rhythm / register / signature phrases / never-does grep) appended to every draft
- Anti-overfitting self-check
- Promotion path from ad-hoc to saved

## Boundary with `writing-voice`

| Situation | Skill |
|---|---|
| "Write me an email" / "draft this for me" | [`writing-voice`](../writing-voice/SKILL.md) |
| "Edit Andrew's L0 script section 3" | this skill (apply) |
| "Build a voice profile from these 3 samples" | this skill (build) |
| "Update this script keeping the instructor's voice" | this skill (apply, ad-hoc if no profile) |
| "Ghostwrite a LinkedIn post as Andrew" | this skill (apply) |

## Anti-overfitting reminder

The profile is a source of truth, not a checklist. Three tendencies used naturally beats ten forced in awkwardly. Ask:

> Does this sound like something [name] would actually write — or does it sound like AI trying very hard to imitate them?

If it feels forced, pull back. Less imitation, more inhabitation.

## See also

- [`writing-voice`](../writing-voice/SKILL.md) — inverse skill: write in Summer's own voice.
- [`writing-workshop`](../writing-workshop/SKILL.md) — style mimicry from samples when there's no need for a reusable SME profile.
- [`sc-marketing-scripts`](../sc-marketing-scripts/SKILL.md) — DLAI course script authoring; pair with this skill when the script is in an SME's voice.
