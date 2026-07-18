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
| Claude articles | `f4003b7e-0e22-4a3a-b6b3-4108f11c4b9d` | The only inbox this skill triages. (Corrected 2026-07-18 — the old ID `089f8552-6db8-47e4-899a-f092873e467c` pointed at a now-empty duplicate collection with the same title; verify with `get_collection` if a run ever finds 0 notes.) |

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

Call `mcp__a5ce767d-48cc-4ac0-b83a-4a0e2432ee4a__list_notes` with `collection_id = f4003b7e-0e22-4a3a-b6b3-4108f11c4b9d` (Claude articles). Subtract anything also in the reviewed collection — those are done.

Do NOT pull from any other collection. If a note appears in both Claude articles and another collection (e.g. Article Collection), it is still in scope, but only because of its Claude-articles membership.

**Queue-size routing:**

- **≤10 notes** → serial triage in the main thread (steps 2–5 below). Below this size, serial is cheaper than fan-out and the cache stays warm.
- **11–40 notes** → **swarm mode** (step 1b): group by theme, one agent per group, all in parallel. Announce the grouping plan in one line, then proceed — no confirmation needed.
- **>40 notes** → ask before burning the fan-out ("62 unread — swarm-process all, or newest 40?").

### 1b. Swarm mode — group, fan out, synthesize

For large queues, don't triage serially and don't dispatch one agent per note — group first, then one agent per group.

1. **Group in the main thread, from titles alone.** `list_notes` already returned titles — cluster them into 3–6 thematic groups of ~4–8 notes each (e.g. "agent orchestration", "prompting/evals", "product/startup", "misc"). Do NOT fetch note bodies to group; titles are enough, and a "misc" group is a legitimate bucket for stragglers.
2. **One agent per group, all dispatched in ONE parallel block.** Use a `general-purpose` executor with an explicit down-tier model override (sonnet) — never let a swarm agent inherit the orchestrator's model. Each brief is self-contained and MUST include:
   - The group's note ids + titles, the full Targets list, and the verdict rubric + per-article output format from steps 2–3 (agents fetch bodies themselves via `get_note` — they can load Mem tools through ToolSearch).
   - The triage-mode rules that bite downstream, restated: body-less captures = LOW-confidence title-level verdicts; known-failure tracking links (Half Baked, Beehiiv) = never fetch; code-repo links = the agent does the source-read itself, inline in its own foreground; video links = the agent pulls the transcript itself (`watch` skill, `--detail transcript`, canonical URL only), inline in its own foreground.
   - `[read-only]` — read, fetch, and assess only. NO archiving, no collection writes, no repo edits, no PRs. Findings come back to the orchestrator.
   - *"Work in your own foreground; do NOT spawn background sub-agents."*
   - *"Return results immediately after the tool call that found them. Do NOT emit commentary between tool calls."* Plus a per-article report cap (~120 words).
3. **Synthesize in the main thread.** Collate group reports into the step-3 per-article sections and the step-4 rollup. Dedup across groups: the same article captured twice gets one section; two groups proposing edits to the same target skill/file get their "next action" merged so the user sees one edit, not two.
4. **Archiving stays in the main thread.** Swarm agents never touch collections — after synthesis, the orchestrator runs step 5's Batch A/B over the full note-id list exactly as in a serial run.

Why grouping instead of per-note fan-out: each dispatch re-pays its briefing + tool-discovery overhead (fan-out costs ~7–10× a serial pass per agent), and related articles triaged together produce coherent, non-duplicative verdicts against the same target.

### 2. Triage each note via `useful-for`

For each unread note:

