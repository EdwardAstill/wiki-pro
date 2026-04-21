---
title: "Chunk Boundary Design"
slug: "spec-chunking"
tags: ["spec", "chunking", "retrieval"]
summary: "Every ## subtree must be readable in isolation — self-contained chunk boundaries are the single most important structural decision in an LLM-first wiki."
related: ["spec-headers", "llm-chunking-behaviour", "authoring-density"]
updated: "2026-04-21"
---

# Chunk Boundary Design

A chunk is the unit of text a retrieval system returns for a query — wiki-pro maps one `##` subtree to one chunk, which means every `##` section must be fully self-contained and independently readable.

## What a Chunk Is in RAG Context

In a retrieval-augmented generation (RAG) pipeline, a chunk is the atomic unit of text returned by a search query and injected into an LLM's context window. The RAG system does not return entire documents — it returns the top-K most relevant chunks, where K is typically 3–10. Each chunk appears in the LLM's context without its neighbours: the LLM cannot see the section that came before or after unless those sections are also among the top-K hits and happen to be fetched in the same call.

## How wiki-pro Maps `##` Sections to Chunks

wiki-pro treats each `##` subtree — the `##` header plus all body text and `###` subsections until the next `##` header — as one chunk. The `wiki read slug#section-anchor` command returns exactly this unit. The `wiki query` command returns the chunk header and its lead paragraph as the preview, then the full chunk text when the caller requests it. The chunk boundary at `##` is enforced structurally: the CLI splits note bodies at `^## ` lines when building the retrieval index.

## The Lead-Paragraph Rule for Context Provision

The first paragraph after the note's frontmatter block (the paragraph that follows the `#` title) is the note-level lead paragraph. wiki-pro includes this lead paragraph when returning any section chunk from that note, providing minimal context about what the note is. This means a chunk always arrives with: (1) the note's `#` title, (2) the note-level lead paragraph (≤3 sentences), and (3) the `##` header and its content. Authors should write the note-level lead paragraph to be maximally useful as a context-setter for any section.

## Cross-Chunk References Using `[[slug#section]]`

When a section references content in another section of the same note or in a different note, use `[[slug#section-anchor]]` rather than prose phrases like "as discussed above" or "see the previous section". Prose cross-references break when the chunk is retrieved in isolation — the referenced section is not present and the phrase becomes a dangling pointer. `[[slug#section-anchor]]` is a resolvable link: `wiki read` can follow it, and the LLM can request the referenced chunk explicitly.

## Anti-Pattern: Monolithic Notes with No `##` Sections

A note with all content under the `#` title and no `##` sections returns as a single chunk for every query that matches any term in it. A 2000-token monolithic note occupies the same retrieval slot as a 200-token section and crowds out more relevant chunks. The fix: decompose into `##` sections of 200–500 tokens each, with each section covering exactly one sub-topic. If the note genuinely has only one sub-topic, the note itself is too small to subdivide — keep it flat, but keep it short (≤400 tokens total). See [[authoring-anti-patterns]] for the full anti-pattern taxonomy.
