"""Ranked search across wiki notes."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from wiki_pro.spec import load_all_notes, Note


@dataclass
class QueryHit:
    slug: str
    path: Path
    root: Path
    title: str
    summary: str
    snippet: str        # best matching body excerpt (<=200 chars)
    header_chain: list[str]  # [title, ## header, ### header] path to the hit
    score: float
    tags: list[str]


def _tokenize(text: str) -> list[str]:
    """Split text into lowercase tokens."""
    return re.findall(r'\w+', text.lower())


def _best_snippet(body: str, terms: list[str], max_len: int = 200) -> str:
    """Find the best matching excerpt from body (<=max_len chars)."""
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', body) if p.strip()]

    best_para = ""
    best_count = 0

    for para in paragraphs:
        para_lower = para.lower()
        count = sum(1 for term in terms if term in para_lower)
        if count > best_count:
            best_count = count
            best_para = para

    if not best_para and paragraphs:
        best_para = paragraphs[0]

    if len(best_para) <= max_len:
        return best_para

    # Try to find a centered window around the first term hit
    for term in terms:
        idx = best_para.lower().find(term)
        if idx != -1:
            start = max(0, idx - 50)
            end = min(len(best_para), start + max_len)
            snippet = best_para[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(best_para):
                snippet = snippet + "..."
            return snippet

    return best_para[:max_len] + "..."


def _score_note(note: Note, terms: list[str]) -> float:
    """Compute relevance score for a note given search terms."""
    score = 0.0

    title_lower = note.title.lower()
    summary_lower = note.summary.lower()
    body_lower = note.body.lower()

    body_hits = 0

    for term in terms:
        if term in title_lower:
            score += 10.0

        for level, htext in note.headers:
            htext_lower = htext.lower()
            if term in htext_lower:
                if level == 2:
                    score += 5.0
                elif level == 3:
                    score += 3.0

        for tag in note.tags:
            if term in tag.lower():
                score += 3.0

        if term in summary_lower:
            score += 2.0

        if term in body_lower and body_hits < 5:
            score += 1.0
            body_hits += 1

    return score


def _best_header_chain(note: Note, terms: list[str]) -> list[str]:
    """Build header chain [title, best ## match, best ### match]."""
    chain = [note.title]
    best_h2: str | None = None
    best_h3: str | None = None

    for level, text in note.headers:
        text_lower = text.lower()
        for term in terms:
            if term in text_lower:
                if level == 2 and best_h2 is None:
                    best_h2 = text
                elif level == 3 and best_h3 is None:
                    best_h3 = text

    if best_h2:
        chain.append(best_h2)
    if best_h3:
        chain.append(best_h3)

    return chain


def query(
    q: str,
    roots: list[Path],
    tags: list[str] | None = None,
    limit: int = 5,
) -> list[QueryHit]:
    """Ranked search across all roots.

    Scoring weights:
    - title match: 10 per term
    - ## header match: 5 per term, ### header: 3 per term
    - tag match: 3 per term
    - summary match: 2 per term
    - body match: 1 per term, capped at 5 per note

    If `tags` given, only notes that have ALL given tags are considered.
    Returns top `limit` hits, highest score first.
    """
    terms = _tokenize(q)
    if not terms:
        return []

    hits: list[QueryHit] = []

    for root in roots:
        notes, _ = load_all_notes(root)
        for note in notes:
            # Intersective tag filter
            if tags:
                note_tags_lower = [t.lower() for t in note.tags]
                if not all(t.lower() in note_tags_lower for t in tags):
                    continue

            score = _score_note(note, terms)
            if score <= 0:
                continue

            snippet = _best_snippet(note.body, terms)
            header_chain = _best_header_chain(note, terms)

            hits.append(QueryHit(
                slug=note.slug,
                path=note.path,
                root=note.root,
                title=note.title,
                summary=note.summary,
                snippet=snippet,
                header_chain=header_chain,
                score=score,
                tags=note.tags,
            ))

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]
