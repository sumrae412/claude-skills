# Phase 3: Semantic Checks

Load `../../claude-flow/references/memory-injection.md` only if needed
to classify domains for contradiction analysis.

## Goal

Run the expensive semantic checks only in full mode.

## Checks

- contradictions across entries in the same domain

## Rules

- Only analyze domains with enough entries to make contradiction likely.
- Report conflicting files and excerpts.
- Do not auto-fix; manual review is required.

## Output

Contradiction findings with domain, conflicting entries, and brief
explanation.
