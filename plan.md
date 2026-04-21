# wiki-pro — Implementation Plan

> A standalone repo that (1) **defines** how LLM-friendly wikis should be structured, (2) **ships CLI tooling** skills/agents invoke to query and extend them, and (3) **dogfoods** itself — the spec lives inside a wiki it can query.

Dated 2026-04-21. Target host: `/home/eastill/projects/wiki-pro/`.

---

## 1. Scope & Non-Goals

### In scope
- A canonical wiki-authoring spec (markdown format, frontmatter schema, header conventions, linking rules) tuned for RAG retrieval and LLM chunking.
- A CLI — `wiki` — that exposes query/read/list/propose-edit operations against any directory that follows the spec.
- A self-referential example wiki (`wiki/`) where every page is itself a wiki note about wikis, used as the test fixture and living documentation.
- Scaffolding templates other projects (e.g. `warden/wiki/`, `knowledge/notes/`) can copy to conform.

### Out of scope (for v1)
- Embedding-based retrieval. Ripgrep + structural parsing first; only add vector search if measurement shows grep ceilings hit.
- Web UI. CLI + markdown only. `readrun` or other renderers can layer on later.
- Git/PR automation. `propose-edit` writes a staged file; humans commit.
- Multi-user write concurrency. Single-author assumption.

---

## 2. Repo Layout

```
wiki-pro/
├── README.md                   # Short orientation + pointer into wiki/
├── plan.md                     # This file.
├── pyproject.toml              # uv-managed Python project (matches warden/tools/python/)
├── uv.lock
├── src/
│   └── wiki_pro/
│       ├── __init__.py
│       ├── cli.py              # `wiki` entrypoint (typer or argparse)
│       ├── config.py           # WIKI_ROOT resolution, env vars, .wiki-pro.toml
│       ├── spec.py             # Parse/validate frontmatter + headers against spec
│       ├── index.py            # Build in-memory index of headers, tags, virtual_paths
│       ├── query.py            # Ranked grep: header > tag > body
│       ├── read.py             # Chunk-aware reader (return single section, not whole file)
│       ├── propose.py          # Stage edits to .wiki-pro/staging/<timestamp>.patch.md
│       └── render.py           # JSON + human-friendly output modes
├── tests/
│   ├── fixtures/               # Tiny malformed + well-formed wikis for testing
│   └── test_*.py
├── templates/
│   ├── page.md                 # Frontmatter + header skeleton
│   ├── synthesis.md            # Optional "overview note" template (replaces MOC)
│   └── scaffold/               # Copy-pasteable minimal wiki dir
│       ├── .wiki-pro.toml
│       ├── README.md
│       └── index.md
└── wiki/                         # The dogfood wiki — FLAT, one kebab-slug per file
    ├── .wiki-pro.toml
    ├── index.md                   # Lead page. Points at tag entry points, not a tree.
    ├── spec-frontmatter.md
    ├── spec-headers.md
    ├── spec-linking.md
    ├── spec-chunking.md
    ├── spec-summaries.md
    ├── architecture-flat-over-nested.md
    ├── architecture-tagging.md
    ├── architecture-related-edges.md
    ├── retrieval-ripgrep-patterns.md
    ├── retrieval-header-ranking.md
    ├── retrieval-when-to-embed.md
    ├── authoring-density.md
    ├── authoring-anti-patterns.md
    ├── authoring-naming.md
    ├── authoring-synthesis-notes.md
    ├── llm-chunking-behaviour.md
    ├── llm-context-budget.md
    ├── llm-why-trees-dont-help.md
    ├── news-2026-rag-state.md
    └── news-markdown-parser-updates.md
```

**Flat on disk.** No sub-folders inside `wiki/`. Categorisation is carried by `tags:` frontmatter and `related:` edges, both queryable via the CLI. Collisions are resolved by kebab-prefix (e.g. `spec-headers.md` vs `retrieval-headers.md`) — the prefix *is* the category hint and is visible to `rg` without needing tree traversal.

