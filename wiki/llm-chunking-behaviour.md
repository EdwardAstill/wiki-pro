---
title: "How LLMs Receive and Use Retrieved Chunks"
slug: "llm-chunking-behaviour"
tags: ["llm", "chunking", "retrieval"]
summary: "How language models receive and use retrieved chunks — understanding this determines every structural decision in an LLM-first wiki."
related: ["spec-chunking", "spec-headers", "llm-context-budget"]
updated: "2026-04-21"
---

# How LLMs Receive and Use Retrieved Chunks

The RAG retrieval loop determines how an LLM encounters wiki content — chunks arrive as independent text fragments with metadata, without any surrounding note context, which is why every `##` section must be self-contained.

## The RAG Retrieval Loop

A retrieval-augmented generation (RAG) call follows this sequence: (1) the user's query is processed by the retrieval system (lexical or vector search); (2) the top-K most relevant chunks are selected from the corpus; (3) the selected chunks are injected into the LLM's context window alongside the query; (4) the LLM generates a response using only the content in its current context window. The LLM does not have access to the full wiki. The LLM does not know what came before or after each retrieved chunk in the original note unless those adjacent chunks are also among the top-K.

## What a Chunk Is in Practice

A chunk in production RAG systems is typically 200–500 tokens, bounded by semantic boundaries (paragraphs, sections) rather than fixed character counts. wiki-pro maps the `##` subtree to one chunk: the `##` header, the body text under it, and any `###` subsections within it, until the next `##` header or end of file. A typical wiki-pro `##` section of 150–400 tokens fits comfortably within this range. The header is always included in the chunk text — it is the primary label.

## What the LLM Sees for Each Chunk

Each chunk arrives in the LLM's context as: (1) the chunk text (header + body); (2) metadata including the note slug, the `title:` value, and the `header_chain` (path from note title to the specific `##`/`###` that was hit). The LLM does not receive the note's `related:` list, `tags:`, or other frontmatter unless the tool implementation explicitly prepends frontmatter metadata to the chunk. wiki-pro's `wiki query` prepends `title:` and `summary:` to each result — the summary provides note-level context even when only a section chunk is returned.

## Why Self-Contained Chunks Are Not Optional

The LLM cannot ask "what did the previous chunk say?" within a single retrieval call. If a `##` section begins with "As explained above, the CLI uses..." and the previous section (which did the explaining) is not in the top-K results, the LLM receives a dangling reference it cannot resolve. Self-contained `##` sections with named entities (not pronouns) and explicit `[[slug#section]]` cross-references are not stylistic preferences — they are functional requirements for correct LLM behaviour on retrieved content.

## The `header_chain` Field

The `header_chain` field returned by `wiki query` is an array of header strings forming the path to the matched chunk: `["How LLMs Receive and Use Retrieved Chunks", "The RAG Retrieval Loop"]`. The LLM uses `header_chain` to issue precise `wiki read slug#section` calls rather than fetching the full note. `header_chain` is built entirely from the note's `#`, `##`, and `###` header texts — which is why those headers must be self-identifying. A `header_chain` of `["How LLMs Receive and Use Retrieved Chunks", "Overview"]` tells the LLM nothing about what "Overview" covers; a `header_chain` of `["How LLMs Receive and Use Retrieved Chunks", "The RAG Retrieval Loop"]` is fully self-describing.
