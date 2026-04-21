"""Index building, saving, and loading for wiki roots."""

from __future__ import annotations

import json
from pathlib import Path

from wiki_pro.config import index_path
from wiki_pro.spec import load_all_notes, Note


def _note_to_dict(note: Note) -> dict:
    return {
        "path": str(note.path),
        "root": str(note.root),
        "title": note.title,
        "tags": note.tags,
        "summary": note.summary,
        "related": note.related,
        "updated": note.updated,
        "headers": note.headers,
    }


def build_index(roots: list[Path]) -> dict:
    """Walk each root, parse all notes, return merged index dict."""
    all_notes: dict[str, dict] = {}
    tag_map: dict[str, list[str]] = {}
    related_graph: dict[str, list[str]] = {}

    for root in roots:
        notes, _ = load_all_notes(root)
        for note in notes:
            slug = note.slug
            all_notes[slug] = _note_to_dict(note)
            related_graph[slug] = note.related
            for tag in note.tags:
                tag_map.setdefault(tag, [])
                if slug not in tag_map[tag]:
                    tag_map[tag].append(slug)

    return {
        "notes": all_notes,
        "tags": tag_map,
        "related_graph": related_graph,
        "roots": [str(r) for r in roots],
    }


def save_index(index: dict, root: Path) -> None:
    """Write index to root/.wiki-pro/index.json."""
    path = index_path(root)
    path.write_text(json.dumps(index, indent=2), encoding="utf-8")


def load_index(roots: list[Path]) -> dict:
    """Load and merge indexes from all roots. If missing for a root, build it."""
    merged: dict = {
        "notes": {},
        "tags": {},
        "related_graph": {},
        "roots": [],
    }

    for root in roots:
        ipath = index_path(root)
        if ipath.exists():
            try:
                idx = json.loads(ipath.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                idx = build_index([root])
                save_index(idx, root)
        else:
            idx = build_index([root])
            save_index(idx, root)

        merged["notes"].update(idx.get("notes", {}))
        merged["roots"].extend(idx.get("roots", [str(root)]))

        for tag, slugs in idx.get("tags", {}).items():
            merged["tags"].setdefault(tag, [])
            for s in slugs:
                if s not in merged["tags"][tag]:
                    merged["tags"][tag].append(s)

        for slug, related in idx.get("related_graph", {}).items():
            merged["related_graph"][slug] = related

    return merged


def rebuild_index(roots: list[Path]) -> dict:
    """Force rebuild index for all roots, save, return merged."""
    merged: dict = {
        "notes": {},
        "tags": {},
        "related_graph": {},
        "roots": [],
    }

    for root in roots:
        idx = build_index([root])
        save_index(idx, root)
        merged["notes"].update(idx.get("notes", {}))
        merged["roots"].extend(idx.get("roots", [str(root)]))

        for tag, slugs in idx.get("tags", {}).items():
            merged["tags"].setdefault(tag, [])
            for s in slugs:
                if s not in merged["tags"][tag]:
                    merged["tags"][tag].append(s)

        for slug, related in idx.get("related_graph", {}).items():
            merged["related_graph"][slug] = related

    return merged
