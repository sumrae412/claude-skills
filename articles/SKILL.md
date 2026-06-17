---
name: articles
description: Use when the user says "/articles", "check my articles", "process Claude articles", "triage my reading queue", or asks whether anything in their Mem reading queue is worth pulling into their projects or skills. Pulls unread notes from Mem's "Claude articles" collection ONLY, runs each through `useful-for` against the user's claude-skills repo and active projects (CourierFlow, BetterBurgh, DeepLearning.ai work), and moves processed notes to "Claude articles — reviewed". Triggers on any phrasing about checking, processing, triaging, or reviewing the reading inbox in Mem.
user-invocable: true
---

# Articles

Triages the user's Mem reading queue against their projects, repos, and skills. Each unread article gets a `useful-for` verdict, then is filed to the "Claude articles — reviewed" collection so it doesn't surface again.

**Announce once at start:** "Running /articles — pulling unread items from Mem and triaging."

---

## Source (Mem collection)

Pull from this collection ONLY. The ID is authoritative — don't search by title.

| Collection | ID | Notes |
|---|---|---|
| Claude articles | `089f8552-6db8-47e4-899a-f092873e467c` | The only inbox this skill triages |

**Do NOT pull from** "Claude Tasks", "Coding", or "Article Collection" — those are separate workflows. If the user wants to triage something in another collection, they will name it explicitly and you should still verify before pulling.

**Reviewed archive:** `bf963978-f4fd-41a5-86b6-989418e3e194` ("Claude articles — reviewed"). Anything already in this collection is done — skip it.

## Targets (what we triage against)

Default target set, in priority order:

1. **claude-skills repo** — every skill directory at the repo root, plus `CLAUDE.md`, `COMMANDS.md`, `CATEGORIES.md`. New patterns may become a new skill, refine an existing one, or update memory.
2. **CourierFlow** — the `courierflow-*` skills in claude-skills repo, plus the actual CourierFlow repo if relevant.
3. **BetterBurgh** — personal advocacy project.
4. **DeepLearning.ai work** — course scripts, evals (see `sc-marketing-scripts`, `Evals` collection).

If the user names a narrower target ("just for claude-skills", "only CourierFlow"), respect it and skip the rest.

---

## Workflow

### 1. Pull the inbox

Call `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__list_notes` with `collection_id = 089f8552-6db8-47e4-899a-f092873e467c` (Claude articles). Subtract anything also in the reviewed collection — those are done.

Do NOT pull from any other collection. If a note appears in both Claude articles and another collection (e.g. Article Collection), it is still in scope, but only because of its Claude-articles membership.

Default cap: 10 notes per run. If the queue is larger, ask the user "20 unread items — process all, or first 10?" before continuing.

### 2. Triage each note via `useful-for`

For each unread note:

1. Fetch the note content (`get_note`).
2. Run the `useful-for` mental model (see `useful-for/SKILL.md`) against the priority target list above. Two modes:
   - **Inline triage** (default for Mem notes): Mem already produces structured summaries (TL;DR, Key Points). For those, apply the useful-for rubric inline — no subagent dispatch needed. Faster, keeps context.
   - **Subagent dispatch**: only when the note is raw long-form content (full article body pasted, transcript, paper) with no Mem summary. Then invoke useful-for as a proper skill call so the heavy lifting happens out of the main thread.
   - **Body-less capture** (bare title + source + tracking-redirect URL, no Mem TL;DR/Key Points — currently the dominant shape): there is nothing to fetch (redirects are dead — see Rules) and nothing to summarize. Triage from the title at LOW confidence and route to the verify-before-author rule below for any item you'd otherwise call "high-value." If the first few notes in a run are all body-less, say so once at the top of the run ("most captures are title-only — verdicts are title-level guesses; I'll verify any high-value pulls against canonical sources before acting") so the user reads the rollup with correct confidence.
3. Capture the verdict (high-value / some-value / skip + confidence) per relevant target.

### 3. Report each article

Output one section per article as you process it:

