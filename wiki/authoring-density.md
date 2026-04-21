---
title: "Authoring Density"
slug: "authoring-density"
tags: ["authoring", "style", "retrieval"]
summary: "High information density per sentence is the core authoring principle — every bullet is a hard fact, command, formula, or concrete trigger; no soft hedges, no filler."
related: ["authoring-anti-patterns", "spec-headers", "spec-summaries"]
updated: "2026-04-21"
---

# Authoring Density

Information density is the ratio of load-bearing words to total words — a dense note delivers maximum facts per token, which directly improves retrieval quality because every retrievable term in the note earns its place.

## What Density Means in Practice

A sentence is load-bearing if removing it loses a fact, a constraint, a threshold, a command, or a definition. A sentence is filler if it contextualises, hedges, or transitions without adding information. `"The summary field is important and authors should pay attention to it."` is filler — it conveys no fact about the summary field. `"The summary field is capped at 200 characters because that is the typical preview window in RAG pipeline result displays."` is load-bearing — it states the constraint (200 chars) and the reason (preview window size).

## The Soft Bullet Anti-Pattern

Every bullet in a wiki-pro note must be a hard fact, a specific command, a formula, or a concrete trigger. Soft bullets use hedging language that signals uncertainty or optionality when the author should be making a decision: "Consider using X", "You might want to try Y", "It can be useful to Z." Either X is correct in this context or it is not. State which: "Use X when condition A holds. Use Y when condition B holds." The reader is relying on the note to make the decision for them — hedge-free bullets are the author doing that work.

## Opening Sentences Must Name the Entity

Lead sentences in every paragraph must open with the named entity they are about, not a pronoun. `"It works by scanning the frontmatter block at file offset 0."` fails when excerpted — the reader does not know what "it" is. `"The wiki-pro CLI scans the frontmatter block at file offset 0."` survives extraction with full context intact. This rule is non-negotiable for RAG-first wikis: a chunk is often returned without its preceding context, so every sentence must be self-identifying.

## Concrete Beats Abstract

Thresholds, quantities, command names, and field names always outperform vague adjectives. `"The summary should be short."` is abstract and useless. `"The summary field is capped at 200 characters — approximately 50 tokens."` is concrete and actionable. `"Ranking uses higher weights for more important fields."` is abstract. `"Title matches score 10; body text scores 1."` is concrete. When the note has a number, use the number. When the note has a command, quote the command in `backticks`.

## The Zero Filler Test

For every sentence: remove it. Does the paragraph lose information? If no, delete the sentence. This test eliminates: topic sentences that merely announce what the paragraph will say, transitional sentences that connect paragraphs by summarising the previous one, and closing sentences that restate the opening. A well-structured `##` section does not need topic announcements — the header announces the topic. The section's first sentence delivers the first fact.

## Formatting Conventions That Serve Density

Four formatting rules enforce density mechanically:
- `backticks` for every code term, command, field name, file extension, and technical jargon — semantic precision prevents ambiguity between the concept and its name
- **Bold** for key concept highlights within body text — visual hierarchy that lets a scanning reader locate the load-bearing terms in a paragraph
- LaTeX for all formulas, variables, quantities, and chemical notation — prevents ambiguity between variable names and prose words
- Fenced code blocks with explicit language tag (` ```python `, ` ```bash `) for all multi-line code — never embed multi-line code inline in a paragraph
