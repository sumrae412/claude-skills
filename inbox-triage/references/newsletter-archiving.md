### G. Curated newsletters — auto-archive to Mem (The Code, a16z Speedrun)

Trigger when the email's `From` matches one of:
- `thecode@mail.joinsuperhuman.ai` (The Code)
- `speedrun@substack.com` (a16z Speedrun)

These are auto-archived; **do not score, do not propose a task, do not draft
a reply.** They bypass Steps 3, 4.A–F, and 6.

**Action:**

1. **Extract article links** from the email body. Include only links that
   point to substantive article/post pages.
2. **Exclude advertisement and chrome links.** Skip:
   - Anything inside a section labeled `Sponsor`, `Sponsored`,
     `Advertisement`, `A Word From Our Sponsor`, `Together With`, or
     `Brought to you by`.
   - Unsubscribe / preferences / "manage subscription" links.
   - Social-share links (`twitter.com/intent`, `facebook.com/sharer`,
     `linkedin.com/sharing`, `mailto:`).
   - Footer / legal links (privacy, terms, contact, view-in-browser).
   - Substack chrome: `Subscribe`, `Recommend`, `Like`, `Comment`, `Share`,
     `Restack`, profile links to `substack.com/@...`.
   - Cross-promo blocks ("More from Superhuman", "More from a16z").
   - Tracking-pixel / image-link beacons.
3. **For each remaining link**, fetch the article via the
   `web-scraping-efficient` skill (do **not** call `WebFetch` directly —
   newsletter article pages are typically large and often JS-rendered,
   exactly the case the skill exists to handle). Extract: title, author (if
   present), publish date (if present), and main body text. Discard nav,
   sidebar, comments, related-posts.
4. **Idempotency check** — before creating a note, search Mem for an
   existing note containing the article URL (`search_notes` with the URL as
   query). If a match exists, skip that link.
5. **Create one Mem note per article** via `create_note`:
   - **Title** (first line of content): the article title.
   - **Body**: blank line, then a metadata block:
     ```
     Source: [The Code | a16z Speedrun]
     Author: <author or "unknown">
     Published: <YYYY-MM-DD or "unknown">
     URL: <article URL>
     Archived: <today's YYYY-MM-DD>

     ---

     <main article body>
     ```
6. **Add each new note to the `Claude articles` collection** (id
   `421a7805-5221-4117-8425-da2dc72a2aa1`) via `add_note_to_collection`. Do
   NOT add to `Claude articles — reviewed` — that's the processed-side
   collection.
7. **Mark the email as auto-handled** — count toward `Articles archived` in
   Step 8's log. No proposal, no draft, no Pending task.

**Hard rules:**

- **Never fetch a non-article URL.** If link extraction is ambiguous (e.g.
  tracking-redirect domains like `link.mail.joinsuperhuman.ai/...`), follow
  one redirect to resolve the destination, then apply the exclusion filter
  against the destination URL — not the redirect host.
- **Per-newsletter cap: 10 articles.** If a newsletter has more, archive the
  first 10 in document order and surface the overflow count in Step 9.
- **On fetch failure** (timeout, 404, paywall, blocked) — skip silently, do
  not retry. Surface a count of failed fetches in Step 9 ("3 articles
  couldn't be fetched").
- **No PII / credentials in note bodies.** Strip query-string tracking
  params (`utm_*`, `?ref=`, `?src=`) from the saved URL before saving.
- **Don't auto-promote to `Claude articles — reviewed`** — that collection
  is for notes Summer has actually read.
