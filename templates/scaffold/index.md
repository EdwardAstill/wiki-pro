---
title: "[YOUR WIKI NAME]"
slug: "index"
tags: ["index", "navigation"]
summary: "Entry point for [YOUR WIKI NAME]. Start here to orient yourself and find notes by tag."
related: []
updated: "2026-04-21"
---

# [YOUR WIKI NAME]

[YOUR WIKI NAME] is a wiki about [YOUR TOPIC]. Notes are flat — no folders — and navigated by tag
and by the `related:` graph. Use the CLI to search, read, and explore.

## Navigating This Wiki

The three most useful commands for finding notes:

- `wiki query "your question"` — ranked full-text search across titles, headers, summaries, and
  bodies. Returns slug, summary, and a snippet showing where the match lives.
- `wiki list --tag <tag>` — all notes with a given tag. Use `wiki tags` to see every tag with counts.
- `wiki neighbours <slug>` — expand the `related:` graph one hop from any note. Useful when a query
  hit looks promising but partial.

Read a single note: `wiki read <slug>`. Read one section only: `wiki read <slug>#section-name`.

## Tags in This Wiki

<!-- TODO: fill in the tags your wiki uses and a one-line description of each. -->

| Tag | What it covers |
| --- | --- |
| `tag-a` | [description] |
| `tag-b` | [description] |

Use `wiki tags` to see the full list at any time, sorted by note count.

## Maintaining This Wiki

- `wiki validate` — lint all notes for spec violations. Run before committing.
- `wiki doctor` — deeper check: broken `[[wikilinks]]`, missing summaries, orphaned notes, suspect tags.
- `wiki propose <slug> <patch>` — stage a proposed edit for human review without touching source files.