```
## <Article title> → <best-fit target>
**Verdict:** <high-value | some-value | skip> (confidence N/5)
**Pull:** <ranked items with concrete "where it goes" + "how to apply">
**Skip:** <items that don't fit + reason>
**Next action:** <one concrete step, or "no action">
```

Keep a running list of `(note_id, source_collection_id)` for every note you triaged — regardless of verdict. This is the archive batch for step 5.

### 4. Summary

After all notes are processed, emit a one-screen rollup:

```
## /articles summary
- Processed: N
- High-value pulls: M (list with target + skill/file)
- Some-value: K
- Skipped: J
- Suggested next actions (ranked): ...
```

### 5. Archive everything processed

At the very end, move every note from step 3's running list into the reviewed archive. **Do it as two sequential batches, not interleaved** — the auto-mode classifier will block a `remove` that runs in parallel with its matching `add` because, from the outside, the add hasn't confirmed yet.

**Batch A** — for every `note_id`, call `add_note_to_collection` → `collection_id = bf963978-f4fd-41a5-86b6-989418e3e194` ("Claude articles — reviewed"). All in one parallel block.

**Batch B** — after Batch A returns successfully, for every `note_id`, call `remove_note_from_collection` with `collection_id = 089f8552-6db8-47e4-899a-f092873e467c` (Claude articles) ONLY. Do not remove from any other collection the note happens to be in. All in one parallel block.

Every triaged note ends in the reviewed archive — including "skip" verdicts. The point of archiving is to keep the inbox small, not to reward high-value pulls. Confirm in the closing line: "Archived N notes to Claude articles — reviewed."

---

## Rules

- **Never auto-edit skills or repos.** This skill produces a triage report and suggested actions. The user (or a follow-up `/claude-flow`, `useful-for`, or skill-creator session) does the actual edits.
- **Always file as reviewed.** Even "skip" verdicts get moved — the point is the inbox stays small.
- **One announce, then quiet.** No per-tool narration. Report results in the structured output, not in chatter.
- **If a note is a bare URL with no content:** fetch the URL via WebFetch first. If fetch fails, mark as "skipped — could not fetch" and file as reviewed.
- **Known-failure tracking links — don't burn fetches on them.** Mem's newsletter captures truncate redirect URLs: Half Baked (`elink2fb.mail.gethalfbaked.com`) returns HTTP 400 and Beehiiv/The Neuron (`link.mail.beehiiv.com`) returns 403 on every fetch attempt. Skip the fetch, triage from the title at reduced confidence, and cite the newsletter issue (source + date are in the note body) as the path to the full piece. Validated 2026-06-10 across 4 fetch attempts in one run.
- **Title-level verdicts on body-less captures over-rate systematically — verify the canonical source before acting on any "high-value" pull.** When a note is bare `title + source + tracking-redirect URL` with no Mem TL;DR/Key-Points body (the common case — most of the inbox can be body-less), the triage verdict is a title-level guess at reduced confidence, NOT an actionable call. Before authoring any repo edit from a "high-value" item: (1) fetch the CANONICAL source (the publisher's own URL, not the dead Mem redirect), and (2) gap-check against the target skill/CLAUDE.md — the claim may already be covered, or its numbers may be unsourced. Validated 2026-06-17: of 4 title-level "high-value" calls, 2 collapsed on verification (one already fully covered by repo CLAUDE.md + carried unsourced figures absent from canonical Anthropic docs; one downgraded to a low-urgency prior-art note). Pull phase = verify-then-author, never author-from-title.
- **If `useful-for` returns "skip" for all targets:** still include a one-line summary so the user sees why it was dropped.

---

## When NOT to use this skill

- User pastes a single article inline → use `useful-for` directly, no need to touch Mem.
- User wants to *add* something to Mem → that's `inbox-triage` or direct Mem tools.
- User wants a deep research dive on one article → use `synthesis-brief` or `research`.

---

## References

- [`references/maturity-progression.md`](references/maturity-progression.md) — where `/articles` sits on Jason Liu's Six Levels framework and what Level 5 (drafts actions) / Level 6 (memory-vault feedback) would look like here.
