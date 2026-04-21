---
title: "Flat Directories Over Nested Folder Hierarchies"
slug: "architecture-flat-over-nested"
tags: ["architecture", "structure", "llm"]
summary: "Flat wiki directories outperform nested folder hierarchies for LLM retrieval — tags and related edges carry the structure that folders would, without tree navigation."
related: ["architecture-tagging", "architecture-related-edges", "llm-why-trees-dont-help"]
updated: "2026-04-21"
---

# Flat Directories Over Nested Folder Hierarchies

wiki-pro stores all notes in a single flat directory per wiki, with no sub-folders — the categorisation that nested folders would express is carried by `tags:` and `related:` instead, which are faster to query and cheaper to maintain.

## The Core Problem with Nested Folders for LLM Retrieval

LLM retrieval is query-driven, not tree-walk-driven. When a RAG system fetches a chunk from `retrieval/advanced/embedding/bm25-scoring.md`, the folder path `retrieval/advanced/embedding/` contributes nothing to retrieval quality — the system found the chunk by matching text in the note body, headers, and summary, not by traversing the folder tree. The path appears in the chunk metadata but carries less signal than a well-written `##` header. Nested folders add filesystem maintenance cost (renaming a folder cascades across all paths that reference it) while adding zero retrieval benefit.

## How `rg` Across a Flat Directory Outperforms Recursive Tree Walking

`rg "term" wiki/ --type md` on a flat directory is a single-depth search with no directory recursion. `rg "term" wiki/ --type md -r` on a nested hierarchy adds directory traversal overhead and forces path-filtering logic when the caller wants to scope to a sub-topic. In a flat directory, tag filtering (`rg "tags:.*retrieval" wiki/ --type md`) is the scoping mechanism — a single regex match on frontmatter lines. See [[retrieval-ripgrep-patterns]] for the full pattern library.

## Kebab-Prefix Collision Resolution as Category Hint

When two notes share the same core concept but belong to different categories — for example, two notes both about "headers" — the kebab-prefix disambiguates: `spec-headers.md` and `retrieval-headers.md` coexist in the flat directory without conflict. The prefix (`spec-`, `retrieval-`, `authoring-`, `architecture-`, `llm-`, `news-`) is an informal category hint that is legible to both `rg` pattern matching and human readers scanning a directory listing. This is a collision-resolution mechanism, not a mandatory taxonomy — notes with globally unique names need no prefix.

## Why Flat Directories Survive Reorganisation

Reorganising a nested folder hierarchy requires: (1) creating new directories, (2) moving files, (3) updating all relative path references in the moved files, (4) updating all incoming links in other files. Reorganising a flat wiki with the kebab-prefix scheme requires: (1) renaming files, (2) the `slug:` remains unchanged so all `[[wikilinks]]` remain valid. Tag changes propagate instantly because tags are inline frontmatter, not filesystem positions.

## The Only Valid Reason to Add Sub-Folders

Sub-folders in a wiki-pro repository are valid only when separating completely independent wikis that happen to share a parent directory — each sub-folder contains its own `.wiki-pro.toml` with a distinct `name:` value. Sub-folders within a single wiki (same `.wiki-pro.toml`) are prohibited. If a domain genuinely requires physical separation from another domain (different access controls, different publish targets, different tooling configs), use a sub-folder with its own config. If the motivation is "these notes feel like they belong together", use tags.
