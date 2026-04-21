# wiki-pro

LLM-first CLI for querying and navigating markdown wikis.

## Install

```bash
uv sync
```

## Quickstart

```bash
# Search across all notes
wiki query "binary search sorted array"

# Read a full note
wiki read binary-search

# Read a specific section
wiki read binary-search#binary-search-time-complexity

# List notes filtered by tag
wiki list --tag algorithms

# Check wiki health
wiki doctor

# Validate spec compliance
wiki validate
```

## Configuration

Mark a directory as a wiki root by placing a `.wiki-pro.toml` file in it. Set `WIKI_ROOT` env var (colon-separated paths) to target specific roots, or pass `--root PATH` to any command.

## Spec

See `wiki/index.md` for the full note spec. Required frontmatter fields: `title`, `slug`, `tags`, `summary`, `updated`.