1. Fetch the note content (`get_note`).
2. Run the `useful-for` mental model (see `useful-for/SKILL.md`) against the priority target list above. Five modes:
   - **Inline triage** (default for Mem notes): Mem already produces structured summaries (TL;DR, Key Points). For those, apply the useful-for rubric inline — no subagent dispatch needed. Faster, keeps context.
   - **Subagent dispatch**: only when the note is raw long-form content (full article body pasted, transcript, paper) with no Mem summary. Then invoke useful-for as a proper skill call so the heavy lifting happens out of the main thread.
   - **Body-less capture** (bare title + source + tracking-redirect URL, no Mem TL;DR/Key Points — currently the dominant shape): there is nothing to fetch (redirects are dead — see Rules) and nothing to summarize. Triage from the title at LOW confidence and route to the verify-before-author rule below for any item you'd otherwise call "high-value." If the first few notes in a run are all body-less, say so once at the top of the run ("most captures are title-only — verdicts are title-level guesses; I'll verify any high-value pulls against canonical sources before acting") so the user reads the rollup with correct confidence.
   - **Video-link transcript-read** (YouTube, Vimeo, X/TikTok video, Loom, anything yt-dlp supports): when a note links a video AND it plausibly maps to one of the priority targets, the Mem capture is NOT sufficient — a video capture carries title + description only; the actual content lives in the audio. Pull the transcript before the verdict via the `watch` skill ([claude-video plugin](https://github.com/bradautomates/claude-video)) in transcript-only mode:

     ```bash
     SKILL_DIR=$(ls -d ~/.claude/plugins/cache/claude-video/watch/*/skills/watch | sort -V | tail -1)
     python3 "$SKILL_DIR/scripts/watch.py" "<canonical-video-url>" --detail transcript --no-whisper
     ```

     `--detail transcript` fetches captions only — no video download, no frames, no API key needed (verified 2026-07-11 on a live run: 19s video → 6 timestamped segments via captions). Rules that bite:
     - **Canonical URL only.** Never feed the Mem tracking redirect to yt-dlp (dead — see the known-failure-link rule). If the capture has only a dead redirect, find the video by title first (web search); if that fails, triage title-level at LOW confidence.
     - **Length routing:** ≤ ~20 min → read the transcript inline. Longer → dispatch a subagent (same *work in your own foreground; do NOT spawn background sub-agents* brief as the code-repo mode) to run the command, read the transcript, and return a concrete assessment — keep the full transcript out of the main thread. `--start`/`--end` scope a section when the note names one.
     - **No captions:** keyless installs have no Whisper fallback, so a caption-less video returns an empty transcript. Don't fake it — fall back to title-level LOW confidence and say so in the article's section.
     - **Plugin missing** (the `ls` above finds nothing): install it (`claude plugin marketplace add bradautomates/claude-video && claude plugin install watch@claude-video`, then run its `scripts/setup.py` once — it auto-installs `yt-dlp`/`ffmpeg` via brew), or triage title-level at LOW confidence and name the gap.
   - **Linked code-repo source-read** (GitHub repos, installable skills, code packages): when a note links a GitHub repo, an installable agent skill, or any source-code target AND it plausibly maps to one of the priority targets above, the Mem summary is NOT sufficient — dispatch a subagent to read the actual source. The dispatch brief MUST include: *work in your own foreground; do NOT spawn background sub-agents* (per Henry's Foreground-execution rule) — else the subagent returns phantom "I'll report back once my background child completes" placeholder text and nested children report late under new task-ids (validated 2026-07-03). The subagent should: (a) fetch the repo tree (`gh api repos/<owner>/<repo>/git/trees/HEAD?recursive=1 | jq '[.tree[].path]'`), (b) read README and key files via `gh api repos/<owner>/<repo>/contents/<path>` (pipe through `base64 -d`), or use `WebFetch` for non-GitHub skill sites; (c) gap-check against the mapped target repo (what's missing in our skills/CLAUDE.md that this repo has); (d) return only a concrete, file-cited assessment — keep raw source OUT of the main thread. Apply this mode only when: the link is a GitHub repo or installable skill AND it maps to one of our active targets. For borderline cases (a public repo that maps to nothing we own), an inline summary pass is fine — note the uncertainty, don't burn a source-read.
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

**Batch B** — after Batch A returns successfully, for every `note_id`, call `remove_note_from_collection` with `collection_id = f4003b7e-0e22-4a3a-b6b3-4108f11c4b9d` (Claude articles) ONLY. Do not remove from any other collection the note happens to be in. All in one parallel block.

Every triaged note ends in the reviewed archive — including "skip" verdicts. The point of archiving is to keep the inbox small, not to reward high-value pulls. Confirm in the closing line: "Archived N notes to Claude articles — reviewed."

---

## Rules

- **Never auto-edit skills or repos.** This skill produces a triage report and suggested actions. The user (or a follow-up `/claude-flow`, `useful-for`, or skill-creator session) does the actual edits.
- **Always file as reviewed.** Even "skip" verdicts get moved — the point is the inbox stays small.
- **One announce, then quiet.** No per-tool narration. Report results in the structured output, not in chatter.
- **If a note is a bare URL with no content:** fetch the URL via WebFetch first. If fetch fails, mark as "skipped — could not fetch" and file as reviewed.
- **Known-failure tracking links — don't burn fetches on them.** Mem's newsletter captures truncate redirect URLs: Half Baked (`elink2fb.mail.gethalfbaked.com`) returns HTTP 400 and Beehiiv/The Neuron (`link.mail.beehiiv.com`) returns 403 on every fetch attempt. Skip the fetch, triage from the title at reduced confidence, and cite the newsletter issue (source + date are in the note body) as the path to the full piece. Validated 2026-06-10 across 4 fetch attempts in one run.
- **Title-level verdicts on body-less captures over-rate systematically — verify the canonical source before acting on any "high-value" pull.** When a note is bare `title + source + tracking-redirect URL` with no Mem TL;DR/Key-Points body (the common case — most of the inbox can be body-less), the triage verdict is a title-level guess at reduced confidence, NOT an actionable call. Before authoring any repo edit from a "high-value" item: (1) fetch the CANONICAL source (the publisher's own URL, not the dead Mem redirect), and (2) gap-check against the target skill/CLAUDE.md — the claim may already be covered, or its numbers may be unsourced. Validated 2026-06-17: of 4 title-level "high-value" calls, 2 collapsed on verification (one already fully covered by repo CLAUDE.md + carried unsourced figures absent from canonical Anthropic docs; one downgraded to a low-urgency prior-art note). Pull phase = verify-then-author, never author-from-title.
- **A Mem summary of a code repo is necessary triage but not sufficient — code-repo / installable-skill links get a source-read before a final verdict, because summaries systematically under-surface adoptable detail.** The inline and body-less modes are correct for articles, tweets, newsletters, and blog posts; they are wrong for repos. Validated 2026-06-26: summary-level triage rated four code repos "some-value/already-covered"; source-reads found a bug-fix repro-loop gate (now [claude-skills #176](https://github.com/sumrae412/claude-skills/pull/176)), a new `codebase-design` skill ([#177](https://github.com/sumrae412/claude-skills/pull/177)), a review-pr two-axis structural split ([#178](https://github.com/sumrae412/claude-skills/pull/178)), and design-polish specs ([#179](https://github.com/sumrae412/claude-skills/pull/179)) — none visible in the summaries. Do NOT source-read news articles, tweets, or blog posts; their Mem summary is the right tool and dead redirect URLs cannot be fetched (the known-failure-link rule still governs those). Video captures are the second exception: they get a transcript-read (step 2's video-link mode), because a Mem capture of a video holds the title/description only — the content is in the audio, and captions are a free fetch.
- **If `useful-for` returns "skip" for all targets:** still include a one-line summary so the user sees why it was dropped.

---

## When NOT to use this skill

- User pastes a single article inline → use `useful-for` directly, no need to touch Mem.
- User wants to *add* something to Mem → that's `inbox-triage` or direct Mem tools.
- User wants a deep research dive on one article → use `synthesis-brief` or the built-in `deep-research`.

---

## References

- [`references/maturity-progression.md`](references/maturity-progression.md) — where `/articles` sits on Jason Liu's Six Levels framework and what Level 5 (drafts actions) / Level 6 (memory-vault feedback) would look like here.
