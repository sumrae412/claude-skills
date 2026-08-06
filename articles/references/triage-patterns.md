# /articles triage patterns

Class-level skip/keep patterns learned from prior runs. Loaded at step 2 to pre-filter the obvious cases; appended at step 5 when a run surfaces a recurring pattern.

This is the Level 6 feedback loop from [`maturity-progression.md`](maturity-progression.md): without it, every verdict disappears into the archive and the next run re-derives the same judgment from scratch.

**Promotion bar.** A pattern earns a line only when the same *class* of item drew the same verdict across **3+ instances spanning 2+ runs** — check [`triage-ledger.md`](triage-ledger.md) for the prior instances before writing one. One bad newsletter is not a pattern; three Codex tutorials that all skipped is.

**How to apply an entry**
- A title matching a `skip` pattern gets an auto-skip verdict at the pattern's stated confidence, no fetch — still archived, still one line in the rollup so the user can see and challenge the pre-filter.
- A title matching a `keep` pattern is triaged normally but flagged `pattern-match: likely high-value`, so a body-less capture in a known-good class doesn't get under-called.
- Patterns are hints, not law. A title that obviously breaks its pattern gets normal triage — and if a pattern misfires twice, delete the line rather than adding exceptions to it.
- Patterns never override a source-read. A code-repo or video link still gets its source-read/transcript-read even under a `skip` pattern; the pattern only saves the fetch on articles and newsletters.

**Format**

`- YYYY-MM-DD | skip|keep | <pattern> | evidence: <N items across M runs>`

<!-- entries below -->
