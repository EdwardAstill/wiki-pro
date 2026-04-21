"""Wiki root resolution and path helpers."""

from __future__ import annotations

import os
from pathlib import Path


MARKER_FILE = ".wiki-pro.toml"


def find_wiki_root(start: Path) -> list[Path]:
    """Walk up from start looking for .wiki-pro.toml marker files. Returns all found roots."""
    roots: list[Path] = []
    current = start.resolve()
    while True:
        marker = current / MARKER_FILE
        if marker.exists():
            roots.append(current)
        parent = current.parent
        if parent == current:
            break
        current = parent
    return roots


def get_roots(root_flag: str | None = None) -> list[Path]:
    """Resolve wiki roots.

    Priority: root_flag > WIKI_ROOT env var (colon-separated) > walk up from cwd.
    Returns list of resolved Path objects.
    """
    if root_flag:
        return [Path(root_flag).resolve()]

    env_roots = os.environ.get("WIKI_ROOT", "")
    if env_roots:
        return [Path(p).resolve() for p in env_roots.split(":") if p]

    found = find_wiki_root(Path.cwd())
    if found:
        return found

    # Fall back to cwd if no marker found
    return [Path.cwd().resolve()]


def dot_dir(root: Path) -> Path:
    """Return root/.wiki-pro, creating it if missing."""
    d = root / ".wiki-pro"
    d.mkdir(exist_ok=True)
    return d


def index_path(root: Path) -> Path:
    """Return dot_dir(root) / index.json."""
    return dot_dir(root) / "index.json"


def staging_dir(root: Path) -> Path:
    """Return dot_dir(root) / staging, creating it if missing."""
    d = dot_dir(root) / "staging"
    d.mkdir(exist_ok=True)
    return d
