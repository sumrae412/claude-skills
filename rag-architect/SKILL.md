---
name: "rag-architect"
description: "Use when the user asks to design RAG pipelines, optimize retrieval strategies, choose embedding models, implement vector search, or build knowledge retrieval systems."
---

# RAG Architect

## Token Economy

Apply `token-economy` whenever this skill would otherwise trigger broad
exploration, repeated file reads, multi-file scans, or heavy reference
loading.

- Load only the phase, reference, or script needed for the current step.
- Prefer targeted search and line-range reads over whole-file slurping.
- Batch independent tool calls and keep narration/results tight.
- If the task is tiny or the file set is already known, apply the relevant
  patterns inline instead of loading extra material.

## Overview

RAG design toolkit for chunking, embedding/model selection, retrieval
architecture, evaluation, and production optimization.

This file is a router. Do not keep the whole RAG catalog resident.

## When to Use

- Designing a new RAG pipeline
- Choosing chunking, embeddings, or vector storage
- Tuning retrieval quality or latency
- Building evaluation loops for RAG quality
- Planning production hardening, caching, or safety controls

## Load Strategy

1. Identify the current design problem.
2. Load only the matching phase file from `phases/`.
3. Load only the reference or script that phase needs.
4. Prefer structured evaluators or design scripts when available.

Do not preload all chunking, model, and database guidance.

## Phase Map

1. `phases/phase-1-corpus-and-chunking.md`
2. `phases/phase-2-embeddings-and-retrieval.md`
3. `phases/phase-3-evaluation-and-quality.md`
4. `phases/phase-4-production-and-cost.md`

## Reference Map

- Chunking comparisons:
  `references/chunking_strategies_comparison.md`
- Embedding benchmarks:
  `references/embedding_model_benchmark.md`
- Evaluation methods:
  `references/rag_evaluation_framework.md`

## Script Map

- Pipeline design:
  `rag_pipeline_designer.py`
- Chunking optimization:
  `chunking_optimizer.py`
- Retrieval evaluation:
  `retrieval_evaluator.py`

## Session Rules

- Start from corpus shape and query behavior, not model brand names.
- Separate retrieval recall problems from answer-generation problems.
- Prefer the simplest architecture that meets recall, faithfulness, and
  latency goals.
- Tie every design choice to a measurable tradeoff.

## Deliverables

Produce only what the user needs:

- RAG architecture
- chunking strategy
- embedding / vector DB recommendation
- retrieval tuning plan
- evaluation plan
- production hardening plan

## Guardrails

- Do not optimize chunking, embeddings, and reranking all at once without
  evaluation.
- Call out when exact-match search, SQL, or a smaller retrieval pattern
  would beat RAG.
- Treat source attribution and hallucination control as first-class
  requirements.

## Out of Scope

This skill does NOT:
- Reduce LLM API spend on the generation calls inside RAG—use `llm-cost-optimizer`.
- Govern prompt versioning, evals, or A/B tests for the generator—use `prompt-governance`.
- Build/tune the Anthropic SDK code with prompt caching—use `claude-api`.
- Search the open web at query time—pair with `web-search-quality` if external sources are needed.
- Migrate an existing vector store to a new schema/provider—use `migration-architect`.
