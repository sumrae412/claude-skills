---
name: synthesis-brief
description: Synthesize multiple sources into one conflict-resolved brief. Use when the user pastes or points to several articles, papers, reports, documents, URLs, notes, or excerpts and asks for synthesis, consensus, contradictions, gaps, strongest evidence, or a concise research brief. Not for single-source summaries.
---

# Synthesis Brief

## Purpose

Turn multiple sources into one useful judgment. Do not summarize source-by-source unless the user explicitly asks; compare claims across sources, resolve conflicts, and separate verified consensus from single-source assertions.

## Inputs

Require:

- topic or decision context
- at least two sources, pasted or retrievable

If sources are links or current facts matter, fetch/verify them before synthesis. If a source cannot be accessed, say so and synthesize only the available material.

## Workflow

1. Identify each source, author/publisher, date, evidence type, and likely credibility.
2. Extract claim-level notes, not article summaries.
3. Group claims into consensus, conflict, and missing-context buckets.
4. Mark single-source claims as `unverified`.
5. Explain the most credible source briefly: evidence quality, recency, expertise, methodology, and conflicts of interest.
6. Produce the requested brief within the user's word limit. Default maximum: 600 words.

## Output

Use this structure by default:

1. **Core Consensus** - 3-5 points all or most credible sources support.
2. **Key Conflicts** - where sources disagree and the likely reason.
3. **Critical Gaps** - important issues none of the sources adequately cover.
4. **Strongest Claim** - the single best-supported insight across sources.
5. **Actionable Takeaway** - one concrete thing the user should do, decide, or investigate next.

## Rules

- Lead with the answer, not a bibliography.
- Do not flatten disagreement into false consensus.
- Do not treat recency as credibility by itself.
- Quote only short snippets when needed to anchor a disputed claim.
- Label uncertainty plainly: `verified`, `inferred`, `unverified`, or `not covered`.
- If evidence is too weak for a definitive takeaway, say that directly and recommend the next source type needed.
