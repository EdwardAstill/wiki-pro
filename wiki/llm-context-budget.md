---
title: "Managing LLM Context Budget"
slug: "llm-context-budget"
tags: ["llm", "context", "retrieval"]
summary: "LLM context windows are finite — wiki tooling must return the minimum sufficient chunk, not entire notes, to leave room for reasoning and response."
related: ["llm-chunking-behaviour", "spec-chunking", "retrieval-header-ranking"]
updated: "2026-04-21"
---

# Managing LLM Context Budget

Context window tokens spent on wiki content are tokens not available for reasoning and response — the two-call retrieval pattern (query for summaries, then read specific sections) minimises retrieval cost while maximising precision.

## Why `wiki read slug#section` Exists

`wiki read slug#section` returns one `##` subtree — approximately 200–400 tokens. `wiki read slug` returns the full note — approximately 500–2000 tokens. The section-scoped read exists because most queries need one fact from one section, not the entire note. When the `wiki query` result includes a `header_chain` pointing to a specific `##`, using `wiki read slug#section` is 5–10× more token-efficient than `wiki read slug`. The full-note read is reserved for cases where the query cannot be answered from a single section.

## Typical Context Budgets and Their Strategies

| Context window | Strategy |
|---|---|
| 8K tokens | Aggressive section-scoped reads; 2-call pattern mandatory; ≤5 query results |
| 32K tokens | Section reads default; full notes only when section insufficient; ≤10 query results |
| 128K tokens | Full notes affordable for short wikis; still use section reads for efficiency |
| 1M tokens | Entire wiki fits; retrieval quality still matters for response precision |

Even at 1M tokens, precision retrieval improves response quality: an LLM presented with 50 relevant notes produces less precise answers than an LLM presented with the 3 most relevant sections. The context budget argument is strongest at ≤32K but remains relevant at all scales.

## The Two-Call Retrieval Pattern

The recommended pattern for LLM agents using wiki-pro:

**Call 1:** `wiki query "question"` — returns top-5 hits as `(title, summary, header_chain, slug, score)`. Token cost: ~50 tokens per result = ~250 tokens for 5 results. The LLM reads summaries to decide which note(s) to fetch.

**Call 2:** `wiki read slug#section` — returns one `##` section. Token cost: ~200–400 tokens.

Total cost for a resolved query: ~450–650 tokens. Compare to fetching the top-5 full notes: ~2500–10000 tokens. The two-call pattern is 5–15× more efficient and produces higher-precision results because the LLM is reading the exact section that matched, not scanning a full note.

## Token Cost Estimates

| Content unit | Approximate token count |
|---|---|
| `summary:` (≤200 chars) | ~50 tokens |
| Note-level lead paragraph | ~50–80 tokens |
| One `##` section | ~200–400 tokens |
| Full note | ~500–2000 tokens |
| Full wiki (20 notes) | ~10000–40000 tokens |

These estimates use standard tiktoken counts for English prose with light markdown formatting.

## `--follow related` Flag: Cost and Benefit

`wiki read slug --follow related` fetches the full note at `slug` plus the summary and lead paragraph of every note in its `related:` list. Token cost: 1 full note (~800 tokens) + N × (~130 tokens per related note's summary + lead). For a note with 3 `related:` entries: ~800 + 3×130 = ~1190 tokens. Use `--follow related` when the primary note establishes a framework and the related notes provide required details — for example, reading [[spec-frontmatter]] with `--follow related` fetches the summaries of [[spec-headers]], [[spec-linking]], and [[architecture-tagging]] in one call.

## Rule of Thumb for Context Budget Decisions

Start with `wiki query` (cheap: ~250 tokens for 5 results) then `wiki read slug#section` (precise: ~300 tokens). Escalate to `wiki read slug` (full note: ~800 tokens) only if the section is insufficient. Escalate to `wiki read slug --follow related` only if the full note plus its neighbourhood is needed. Never fetch the full wiki except for bulk analysis tasks.
