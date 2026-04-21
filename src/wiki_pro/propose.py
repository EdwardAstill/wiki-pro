"""Staging and applying edit proposals for wiki notes."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from wiki_pro.config import staging_dir
from wiki_pro.spec import load_all_notes


def _find_note_path(slug: str, roots: list[Path]) -> Path | None:
    """Find the path of a note by slug."""
    for root in roots:
        notes, _ = load_all_notes(root)
        for note in notes:
            if note.slug == slug:
                return note.path
    return None


def propose_edit(slug: str, patch_content: str, roots: list[Path], reason: str = "") -> Path:
    """Write a patch file to <primary_root>/.wiki-pro/staging/<iso-timestamp>-<slug>.patch.md.

    Format:
      ---
      target_slug: <slug>
      target_path: <resolved path>
      author: <WIKI_AUTHOR env or $USER>
      reason: <reason>
      timestamp: <iso>
      ---
      <patch_content>
    Returns the patch file path.
    """
    primary_root = roots[0]
    stage_dir = staging_dir(primary_root)

    target_path = _find_note_path(slug, roots)
    target_path_str = str(target_path) if target_path else "NOT_FOUND"

    author = os.environ.get("WIKI_AUTHOR") or os.environ.get("USER") or "unknown"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    patch_filename = f"{timestamp}-{slug}.patch.md"
    patch_file = stage_dir / patch_filename

    frontmatter_block = f"""---
target_slug: {slug}
target_path: {target_path_str}
author: {author}
reason: {reason}
timestamp: {timestamp}
---
"""

    patch_file.write_text(frontmatter_block + patch_content, encoding="utf-8")
    return patch_file


def list_staged(roots: list[Path]) -> list[dict]:
    """List all .patch.md files in staging dirs. Returns [{id, slug, reason, timestamp, path}]."""
    results: list[dict] = []

    for root in roots:
        stage_dir = staging_dir(root)
        for patch_file in sorted(stage_dir.glob("*.patch.md")):
            content = patch_file.read_text(encoding="utf-8")
            meta = _parse_patch_frontmatter(content)
            results.append({
                "id": patch_file.stem,
                "slug": meta.get("target_slug", ""),
                "reason": meta.get("reason", ""),
                "timestamp": meta.get("timestamp", ""),
                "path": str(patch_file),
            })

    return results


def _parse_patch_frontmatter(content: str) -> dict:
    """Parse simple frontmatter from patch file."""
    meta: dict = {}
    if not content.startswith("---"):
        return meta

    lines = content.splitlines()
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return meta

    for line in lines[1:end_idx]:
        if ":" in line:
            key, _, value = line.partition(":")
            meta[key.strip()] = value.strip()

    return meta


def _get_patch_body(content: str) -> str:
    """Extract body after frontmatter from patch file."""
    if not content.startswith("---"):
        return content

    lines = content.splitlines()
    end_idx = -1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            end_idx = i
            break

    if end_idx == -1:
        return content

    body_lines = lines[end_idx + 1:]
    return '\n'.join(body_lines).lstrip('\n')


def _find_patch(patch_id: str, roots: list[Path]) -> Path | None:
    """Find a patch file by id (timestamp prefix or full filename stem)."""
    for root in roots:
        stage_dir = staging_dir(root)
        for patch_file in stage_dir.glob("*.patch.md"):
            if patch_file.stem == patch_id or patch_file.stem.startswith(patch_id):
                return patch_file
    return None


def apply_patch(patch_id: str, roots: list[Path]) -> Path:
    """Find patch by id, append its content to the target note, delete patch. Returns modified note path."""
    patch_file = _find_patch(patch_id, roots)
    if patch_file is None:
        raise FileNotFoundError(f"No patch found with id '{patch_id}'")

    content = patch_file.read_text(encoding="utf-8")
    meta = _parse_patch_frontmatter(content)
    patch_body = _get_patch_body(content)

    target_path_str = meta.get("target_path", "")
    if not target_path_str or target_path_str == "NOT_FOUND":
        raise FileNotFoundError(f"Patch target path not found: '{target_path_str}'")

    target_path = Path(target_path_str)
    if not target_path.exists():
        raise FileNotFoundError(f"Target note file does not exist: {target_path}")

    existing = target_path.read_text(encoding="utf-8")
    if not existing.endswith('\n'):
        existing += '\n'
    target_path.write_text(existing + '\n' + patch_body, encoding="utf-8")

    patch_file.unlink()
    return target_path


def discard_patch(patch_id: str, roots: list[Path]) -> Path:
    """Delete the patch file without applying. Returns deleted patch path."""
    patch_file = _find_patch(patch_id, roots)
    if patch_file is None:
        raise FileNotFoundError(f"No patch found with id '{patch_id}'")

    path = patch_file
    patch_file.unlink()
    return path
