---
title: "Why Folder Hierarchies Don't Help LLM Retrieval"
slug: "llm-why-trees-dont-help"
tags: ["llm", "architecture", "structure"]
summary: "Folder hierarchies help humans orient themselves in a file browser — LLMs navigate by retrieval, not traversal, so tree structure adds maintenance cost with no retrieval benefit."
related: ["architecture-flat-over-nested", "architecture-tagging", "llm-chunking-behaviour"]
updated: "2026-04-21"
---

# Why Folder Hierarchies Don't Help LLM Retrieval

LLMs retrieve content by matching query terms against text fields, not by traversing filesystem paths — a folder hierarchy is invisible to the retrieval loop and adds maintenance cost without improving result quality.

## How Humans Navigate a Wiki

Human navigation of a wiki is hierarchical and sequential: open a folder, scan filenames, open a likely file, read the table of contents, scroll to the relevant section. Folder hierarchies serve this navigation pattern: they provide a visual map, group related files, and let the reader build a mental model of the wiki's scope by browsing the tree. This is the use case for which nested folders were designed.

## How LLMs Navigate a Wiki

LLM navigation is query-driven and non-linear: issue a query, receive ranked chunks with metadata, decide which chunk(s) answer the question, follow `related:` edges if needed. No step in this loop requires or benefits from a folder hierarchy. The retrieval system receives the query, scans all notes' titles, headers, summaries, tags, and bodies, and returns ranked results. The note's filesystem path is in the result metadata but carries less signal than a well-written `##` header — it is rarely the decisive factor in ranking.

## The Folder Hierarchy Problem for Retrieved Chunks

A chunk retrieved from `notes/retrieval/advanced/embedding/bm25-scoring.md` carries the path `retrieval/advanced/embedding/` in its metadata. The LLM cannot infer from this path that the note is about BM25's term frequency component vs its IDF component vs its length normalisation — that distinction is in the `##` headers. The path `retrieval/advanced/embedding/` is a coarser label than the header `## BM25 Term Frequency Scoring in wiki-pro Query Ranking`. The folder hierarchy adds structural information that is already expressed more precisely in the note's headers and summary.

## What `virtual_path` Was Supposed to Solve and Why Tags Solve It Better

The `virtual_path` frontmatter field (used in some knowledge base systems) declares a hierarchical position (`retrieval/advanced/embeddings`) in the frontmatter, decoupled from the physical filesystem. This addresses the filesystem rename problem — `virtual_path` doesn't change when the file moves — but it still encodes a single-parent hierarchy. A note about BM25 that belongs to both `retrieval/lexical` and `ranking/algorithms` cannot express this with one `virtual_path` value. Tags solve the same problem multi-parentally: `tags: ["retrieval", "ranking"]` places the note in both categories simultaneously with no structural overhead.

## Maintenance Cost of Folder Hierarchies

Renaming a folder in a filesystem-path-resolved wiki requires: (1) moving all files in the folder; (2) updating all relative path references in every moved file; (3) updating all incoming links from other files that referenced paths in the folder. In a slug-resolved wiki with a flat directory, moving a file requires: (1) renaming the file; (2) nothing else, because links resolve against `slug:` not paths. The maintenance delta is proportional to wiki size — in a 200-note wiki, renaming one folder can cascade into 50+ file edits.

## The Only Tree the LLM Uses

The one hierarchical structure that benefits LLM retrieval is the `header_chain` within a note: `["note title", "## section", "### subsection"]`. This chain is built from the note's header structure, not from folder structure, and is returned in query results so the LLM can identify the exact location of the match. The `header_chain` is the LLM's equivalent of a folder path — and it is built from author-written headers, not from filesystem layout. This is the correct level at which to invest structural effort.
