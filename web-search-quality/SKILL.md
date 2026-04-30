---
name: web-search-quality
description: Use when running WebSearch, WebFetch, or browser navigation on the open web, or before citing/paraphrasing any external source. Covers source-tier filtering, publish-date thresholds by topic type, and triangulation before stating external info as fact.
---

# Web Search Quality

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad exploration, repeated file reads, multi-file scans, or heavy reference loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant patterns inline instead of loading extra material.


## Overview

Web results are noisy — SEO farms, stale tutorials, AI-generated summary sites, and single-author opinions all rank on page one. Unfiltered citations degrade answer quality and introduce wrong facts. This skill sets minimum quality gates for any web-sourced claim.

## When to Use

- Any `WebSearch`, `WebFetch`, or `browser_navigate` against the open web
- Before citing, paraphrasing, or acting on an external source
- When verifying a factual claim (version numbers, API signatures, CLI flags, prices, dates)
- When fetching docs for a library, API, or framework version

**Skip** for: the user's own URLs, internal/company docs, or structured registry endpoints (npm/PyPI/crates.io metadata JSON).

## Source Tier Ladder

Prefer in order. Drop to a lower tier only when higher tiers miss.

| Tier | Examples | Trust |
|---|---|---|
| 1 — Primary | Official docs, vendor changelogs, RFCs/specs, source code, first-party blogs | High |
| 2 — Reputable | Major outlets with editorial standards, established tech publications, well-known maintainer blogs | Medium-high |
| 3 — Community | Stack Overflow (weight by date + votes), GitHub issues/discussions, Reddit with linked primary sources | Medium |
| 4 — Low signal | SEO content farms, AI-generated summary sites, undated/unauthored tutorials, listicles | Avoid |

**Domain red flags:** no publish date, no author, copy-paste of another site's text, keyword-stuffed domain, no "last updated" anywhere.

## Freshness Thresholds

Capture the publish/update date of every cited source. Re-verify (or drop) if older than:

| Topic | Stale after |
|---|---|
| Active security advisories, CVEs, zero-days | 7 days (active) / 90 days (general) |
| Framework/library APIs (JS, Python web frameworks) | 6–12 months |
| Cloud/SaaS pricing, UI paths, console screenshots | 6 months |
| LLM API pricing, model catalogs (Anthropic/OpenAI/Google) | 30 days — verify at start of every cost eval |
| Language syntax and stdlib | 2–3 years |
| Algorithms, data structures, math | Rarely stale |
| Historical facts | Evergreen |

If the page has no visible date, treat it as unknown-age: either skip, or mark the claim "date unverified" in your response so the user can judge.

Calibrate against today's date, not training cutoff. A "2024 guide" may already be stale.

**Rule for cost analyses:** Before committing a pricing premise to a plan or cost estimate, triangulate against the provider's live pricing page AND a second provider surface (docs, console, API response). LLM vendor prices can move 50%+ between plan authoring and execution (Anthropic Opus 4.7 dropped 66% in ~6 weeks, Apr 2026). Record the verification date alongside the rates in code (e.g. `# verified YYYY-MM-DD against <url>`).

## Triangulation Rule

For any non-trivial factual claim:

1. Find it in a Tier 1 source. Done.
2. If only Tier 2/3 sources exist, require **≥2 independent sources that agree** (not two sites quoting the same blog post).
3. If sources disagree, **surface the conflict** to the user instead of silently picking one.

A single blog post is not evidence. A single forum answer is not evidence.

## Quick Reference

Before stating X as fact from the web, answer:

- What tier is the source?
- When was it published or last updated?
- Is there an independent second source that agrees?
- Does the version/release in the source match the user's context?

If any answer is shaky, say so in your response: `per [source], published [date]` or `couldn't confirm across independent sources — flagging as unverified`.

## Common Mistakes

- **Grabbing the first result.** Rank ≠ quality. Check tier first.
- **Ignoring publish date** on tutorials for fast-moving libraries — 2021 React advice is often wrong in 2026.
- **Treating old accepted answers as current.** Stack Overflow answers from 2015 often describe dead APIs.
- **Citing AI summary sites** that paraphrase without attribution — go to the source they paraphrased.
- **Silently resolving disagreement.** If sources conflict, surface it; don't pick.
- **Forgetting to date-stamp in the reply.** Users can't assess freshness of claims you don't date.

## Out of Scope

This skill does NOT:
- Run the actual WebSearch/WebFetch calls—it sets quality gates; you call the tools.
- Search GitHub code, repos, issues, or PRs—use `github-search`.
- Fetch/cache versioned API docs for coding tasks—use `fetch-api-docs`.
- Validate facts inside the user's own repo or internal docs—skip the gates for those.
- Replace primary-source verification when stakes are legal/medical/financial—escalate to `gdpr-dsgvo-expert`, `fda-consultant-specialist`, or qualified counsel.

## Red Flags — Stop and Re-search

- Stating a version number, API signature, CLI flag, or price without a Tier 1 check
- Single-source citation for a non-trivial claim
- Source date is old but you're citing it anyway because it "looks right"
- The source is paraphrasing another source you haven't opened
- You can't find a publish date and are citing the claim as fact anyway

**All of these mean: re-search or mark the claim as unverified.**
