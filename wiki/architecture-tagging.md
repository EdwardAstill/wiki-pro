---
title: "Tagging as Primary Categorisation"
slug: "architecture-tagging"
tags: ["architecture", "tags", "retrieval"]
summary: "Tags are the primary categorisation mechanism in wiki-pro — multi-parent, query-filterable, and cheaper to maintain than folder hierarchies."
related: ["architecture-flat-over-nested", "architecture-related-edges", "spec-frontmatter"]
updated: "2026-04-21"
---

# Tagging as Primary Categorisation

Tags in wiki-pro replace folder hierarchies as the primary categorisation mechanism, providing multi-parent membership, direct CLI query support, and zero filesystem coupling.

## Multi-Parenthood: What Tags Enable That Folders Cannot

A note tagged `["retrieval", "ranking", "anti-patterns"]` belongs to three conceptual categories simultaneously. A filesystem folder can hold a file in exactly one location — simulating multi-parenthood requires symlinks or duplicate files, both of which create maintenance liabilities. Tags are frontmatter values: changing a tag requires editing one line in one file, with no filesystem side effects and no risk of link breakage. The [[architecture-flat-over-nested]] note examines this from the filesystem perspective; the retrieval perspective is: `wiki list --tag retrieval` and `wiki list --tag anti-patterns` both correctly return this note.

## `wiki list --tag X` as the Navigation Primitive

`wiki list --tag X` is the recommended navigation entry point for humans and LLMs exploring a topic area. The command returns all notes carrying tag `X`, sorted by `updated:` date descending. Combined with `wiki query "term" --tag X`, it provides scoped search within a category without requiring folder navigation. `wiki tags` lists the full tag vocabulary with per-tag note counts — use this first to confirm a tag exists before listing it.

## Freeform vs Controlled Vocabulary

wiki-pro supports both approaches and recommends a middle path: start freeform (any tag that usefully describes the note), then run `wiki doctor` periodically to identify singleton tags (tags used by exactly one note) and near-duplicate tag variants (`chunking` vs `chunk` vs `chunks`). Consolidate synonyms — pick one canonical form and update all notes. The goal is a vocabulary of 15–30 tags for a wiki of 20–50 notes, where each tag has ≥2 notes and ≤30% of notes. A tag that appears on every note is as useless as no tag at all.

## `wiki doctor` Tag Heuristics

`wiki doctor` runs three tag-quality checks:

1. **Singleton tags** — tags used by exactly one note. Flag for review: either promote to a recurring tag by tagging more notes correctly, or remove as over-specific.
2. **Edit-distance ≤2 variants** — `chunking` and `chunks` differ by one character (suffix drop). `wiki doctor` surfaces these pairs for manual consolidation.
3. **Notes with >5 tags** — a note tagged with 6 or more tags likely has a focus problem. The fix is usually to split the note into two notes, each with 2–3 precise tags, rather than to keep adding tags to a sprawling note.

## Tag Naming Conventions

Tags follow four rules: (1) lowercase only; (2) hyphens for multi-word tags (`anti-patterns`, not `antiPatterns` or `anti_patterns`); (3) prefer nouns over verbs or adjectives (`retrieval`, not `retrieving` or `retrievable`); (4) prefer the most specific term that will be searched (`wikilinks`, not `links`, which collides with every note that mentions any link). These conventions maximise the precision of `wiki list --tag X` — a tag should return exactly the notes a user expects when they search for that term.