Rationale: mirrors `warden/tools/python/` conventions (uv, `src/` layout) so the `wiki` CLI can be pip-installed into warden's env or run standalone via `uv run wiki ...`.

---

## 3. The Spec (what `wiki/` enforces)

The spec itself is content in `wiki/spec-*.md`, but the load-bearing rules the CLI will **validate and rely on** are:

### 3.1 Frontmatter (required on every page)
```yaml
---
title: "Header Discipline for LLM-Retrievable Wikis"
slug: "spec-headers"
tags: ["spec", "headers", "chunking"]
summary: "Headers must name their topic in isolation — a retrieved ## subtree read without the page title must still identify what it's about."
related: ["spec-chunking", "authoring-density"]
updated: "2026-04-21"
---
```

- `title` — human-facing, free-form.
- `slug` — the stable identifier. Filename *may* equal slug but doesn't have to; decoupling lets you rename files without breaking `[[wikilinks]]`.
- `tags` — **the primary categorisation mechanism.** Multi-parent by nature. A note can be `retrieval` + `ranking` + `anti-pattern` at once — something a folder tree cannot express.
- `summary` — **the single most retrieval-critical field.** ≤200 chars. `wiki query` returns it as the preview line; LLMs read it to decide whether to fetch the full note. Author-written, not auto-extracted.
- `related` — explicit hop edges to other notes by slug. Replaces the need for `-moc.md` files: the graph of what-relates-to-what is emitted at author time per-note.
- `updated` — ISO date. Used to decay stale hits in ranking later.

**No `virtual_path`.** Rejected explicitly. Virtual paths encode a hierarchy that humans navigate and LLMs don't. `tags` + `related` express the same relationships in a form the CLI can query (`wiki query --tag retrieval`, `wiki read slug --follow related`) without simulating a tree.

### 3.2 Header discipline
- `#` exactly once (the page title, matching `title:`).
- `##` and `###` must be **topic-bearing when read in isolation**. No bare `## Mechanism`, `## Overview`, `## Why`. Name the thing.
- A paragraph directly under every `##` that restates the section's thesis in one sentence (the "RAG-priority paragraph" pattern from `knowledge/AI-NOTE-GUIDE.md`). This is what the chunked retrieval surface looks like.

### 3.3 Linking
- Internal: `[[slug]]` resolved by frontmatter `slug:`, not filename. Optional alias `[[slug|display]]`.
- External: standard markdown.
- The CLI's `wiki doctor` reports broken `[[...]]` targets.

### 3.4 No required structural files
Dropped from spec: `-moc.md`, `-roadmap.md`, `-glossary.md`, `-sources.md`, `-guide.md` as *required* conventions.

Reasoning:
- **Roadmaps** encode a linear reading order. LLMs retrieve non-linearly — a roadmap is pure human scaffolding and its cost (maintenance, reading-time overhead when retrieved) outweighs its value in an LLM-first wiki.
- **MOCs** duplicate what `tags` + `related` + `wiki query` already provide at query time.
- **Glossaries** duplicate what per-note definition-on-first-use already gives a retrieving LLM.

A high-density *synthesis note* (tagged `synthesis`) is still welcome — it's a first-class content piece, not a structural requirement. See `authoring-synthesis-notes.md` in the dogfood wiki for when to write one.

### 3.5 Naming
- kebab-case, **single flat dir per wiki**, no numeric prefixes, no sub-folders.
- Collisions resolved by kebab-prefix (`spec-headers.md` vs `retrieval-headers.md`). The prefix doubles as an informal category hint for `rg`.

---

## 4. The CLI — `wiki`

Single binary, subcommand-driven. All commands accept `--json` for machine consumption and default to a compact human format.

### 4.1 Commands

