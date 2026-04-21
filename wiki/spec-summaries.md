---
title: "Writing Effective Summaries"
slug: "spec-summaries"
tags: ["spec", "frontmatter", "retrieval"]
summary: "The summary field is the highest-leverage character you will write — it determines whether an LLM fetches the full note or skips it."
related: ["spec-frontmatter", "authoring-density"]
updated: "2026-04-21"
---

# Writing Effective Summaries

The `summary:` frontmatter field is the preview line an LLM reads when scanning query results to decide which notes to fetch — a weak summary causes correct notes to be skipped.

## What Happens to `summary` at Query Time

`wiki query "question"` returns a ranked list of hits. Each hit includes `title`, `summary`, `slug`, and `header_chain` — but not the note body. The LLM (or human) reads the summary to decide whether to issue a `wiki read slug` call to fetch the full note. If the summary does not communicate the note's specific value within the first reading, the note is skipped regardless of how good its body content is. The summary is the gate, not the content.

## How to Write a Summary That Works

An effective `summary:` satisfies four conditions simultaneously:

1. **Reads correctly in isolation** — no pronouns, no "this note", no references to context the reader doesn't have.
2. **Contains the primary retrievable term** — the term a user is most likely to query when they need this note. For `spec-headers.md`, the retrievable term is "headers" or "chunking". For `retrieval-when-to-embed.md`, it is "embeddings" or "when to add".
3. **States the key constraint or differentiator** — not just the topic, but the specific angle. "Frontmatter fields" is a topic. "The six frontmatter fields required by wiki-pro and why each one exists" is a differentiator.
4. **Fits in ≤200 characters** — the 200-char limit matches the typical preview window in RAG pipeline result displays. Summaries that exceed 200 chars are truncated at the cut point, which may land mid-sentence.

## Bad Summary Examples and Why They Fail

`"This note covers wikis."` — fails conditions 1 (implicit "this"), 2 (no retrievable term), and 3 (no differentiator). Every note in this wiki "covers wikis".

`"An overview of the frontmatter specification for wiki-pro notes."` — fails condition 3. "Overview" signals no specific value. The LLM cannot determine from this whether to prefer this note over [[spec-headers]] for a query about frontmatter.

`"Frontmatter fields."` — fails conditions 1, 3, and 4 (too short, not a sentence). Does not state what the note says about frontmatter fields.

## Good Summary Examples from This Wiki

`"The six frontmatter fields required by wiki-pro and why each one exists — title, slug, tags, summary, related, updated."` — 89 chars. Contains the retrievable terms (`frontmatter`, `title`, `slug`, `tags`, `summary`, `related`, `updated`). States the specific value (six fields, with names). Readable in isolation.

`"wiki-pro query ranking is deterministic and weighted: title matches score 10, ## headers 5, ### 3, tags 3, summary 2, body 1 — no ML required."` — 143 chars. Leads with the most differentiating fact (the weights). Contains the key terms (`query`, `ranking`, `weighted`). The phrase "no ML required" disambiguates from embedding-based systems.

`"Add embedding-based retrieval only when lexical search demonstrably fails — well-structured wikis with strong headers rarely hit this ceiling."` — 142 chars. States the decision threshold explicitly. Prevents the LLM from fetching this note for generic embedding questions when lexical search is sufficient.

## Why 200 Characters

200 characters is approximately 40–50 tokens in standard tokenisers. In a RAG pipeline returning 10 hits, reading 10 summaries at 50 tokens each costs 500 tokens — a small fraction of any modern context window. Summaries longer than 200 chars push total preview cost above 1000 tokens for 10 hits, which starts to crowd out the chunks the LLM needs for its actual response. The 200-char limit is a context budget decision, not an aesthetic one.

## Author-Written vs Auto-Extracted Summaries

Auto-extracted summaries (the first sentence of the note body, or the first `##` section's lead) reliably underperform author-written summaries. Auto-extracted first sentences are often structural (`"This note explains X."`) rather than value-declarative. Author-written summaries have full context about what makes the note distinctive. The `wiki validate` command enforces that `summary:` is non-empty and ≤200 chars but cannot enforce quality — quality is the author's responsibility.
