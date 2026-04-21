"""Rendering output for CLI commands."""

from __future__ import annotations

import json

from wiki_pro.query import QueryHit
from wiki_pro.spec import Note, SpecViolation


def render_hits(hits: list[QueryHit], as_json: bool = False) -> str:
    """Human: rich table with slug, score, summary, snippet. JSON: list of dicts."""
    if as_json:
        return json.dumps([
            {
                "slug": h.slug,
                "title": h.title,
                "score": h.score,
                "summary": h.summary,
                "snippet": h.snippet,
                "header_chain": h.header_chain,
                "tags": h.tags,
                "path": str(h.path),
            }
            for h in hits
        ], indent=2)

    if not hits:
        return "No results found."

    lines = []
    for h in hits:
        lines.append(f"[{h.score:.1f}] {h.slug}  —  {h.title}")
        lines.append(f"  Tags: {', '.join(h.tags)}")
        lines.append(f"  {h.summary}")
        if h.snippet:
            lines.append(f"  > {h.snippet}")
        if len(h.header_chain) > 1:
            lines.append(f"  Path: {' > '.join(h.header_chain)}")
        lines.append("")

    return '\n'.join(lines).rstrip()


def render_note(content: str, as_json: bool = False) -> str:
    """Human: raw markdown. JSON: {content: str}."""
    if as_json:
        return json.dumps({"content": content}, indent=2)
    return content


def render_list(notes: list[Note], as_json: bool = False) -> str:
    """Human: slug\\ttitle\\ttags lines. JSON: list of {slug, title, tags}."""
    if as_json:
        return json.dumps([
            {"slug": n.slug, "title": n.title, "tags": n.tags}
            for n in notes
        ], indent=2)

    if not notes:
        return "No notes found."

    lines = []
    for n in notes:
        tags_str = ", ".join(n.tags) if n.tags else "-"
        lines.append(f"{n.slug}\t{n.title}\t{tags_str}")
    return '\n'.join(lines)


def render_tags(tag_counts: dict[str, int], as_json: bool = False) -> str:
    """Human: tag (count) lines. JSON: {tag: count}."""
    if as_json:
        return json.dumps(tag_counts, indent=2)

    if not tag_counts:
        return "No tags found."

    lines = []
    for tag, count in sorted(tag_counts.items()):
        lines.append(f"{tag} ({count})")
    return '\n'.join(lines)


def render_violations(violations: list[SpecViolation], as_json: bool = False) -> str:
    """Human: path: field: message lines. JSON: list of dicts."""
    if as_json:
        return json.dumps([
            {"path": str(v.path), "field": v.field, "message": v.message}
            for v in violations
        ], indent=2)

    if not violations:
        return "No violations found."

    lines = []
    for v in violations:
        lines.append(f"{v.path}: {v.field}: {v.message}")
    return '\n'.join(lines)


def render_neighbours(hops: list[dict], as_json: bool = False) -> str:
    """Human: slug -> title (tags) lines. JSON: list of dicts."""
    if as_json:
        return json.dumps(hops, indent=2)

    if not hops:
        return "No neighbours found."

    lines = []
    for hop in hops:
        tags_str = ", ".join(hop.get("tags", [])) if hop.get("tags") else ""
        tag_part = f" ({tags_str})" if tags_str else ""
        lines.append(f"{hop['slug']} -> {hop['title']}{tag_part}")
    return '\n'.join(lines)
