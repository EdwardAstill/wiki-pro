---
title: "Markdown Parsing Landscape for wiki-pro Tooling"
slug: "news-markdown-parser-updates"
tags: ["news", "tools", "markdown"]
summary: "Markdown parsing landscape relevant to wiki-pro tooling — frontmatter libraries, header extraction, and CommonMark compliance as of 2026."
related: ["spec-frontmatter", "spec-headers"]
updated: "2026-04-21"
---

# Markdown Parsing Landscape for wiki-pro Tooling

wiki-pro's parsing requirements are narrow: extract YAML frontmatter, extract `#`/`##`/`###` headers, and split note bodies at `##` boundaries — tasks achievable without a full markdown AST.

## `python-frontmatter` for YAML Frontmatter Extraction

`python-frontmatter` is the recommended library for reading wiki-pro frontmatter. The library reads the YAML block delimited by `---` at the start of a file, parses it using `pyyaml`, and returns a `Post` object with `.metadata` (dict) and `.content` (string). The `title`, `slug`, `tags`, `summary`, `related`, and `updated` fields are accessible as `post.metadata["field"]`. Installation: `pip install python-frontmatter`. The library handles the `---` delimiter detection, YAML parsing, and body separation in one call: `post = frontmatter.load(filepath)`.

## `pyyaml` SafeLoader Requirement

`python-frontmatter` uses `pyyaml` as its YAML backend. All wiki-pro tooling must use `SafeLoader` exclusively — never `FullLoader`, `UnsafeLoader`, or `Loader`. `FullLoader` and `UnsafeLoader` can deserialise arbitrary Python objects from YAML, creating remote code execution risk if a wiki note is tampered with. `SafeLoader` deserialises only standard YAML types (strings, ints, floats, lists, dicts, booleans, null). The `tags:` and `related:` fields are YAML lists of strings — `SafeLoader` handles them correctly. `python-frontmatter` accepts a `handler` argument to specify the loader: `frontmatter.load(filepath, handler=frontmatter.YAMLHandler())` uses SafeLoader by default in current versions; verify this on upgrade.

## Header Extraction Without a Full AST

wiki-pro header extraction does not require a full markdown AST. The regex `^(#{1,3}) (.+)$` applied line-by-line correctly identifies `#`, `##`, and `###` headers for all wiki-pro notes, which follow the spec constraint of one `#` and well-formed `##`/`###` headers with no ambiguous ATX or Setext syntax. A full AST parser (`mistune`, `markdown-it-py`) is only required if the tool needs to: (1) render notes to HTML; (2) handle pathological markdown edge cases (headers inside code blocks, escaped `#` characters); (3) extract structured content beyond headers and frontmatter. For index building, chunk boundary detection, and `wiki validate`, the regex approach is sufficient and adds no dependencies.

## CommonMark vs GitHub Flavored Markdown

wiki-pro notes must be CommonMark-compatible — the strictest common subset of markdown syntax, with the widest renderer support. GitHub Flavored Markdown (GFM) is a superset of CommonMark that adds tables, strikethrough, task lists, and autolinks. wiki-pro notes use GFM tables (the `|---|` pipe table syntax) for comparison tables, which are a GFM extension not in base CommonMark. All other wiki-pro syntax is CommonMark-compatible. The practical implication: wiki-pro notes render correctly in GitHub, Obsidian, VS Code, and any CommonMark renderer; GFM tables degrade gracefully to literal `|` characters in pure CommonMark renderers.

## Frontmatter Position Constraint

The YAML frontmatter block must be the absolute first content in the file — no blank lines, no BOM, no content before the opening `---`. `python-frontmatter` enforces this: if the file does not start with `---`, the library returns an empty metadata dict and treats the entire file as body content. `wiki validate` checks for this condition and reports `"frontmatter not found at file offset 0"` when the delimiter is missing or preceded by content. The most common cause is a text editor that adds a trailing newline to a previously empty file before the author adds frontmatter — check with `head -1 notefile.md | xxd` if `wiki validate` reports unexpected frontmatter failures.
