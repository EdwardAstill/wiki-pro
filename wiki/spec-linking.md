---
title: "Internal Linking Spec"
slug: "spec-linking"
tags: ["spec", "linking", "wikilinks"]
summary: "Internal links use [[slug]] syntax resolved against frontmatter slug: fields — not filenames — so files can be renamed without breaking links."
related: ["spec-frontmatter", "architecture-related-edges"]
updated: "2026-04-21"
---

# Internal Linking Spec

Internal cross-references in wiki-pro use `[[slug]]` wikilink syntax resolved against the `slug:` frontmatter field of the target note, not against filenames — this decouples the link graph from the file system so that renaming a file never breaks a link.

## `[[slug]]` vs `[[slug|display label]]` Syntax

`[[slug]]` renders using the target note's `title:` as the display text. `[[slug|display label]]` overrides the display text with a custom label, useful when the note title is long or the surrounding prose calls for a different phrasing. Both forms resolve identically at query time — the slug is the identity, not the label. Example: `[[spec-headers|header discipline]]` links to the `spec-headers` note but displays as "header discipline" in rendered output.

## Why Slug-Resolved Links Beat Filename-Resolved Links

Slug-resolved links survive file renames without any link-update sweep. When the note `spec-frontmatter.md` is renamed to `frontmatter-spec.md`, every `[[spec-frontmatter]]` link remains valid because the file still declares `slug: "spec-frontmatter"` in its frontmatter. Filename-resolved links break on rename and require a grep-and-replace across the entire wiki. The slug is a stable identifier chosen at note creation and never changed — the filename is a display artifact that can evolve.

## External URLs Use Standard Markdown Syntax

External links use `[display text](https://url)` — standard CommonMark syntax. The `[[...]]` syntax is reserved for internal slug resolution only. Mixing the two syntaxes in the same note is correct: `[[spec-headers]]` for an internal hop, `[CommonMark spec](https://spec.commonmark.org)` for an external reference.

## `wiki doctor` Validates `[[...]]` Targets

`wiki doctor` scans every `[[slug]]` and `[[slug|label]]` occurrence in the wiki and checks each slug against the index of known `slug:` values. Broken links — slugs with no matching note — are reported with the file and line number. `wiki doctor` also reports orphaned notes (notes with no incoming `[[...]]` links and no `related:` entries) and notes that appear in `related:` lists but whose slugs do not exist.

## `related:` vs Inline `[[...]]` — When to Use Each

The `related:` frontmatter field and inline `[[wikilinks]]` serve different purposes. `related:` is a curated navigation graph: it lists the notes a reader should visit next, expressed as an author-declared structural relationship. Inline `[[...]]` links are prose references: they appear where the text naturally mentions another concept and the reader might want to follow the reference. The rule: if the connection is "this note and that note are closely related in topic", use `related:`. If the connection is "this sentence references a concept explained in that note", use `[[...]]` inline. A note can have both — they are not redundant.
