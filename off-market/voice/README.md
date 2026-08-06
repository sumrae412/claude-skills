# Voice directory

This directory holds your **personal voice profile** — the file the off-market skill reads when drafting outreach letters so they sound like you, not like a generic template.

## Files

- `profile-template.md` — the empty schema. Tracked in git as the canonical structure.
- `profile.md` — **your** populated voice profile. **Gitignored** so personal writing samples never leak into the repo. Copy `profile-template.md` to `profile.md` and fill it in.

## How to populate

You have two paths:

### Path 1 — let the skill do it (recommended)

Run `/off-market voice` in a Claude Code session and paste 1-3 sample paragraphs you've written (an email, a journal entry, a note — anything in your natural voice, ~100+ words each). The skill:

1. Computes deterministic stats via `scripts/voice_capture.py:summarize_samples` (sentence length, top content words, openers/closers).
2. Hands the stats + your raw samples to Claude.
3. Claude fills in the `profile-template.md` headings — tone adjectives, cadence description, signature openers, vocabulary lists — and writes the result to `voice/profile.md`.

### Path 2 — fill it in by hand

Copy `profile-template.md` to `profile.md` and write each section yourself. The template's HTML comments explain what each section is for. Read `references/letter-craft.md` first — the "Forbidden phrases" seed list comes from there.

## What goes where

| Section | What it captures |
|---|---|
| Tone | Two adjectives + one anti-adjective. "Warm, specific. NOT slick." |
| Sentence cadence | Rhythm of your sentences — short declaratives, long descriptive, mixed. |
| Vocabulary I use | 10-20 words/phrases that genuinely recur in your writing. |
| Vocabulary I avoid | 5-10 words/phrases that don't sound like you. |
| Signature openers | 2-3 real ways you typically start a personal letter. |
| Signature closers | 2-3 real ways you sign off. |
| Forbidden phrases | Investor jargon and corporate fluff the skill must never produce. |

## Why `profile.md` is gitignored

The voice profile is personal — it contains your phrasing patterns, sample openings, and signature lines. Keeping it out of git means:

- You can clone the skill repo on a different machine without dragging your voice profile along.
- Sample paragraphs you fed in (or quoted in the profile) never end up in PR diffs.
- Multiple users of the same skill keep their voices separate.

If you ever want to share a voice profile across machines, copy it manually — don't add an exception to `.gitignore`.