| Command | Purpose | Example |
| --- | --- | --- |
| `wiki query <q> [--tag T]... [--limit N]` | Ranked search across one or more wikis. Tags filter is intersective (all must match). Returns `{slug, path, header_chain, summary, snippet, score}` list. | `wiki query "vacuum" --tag postgres` |
| `wiki read <slug>[#section] [--follow related]` | Return one note or one section. `#section` returns only that `##`/`###` subtree plus the page lead. `--follow related` additionally emits the lead+summary of each note listed in `related:` frontmatter. | `wiki read spec-headers#header-discipline` |
| `wiki list [--tag T]...` | Flat list of notes, optionally filtered by tag(s). Output is `slug\ttitle\ttags` by default. | `wiki list --tag retrieval` |
| `wiki tags` | All tags with counts, descending. | `wiki tags` |
| `wiki neighbours <slug>` | Expand the `related:` graph one hop (or more with `--depth N`). Useful for LLM hop-expansion after a query hit. | `wiki neighbours spec-headers --depth 2` |
| `wiki validate [path]` | Lint frontmatter/headers/links against spec. Exit non-zero on failure. | `wiki validate wiki/` |
| `wiki propose <slug> <<<patch>` | Stage a proposed edit to `.wiki-pro/staging/`. Does not touch source files. | `wiki propose spec-headers "## New section\n..."` |
| `wiki index --rebuild` | Rebuild cached header/tag/related index (`.wiki-pro/index.json`). | |
| `wiki doctor` | Report broken `[[wikilinks]]`, broken `related:` slugs, untagged pages, missing summaries, spec violations. | |

Notably absent: no `--under <path>` filter. Navigation is by **tag and `related:` graph**, not by tree.

### 4.2 Wiki discovery
- `WIKI_ROOT` env var — colon-separated list of wiki roots (like `PATH`).
- `.wiki-pro.toml` in a dir marks it as a wiki root (analogous to `.git`). Commands walk up from `$PWD`.
- `--root <path>` flag overrides both.

A single `wiki query` can fan out across multiple roots so warden skills can query warden's own wiki **and** the personal knowledge base in one call.

### 4.3 Query ranking (v1)
Deterministic, no ML. Per-match score:
1. Title match (`title:` frontmatter) — weight 10.
2. Header match (`##`/`###`) — weight 5, decays with depth.
3. Tag match — weight 3.
4. `summary` match — weight 2.
5. Body match — weight 1, capped per note to prevent stuffing.

Returns top-N (default 5) with `header_chain` so the caller knows where in the doc the hit lives.

### 4.4 Read chunking
- `wiki read slug` → whole file.
- `wiki read slug#section` → the `##` or `###` subtree whose slugified header matches `section`, plus the page lead paragraph for context.
- Keeps token usage tight: a skill fetching one fact doesn't need the whole note.

### 4.5 Propose-edit
- Writes `<root>/.wiki-pro/staging/<iso-timestamp>-<slug>.patch.md` with:
  - Target file path
  - Proposer (env `WIKI_AUTHOR` or `$USER`)
  - Rationale (first line of patch or `--reason`)
  - Proposed new/edited markdown block
- Human reviews by running `wiki doctor --staged` (shows staged patches) and applies via `wiki apply <patch>` (v2 — v1 is manual copy).

---

## 5. Build Phases

Each phase leaves the repo in a usable state.

### Phase 0 — Bootstrap (half-day)
- `git init`, `uv init`, `pyproject.toml` with typer + rich + pyyaml + python-frontmatter.
- `README.md` pointing at `plan.md` and `wiki/index.md`.
- `wiki --version` runs.

### Phase 1 — Spec + dogfood wiki seed (1 day)
- Write `wiki/spec-frontmatter.md`, `spec-headers.md`, `spec-linking.md`, `spec-chunking.md`.
- Write `wikis-moc.md`, `wikis-roadmap.md`, `wikis-glossary.md`, `index.md`.
- Add `.wiki-pro.toml` marker.
- Commit: the spec now exists and is retrievable by eye.

