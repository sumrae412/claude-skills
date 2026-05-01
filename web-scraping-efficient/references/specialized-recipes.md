# Specialized recipes

Load this when scraping Notion, LinkedIn jobs, YouTube, or another source with a known shortcut.

## Notion public pages

Notion pages render client-side from JSON, so you do **not** need a browser. The page exposes an internal API that returns the entire block tree:

- Endpoint: `POST https://www.notion.so/api/v3/loadPageChunk` with body `{"pageId": "<uuid-with-dashes>", "limit": 100, "cursor": {"stack": []}, "chunkNumber": 0, "verticalColumns": false}`.
- The page ID is the 32-hex string at the end of the URL; insert dashes to get the UUID form (`8-4-4-4-12`).
- The response has `recordMap.block.<id>.value` entries. Each block has a `type` (`header`, `sub_header`, `text`, `bulleted_list`, `callout`, `toggle`, `bookmark`, `quote`, etc.) and `properties.title`, which is a rich-text array: `[["plain text"], ["linked text", [["a", "https://..."]]]]`.
- **Walk every block type, not just headings and paragraphs.** Callouts, toggles, bookmarks, and quotes routinely contain links and important text that a heading-only walk misses. Recurse into block `content` arrays — nested children aren't in the top-level chunk.
- For long pages, paginate with `cursor.stack` from the previous response until `cursor.stack` is empty.

## LinkedIn job postings

LinkedIn aggressively blocks scrapers and requires login for most data, so the cheap, durable path is the **public guest job-view endpoint**:

- URL pattern: `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/<jobId>` where `<jobId>` is the numeric ID from a job URL (`/jobs/view/<jobId>`).
- Returns server-rendered HTML — no JS, no login.
- Selectors with `selectolax`:
  - **Title:** `h2.top-card-layout__title` or `h1` (fallback)
  - **Company:** `a.topcard__org-name-link` or `.topcard__flavor` (first `<a>`)
  - **Location:** `.topcard__flavor.topcard__flavor--bullet`
  - **Posted date:** `time.posted-time-ago__text` or `time[datetime]`
  - **Description HTML:** `div.show-more-less-html__markup` — pass to `trafilatura.extract` or `html2text` to get clean prose; this is the only field you'd ever need to clean rather than select.
  - **Seniority / employment type / function / industry:** `ul.description__job-criteria-list li` (each `<li>` has a `<h3>` label and `<span>` value).
- For search results pages, hit `https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=...&location=...&start=<N>` (pagination by 25). Returns a list of job cards with IDs you can then dereference.
- Be polite: 2–3 second delay between requests, set a real User-Agent. Don't try to log in or use authenticated endpoints — LinkedIn's ToS is explicit and enforcement is real.

**Output shape per job:** `{job_id, title, company, location, posted_date, description, seniority, employment_type, function, industries, url}`.

## YouTube video transcripts

The transcript is already a structured caption track — don't scrape the page, fetch the captions directly:

- Easiest path: `youtube-transcript-api` (`pip install youtube-transcript-api`).
  ```python
  from youtube_transcript_api import YouTubeTranscriptApi
  segments = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US"])
  # segments: [{"text": "...", "start": 0.0, "duration": 3.2}, ...]
  ```
  - `video_id` is the 11-char string after `v=` in the URL (or after `youtu.be/`).
  - Falls back gracefully across language codes; raises if no transcript exists.
- For metadata (title, channel, description, duration, publish date) use the `oEmbed` endpoint `https://www.youtube.com/oembed?url=<video_url>&format=json` for title and channel; or the YouTube Data API v3 `videos.list?part=snippet,contentDetails,statistics&id=<id>` if the user has an API key. Don't scrape the watch page — it's huge and JS-rendered.
- Output format choices:
  - **Plain text:** join segment texts with spaces. Smallest output, best for summarization.
  - **Timestamped:** keep `[hh:mm:ss] text` lines. Useful when the user wants to cite or jump to specific moments.
  - **Chapter-aligned:** if the description contains chapter markers, parse them and group transcript segments into chapters.

**Output shape per video:** `{video_id, title, channel, published_at, duration_seconds, transcript: [{start, text}], full_text}`.

## Adding new recipes

When you find another source that comes up repeatedly, add a recipe here with: the cheapest endpoint, the exact selectors or JSON path, the output shape, and any politeness/auth gotchas.
