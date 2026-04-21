---
title: "Writing Synthesis Notes"
slug: "authoring-synthesis-notes"
tags: ["authoring", "synthesis", "structure"]
summary: "A synthesis note weaves connections across multiple notes into a single high-density overview — write one when the relationships between notes are the insight, not any single note's content."
related: ["architecture-related-edges", "architecture-tagging", "authoring-density"]
updated: "2026-04-21"
---

# Writing Synthesis Notes

A synthesis note is a note tagged `synthesis` that explicitly states the relationships between four or more other notes, producing an insight that no single note delivers on its own.

## What a Synthesis Note Is

A synthesis note is not a list of links. A synthesis note is not a MOC (Map of Content) file. A synthesis note has content — its primary value is the stated relationship between the notes it references, not the references themselves. The defining test: if you remove all the `[[slug]]` links from the note, does the remaining prose still convey a useful insight? If yes, the note is a synthesis note. If the remaining prose is just a list of names and "see also" references, the note is a MOC, which wiki-pro does not use.

## When to Write a Synthesis Note

Write a synthesis note when: (1) a query would require reading ≥5 individual notes and mentally assembling the picture to answer; (2) the assembled picture reveals a relationship, trade-off, or decision tree that is not explicit in any single note; (3) the relationship is stable enough to remain true across note updates. Do not write a synthesis note as a substitute for good `related:` edges — if the connection between two notes is navigational ("read A then B"), express it in `related:`. Synthesis notes are for the cases where the connection is semantic ("A and B together imply C, which contradicts D unless E holds").

## When NOT to Write a Synthesis Note

Do not write a synthesis note as a replacement for authoring discipline. If five notes have weak summaries and bare headers, writing a sixth note that explains them all is a patch on an authoring quality problem. Fix the five notes first. Do not write a synthesis note to express a topic hierarchy — that is a MOC, and MOCs go stale. Do not write a synthesis note for a connection between two notes — add a `related:` entry and an inline `[[...]]` link.

## Structure of a Synthesis Note

A synthesis note follows the same frontmatter and header rules as all notes, with these additions:

- **Lead paragraph** states the relationship thesis: "The [[spec-headers]], [[spec-chunking]], and [[llm-chunking-behaviour]] notes together define a single constraint: every structural decision in a wiki-pro note is a chunk boundary decision."
- **`##` sections** are named for each relationship being stated, not for the individual notes: `## How Header Discipline Determines Chunk Quality` rather than `## spec-headers`.
- **Explicit `[[slug]]` links** appear inline where the referenced note is relevant to the stated relationship.
- **`related:` list** contains every note referenced in the synthesis — typically 4–8 entries.
- **`tags:`** includes `synthesis` plus the most relevant domain tags.

## Synthesis Notes Are Not MOCs

MOC files are centralised lists of notes in a topic area. They go stale, express only one hierarchy, and have no content beyond the list. Synthesis notes have content — the relationship statements are the value. A synthesis note that references [[spec-frontmatter]], [[spec-headers]], [[spec-chunking]], [[spec-summaries]], and [[spec-linking]] must say something new about how those five notes relate to each other. "Here are the five spec notes" is a MOC. "The five spec notes collectively express one constraint — every authoring decision is a retrieval decision — and each note covers the application of that constraint to one structural level of the note" is a synthesis note.