### Phase 2 — Index + query (2 days)
- `wiki index --rebuild` walks root, parses frontmatter + headers, writes `.wiki-pro/index.json`.
- `wiki query` reads index, ranks, returns JSON + human output.
- Test against the seed wiki: `wiki query "chunking"` must return `spec-chunking.md` top.

### Phase 3 — Read + list + tags (1 day)
- Chunk-aware `wiki read`.
- `wiki list`, `wiki tags`.
- At this point a skill could usefully call `wiki query X && wiki read <top-hit>#<header>`.

### Phase 4 — Validate + doctor (1 day)
- Spec linter. Run it over the dogfood wiki; fix anything it flags. Repo now enforces its own rules.
- Broken-wikilink, orphan-page, untagged-page checks.

### Phase 5 — Fill out dogfood content (2–3 days)
- All files in §2 populated. Each one is itself a demonstration of the spec.
- Hits: architecture, retrieval, authoring, llm, news.
- This is also the acceptance test: a real LLM should be able to answer "how should I structure links in a wiki?" by calling `wiki query "link conventions"` and reading the top result.

### Phase 6 — Templates + scaffold (half-day)
- `templates/scaffold/` is a working minimal wiki you can `cp -r` into any project.
- `wiki new-wiki <path>` (optional convenience) copies the scaffold.

### Phase 7 — Propose-edit (1 day)
- Staging dir, patch format, `wiki propose`, `wiki doctor --staged`.

### Phase 8 — Warden integration (separate task, out of this repo)
- Add `warden/wiki/` using the scaffold.
- Pick 2–3 warden skills (`database-expert`, `python`, `observability`) and rewrite them to delegate reference lookups to `wiki query` across `WIKI_ROOT=warden/wiki:knowledge/notes`.
- Measure: do the skills get smaller? Do answers stay as good or improve?

### Phase 9 (maybe, later) — Embedding retrieval
- Only if Phase 8 shows `wiki query` missing obvious hits.
- Would add `wiki index --embed` producing a vector store; `wiki query --semantic` flag.
- Explicitly deferred — most value lands before this.

---

## 6. Key Decisions (flagged for confirmation)

1. **Language: Python 3.12 + uv.** Matches `warden/tools/python/`. Alternative was Rust (faster, single binary) — rejected for v1 because iteration speed > startup time, and skills can afford 50ms.
2. **CLI is both human- and LLM-facing.** Default output is compact human; `--json` for skill consumption. Not two separate tools.
3. **No hierarchy.** No `virtual_path`, no sub-folders inside a wiki, no required MOC/roadmap/glossary. Categorisation is carried entirely by `tags` + `related`. This is the single biggest departure from the `knowledge/` repo's pattern, and it's deliberate: this wiki is LLM-first, not dual-audience.
4. **No daemon, no server.** Every invocation re-reads the index file (cheap, <10ms for thousands of notes). Simpler than keeping a process alive.
5. **`.wiki-pro/` is the "dot-dir"** — stores `index.json`, `staging/`, maybe a `config.local.toml`. Gitignored by default in scaffolds.
6. **`slug` ≠ filename (by convention).** Links resolve by frontmatter `slug:`, not basename. Lets files be renamed/merged without link churn.

Decisions still open:
- Should `wiki query` support multi-root ranking out of the box, or require explicit `--root` per call?
- Should `propose` integrate with git (create a branch) or stay pure-filesystem? Lean toward pure-fs for v1.
- `summary` in frontmatter vs. first-paragraph-as-summary (auto-extracted)? Lean author-written: more reliable, and the friction is exactly the discipline we want.
- How strict should `validate` be about `related:` reciprocity? (If A lists B, must B list A?) Default lean: no — `related:` is a unidirectional author hint, not a symmetric graph assertion.

---

## 7. Success Criteria

