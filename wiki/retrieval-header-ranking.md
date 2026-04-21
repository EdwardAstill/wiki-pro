---
title: "wiki-pro Query Ranking Algorithm"
slug: "retrieval-header-ranking"
tags: ["retrieval", "ranking", "query"]
summary: "wiki-pro query ranking is deterministic and weighted: title matches score 10, ## headers 5, ### 3, tags 3, summary 2, body 1 — no ML required."
related: ["retrieval-ripgrep-patterns", "retrieval-when-to-embed", "spec-headers"]
updated: "2026-04-21"
---

# wiki-pro Query Ranking Algorithm

wiki-pro ranking is deterministic, weighted lexical scoring — no vector index, no model inference, no per-query ML — which means results are reproducible, debuggable, and correct for well-structured notes.

## Full Scoring Table

| Field | Weight per term match |
|---|---|
| `title:` (frontmatter) | 10 |
| `#` header (body) | 10 |
| `##` header | 5 |
| `###` header | 3 |
| `tags:` list | 3 |
| `summary:` | 2 |
| Body text | 1 |

Each weight applies per matched query term, per note. A note with two `##` headers matching the same query term scores 10 (5 + 5), not 5.

## Why Title and Header Hits Weight Highest

Title and `##` header hits weight at 10 and 5 respectively because these fields are author-declared topic signals — the author chose to put a term in a header because that term is the topic of that section. A body mention of "chunking" might be incidental; a `## Chunk Boundary Design` header is a direct statement that this section is about chunking. The asymmetry between header and body weights (5:1 for `##`) means a note whose author followed [[spec-headers]] discipline will outrank a note that merely mentions the same term in passing body text.

## Body Scoring Cap Per Note

Body text scoring is capped at 5 points per note regardless of how many times the query term appears in the body. Without this cap, a keyword-dense note (a glossary, a list of definitions) would dominate results for any term it mentions, even if it mentions the term only as a sub-item in a longer list and the term is not the note's topic. The cap prevents keyword stuffing from gaming the lexical ranker.

## Term Splitting and Score Accumulation

Multi-word queries are split on whitespace. Each term is scored independently against the same note, and the scores are summed. A query `"query ranking"` scores both `"query"` and `"ranking"` separately: a note with `## wiki-pro Query Ranking Algorithm` in its title matches both terms at weight 10 + 10 = 20. This additive model means that specificity improves results — longer queries with more terms produce tighter result sets.

## Case-Insensitive Matching

All term matching is case-insensitive. `"BM25"`, `"bm25"`, and `"Bm25"` all match the same note fields. This is the correct default for a human-authored wiki where capitalisation is inconsistent across notes.

## Interaction Between `--tag` Filter and Ranking

`wiki query "term" --tag retrieval` pre-filters the note set to only notes carrying the `retrieval` tag, then applies the scoring weights to the filtered set. The tag filter is not a ranking boost — it is a hard pre-filter. A note not carrying `retrieval` scores zero regardless of its body content match. Use `--tag` when the query term is too generic to surface the right category (e.g., `wiki query "headers" --tag spec` to find spec notes about headers, not all notes that mention headers).

## The `header_chain` Field in Query Results

Each query result includes a `header_chain` field: an array `[title, ## header, ### header]` that identifies the exact location within the note where the top-scoring match lives. The LLM uses `header_chain` to issue a precise `wiki read slug#section` call for the matching section rather than fetching the full note. A result with `header_chain: ["wiki-pro Query Ranking Algorithm", "Full Scoring Table"]` tells the LLM to read `retrieval-header-ranking#full-scoring-table` — approximately 200 tokens — rather than the full note at ~800 tokens.
