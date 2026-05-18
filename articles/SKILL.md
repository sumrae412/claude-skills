---
name: articles
description: Use when the user says "/articles", "check my articles", "process Claude articles", "triage my reading queue", or asks whether anything in their Mem reading queue is worth pulling into their projects or skills. Pulls unread notes from Mem's "Claude articles", "Claude Tasks", "Coding", and "Article Collection" collections, runs each through `useful-for` against the user's claude-skills repo and active projects (CourierFlow, BetterBurgh, DeepLearning.ai work), and moves processed notes to "Claude articles — reviewed". Triggers on any phrasing about checking, processing, triaging, or reviewing the reading inbox in Mem.
user-invocable: true
---

# Articles

Triages the user's Mem reading queue against their projects, repos, and skills. Each unread article gets a `useful-for` verdict, then is filed to the "Claude articles — reviewed" collection so it doesn't surface again.

**Announce once at start:** "Running /articles — pulling unread items from Mem and triaging."

---

## Sources (Mem collections)

Pull from these collections. Each has a stable ID — don't search by title, the IDs are authoritative.

| Collection | ID | Notes |
|---|---|---|
| Claude articles | `421a7805-5221-4117-8425-da2dc72a2aa1` | Primary inbox — Claude/Anthropic articles |
| Claude Tasks | `bb346d7f-4630-4fda-8f7a-e7a432f4cd68` | Tasks routed for Claude to handle |
| Coding | `a5477b3e-cebc-4ae5-960e-2e0157d17a67` | Programming articles |
| Article Collection | `ef920cfc-1abe-4edc-a6eb-2a24ec2af449` | General reading — filter to programming/AI only |

**Reviewed archive:** `bf963978-f4fd-41a5-86b6-989418e3e194` ("Claude articles — reviewed"). Anything already in this collection is done — skip it.

## Targets (what we triage against)

Default target set, in priority order:

1. **claude-skills repo** (`/Users/summerrae/repos/claude-skills`) — every skill directory, plus `CLAUDE.md`, `COMMANDS.md`, `CATEGORIES.md`. New patterns may become a new skill, refine an existing one, or update memory.
2. **CourierFlow** — the `courierflow-*` skills in claude-skills repo, plus the actual CourierFlow repo if relevant.
3. **BetterBurgh** — personal advocacy project.
4. **DeepLearning.ai work** — course scripts, evals (see `sc-marketing-scripts`, `Evals` collection).

If the user names a narrower target ("just for claude-skills", "only CourierFlow"), respect it and skip the rest.

---

## Workflow

### 1. Pull the inbox

For each source collection, call `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__get_collection` with the ID to list its notes. Then subtract anything that is also in the reviewed collection — those are done.

Default cap: 10 notes per run. If the queue is larger, ask the user "20 unread items — process all, or first 10?" before continuing.

### 2. Triage each note via `useful-for`

For each unread note:

1. Fetch the note content (`get_note`).
2. Run the `useful-for` mental model (see `useful-for/SKILL.md`) against the priority target list above. Two modes:
   - **Inline triage** (default for Mem notes): Mem already produces structured summaries (TL;DR, Key Points). For those, apply the useful-for rubric inline — no subagent dispatch needed. Faster, keeps context.
   - **Subagent dispatch**: only when the note is raw long-form content (full article body pasted, transcript, paper) with no Mem summary. Then invoke useful-for as a proper skill call so the heavy lifting happens out of the main thread.
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

**Batch B** — after Batch A returns successfully, for every `(note_id, source_collection_id)`, call `remove_note_from_collection`. All in one parallel block.

Every triaged note ends in the reviewed archive — including "skip" verdicts. The point of archiving is to keep the inbox small, not to reward high-value pulls. Confirm in the closing line: "Archived N notes to Claude articles — reviewed."

---

## Rules

- **Never auto-edit skills or repos.** This skill produces a triage report and suggested actions. The user (or a follow-up `/claude-flow`, `useful-for`, or skill-creator session) does the actual edits.
- **Always file as reviewed.** Even "skip" verdicts get moved — the point is the inbox stays small.
- **One announce, then quiet.** No per-tool narration. Report results in the structured output, not in chatter.
- **If a note is a bare URL with no content:** fetch the URL via WebFetch first. If fetch fails, mark as "skipped — could not fetch" and file as reviewed.
- **If `useful-for` returns "skip" for all targets:** still include a one-line summary so the user sees why it was dropped.

---

## When NOT to use this skill

- User pastes a single article inline → use `useful-for` directly, no need to touch Mem.
- User wants to *add* something to Mem → that's `inbox-triage` or direct Mem tools.
- User wants a deep research dive on one article → use `synthesis-brief` or `research`.
