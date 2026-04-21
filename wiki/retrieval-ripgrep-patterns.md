---
title: "Ripgrep Patterns for wiki-pro Navigation"
slug: "retrieval-ripgrep-patterns"
tags: ["retrieval", "tools", "ripgrep"]
summary: "Ripgrep patterns for navigating wiki-pro wikis directly from the terminal — useful for debugging, one-off lookups, and understanding what the wiki CLI does internally."
related: ["retrieval-header-ranking", "architecture-flat-over-nested"]
updated: "2026-04-21"
---

# Ripgrep Patterns for wiki-pro Navigation

`rg` (ripgrep) against a flat wiki directory covers the same retrieval operations as the `wiki` CLI in fewer keystrokes — useful for debugging broken indexes, shell scripting, and one-shot lookups where starting the CLI is overhead.

## File-Level Search Patterns

`rg "term" wiki/ -l --type md` returns the list of markdown files containing `term` without showing match context. The `-l` flag is the wiki equivalent of `wiki query "term"` with no body expansion — a fast triage pass before reading any note.

`rg "term" wiki/ --type md` returns the matching lines with file paths and line numbers, equivalent to `wiki query "term" --show-body`.

`rg "slug: " wiki/ --type md` returns every `slug:` declaration across all notes — useful for auditing that slugs are unique and for building a manual index.

## Section and Header Search Patterns

`rg "^## " wiki/ --type md` lists every `##` section header in the wiki with file and line number. Running this after authoring a batch of notes quickly reveals any bare generic headers (`## Overview`, `## Why`) that violate the [[spec-headers]] rules.

`rg "^#{1,3} " wiki/ --type md` captures `#`, `##`, and `###` headers in one pass — the full header tree across the wiki.

`rg "^## .*[Oo]verview|^## .*[Ww]hy$|^## .*[Ww]hat$|^## .*[Hh]ow$" wiki/ --type md` flags banned bare headers in one regex sweep. Pipe to `-l` to get a file list for repair.

## Frontmatter-Targeted Search Patterns

`rg "tags:.*retrieval" wiki/ --type md -l` returns all notes tagged `retrieval`. This is the `rg` equivalent of `wiki list --tag retrieval` — the frontmatter grep pattern matches the YAML array literal. Note: this pattern matches `"retrieval"` appearing anywhere in the `tags:` value, including `"retrieval-adjacent"` — add word boundaries (`\bretrievals?\b`) for precision when tag names share prefixes.

`rg "related:.*spec-headers" wiki/ --type md` returns all notes whose `related:` list includes the slug `spec-headers`. This is the `rg` equivalent of `wiki neighbours spec-headers --incoming` and is useful for auditing incoming link density.

`rg "summary: " wiki/ --type md` returns all summary lines — pipe through `awk '{print length, $0}' | sort -n` to find the longest summaries and check for ≤200 char violations.

`rg "updated: " wiki/ --type md` returns all `updated:` dates — useful for identifying stale notes (dates more than 6 months old) in a single pass.

## Why These Patterns Remain Useful When the CLI Exists

`rg` is available in any shell without process startup overhead or index state. Three scenarios where raw `rg` beats the CLI: (1) **Debugging a broken index** — when `wiki query` returns wrong results, `rg` against the raw files verifies whether the issue is in the source content or the index build; (2) **Shell scripting** — `rg` output pipes cleanly to standard Unix tools (`sort`, `awk`, `xargs`) without parsing CLI output formats; (3) **Bulk auditing** — checking the entire wiki for spec violations (bare headers, missing summaries, summary length) is faster as a one-liner than as a series of `wiki validate` calls.
