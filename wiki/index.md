---
title: "wiki-pro Dogfood Wiki"
slug: "index"
tags: ["index", "navigation", "synthesis"]
summary: "Entry point for the wiki-pro wiki — explains what this wiki contains and how to navigate it by tag, not by tree."
related: ["spec-frontmatter", "architecture-flat-over-nested", "retrieval-ripgrep-patterns"]
updated: "2026-04-21"
---

# wiki-pro Dogfood Wiki

This wiki is a self-referential specification: every note documents how to build LLM-optimised wikis, and every note is itself an example of the spec it describes.

## What This Wiki Contains

This wiki covers the full stack of decisions required to build a wiki that serves both human readers and LLM retrieval pipelines well. The notes are grouped into five categories — `spec`, `architecture`, `retrieval`, `authoring`, and `llm` — plus a `news` category for time-sensitive state-of-the-field notes. Each category-prefix is a navigable tag.

The two audiences this wiki serves:
- **Human authors** who want clear rules for writing notes that survive being excerpted by a retrieval system.
- **LLM agents** that query this wiki to answer questions about how wiki-pro works.

## How to Navigate This Wiki

Navigation in wiki-pro is tag-first, not tree-first. There is no folder hierarchy to browse.

- `wiki query "your question"` — ranked full-text search across all notes; returns title, summary, and header chain for each hit.
- `wiki list --tag spec` — lists all notes tagged `spec`; use this to see every constraint in the spec.
- `wiki neighbours slug --depth 2` — traverses the `related:` graph from a starting note; use this to explore a topic area.
- `wiki tags` — lists every tag in the vocabulary with note counts.
- `wiki read slug` — fetches a full note by slug.
- `wiki read slug#section-anchor` — fetches one `##` section without loading the full note.

## Tag Map

Every tag used in this wiki, with a one-line description of the notes it marks:

| Tag | Notes carrying it |
|---|---|
| `index` | Entry point and synthesis overviews |
| `navigation` | Notes about how to move through the wiki |
| `synthesis` | Notes that weave connections across multiple notes into a single view |
| `spec` | Normative rules — the "must" and "must not" of wiki-pro |
| `frontmatter` | The YAML header block and its six required fields |
| `headers` | `##` and `###` discipline, naming, and chunking boundaries |
| `chunking` | How notes are split into retrieval units |
| `linking` | `[[slug]]` wikilinks and the `related:` graph |
| `architecture` | Structural decisions — flat vs nested, tagging, graph edges |
| `structure` | File and directory layout rules |
| `llm` | How language models receive, parse, and use retrieved content |
| `retrieval` | Query execution, ranking, and result presentation |
| `ranking` | Scoring weights for title, header, tag, summary, and body hits |
| `query` | The `wiki query` command and its behaviour |
| `embeddings` | Vector search, when to add it, and its costs |
| `tradeoffs` | Decision notes that weigh competing approaches |
| `tools` | CLI commands and external tools (`rg`, `python-frontmatter`, etc.) |
| `ripgrep` | Terminal-native search patterns for wiki content |
| `authoring` | Rules for writing notes — density, naming, anti-patterns |
| `style` | Prose and formatting conventions |
| `anti-patterns` | Failure modes and how to fix them |
| `naming` | File and slug naming conventions |
| `graph` | The `related:` edge structure and graph traversal |
| `wikilinks` | `[[slug]]` syntax, resolution, and `wiki doctor` checks |
| `context` | LLM context window budget and retrieval strategy |
| `markdown` | Parsing, frontmatter libraries, and CommonMark compliance |
| `news` | Time-sensitive state-of-the-field notes |

## Where to Start

New to wiki-pro: read [[spec-frontmatter]] first (the six required fields), then [[spec-headers]] (the most commonly violated rule), then [[authoring-density]] (the tone standard).

Debugging a retrieval problem: start at [[retrieval-header-ranking]], then [[llm-chunking-behaviour]].

Deciding whether to add embeddings: read [[retrieval-when-to-embed]].

Understanding why this wiki is flat: read [[architecture-flat-over-nested]] and [[llm-why-trees-dont-help]].