v1 ships when all of the following are true:

1. `wiki validate wiki/` passes with zero warnings.
2. `wiki query "how should headers survive chunking"` returns `spec-headers.md` or `spec-chunking.md` as the top hit with a coherent snippet.
3. `wiki read spec-headers#header-discipline` returns only that subsection plus the page lead.
4. A fresh `cp -r templates/scaffold/ /tmp/test-wiki/` gives a working, validate-clean wiki.
5. A warden skill (pilot: `database-expert`) is rewritten to delegate to `wiki query` and observed to produce answers as good as the pre-delegation version on 3 sample questions.
6. The dogfood wiki is genuinely readable end-to-end by a human in ~20 minutes — not a stub farm.

---

## 8. Resolved Decisions

Answered with best-judgment defaults. Each is revisable before Phase 0 kicks off.

### 8.1 CLI name → `wiki`
No `$PATH` collisions observed on the target machine. Short, discoverable, self-documenting. If a future system tool claims it, rename is a one-line `pyproject.toml` change; wiki contents don't care.

### 8.2 Dogfood ownership → stays in `wiki-pro/wiki/` permanently
It *is* the spec and the test fixture simultaneously. Moving it into `knowledge/notes/` later would:
- decouple the spec from the validator that enforces it (`wiki validate wiki/` becomes a cross-repo coupling),
- force the personal KB to adopt this spec (it shouldn't — KB is dual-audience, wiki-pro is LLM-first),
- lose the self-referential check that every spec change is immediately pressure-tested on real content.

Keep it here. The `warden/wiki/` and any other downstream wikis are separate instances.

### 8.3 `propose-edit` ships with `apply` in v1
Reasoning: staged patches with no apply path rot. Primary audience is **LLMs suggesting updates mid-conversation, human-reviewed async**, which means the human needs a low-friction "accept this patch" command or they'll stop reviewing. v1 ships:
- `wiki propose` — stage.
- `wiki doctor --staged` — list pending patches with diff preview.
- `wiki apply <patch-id>` — apply + delete the patch file. Writes are pure-filesystem, no git integration; if the wiki is in a git repo, the human commits separately (explicit, predictable, no surprise commits).
- `wiki discard <patch-id>` — delete without applying.

### 8.4 Tags → freeform in v1, with `doctor` heuristics
Controlled vocabularies are good in mature systems and friction in young ones. The wiki won't have enough content in weeks 1–4 to know what the right tag list even is. v1 is freeform; `wiki doctor` flags:
- tags appearing on exactly 1 note (likely typo or one-off, candidate for merge/removal),
- tags within edit-distance ≤2 of a more-common tag (likely typo: `retreival` → `retrieval`),
- notes with >5 tags (likely unfocused).

If after Phase 8 the tag set has stabilised, Phase 9+ can introduce optional `[tags.controlled]` in `.wiki-pro.toml` to lock it down.

### 8.5 `knowledge/` interop → compatibility mode, deferred to Phase 8
The wiki-pro index parser will have a `--strict` flag (default true) that enforces this spec. A `--lenient` / `compat.knowledge = true` config mode will:
- accept `virtual_path:` but ignore it for ranking/queries,
- skip the "missing `summary:`" validator (fall back to first paragraph),
- skip the "missing `slug:`" validator (fall back to filename stem),
- skip the "missing `related:`" warning entirely,
- tolerate `-moc.md` / `-roadmap.md` files without flagging them as orphans.

This lets `WIKI_ROOT=warden/wiki:~/projects/knowledge/notes` work in Phase 8 without either touching the personal KB or polluting wiki-pro's strict spec. The compatibility mode is **read-only** — `wiki propose` refuses to write into a lenient root. You hand-edit the KB with your existing workflow.

---

## 9. Next Action

All blocking questions resolved. Phase 0 (bootstrap: `uv init`, `pyproject.toml`, `wiki --version`) is ready to start on request.
