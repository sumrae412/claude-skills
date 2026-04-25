# jd-prep

Extract a LinkedIn job posting into a clean `jd.md` ready for `resume-tailor`.

## Usage

### Single URL

```bash
./jd_prep.py https://www.linkedin.com/jobs/view/4403649158/
# or equivalently:
./jd_prep.py --url https://www.linkedin.com/jobs/view/4403649158/
# → writes ~/Documents/resumes/Deltek/jd.md

./jd_prep.py --url https://www.linkedin.com/jobs/view/4398546943/ --company ReedSmith
# → writes ~/Documents/resumes/ReedSmith/jd.md (company override for folder slug)

./jd_prep.py --url <url> --output-dir /tmp/test
# → custom output base
```

### Batch mode

```bash
./jd_prep.py --batch urls.txt
# → reads URLs (one per line; blank lines and # comments ignored)
# → rate-limited at 1 req/sec (configurable with --rate-limit)
# → skips companies that already have jd.md (override with --no-skip-existing)
# → prints summary: "N written · M skipped · K failed"
```

Example `urls.txt`:
```
# Today's target batch
https://www.linkedin.com/jobs/view/4403649158/
https://www.linkedin.com/jobs/view/4398546943/
https://www.linkedin.com/jobs/view/4402602064/
```

Then invoke `/resume-tailor` pointing at a single generated folder, or `/jd-screener` to triage the batch of folders.

## What it does

1. Extracts the numeric job ID from the LinkedIn URL.
2. Fetches the unauthenticated guest endpoint (`/jobs-guest/jobs/api/jobPosting/<id>`).
3. Parses structured metadata (title, company, location, comp) from the topcard.
4. Classifies bullets under Required / Preferred / Top responsibilities when heading vocabulary matches the alias map.
5. Strips LinkedIn boilerplate ("About the job", "Show more Show less").
6. De-duplicates exact-match paragraphs (LinkedIn sometimes double-renders descriptions).
7. Writes `~/Documents/resumes/<CompanySlug>/jd.md` with a structured key-points header + verbatim full description.

## What it does NOT do

- **No LLM summarization of JD prose.** `resume-tailor` Phase 1 needs verbatim text for ATS keyword scoring and Phase 2 reframing. The "summary" is the structured metadata header only.
- **No auto-invocation of resume-tailor.** The script writes `jd.md` and exits. Chain it by calling the skill yourself (in Claude Code, via Bash + skill invocation).
- **No authenticated scraping.** Guest endpoint only. Some postings (closed/internal) may not be accessible; fall back to manual paste in that case.

## Output shape

```markdown
# <Title> — <Company>

**Source:** <URL>
**Captured:** YYYY-MM-DD
**Location:** ...
**Comp:** ...

---

## Key Points

### Top responsibilities
- ...

### Required
- ...

### Preferred / Nice-to-have
- ...

---

## Full Description

<verbatim deduplicated body>
```

## Dependencies

- Python 3.10+
- `requests`
- `beautifulsoup4`

## Failure modes

| Exit code | Meaning | Recovery |
|---|---|---|
| 1 | URL doesn't contain `/jobs/view/<id>/` | Check the URL format |
| 2 | LinkedIn returned non-200 (often 403 or 429) | Wait + retry, or paste manually |
| 3 | Description block couldn't be extracted (layout changed) | Paste manually; report if recurring |

When the script fails, fall back to hand-writing `jd.md` from a paste — same shape as the auto-generated file.

## Integration with skills

### With `/jd-screener` (batch triage)

```bash
./jd_prep.py --batch ~/Documents/jd-batches/2026-04-24.txt
# → ~/Documents/resumes/<Co>/jd.md per URL, idempotent skip on existing
```

Then invoke `/jd-screener` and point it at the company folders. Phase 2 dedupe + fetch is short-circuited because `jd.md` files already exist on disk — the screener moves straight to scoring + triage.

### With `/resume-tailor` (single JD)

```bash
./jd_prep.py https://www.linkedin.com/jobs/view/<id>/
# → ~/Documents/resumes/<Co>/jd.md
```

Then invoke `/resume-tailor` pointing at the generated folder. The skill's §0/§0.1 input-validation is satisfied — URL retained in the `jd.md` header, full JD body verbatim below it.

### Token efficiency

Replacing inline JD pastes with jd-prep saves ~3-5K tokens per JD on the orchestrator side. The full JD text lives on disk; downstream phases load only the part they need (key points for scoring, full body for keyword scanning) instead of carrying the entire posting in conversation context.

## Notes

- **Terms of Service.** LinkedIn's ToS prohibits automated scraping. The guest endpoint is a semi-public preview URL; using it for your own job-search workflow is low-risk practically but not zero-risk legally. Low volume, personal use only.
- **Section classification is heuristic.** Headings that aren't in the alias map (e.g., "Skills", "Essential Job Functions", "Pay Ranges") reset the current section to None, so bullets under them are excluded from Key Points rather than bleeding into the preceding classified section. The full text is always preserved in the Full Description block.
- **Company slug** is derived by stripping non-alphanumerics from the LinkedIn-reported company name (e.g., "Reed Smith LLP" → `ReedSmithLLP`). Use `--company` to override for folder naming.
