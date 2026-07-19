# /articles triage ledger

One line per triaged item, appended at the end of every run (step 5). Checked at the top of step 2 — a title or canonical-URL match here means "already triaged": report the prior verdict in one line, archive the note, do NOT re-fetch or re-triage.

Why this exists: the same piece routinely gets captured twice (two newsletters, two weeks apart, different tracking redirects). Without a ledger, the second capture pays full triage cost — including a transcript pull for a video already transcribed — to reach the verdict we already had.

**Matching rules**
- Match on canonical URL first (exact), then on normalized title (lowercased, punctuation stripped) — a redirect URL never matches anything, so title is the workhorse for body-less captures.
- A match is a stop, not a hint: emit `**Already triaged** YYYY-MM-DD as <verdict> — <one-line why>`, add the note to the archive batch, move on.
- If the new capture plainly supersedes the old (the first was title-only, this one carries a full body), re-triage anyway and append a second ledger line noting the upgrade. Say so in the article's section.

**Format**

`- YYYY-MM-DD | <verdict> | <title> | <canonical URL or note_id>`

Verdict is one of `high-value`, `some-value`, `skip`. Append repeats and skips too — a skip that isn't recorded gets re-triaged forever, which is the exact cost this file removes.

<!-- entries below -->
