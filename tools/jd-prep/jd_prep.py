#!/usr/bin/env python3
"""jd_prep.py — Extract a LinkedIn job posting into a clean jd.md for resume-tailor.

Usage:
    ./jd_prep.py <linkedin-url> [--company NAME] [--output-dir DIR]

What it does:
    1. Pulls the job ID from the LinkedIn URL
    2. Fetches the HTML via LinkedIn's unauthenticated guest endpoint
    3. Extracts structured key points (title, company, location, required/preferred lists)
    4. De-duplicates repeated paragraphs and strips boilerplate
    5. Writes ~/Documents/resumes/<CompanySlug>/jd.md with key-points header + verbatim body

What it deliberately does NOT do:
    - LLM summarization of JD prose. resume-tailor Phase 1 needs verbatim text for ATS
      keyword scoring and reframing. The "summary" here is the structured header only.
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

GUEST_ENDPOINT = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

DEFAULT_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

# Common LinkedIn boilerplate paragraphs to strip from the description body
BOILERPLATE_PATTERNS = [
    r"^About the job\s*$",
    r"^Show more\s*Show less\s*$",
    r"^See who .* has hired for this role\s*$",
    r"^Apply\s*$",
]

# Heading keywords used to slot bullets into Required / Preferred / Responsibilities.
# Matched by startswith against the lowercased heading (alias map, not substring search —
# substring would misclassify "Preferred Experience" and similar).
SECTION_ALIASES = {
    "responsibilities": [
        "job duties and responsibilities",
        "duties and responsibilities",
        "responsibilities",
        "what you'll do",
        "what you will do",
        "what you'll lead",
        "what you will lead",
        "you will",
        "role",
        "duties",
        "job duties",
    ],
    "preferred": [
        "preferred qualifications",
        "preferred",
        "nice to have",
        "nice-to-have",
        "bonus",
        "exceptional candidates",
        "ideal candidate",
        "plus",
    ],
    "required": [
        "required qualifications",
        "required",
        "requirements",
        "qualifications and experience",
        "qualifications",
        "experience",
        "what you'll need",
        "what you need",
        "must have",
        "must-have",
        "you have",
    ],
}


def extract_job_id(url: str) -> str:
    """Pull the numeric job ID out of a LinkedIn /jobs/view/<id>/ URL."""
    m = re.search(r"/jobs/view/(\d+)", url)
    if not m:
        raise ValueError(f"No /jobs/view/<id>/ segment found in URL: {url}")
    return m.group(1)


def fetch_guest_html(job_id: str, timeout: float = 15.0) -> str:
    """Fetch the guest-endpoint HTML. Raises requests.HTTPError on non-200."""
    url = GUEST_ENDPOINT.format(job_id=job_id)
    resp = requests.get(url, headers={"User-Agent": DEFAULT_UA}, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def _first_text(soup: BeautifulSoup, selectors: list[str]) -> str:
    for sel in selectors:
        el = soup.select_one(sel)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    return ""


def parse_metadata(soup: BeautifulSoup) -> dict:
    """Extract title / company / location / comp from the topcard area."""
    title = _first_text(
        soup,
        [
            "h2.top-card-layout__title",
            "h1.top-card-layout__title",
            ".topcard__title",
            "h1",
            "h2",
        ],
    )
    company = _first_text(
        soup,
        [
            "a.topcard__org-name-link",
            ".topcard__org-name-link",
            ".topcard__flavor--black-link",
            "a[data-tracking-control-name='public_jobs_topcard-org-name']",
        ],
    )
    # Location is usually the second .topcard__flavor; scan candidates
    location = ""
    for el in soup.select(".topcard__flavor"):
        txt = el.get_text(strip=True)
        if txt and txt != company and not txt.lower().startswith("see who"):
            location = txt
            break

    # Comp / salary — LinkedIn surfaces this sporadically
    comp = _first_text(
        soup,
        [
            ".compensation__salary",
            ".salary",
            "[class*='salary']",
        ],
    )

    return {
        "title": title,
        "company": company,
        "location": location,
        "comp": comp,
    }


def parse_description_block(soup: BeautifulSoup) -> str:
    """Extract the main description HTML-to-text, preserving paragraph breaks."""
    candidates = [
        ".show-more-less-html__markup",
        ".description__text",
        ".jobs-description__content",
        "[class*='description']",
    ]
    for sel in candidates:
        el = soup.select_one(sel)
        if el:
            # Convert <br> and <li> into sensible text breaks before get_text.
            # Replace each <li> atomically with "- <text>\n" so bullet marker + text
            # stay on the same line after get_text(separator="\n") collapses things.
            for br in el.find_all("br"):
                br.replace_with("\n")
            for li in el.find_all("li"):
                li_text = li.get_text(separator=" ", strip=True)
                li.replace_with(f"- {li_text}\n")
            return el.get_text(separator="\n", strip=True)
    return ""


def strip_boilerplate(text: str) -> str:
    """Remove LinkedIn boilerplate lines and collapse whitespace."""
    kept = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        if any(re.match(pat, stripped, re.IGNORECASE) for pat in BOILERPLATE_PATTERNS):
            continue
        kept.append(line)
    text = "\n".join(kept)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def dedupe_paragraphs(text: str) -> str:
    """Drop exact-duplicate paragraphs (common LinkedIn bug: description repeats)."""
    paragraphs = re.split(r"\n\s*\n", text)
    seen: set[str] = set()
    out: list[str] = []
    for p in paragraphs:
        key = re.sub(r"\s+", " ", p.strip()).lower()
        if len(key) < 20:  # keep short lines (headings) even if duplicated
            out.append(p)
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append(p)
    return "\n\n".join(out).strip()


def _is_heading_like(line: str) -> bool:
    """Return True if line looks like a section heading (short, title-ish, or colon-terminated).

    Broader than the alias map — any heading-looking line should reset section tracking
    so bullets don't bleed from Required into an unclassified 'Skills' or 'Pay Ranges' block.
    """
    s = line.strip()
    if not s or len(s) > 80:
        return False
    if s.endswith(":"):
        return True
    if s.isupper() and len(s.split()) <= 8:
        return True
    words = s.split()
    if 1 <= len(words) <= 8:
        caps = sum(1 for w in words if w and w[0].isupper())
        if caps >= max(1, int(len(words) * 0.6)):
            return True
    return False


def _classify_heading(line: str) -> str | None:
    """Return 'required' / 'preferred' / 'responsibilities' if line matches the alias map, else None."""
    s = line.strip().lower().rstrip(":").rstrip()
    if len(s) > 80 or not s:
        return None
    for section, aliases in SECTION_ALIASES.items():
        for alias in aliases:
            if s == alias or s.startswith(alias + " ") or s.startswith(alias + ":"):
                return section
    return None


def extract_sections(text: str) -> dict[str, list[str]]:
    """Slot bulleted content under Required / Preferred / Responsibilities by scanning headings.

    Uses two-stage detection: (1) is this line heading-like at all? (2) if so, does it match
    a known section alias? Heading-like lines that don't match an alias reset current to None,
    so bullets under 'Skills' / 'Pay Ranges' / 'About Us' stop accumulating into the preceding
    classified section.
    """
    sections: dict[str, list[str]] = {"required": [], "preferred": [], "responsibilities": []}
    current: str | None = None

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        if _is_heading_like(line):
            current = _classify_heading(line)
            continue
        bullet_match = re.match(r"^\s*(?:[-*•]|\d+[.)])\s+(.*)", line)
        if bullet_match and current:
            item = bullet_match.group(1).strip()
            if item:
                sections[current].append(item)
    return sections


def slugify_company(name: str) -> str:
    """'Reed Smith' → 'ReedSmith'. Strip punctuation and spaces."""
    slug = re.sub(r"[^A-Za-z0-9]", "", name or "")
    return slug or "UnknownCompany"


def build_jd_md(*, url: str, meta: dict, body: str, sections: dict) -> str:
    captured = datetime.now(timezone.utc).date().isoformat()
    title = meta.get("title") or "Untitled"
    company = meta.get("company") or "Unknown"
    location = meta.get("location") or "—"
    comp = meta.get("comp") or "Not posted"

    lines = [
        f"# {title} — {company}",
        "",
        f"**Source:** {url}",
        f"**Captured:** {captured}",
        f"**Location:** {location}",
        f"**Comp:** {comp}",
        "",
        "---",
        "",
        "## Key Points",
        "",
    ]

    if sections["responsibilities"]:
        lines.append("### Top responsibilities")
        lines.append("")
        for item in sections["responsibilities"][:8]:
            lines.append(f"- {item}")
        lines.append("")

    if sections["required"]:
        lines.append("### Required")
        lines.append("")
        for item in sections["required"]:
            lines.append(f"- {item}")
        lines.append("")

    if sections["preferred"]:
        lines.append("### Preferred / Nice-to-have")
        lines.append("")
        for item in sections["preferred"]:
            lines.append(f"- {item}")
        lines.append("")

    if not any(sections.values()):
        lines.append("_No structured sections detected. See full description below._")
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## Full Description")
    lines.append("")
    lines.append(body)
    lines.append("")

    return "\n".join(lines)


MANUAL_FALLBACK_HINT = (
    "\nFallback: hand-write jd.md with this structure:\n"
    "  # <Title> - <Company>\n"
    "  **Source:** <URL>\n"
    "  **Captured:** YYYY-MM-DD\n"
    "  ---\n"
    "  ## Full Description\n"
    "  <paste the JD body here>\n"
)


@dataclass
class RunResult:
    url: str
    status: str  # "written" | "skipped" | "failed"
    path: Path | None = None
    reason: str = ""


def run(
    url: str,
    company_override: str | None,
    output_dir: Path,
    skip_existing: bool = False,
) -> RunResult:
    """Extract one JD. Returns a RunResult; raises only for programmer errors."""
    try:
        job_id = extract_job_id(url)
    except ValueError as e:
        return RunResult(url=url, status="failed", reason=f"bad URL: {e}")

    # Pre-check idempotency when we can guess the company slug after fetch.
    # Full idempotency check happens post-fetch (we need the slug). For skip_existing
    # batch callers, the savings here are modest; correctness first.

    try:
        html = fetch_guest_html(job_id)
    except requests.HTTPError as e:
        code = e.response.status_code if e.response is not None else "?"
        return RunResult(
            url=url,
            status="failed",
            reason=f"HTTP {code} from LinkedIn guest endpoint (posting may be closed or blocked)",
        )
    except requests.RequestException as e:
        return RunResult(url=url, status="failed", reason=f"network error: {e}")

    soup = BeautifulSoup(html, "html.parser")
    meta = parse_metadata(soup)
    if company_override:
        meta["company"] = company_override

    if not meta.get("company"):
        return RunResult(
            url=url,
            status="failed",
            reason="no company name in response (pass --company explicitly)",
        )

    raw_body = parse_description_block(soup)
    if not raw_body:
        return RunResult(
            url=url,
            status="failed",
            reason="no description block (LinkedIn layout may have changed)",
        )

    folder = output_dir / slugify_company(meta["company"])
    jd_path = folder / "jd.md"

    if skip_existing and jd_path.exists() and jd_path.stat().st_size > 200:
        return RunResult(
            url=url,
            status="skipped",
            path=jd_path,
            reason="jd.md already exists and is non-empty",
        )

    cleaned = strip_boilerplate(raw_body)
    deduped = dedupe_paragraphs(cleaned)
    sections = extract_sections(deduped)

    folder.mkdir(parents=True, exist_ok=True)
    jd_path.write_text(build_jd_md(url=url, meta=meta, body=deduped, sections=sections))
    return RunResult(url=url, status="written", path=jd_path)


def load_batch_file(path: Path) -> list[str]:
    """Read URLs from a file (one per line, # comments and blank lines ignored)."""
    urls: list[str] = []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def run_batch(
    urls: list[str],
    output_dir: Path,
    rate_limit_seconds: float = 1.0,
    skip_existing: bool = True,
) -> list[RunResult]:
    """Extract a batch of JDs with rate limiting and idempotent skipping."""
    results: list[RunResult] = []
    total = len(urls)
    for i, url in enumerate(urls, start=1):
        print(f"[jd_prep] [{i}/{total}] {url}", file=sys.stderr)
        result = run(url, company_override=None, output_dir=output_dir, skip_existing=skip_existing)
        results.append(result)
        marker = {"written": "✓", "skipped": "·", "failed": "✗"}[result.status]
        detail = str(result.path) if result.path else result.reason
        print(f"[jd_prep]   {marker} {result.status}: {detail}", file=sys.stderr)
        # Rate-limit between non-final requests; skip the delay after skipped (no HTTP call)
        if i < total and result.status != "skipped":
            time.sleep(rate_limit_seconds)
    return results


def print_batch_summary(results: list[RunResult]) -> None:
    written = [r for r in results if r.status == "written"]
    skipped = [r for r in results if r.status == "skipped"]
    failed = [r for r in results if r.status == "failed"]
    print(file=sys.stderr)
    print(
        f"[jd_prep] Summary: {len(written)} written · {len(skipped)} skipped · {len(failed)} failed",
        file=sys.stderr,
    )
    if failed:
        print("[jd_prep] Failures:", file=sys.stderr)
        for r in failed:
            print(f"[jd_prep]   - {r.url}: {r.reason}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract LinkedIn JD(s) to clean jd.md files for resume-tailor.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="LinkedIn job URL (must contain /jobs/view/<id>/)")
    group.add_argument(
        "--batch",
        type=Path,
        help="Path to a file of LinkedIn URLs (one per line; blank lines and # comments ignored)",
    )
    parser.add_argument(
        "--company",
        help="Override company name for folder slug (single-URL mode only)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.home() / "Documents" / "resumes",
        help="Base output directory (default: ~/Documents/resumes)",
    )
    parser.add_argument(
        "--rate-limit",
        type=float,
        default=1.0,
        help="Seconds to wait between requests in batch mode (default: 1.0)",
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="In batch mode, overwrite jd.md files that already exist (default: skip)",
    )

    # Accept positional URL for backward compatibility: if first argv isn't a flag,
    # treat it as --url.
    raw = sys.argv[1:]
    if raw and not raw[0].startswith("-"):
        raw = ["--url", raw[0]] + raw[1:]

    args = parser.parse_args(raw)

    if args.batch:
        if args.company:
            print("[jd_prep] --company is ignored in batch mode", file=sys.stderr)
        urls = load_batch_file(args.batch)
        if not urls:
            print(f"[jd_prep] No URLs found in {args.batch}", file=sys.stderr)
            return 1
        results = run_batch(
            urls,
            output_dir=args.output_dir,
            rate_limit_seconds=args.rate_limit,
            skip_existing=not args.no_skip_existing,
        )
        print_batch_summary(results)
        return 0 if any(r.status == "written" for r in results) else 2

    # Single-URL mode
    result = run(args.url, args.company, args.output_dir)
    if result.status == "written":
        print(f"Wrote: {result.path}")
        print(f"Next: invoke /resume-tailor on {result.path.parent}")
        return 0
    if result.status == "skipped":
        print(f"Skipped (already exists): {result.path}", file=sys.stderr)
        return 0

    # failed
    print(f"[jd_prep] Failed: {result.reason}", file=sys.stderr)
    print(MANUAL_FALLBACK_HINT, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
