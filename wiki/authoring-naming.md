---
title: "File Naming Rules for wiki-pro"
slug: "authoring-naming"
tags: ["authoring", "naming", "structure"]
summary: "File naming rules for wiki-pro: kebab-case, flat, no numeric prefixes — the kebab-prefix doubles as a category hint legible to both rg and humans."
related: ["architecture-flat-over-nested", "spec-frontmatter"]
updated: "2026-04-21"
---

# File Naming Rules for wiki-pro

wiki-pro filenames are kebab-case, flat, unprefixed by numbers, and optionally category-prefixed — the filename is a display artifact; the `slug:` field is the stable identifier.

## Kebab-Case Rule

All wiki-pro filenames use lowercase letters, hyphens as word separators, and the `.md` extension. No spaces (`my note.md`), underscores (`my_note.md`), PascalCase (`MyNote.md`), or special characters. This rule applies to filenames only — `title:` and `summary:` use normal sentence capitalisation. Kebab-case makes files tab-completable in any shell, safe in URLs without encoding, and compatible with case-insensitive filesystems.

## No Numeric Prefixes

Numeric prefixes (`01-introduction.md`, `02-setup.md`) are prohibited. Reading order is not expressed by filename alphabetical sort — it is expressed by `wiki roadmap` or by the author's recommended reading path in a synthesis note. Numeric prefixes create false ordering obligations (adding a note between `01` and `02` requires renumbering), become stale when notes are reordered, and convey no information to a retrieval system. The only exception to this rule: version numbers that are intrinsic to the name (`harpers-biochemistry-32nd-ed.pdf`).

## The Category-Prefix Pattern

wiki-pro uses an informal category-prefix convention: `spec-`, `architecture-`, `retrieval-`, `authoring-`, `llm-`, `news-`. The prefix is a human-legible category hint visible in directory listings and `rg` output without requiring any tooling. `rg "spec-" wiki/ --type md -l` returns all spec notes as a path-level filter — a faster operation than a frontmatter tag grep. The prefix is not mandatory for notes with globally unique names (`index.md`, `glossary.md`) and is not enforced by `wiki validate`. It is a convention, not a rule.

## Collision Resolution via Category Prefix

When two notes share the same core concept, the category prefix disambiguates: `spec-headers.md` (the normative rule for header discipline) and `retrieval-headers.md` (how header hits are scored in ranking) coexist without filesystem conflict. The collision resolution rule: add the category prefix to both conflicting filenames. If only one of them needs the prefix to disambiguate, add the prefix to both anyway for consistency.

## `slug:` Is Decoupled from Filename by Design

The `slug:` frontmatter value is the stable identifier for the note — `[[wikilinks]]` resolve against `slug:`, not against filenames. A note can be renamed from `spec-frontmatter.md` to `frontmatter-spec.md` without breaking any link, as long as `slug: "spec-frontmatter"` remains in the frontmatter. The slug is set at note creation and never changed. The filename is free to evolve with the wiki's organisational conventions. `wiki doctor` validates that all `[[slug]]` references resolve to existing `slug:` values regardless of what the files are named.

## The `index.md` Special Case

`index.md` with `slug: "index"` is the only special-cased filename in wiki-pro. `wiki read` with no arguments loads `index.md`. `wiki` with no subcommand displays the index note's content. No other filename receives special CLI treatment — `home.md`, `readme.md`, and `start.md` are regular notes.
