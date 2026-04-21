---
title: "Your Page Title Here"          # Human-readable. Matches the # heading below.
slug: "your-page-slug"                  # Stable kebab identifier. [[wikilinks]] resolve to this, not the filename.
tags: ["tag-a", "tag-b"]               # Primary categorisation. No folders — tags are the hierarchy.
summary: "One sentence describing this note. ≤200 chars. The preview line wiki query returns — write it for a reader who has never seen this note." # Required. Author-written.
related: ["related-slug-1", "related-slug-2"]  # Explicit hop edges to related notes by slug.
updated: "2026-04-21"                   # ISO date of last meaningful edit.
---

# Your Page Title Here

One sentence defining the topic and why it matters — this is the page lead. Every section retrieval
includes this paragraph for context, so it must stand alone. Name the thing directly; no "This page
covers...".

## First Section Name — Topic Specific

One sentence restating what this section covers and why it is worth reading. This is the RAG-priority
paragraph for the section: if this `##` block is retrieved without the rest of the note, this sentence
tells the reader what they are looking at.

- Hard fact, specific command, formula, or concrete trigger. No soft bullets.
- Reference the named entity explicitly (`The {{concept}} does X`) rather than `It does X`.
- Define any acronym on first use within this section — a chunked paragraph cannot rely on definitions
  elsewhere in the note.

## Second Section Name — Topic Specific

One sentence restating what this section covers and why it is worth reading.

- Bullet or prose continues here.
- Use `[[slug]]` to link to a related note or `[[slug|display label]]` to alias the link text.

<!-- 
  Before publishing:
  - Add [[wikilinks]] to any related notes you reference in the body.
  - Update `related:` in frontmatter to list those slugs.
  - Confirm `summary:` is ≤200 characters and author-written.
-->
