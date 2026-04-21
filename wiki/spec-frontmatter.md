---
title: "Frontmatter Spec"
slug: "spec-frontmatter"
tags: ["spec", "frontmatter", "retrieval"]
summary: "The six frontmatter fields required by wiki-pro and why each one exists — title, slug, tags, summary, related, updated."
related: ["spec-headers", "spec-linking", "architecture-tagging"]
updated: "2026-04-21"
---

# Frontmatter Spec

Every wiki-pro note opens with a YAML frontmatter block containing six required fields — the block is the machine-readable contract that makes the note queryable, linkable, and previewable without parsing the note body.

## Why Frontmatter Over Prose Metadata

Frontmatter is machine-parseable without body parsing, which means the wiki CLI can build its index by reading only the first N bytes of each file. Prose metadata buried in the body requires a full parse, full AST construction, and heuristic extraction — all of which fail on malformed or inconsistently structured notes. The frontmatter block gives `python-frontmatter` (backed by `pyyaml` SafeLoader) a single structured target at a known file offset.

## The Six Required Fields

The six fields form a complete description of the note for retrieval and graph-traversal purposes.

### `title:`

`title:` is the human-readable name of the note. The CLI uses it as the display string in `wiki query` results. The value must exactly match the text of the single `#` header in the note body — the `wiki validate` check enforces this. Maximum length: 80 characters.

### `slug:`

`slug:` is the stable identifier used in `[[wikilink]]` resolution. The slug is decoupled from the filename: renaming `spec-frontmatter.md` to `frontmatter-spec.md` does not break any `[[spec-frontmatter]]` link as long as `slug: "spec-frontmatter"` remains in the frontmatter. Slugs are kebab-case, globally unique within a wiki, and never change once set. The CLI resolves `[[target]]` by scanning all `slug:` fields, not by matching filenames.

### `tags:`

`tags:` is a YAML list of lowercase hyphenated strings. `wiki list --tag X` filters on this field. Tags are the multi-parent categorisation mechanism: a note can carry `["retrieval", "spec", "anti-patterns"]` simultaneously, which no folder hierarchy can express. See [[architecture-tagging]] for tag vocabulary conventions.

### `summary:`

`summary:` is the highest-leverage field in the note. At query time, the CLI returns the `title` and `summary` for each hit before the caller decides whether to fetch the full note body. The `summary` must be one sentence, ≤200 characters, readable in isolation, and must contain the most retrievable term in the note. See [[spec-summaries]] for the full writing guide.

### `related:`

`related:` is a YAML list of slugs identifying the notes most directly connected to this one. The field builds an explicit hop graph that `wiki neighbours` traverses. `related:` is for deliberate "next step" connections; inline `[[wikilinks]]` in the body are for prose references. See [[architecture-related-edges]] for the semantic distinction.

### `updated:`

`updated:` is an ISO 8601 date string (`YYYY-MM-DD`) recording the last substantive edit. The CLI surfaces this in `wiki list` output to help identify stale notes. Update this field whenever the note content changes — not on trivial formatting fixes.

## Why `virtual_path` Was Rejected

The `virtual_path` field (used in some KB systems to declare a hierarchical position like `retrieval/advanced/embeddings`) was evaluated and rejected for wiki-pro. `virtual_path` encodes a tree structure that LLMs never traverse: retrieval is query-driven, not tree-walk-driven. The same multi-parent grouping that `virtual_path` approximates is covered more flexibly by `tags:` — a note can belong to three conceptual "folders" simultaneously with no additional structure. See [[llm-why-trees-dont-help]] for the retrieval argument and [[architecture-tagging]] for the tagging argument.

## What `summary` Must Achieve

The `summary` field must satisfy four conditions simultaneously: (1) it reads correctly in isolation without surrounding context; (2) it contains the primary retrievable term for this note; (3) it states the key constraint or differentiator, not just the topic; (4) it fits in ≤200 characters. A summary that says "This note is about frontmatter" satisfies none of these. A summary that says "The six frontmatter fields required by wiki-pro and why each one exists — title, slug, tags, summary, related, updated" satisfies all four.
