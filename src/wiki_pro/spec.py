"""Parse and validate wiki notes against the spec."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter


REQUIRED_FIELDS = ("title", "slug", "tags", "summary", "updated")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
BANNED_HEADERS = {
    "overview", "mechanism", "why", "what", "how",
    "introduction", "background", "summary", "conclusion",
    "notes", "details",
}


@dataclass
class Note:
    path: Path
    root: Path
    title: str
    slug: str
    tags: list[str]
    summary: str
    related: list[str]  # slugs
    updated: str
    headers: list[tuple[int, str]]  # (level, text) for each ## and ###
    body: str  # full markdown body after frontmatter


@dataclass
class SpecViolation:
    path: Path
    field: str
    message: str


def _extract_headers(body: str) -> list[tuple[int, str]]:
    """Extract ## and ### headers from markdown body, ignoring fenced code blocks."""
    headers: list[tuple[int, str]] = []
    in_code_block = False
    for line in body.splitlines():
        if line.startswith("```") or line.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        m = re.match(r'^(#{2,3})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            headers.append((level, text))
    return headers


def _count_h1(body: str) -> int:
    """Count # (H1) headers in body, ignoring lines inside fenced code blocks."""
    count = 0
    in_code_block = False
    for line in body.splitlines():
        if line.startswith("```") or line.startswith("~~~"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue
        if re.match(r'^#\s+', line):
            count += 1
    return count


def parse_note(path: Path, root: Path) -> tuple[Note | None, list[SpecViolation]]:
    """Parse a .md file. Returns (Note, []) on success or (None, [violations]) on failure."""
    violations: list[SpecViolation] = []

    try:
        post = frontmatter.load(str(path))
    except Exception as e:
        return None, [SpecViolation(path=path, field="frontmatter", message=f"Failed to parse: {e}")]

    meta = post.metadata
    body = post.content

    # Check required fields
    for field_name in REQUIRED_FIELDS:
        val = meta.get(field_name)
        if val is None or val == "" or val == [] or val == {}:
            violations.append(SpecViolation(
                path=path,
                field=field_name,
                message=f"Required field '{field_name}' is missing or empty",
            ))

    if violations:
        return None, violations

    title = str(meta["title"])
    slug = str(meta["slug"])
    tags_raw = meta.get("tags", [])
    summary = str(meta["summary"])
    related_raw = meta.get("related", [])
    updated = str(meta["updated"])

    # Validate tags
    if not isinstance(tags_raw, list):
        violations.append(SpecViolation(path=path, field="tags", message="'tags' must be a list"))
    else:
        for t in tags_raw:
            if not isinstance(t, str):
                violations.append(SpecViolation(path=path, field="tags", message=f"Tag '{t}' must be a string"))

    # Validate related
    if related_raw is not None and not isinstance(related_raw, list):
        violations.append(SpecViolation(path=path, field="related", message="'related' must be a list"))
    else:
        if related_raw:
            for r in related_raw:
                if not isinstance(r, str):
                    violations.append(SpecViolation(path=path, field="related", message=f"Related '{r}' must be a string"))

    # Validate summary length
    if len(summary) > 200:
        violations.append(SpecViolation(
            path=path,
            field="summary",
            message=f"'summary' exceeds 200 chars (got {len(summary)})",
        ))

    # Validate updated format
    if not ISO_DATE_RE.match(updated):
        violations.append(SpecViolation(
            path=path,
            field="updated",
            message=f"'updated' must be YYYY-MM-DD, got '{updated}'",
        ))

    # Validate # appears exactly once in body
    h1_count = _count_h1(body)
    if h1_count != 1:
        violations.append(SpecViolation(
            path=path,
            field="body",
            message=f"Body must have exactly one # heading, found {h1_count}",
        ))

    # Extract headers
    headers = _extract_headers(body)

    # Check for banned generic headers
    for level, text in headers:
        normalized = text.strip().lower().rstrip(":").strip()
        if normalized in BANNED_HEADERS:
            violations.append(SpecViolation(
                path=path,
                field="headers",
                message=f"Banned generic header '{'#' * level} {text}' — name the topic instead",
            ))

    if violations:
        return None, violations

    return Note(
        path=path,
        root=root,
        title=title,
        slug=slug,
        tags=list(tags_raw) if isinstance(tags_raw, list) else [],
        summary=summary,
        related=list(related_raw) if isinstance(related_raw, list) else [],
        updated=updated,
        headers=headers,
        body=body,
    ), []


def load_all_notes(root: Path) -> tuple[list[Note], list[SpecViolation]]:
    """Walk root/*.md (flat), parse each, return all notes + all violations."""
    notes: list[Note] = []
    all_violations: list[SpecViolation] = []

    for md_file in sorted(root.glob("*.md")):
        note, violations = parse_note(md_file, root)
        if note is not None:
            notes.append(note)
        all_violations.extend(violations)

    return notes, all_violations
