# Phase 2: Embeddings and Retrieval

Load `../references/embedding_model_benchmark.md` before running this
phase.

## Goal

Choose embedding models, retrieval strategy, and vector storage.

## Ask

- What quality, latency, and cost targets matter?
- Is the domain general, code-heavy, scientific, or multilingual?
- Do you need dense, sparse, hybrid, or reranked retrieval?
- What operational constraints exist for storage and scaling?

## Consider

- embedding dimension and speed/quality tradeoffs
- dense vs sparse vs hybrid retrieval
- reranking need
- vector store fit: Pinecone, Weaviate, Qdrant, Chroma, pgvector

Use `rag_pipeline_designer.py` when structured design output helps.

## Output

Retrieval architecture with model choice, retrieval mode, vector store,
and tradeoff rationale.
