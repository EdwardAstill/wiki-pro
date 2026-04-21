---
title: "Header Discipline for LLM-Retrievable Wikis"
slug: "spec-headers"
tags: ["spec", "headers", "chunking"]
summary: "Header discipline for LLM-retrievable wikis — every ## must name its topic in isolation because chunks are retrieved without surrounding context."
related: ["spec-chunking", "authoring-density", "llm-chunking-behaviour"]
updated: "2026-04-21"
---

# Header Discipline for LLM-Retrievable Wikis

Every `##` and `###` header must identify its topic when read with no surrounding context — a chunk retrieved by a RAG system carries only its own header, not the note title or preceding sections.

## The Core Chunking Problem for Headers

When a retrieval system returns a `##` subtree as a chunk, the LLM receives the header text as the primary label for that chunk's content. A header like `## Overview` or `## Mechanism` is meaningless in isolation: the LLM cannot determine what is being overviewed or what mechanism is described. A header like `## Scoring Weights in wiki-pro Query Ranking` or `## Mechanism of BM25 Term Frequency Scoring` survives extraction intact — the topic is fully specified in the header itself.

## The Banned Bare Headers List

The following headers are prohibited in all wiki-pro notes because each fails to identify its topic when excerpted:

- `## Overview` — topic unspecified; retrieves for every note
- `## Mechanism` — mechanism of what? Useless when chunked
- `## Why` — why what? The implied subject drops when the note title is absent
- `## What` — same failure as `## Why`
- `## How` — same failure
- `## Introduction` — content type label, not topic label
- `## Background` — same failure as `## Introduction`
- `## Summary` — same failure; also conflicts with the `summary:` frontmatter field
- `## Conclusion` — position label, not topic label
- `## Notes` — too broad; signals "miscellaneous", which is the worst possible topic signal
- `## Details` — topic unspecified; scores as a hit for "details" searches against every note

Fix: replace each banned header with `## [BannedLabel] of [Named Topic]` — for example `## Overview of BM25 Scoring` or `## Mechanism of Slug Resolution`.

## The RAG-Priority Paragraph Rule

The first sentence under every `##` header must restate the section's thesis — this sentence is the RAG-priority paragraph for that chunk. When the retrieval system returns a ranked chunk, the LLM reads the header and the first sentence to decide whether to read further. A first sentence that says "This section covers X" is a wasted sentence. A first sentence that says "BM25 scores term X by multiplying term frequency by inverse document frequency, normalised by document length" delivers the core fact immediately.

## The Single `#` Rule

Each note contains exactly one `#` header, positioned at the top of the body (after frontmatter). The `#` header text must exactly match the `title:` frontmatter field — `wiki validate` enforces this. Multiple `#` headers break the title-match check and confuse chunking boundary detection.

## Before and After: Bad Headers Fixed

Bad:
```
## Overview
The wiki uses frontmatter for metadata.

## Why
Frontmatter is faster to parse.

## Mechanism
The CLI reads YAML at file offset 0.
```

Good:
```
## Why Frontmatter Outperforms Prose Metadata
Frontmatter is machine-parseable without body parsing, which lets the CLI index a wiki by reading only the first N bytes of each file.

## Mechanism of Frontmatter Parsing in wiki-pro
The CLI uses `python-frontmatter` backed by `pyyaml` SafeLoader to extract YAML at file offset 0 without a full markdown parse.
```

The good headers work as standalone labels in a retrieval result. The bad headers do not.

## Subsection Headers Follow the Same Rule

`###` headers carry the same isolation requirement as `##` headers. A `###` that says `### Example` tells the retrieval system nothing. A `###` that says `### Example: Scoring a Query with Two Terms` provides full context. The `header_chain` field in query results reports the path `[title, ## header, ### header]` — every level must be self-identifying.
