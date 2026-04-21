"""Read notes and sections from wiki roots."""

from __future__ import annotations

import re
from pathlib import Path

import frontmatter

from wiki_pro.spec import load_all_notes, Note


def slugify_header(header: str) -> str:
    """Convert ## header text to slug format: lowercase, spaces->hyphens, punctuation stripped."""
    slug = header.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = slug.strip('-')
    return slug


def _find_note(slug: str, roots: list[Path]) -> tuple[Note | None, str | None]:
    """Find a note by slug across roots. Returns (note, raw_content)."""
    for root in roots:
        notes, _ = load_all_notes(root)
        for note in notes:
            if note.slug == slug:
                raw = note.path.read_text(encoding="utf-8")
                return note, raw
    return None, None


def _get_lead_paragraph(body: str) -> str:
    """Extract first paragraph after frontmatter, before first ##."""
    lines = body.splitlines()
    paragraphs: list[str] = []
    current: list[str] = []
    past_h1 = False

    for line in lines:
        if re.match(r'^#\s+', line):
            past_h1 = True
            if current:
                paragraphs.append('\n'.join(current).strip())
                current = []
            continue
        if re.match(r'^#{2,}', line):
            break
        if past_h1:
            if line.strip() == '':
                if current:
                    paragraphs.append('\n'.join(current).strip())
                    current = []
            else:
                current.append(line)

    if current:
        paragraphs.append('\n'.join(current).strip())

    return paragraphs[0] if paragraphs else ""


def read_note(slug: str, roots: list[Path]) -> str | None:
    """Return full markdown content of note with given slug. None if not found."""
    for root in roots:
        notes, _ = load_all_notes(root)
        for note in notes:
            if note.slug == slug:
                return note.path.read_text(encoding="utf-8")
    return None


def read_section(slug: str, section: str, roots: list[Path]) -> str | None:
    """Return only the ## or ### subtree whose slugified header matches `section`.

    Prepends the note's lead paragraph (first paragraph after H1, before first ##).
    `section` is slugified: lowercase, spaces->hyphens, punctuation stripped.
    Returns None if slug or section not found.
    """
    note, raw = _find_note(slug, roots)
    if note is None or raw is None:
        return None

    body = note.body
    lead = _get_lead_paragraph(body)

    lines = body.splitlines()
    section_lines: list[str] = []
    in_section = False
    section_level: int | None = None
    in_code_block = False

    for line in lines:
        # Track fenced code blocks to avoid matching headers inside them
        if line.startswith("```") or line.startswith("~~~"):
            in_code_block = not in_code_block
            if in_section:
                section_lines.append(line)
            continue

        if in_code_block:
            if in_section:
                section_lines.append(line)
            continue

        m = re.match(r'^(#{2,3})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            header_slug = slugify_header(text)

            if header_slug == section and not in_section:
                in_section = True
                section_level = level
                section_lines.append(line)
                continue

            if in_section:
                # Stop if we hit a header of same or higher level
                if level <= section_level:  # type: ignore[operator]
                    break
                section_lines.append(line)
        elif in_section:
            section_lines.append(line)

    if not section_lines:
        return None

    result_parts = []
    if lead:
        result_parts.append(lead)
        result_parts.append("")
    result_parts.extend(section_lines)

    return '\n'.join(result_parts)


def follow_related(slug: str, roots: list[Path]) -> list[dict]:
    """Return list of {slug, title, summary, lead_paragraph} for each slug in the note's related list."""
    note, _ = _find_note(slug, roots)
    if note is None:
        return []

    results: list[dict] = []
    for related_slug in note.related:
        related_note, _ = _find_note(related_slug, roots)
        if related_note is not None:
            lead = _get_lead_paragraph(related_note.body)
            results.append({
                "slug": related_note.slug,
                "title": related_note.title,
                "summary": related_note.summary,
                "lead_paragraph": lead,
            })

    return results
