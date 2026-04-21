"""wiki-pro CLI — LLM-first wiki tooling."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Optional

import typer

from wiki_pro import __version__
from wiki_pro.config import get_roots
from wiki_pro.index import build_index, load_index, rebuild_index, save_index
from wiki_pro.propose import apply_patch, discard_patch, list_staged, propose_edit
from wiki_pro.query import query as _query
from wiki_pro.read import follow_related, read_note, read_section, slugify_header
from wiki_pro.render import (
    render_hits,
    render_list,
    render_neighbours,
    render_note,
    render_tags,
    render_violations,
)
from wiki_pro.spec import SpecViolation, load_all_notes, parse_note


app = typer.Typer(name="wiki", help="LLM-first wiki CLI", no_args_is_help=True)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"wiki-pro {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option("--version", callback=_version_callback, is_eager=True, help="Show version and exit."),
    ] = None,
) -> None:
    """LLM-first wiki CLI."""


def _resolve_roots(root: list[str]) -> list[Path]:
    """Resolve root flags to list of Paths."""
    if root:
        return [Path(r).resolve() for r in root]
    return get_roots(None)


@app.command()
def query(
    q: Annotated[str, typer.Argument(help="Search query")],
    tag: Annotated[list[str], typer.Option("--tag", "-t", help="Filter by tag (repeatable, intersective)")] = [],
    limit: Annotated[int, typer.Option("--limit", "-n", help="Max results")] = 5,
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
    json_: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Search wiki notes by relevance."""
    roots = _resolve_roots(root)
    hits = _query(q, roots, tags=list(tag) if tag else None, limit=limit)
    typer.echo(render_hits(hits, as_json=json_))


