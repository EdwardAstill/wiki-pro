---
title: "When to Add Embedding-Based Retrieval"
slug: "retrieval-when-to-embed"
tags: ["retrieval", "embeddings", "tradeoffs"]
summary: "Add embedding-based retrieval only when lexical search demonstrably fails — well-structured wikis with strong headers rarely hit this ceiling."
related: ["retrieval-header-ranking", "retrieval-ripgrep-patterns"]
updated: "2026-04-21"
---

# When to Add Embedding-Based Retrieval

Embedding-based retrieval is an optional upgrade, not a default component — lexical search over well-structured wiki-pro notes with author-written headers and summaries performs at a level that makes embedding infrastructure unnecessary for most wikis.

## Why Lexical Search Works Well for Structured Wikis

Author-written headers and summaries ARE the semantic signal. A well-named `##` header like `## Mechanism of BM25 Term Frequency Scoring` already encodes the semantic intent that an embedding model would need to infer from body text. When every note follows [[spec-headers]] discipline and every `summary:` follows [[spec-summaries]] discipline, the lexical index built from those fields is a high-quality semantic index written in natural language — not bag-of-words keyword matching. The [[retrieval-header-ranking]] scoring model weights author-declared topic signals (headers, titles) above body text precisely because of this.

## The Failure Mode That Justifies Adding Embeddings

Lexical search fails when a wiki has high synonym density: the same concept is referred to by five different terms across different notes, none of which appears in the others' headers. Example: if one note uses "chunk", another "segment", another "excerpt", another "passage", and another "retrieval unit" — all meaning the same thing — a query for any one of these terms misses the others. This is a vocabulary consistency failure (see [[authoring-anti-patterns]] on synonym drift) that is better fixed by authoring discipline than by adding embedding infrastructure. If the vocabulary cannot be made consistent (cross-team wikis, domain jargon with genuine synonyms), embeddings become justified.

## Cost of Embeddings

Embedding infrastructure adds four costs: (1) **Index build time** — every note must be chunked, embedded, and stored at initial build; (2) **Dependency weight** — an embedding model (even a small one like `all-MiniLM-L6-v2` at 80 MB) adds a large binary dependency; (3) **Staleness** — the vector store must be re-embedded on every note update, not just re-indexed with lightweight frontmatter parsing; (4) **Debuggability** — lexical ranking is deterministic and explainable (`title match, weight 10`); embedding similarity scores are opaque (cosine distance 0.83 — between what and what?).

## The Measurement Gate

Before adding embeddings: run `wiki query` on 20 representative questions that real users or LLMs would ask of this wiki. If fewer than 7 of the 20 return the correct note as the top hit, investigate whether the failure is authoring quality (wrong headers, missing summaries) or vocabulary mismatch. Fix authoring quality first. If vocabulary mismatch accounts for >30% of misses after authoring fixes, embeddings are justified. This is the only legitimate trigger.

## Adding Embeddings Without Breaking the Lexical Path

If adding embeddings: use `wiki index --embed` to build the vector store separately from the lexical index. The `wiki query` command defaults to lexical; `wiki query --semantic` uses the vector store; `wiki query --hybrid` combines both with RRF (Reciprocal Rank Fusion) reranking. The lexical path remains the default and is never disabled — this preserves debuggability and zero-dependency fallback when the embedding model is unavailable or stale.
