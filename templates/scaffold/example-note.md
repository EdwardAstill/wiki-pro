---
title: "How to Write a Good Wiki Note"
slug: "example-note"
tags: ["authoring", "spec"]
summary: "A wiki note is retrievable by design: every field, every header, every sentence is written assuming it will be read in isolation, not top-to-bottom."
related: ["index"]
updated: "2026-04-21"
---

# How to Write a Good Wiki Note

A wiki note is retrievable by design: every field, every header, and every sentence is written
assuming it will be read in isolation, not top-to-bottom. The three things that make a note
retrievable are a precise `summary:`, topic-bearing headers, and a lead sentence under each `##`.

## Frontmatter Fields That Drive Retrieval

The `summary:` field is the single most retrieval-critical part of a note. `wiki query` returns it
as the preview line before the caller decides whether to fetch the full note — so write it for a
reader who has never seen the note and needs to decide in one sentence whether it is relevant.

- `slug:` is the stable identifier that `[[wikilinks]]` resolve to. Set it once; do not change it
  if other notes link here. The filename can be renamed freely — slug is what matters.
- `tags:` are the primary categorisation. There are no folders. A note can carry multiple tags
  simultaneously, which a folder tree cannot express.
- `related:` lists the slugs of notes that are meaningfully connected. It is the author's explicit
  hop graph — `wiki neighbours` traverses it.
- `updated:` is an ISO date. Keep it current; stale dates decay a note's ranking over time.

## Header Discipline for Isolated Retrieval

Every `##` and `###` header must identify its topic when the section is read without the page title.
A retrieved `##` subtree has no surrounding context — the header is the only label it carries.

Bad: `## Overview`, `## Why`, `## Mechanism`, `## Introduction`
Good: `## Frontmatter Fields That Drive Retrieval`, `## Header Discipline for Isolated Retrieval`

The rule: if you can replace the header with "Section 1" and lose no information, the header is not
specific enough. Name the thing, not the role it plays in the document.

## The Lead Sentence Under Each Section

The first sentence under a `##` restates what that section covers and why. This sentence is the
RAG-priority paragraph: chunk-based retrieval surfaces the `##` header plus the first paragraph —
so if that paragraph is vague or missing, the chunk is useless to a downstream LLM.

- Write the lead sentence as a complete, named claim: `The slug field is the stable identifier...`
  not `This field is used for...`.
- Define any acronym on first use within the section. A chunked paragraph cannot rely on definitions
  earlier in the note.

## Linking to Other Notes

Internal links use `[[slug]]` syntax, resolved by frontmatter `slug:` not by filename. Use
`[[slug|display label]]` to alias the link text when the slug is not readable prose. Every note
you link to in the body should also appear in `related:` frontmatter — `wiki doctor` flags the gap
if you forget.

External links use standard markdown: `[display](https://example.com)`.

## Anti-Patterns That Break Retrieval

These patterns make notes hard to find and hard to use when found:

- **Bare generic headers** — `## Overview`, `## Background`, `## The Problem`. Name the topic.
- **Soft bullets** — "This can be useful in some cases." Every bullet must contain a fact, command,
  formula, or concrete trigger.
- **Pronoun openings** — "It works by...". Name the subject: "The slug field works by...".
- **Over-tagging** — more than 5 tags usually means the note is unfocused; consider splitting.
- **Empty `related:`** — if a note has no related notes, it is either a stub or an orphan.
  `wiki doctor` will flag it.