@app.command()
def read(
    slug_section: Annotated[str, typer.Argument(help="slug or slug#section")],
    follow_rel: Annotated[bool, typer.Option("--follow-related", help="Include related notes")] = False,
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
    json_: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Read a note or a specific section."""
    roots = _resolve_roots(root)

    if "#" in slug_section:
        slug, section = slug_section.split("#", 1)
        content = read_section(slug, section, roots)
        if content is None:
            typer.echo(f"Error: note '{slug}' or section '{section}' not found.", err=True)
            raise typer.Exit(1)
    else:
        slug = slug_section
        content = read_note(slug, roots)
        if content is None:
            typer.echo(f"Error: note '{slug}' not found.", err=True)
            raise typer.Exit(1)

    typer.echo(render_note(content, as_json=json_))

    if follow_rel:
        related = follow_related(slug, roots)
        if related:
            if json_:
                import json
                typer.echo(json.dumps({"related": related}, indent=2))
            else:
                typer.echo("\n--- Related Notes ---")
                for r in related:
                    typer.echo(f"\n## {r['title']} ({r['slug']})")
                    typer.echo(r['summary'])
                    if r['lead_paragraph']:
                        typer.echo(r['lead_paragraph'])


@app.command("list")
def list_(
    tag: Annotated[list[str], typer.Option("--tag", "-t", help="Filter by tag (repeatable, intersective)")] = [],
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
    json_: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """List all notes, optionally filtered by tag."""
    roots = _resolve_roots(root)
    all_notes = []

    for r in roots:
        notes, _ = load_all_notes(r)
        all_notes.extend(notes)

    if tag:
        tag_set = {t.lower() for t in tag}
        all_notes = [
            n for n in all_notes
            if tag_set.issubset({t.lower() for t in n.tags})
        ]

    typer.echo(render_list(all_notes, as_json=json_))


@app.command()
def tags(
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
    json_: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Show all tags and their note counts."""
    roots = _resolve_roots(root)
    tag_counts: dict[str, int] = {}

    for r in roots:
        notes, _ = load_all_notes(r)
        for note in notes:
            for t in note.tags:
                tag_counts[t] = tag_counts.get(t, 0) + 1

    typer.echo(render_tags(tag_counts, as_json=json_))


def _collect_neighbours(slug: str, roots: list[Path], depth: int, visited: set[str]) -> list[dict]:
    """Recursively collect neighbour notes up to depth hops."""
    if depth <= 0 or slug in visited:
        return []
    visited.add(slug)

    all_notes = []
    for r in roots:
        notes, _ = load_all_notes(r)
        all_notes.extend(notes)

    slug_map = {n.slug: n for n in all_notes}
    target = slug_map.get(slug)
    if target is None:
        return []

    results: list[dict] = []
    for related_slug in target.related:
        if related_slug in visited:
            continue
        rn = slug_map.get(related_slug)
        if rn:
            results.append({
                "slug": rn.slug,
                "title": rn.title,
                "summary": rn.summary,
                "tags": rn.tags,
                "depth": 1,
            })
            if depth > 1:
                sub = _collect_neighbours(related_slug, roots, depth - 1, visited)
                results.extend(sub)

    return results


@app.command()
def neighbours(
    slug: Annotated[str, typer.Argument(help="Note slug to start from")],
    depth: Annotated[int, typer.Option("--depth", "-d", help="Hop depth")] = 1,
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
    json_: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Show notes reachable from a slug via related links."""
    roots = _resolve_roots(root)
    hops = _collect_neighbours(slug, roots, depth, set())
    typer.echo(render_neighbours(hops, as_json=json_))


@app.command()
def validate(
    path: Annotated[Optional[str], typer.Argument(help="Specific file to validate (default: all)")] = None,
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
    json_: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Validate notes against spec. Reports all violations."""
    roots = _resolve_roots(root)
    all_violations: list[SpecViolation] = []

    if path:
        p = Path(path).resolve()
        # Use the first root or the file's parent as root
        note_root = roots[0] if roots else p.parent
        _, violations = parse_note(p, note_root)
        all_violations.extend(violations)
    else:
        for r in roots:
            _, violations = load_all_notes(r)
            all_violations.extend(violations)

    typer.echo(render_violations(all_violations, as_json=json_))
    if all_violations:
        raise typer.Exit(1)


@app.command()
def propose(
    slug: Annotated[str, typer.Argument(help="Target note slug")],
    patch: Annotated[str, typer.Argument(help="Patch content (markdown text to append)")],
    reason: Annotated[str, typer.Option("--reason", help="Reason for the edit")] = "",
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
) -> None:
    """Stage an edit proposal for a note."""
    roots = _resolve_roots(root)
    patch_file = propose_edit(slug, patch, roots, reason=reason)
    typer.echo(f"Staged: {patch_file}")


@app.command()
def apply(
    patch_id: Annotated[str, typer.Argument(help="Patch ID (timestamp prefix or full stem)")],
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
) -> None:
    """Apply a staged patch to its target note."""
    roots = _resolve_roots(root)
    try:
        target = apply_patch(patch_id, roots)
        typer.echo(f"Applied to: {target}")
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def discard(
    patch_id: Annotated[str, typer.Argument(help="Patch ID (timestamp prefix or full stem)")],
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
) -> None:
    """Discard a staged patch without applying it."""
    roots = _resolve_roots(root)
    try:
        deleted = discard_patch(patch_id, roots)
        typer.echo(f"Discarded: {deleted}")
    except FileNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


def _levenshtein(a: str, b: str) -> int:
    """Compute edit distance between two strings."""
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            curr.append(min(prev[j + 1] + 1, curr[j] + 1, prev[j] + (ca != cb)))
        prev = curr
    return prev[-1]


@app.command()
def doctor(
    staged: Annotated[bool, typer.Option("--staged", help="Show staged patches instead of wiki health")] = False,
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
    json_: Annotated[bool, typer.Option("--json", help="Output JSON")] = False,
) -> None:
    """Check wiki health: broken links, spec violations, tag heuristics."""
    roots = _resolve_roots(root)

    if staged:
        patches = list_staged(roots)
        if json_:
            import json
            typer.echo(json.dumps(patches, indent=2))
        else:
            if not patches:
                typer.echo("No staged patches.")
            else:
                for p in patches:
                    typer.echo(f"{p['id']}  slug={p['slug']}  reason={p['reason']}  ts={p['timestamp']}")
        return

    all_notes = []
    all_violations: list[SpecViolation] = []

    for r in roots:
        notes, violations = load_all_notes(r)
        all_notes.extend(notes)
        all_violations.extend(violations)

    slug_set = {n.slug for n in all_notes}
    issues: list[dict] = []

    # Spec violations
    for v in all_violations:
        issues.append({"type": "spec_violation", "path": str(v.path), "field": v.field, "message": v.message})

    # Broken related slugs
    for note in all_notes:
        for rel in note.related:
            if rel not in slug_set:
                issues.append({
                    "type": "broken_related",
                    "slug": note.slug,
                    "broken_slug": rel,
                    "message": f"related slug '{rel}' not found",
                })

    # Broken wikilinks in body text
    import re
    _INLINE_CODE_RE = re.compile(r'`[^`\n]+`')
    _FENCED_CODE_RE = re.compile(r'```[\s\S]*?```', re.MULTILINE)
    for note in all_notes:
        # Strip fenced and inline code spans so backtick-quoted syntax examples
        # are not scanned for wikilink resolution.
        body_stripped = _FENCED_CODE_RE.sub('', note.body)
        body_stripped = _INLINE_CODE_RE.sub('', body_stripped)
        for match in re.finditer(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', body_stripped):
            link_slug = match.group(1).strip()
            if link_slug not in slug_set:
                issues.append({
                    "type": "broken_wikilink",
                    "slug": note.slug,
                    "broken_slug": link_slug,
                    "message": f"wikilink '[[{link_slug}]]' not found",
                })

    # Untagged notes
    for note in all_notes:
        if not note.tags:
            issues.append({"type": "untagged", "slug": note.slug, "message": "note has no tags"})

    # Missing summary
    for note in all_notes:
        if not note.summary.strip():
            issues.append({"type": "missing_summary", "slug": note.slug, "message": "note has empty summary"})

    # Tag heuristics
    tag_counts: dict[str, int] = {}
    for note in all_notes:
        for t in note.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1

    # Singleton tags
    for tag, count in tag_counts.items():
        if count == 1:
            issues.append({"type": "singleton_tag", "tag": tag, "message": f"tag '{tag}' used on only 1 note"})

    # Similar tags (edit distance <= 2)
    tag_list = sorted(tag_counts.keys())
    seen_pairs: set[frozenset] = set()
    for i, ta in enumerate(tag_list):
        for tb in tag_list[i + 1:]:
            pair = frozenset([ta, tb])
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if _levenshtein(ta, tb) <= 2:
                issues.append({
                    "type": "similar_tags",
                    "tag_a": ta,
                    "tag_b": tb,
                    "message": f"tags '{ta}' and '{tb}' are similar (edit distance <= 2)",
                })

    # Notes with >5 tags
    for note in all_notes:
        if len(note.tags) > 5:
            issues.append({
                "type": "too_many_tags",
                "slug": note.slug,
                "count": len(note.tags),
                "message": f"note has {len(note.tags)} tags (max recommended: 5)",
            })

    if json_:
        import json
        typer.echo(json.dumps(issues, indent=2))
    else:
        if not issues:
            typer.echo("Wiki looks healthy. No issues found.")
        else:
            for issue in issues:
                issue_type = issue.get("type", "unknown")
                msg = issue.get("message", "")
                ctx = issue.get("slug") or issue.get("tag") or issue.get("path") or ""
                if ctx:
                    typer.echo(f"[{issue_type}] {ctx}: {msg}")
                else:
                    typer.echo(f"[{issue_type}] {msg}")
        typer.echo(f"\n{len(issues)} issue(s) found across {len(all_notes)} note(s).")


@app.command("index")
def index_cmd(
    rebuild: Annotated[bool, typer.Option("--rebuild", help="Force rebuild")] = False,
    root: Annotated[list[str], typer.Option("--root", "-r", help="Wiki root path (repeatable)")] = [],
) -> None:
    """Build or rebuild the search index."""
    roots = _resolve_roots(root)
    if rebuild:
        idx = rebuild_index(roots)
        typer.echo(f"Rebuilt index: {len(idx.get('notes', {}))} notes across {len(roots)} root(s).")
    else:
        idx = load_index(roots)
        typer.echo(f"Index loaded: {len(idx.get('notes', {}))} notes across {len(roots)} root(s).")
