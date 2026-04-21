---
title: "Six Wiki Authoring Anti-Patterns"
slug: "authoring-anti-patterns"
tags: ["authoring", "anti-patterns", "spec"]
summary: "The six most common wiki authoring failures that degrade LLM retrieval — each one and its fix."
related: ["authoring-density", "spec-headers", "spec-chunking", "llm-chunking-behaviour"]
updated: "2026-04-21"
---

# Six Wiki Authoring Anti-Patterns

These six failure modes are the most common causes of degraded retrieval quality in wikis that otherwise follow the wiki-pro spec — each one has a precise fix.

## Anti-Pattern 1: Bare Generic Headers

Bare generic headers (`## Overview`, `## Why`, `## Background`, `## Details`) retrieve for every query that includes a generic term and carry zero topic signal when the chunk is excerpted.

**Bad:**
```markdown
## Overview
The ranking algorithm uses weighted scoring.
```

**Good:**
```markdown
## Overview of wiki-pro Weighted Query Ranking
wiki-pro ranks query results using deterministic field weights: title 10, ## header 5, ### header 3, tags 3, summary 2, body 1.
```

The fix: replace `## [GenericLabel]` with `## [GenericLabel] of [NamedTopic]`. See [[spec-headers]] for the full banned-header list and the isolation test.

## Anti-Pattern 2: Pronoun-Opening Sentences

Sentences that open with a pronoun (`"It works by..."`, `"They are used when..."`, `"This means that..."`) fail when the chunk is retrieved in isolation because the referent is absent.

**Bad:**
```markdown
It parses the frontmatter block first, then extracts the slug.
```

**Good:**
```markdown
The wiki-pro CLI parses the frontmatter block first, then extracts the `slug:` value for link resolution.
```

The fix: open every sentence in a `##` section with the named entity. `"The CLI"`, `"The `summary:` field"`, `"BM25 scoring"` — never `"it"`, `"they"`, or `"this"` as the grammatical subject of the opening clause.

## Anti-Pattern 3: Under-Frontmattering

A note with a missing or one-word `summary:` forces the LLM to fetch the full note to determine relevance, multiplying token cost by 10× per retrieval decision.

**Bad:**
```yaml
summary: "About frontmatter."
```

**Good:**
```yaml
summary: "The six frontmatter fields required by wiki-pro and why each one exists — title, slug, tags, summary, related, updated."
```

The fix: write the `summary:` last, after the note body is complete, so you know exactly what the note's specific value is. The summary must contain the primary retrievable term, state the key constraint, and be ≤200 characters. See [[spec-summaries]] for examples and the four-condition test.

## Anti-Pattern 4: Monolithic Notes

A note with all content under the `#` title and no `##` sections returns as a single 2000-token chunk for every query that matches any term in it, crowding out more relevant chunks and forcing the LLM to read the entire note to find one fact.

**Bad structure:**
```markdown
# Ranking Algorithm

The algorithm uses BM25. Title matches score higher. Body text scores lower. [2000 tokens of undivided prose]
```

**Good structure:**
```markdown
# Ranking Algorithm

The wiki-pro ranking algorithm is deterministic lexical scoring across five field types.

## Scoring Weights in wiki-pro Query Ranking
[200-token section on weights]

## Term Splitting and Score Accumulation
[200-token section on multi-term queries]

## Body Scoring Cap to Prevent Keyword Stuffing
[200-token section on the cap]
```

The fix: decompose any note over ~600 tokens into `##` sections of 150–400 tokens each. Each section covers exactly one sub-topic and is labelled with a self-identifying header.

## Anti-Pattern 5: Synonym Drift

Synonym drift occurs when the same concept is named differently across notes — `"chunk"` in one note, `"segment"` in another, `"excerpt"` in a third — causing queries for any one term to miss the others.

**Bad (three notes):**
- Note 1: `"A retrieval segment is the unit of text returned..."`
- Note 2: `"Chunks are bounded by ## headers..."`
- Note 3: `"The excerpt delivered to the LLM context..."`

**Good:**
- Pick one canonical term: `"chunk"` is canonical in wiki-pro.
- Use `"chunk"` in every note, every header, every summary.
- If a synonym must appear (quoting external sources), define it: `"A 'passage' (wiki-pro canonical term: chunk) is the unit of text..."`

The fix: run `wiki doctor --synonyms` after authoring a batch of notes to surface term variants. Consolidate to the canonical term wiki-wide. Define the canonical term in the most foundational note (in this wiki: [[llm-chunking-behaviour]]) and reference that definition from notes where ambiguity might arise.

## Anti-Pattern 6: Unfocused Tags

A note with 6–8 tags signals that the note has no clear topic and that no single tag "owns" it — which means `wiki list --tag X` for any of those tags returns this note as a diluted result, reducing tag precision across the wiki.

**Bad:**
```yaml
tags: ["retrieval", "ranking", "query", "llm", "embeddings", "architecture", "spec", "tools"]
```

**Good:**
```yaml
tags: ["retrieval", "ranking", "query"]
```

The fix: limit every note to ≤5 tags, prefer ≤3. If a note legitimately touches 6+ topic areas, it is probably two notes. Split the note, reduce the tag count on each half, and add a `related:` link between the two halves. A note's tags should describe its primary topic, not every topic it mentions.
