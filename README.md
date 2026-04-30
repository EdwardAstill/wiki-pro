# wiki-pro

LLM-first CLI for querying and navigating markdown wikis.

wiki-pro defines a compact authoring spec for markdown-based wikis and ships
a `wiki` command that agents and humans can call to search, read, and propose
edits without loading entire note directories into context. It is designed to
be invoked by LLM skills where token efficiency matters: a single
`wiki query` + `wiki read slug#section` retrieves exactly the relevant
subsection rather than a whole file.

## Install

```bash
uv tool install git+https://github.com/EdwardAstill/wiki-pro
```

## Usage

```bash
# Search across all notes, return top 5 by relevance
wiki query "binary search sorted array"

# Filter search results by tag
wiki query "retrieval" --tag algorithms --limit 3

# Read an entire note
wiki read binary-search

# Read only one section (returns the ## subtree + the page lead)
wiki read binary-search#binary-search-time-complexity

# Follow related notes automatically
wiki read spec-headers --follow-related

# List all notes, or filter by tag
wiki list
wiki list --tag algorithms

# Show all tags with note counts
wiki tags

# Traverse the related-edge graph from a starting slug
wiki neighbours spec-headers --depth 2

# Validate all notes in the current wiki against spec
wiki validate

# Validate a single file
wiki validate wiki/spec-headers.md

# Check wiki health: broken wikilinks, broken related slugs, untagged notes, tag heuristics
wiki doctor

# Stage a proposed edit (does not modify the source file)
wiki propose spec-headers "## New subsection\nContent here." --reason "add missing guidance"

# List staged patches
wiki doctor --staged

# Apply or discard a staged patch
wiki apply 20260421T143000
wiki discard 20260421T143000

# Build or force-rebuild the search index
wiki index
wiki index --rebuild

# All commands accept --json for machine-readable output
wiki query "chunking" --json
```

## Configuration

**Wiki root discovery** — priority order:

1. `--root PATH` flag (repeatable; pass multiple roots for cross-wiki queries)
2. `WIKI_ROOT` environment variable — colon-separated list of root paths,
   same convention as `PATH`
3. Automatic walk-up from `$PWD` looking for a `.wiki-pro.toml` marker file

Mark a directory as a wiki root by placing an empty `.wiki-pro.toml` in it.

```bash
touch /path/to/my-wiki/.wiki-pro.toml
```

**Cross-wiki queries** — point at multiple roots to fan out a single query:

```bash
WIKI_ROOT=/home/user/warden/wiki:/home/user/notes wiki query "vacuum autovacuum"
# or
wiki query "vacuum autovacuum" --root /home/user/warden/wiki --root /home/user/notes
```

**Dot directory** — each wiki root gains a `.wiki-pro/` directory (gitignore
this) containing:

- `index.json` — cached header/tag/related index rebuilt by `wiki index`
- `staging/` — patch files written by `wiki propose`

**Note spec** — every note requires these frontmatter fields:

```yaml
---
title: "Header Discipline for LLM-Retrievable Wikis"
slug: "spec-headers"
tags: ["spec", "headers", "chunking"]
summary: "One sentence ≤200 chars — this is the preview line wiki query returns."
related: ["spec-chunking", "authoring-density"]
updated: "2026-04-21"
---
```

`slug` is the stable identifier; `[[wikilinks]]` and `wiki read` resolve by
slug, not filename. Links use `[[slug]]` or `[[slug|display label]]`.

## Templates

`templates/` contains copy-pasteable starters:

| File | Purpose |
|---|---|
| `templates/page.md` | Standard note skeleton with annotated frontmatter and section structure. Start here for any new note. |
| `templates/synthesis.md` | For notes that argue a relationship between two or more existing notes, rather than describing a single topic. Tag these `synthesis`. |
| `templates/scaffold/` | Minimal working wiki directory (`index.md` + `.wiki-pro.toml` + `example-note.md`). Copy it into any project to bootstrap a wiki: `cp -r templates/scaffold/ /path/to/new-wiki/` |

## Development

```bash
git clone https://github.com/EdwardAstill/wiki-pro
cd wiki-pro
uv sync
uv run wiki --version
```

Run tests:

```bash
uv run pytest
```

The `wiki/` directory in this repo is the dogfood wiki — the spec itself is
written as wiki notes and can be queried with `wiki query` against this repo.
It doubles as the primary test fixture for the CLI.
