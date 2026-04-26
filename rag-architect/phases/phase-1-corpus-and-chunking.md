# Phase 1: Corpus and Chunking

Load `../references/chunking_strategies_comparison.md` before running
this phase.

## Goal

Choose a chunking strategy that matches the corpus shape and query style.

## Ask

- What document types are in the corpus?
- How structured are they?
- What kinds of questions will users ask?
- Are metadata, tables, or section boundaries important?

## Consider

- fixed-size
- sentence-based
- paragraph-based
- semantic
- recursive
- document-aware chunking

Use `chunking_optimizer.py` when testing chunk size and overlap is useful.

## Output

Chunking recommendation with chunk size, overlap, boundary rules, and
expected tradeoffs.
