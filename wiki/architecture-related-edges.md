---
title: "The related: Edge Graph"
slug: "architecture-related-edges"
tags: ["architecture", "linking", "graph"]
summary: "The related: frontmatter field builds an explicit hop graph between notes — use it for deliberate 'next step' connections, not as a replacement for inline [[wikilinks]]."
related: ["spec-linking", "architecture-tagging", "spec-frontmatter"]
updated: "2026-04-21"
---

# The related: Edge Graph

The `related:` frontmatter field is a curated navigation graph — each entry declares a deliberate "next note to read" connection, which `wiki neighbours` traverses to map a topic area without requiring a MOC file.

## `related:` vs Inline `[[...]]` — The Semantic Distinction

`related:` and inline `[[wikilinks]]` are not interchangeable. `related:` is a structural claim: "this note and that note are closely related in topic, and a reader finishing this note should consider reading that one." An inline `[[slug]]` is a prose reference: "this sentence references a concept that is defined or expanded in that note." A note on [[spec-chunking]] might inline-link to `[[spec-headers]]` when discussing how headers define chunk boundaries, and also list `[[llm-chunking-behaviour]]` in `related:` because that note explains the downstream effect. The inline link is contextual; the `related:` entry is topical.

## `wiki neighbours slug --depth N` for Graph Traversal

`wiki neighbours spec-frontmatter --depth 2` returns all notes reachable from `spec-frontmatter` by following `related:` edges up to two hops. Depth 1 returns direct neighbours; depth 2 returns neighbours-of-neighbours. This is the mechanism that replaces MOC (Map of Content) files: instead of maintaining a central list, each note declares its own neighbourhood and the CLI assembles the graph on demand. The traversal is unidirectional: following `related:` edges from A to B does not guarantee that B lists A.

## `--follow related` Flag in `wiki read`

`wiki read slug --follow related` fetches the note at `slug` and also fetches the lead paragraph and summary of every note in its `related:` list. This provides one-call context expansion without fetching full note bodies for every related note. The flag is useful when a single note is insufficient to answer a question but a full graph traversal is too expensive. Token cost: one full note + N summaries + N lead paragraphs, where N is the length of the `related:` list (typically 2–4 entries).

## When NOT to Add a `related:` Entry

Transient or context-dependent connections belong as inline `[[...]]` links, not in `related:`. If note A mentions note B's concept in one sentence out of ten, that is an inline link, not a structural relationship. If the connection is "these two notes together explain one coherent idea and a reader should read both", that is a `related:` entry. The `related:` list should be ≤5 entries — if more than five notes are genuinely structurally related, consider writing a [[authoring-synthesis-notes|synthesis note]] that explicitly weaves them together.

## Unidirectionality Is Correct by Design

`related:` is unidirectional: note A listing note B in its `related:` field does not require note B to list note A. This is intentional. A foundational note like [[spec-frontmatter]] would accumulate dozens of back-references if bidirectionality were enforced — every note that builds on frontmatter concepts would be forced into its `related:` list, making it useless as a navigation signal. The `wiki neighbours` command handles reverse-lookup: `wiki neighbours spec-frontmatter --incoming` returns all notes that list `spec-frontmatter` in their `related:` field.

## How `related:` Replaced MOC Files

MOC (Map of Content) files are centralised index notes that list all notes in a topic area. MOC files have two failure modes: (1) they go stale when new notes are added and the MOC author forgets to update the list; (2) they express only one hierarchy, while a note may belong to multiple valid hierarchies. `related:` distributes the graph declaration: each note maintains its own neighbourhood, and `wiki neighbours` assembles the full graph dynamically. No MOC file can go stale because no MOC file exists.
