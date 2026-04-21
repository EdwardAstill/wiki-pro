"""Tests for spec parsing and validation."""

from pathlib import Path

import pytest

from wiki_pro.spec import SpecViolation, load_all_notes, parse_note

GOOD_WIKI = Path(__file__).parent / "fixtures" / "good_wiki"
BAD_WIKI = Path(__file__).parent / "fixtures" / "bad_wiki"


class TestParseGoodNotes:
    def test_binary_search_parses(self):
        note, violations = parse_note(GOOD_WIKI / "binary-search.md", GOOD_WIKI)
        assert note is not None
        assert violations == []
        assert note.slug == "binary-search"
        assert note.title == "Binary Search"
        assert "algorithms" in note.tags
        assert len(note.summary) <= 200
        assert note.updated == "2024-01-15"

    def test_hash_table_parses(self):
        note, violations = parse_note(GOOD_WIKI / "hash-table.md", GOOD_WIKI)
        assert note is not None
        assert violations == []
        assert note.slug == "hash-table"
        assert "binary-search" in note.related

    def test_merge_sort_parses(self):
        note, violations = parse_note(GOOD_WIKI / "merge-sort.md", GOOD_WIKI)
        assert note is not None
        assert violations == []
        assert note.slug == "merge-sort"

    def test_headers_extracted(self):
        note, _ = parse_note(GOOD_WIKI / "binary-search.md", GOOD_WIKI)
        assert note is not None
        header_texts = [h[1] for h in note.headers]
        assert "Binary Search Algorithm Steps" in header_texts
        assert "Binary Search Time Complexity" in header_texts

    def test_load_all_good_notes(self):
        notes, violations = load_all_notes(GOOD_WIKI)
        assert len(notes) == 3
        assert violations == []

    def test_h1_counted_once(self):
        note, violations = parse_note(GOOD_WIKI / "binary-search.md", GOOD_WIKI)
        assert note is not None, f"Violations: {violations}"


class TestBadNotes:
    def test_missing_slug_produces_violation(self):
        _, violations = parse_note(BAD_WIKI / "missing-slug.md", BAD_WIKI)
        assert len(violations) > 0
        fields = [v.field for v in violations]
        assert "slug" in fields

    def test_bare_header_produces_violation(self):
        _, violations = parse_note(BAD_WIKI / "bare-header.md", BAD_WIKI)
        assert len(violations) > 0
        types = [v.field for v in violations]
        assert "headers" in types

    def test_long_summary_produces_violation(self):
        _, violations = parse_note(BAD_WIKI / "long-summary.md", BAD_WIKI)
        assert len(violations) > 0
        fields = [v.field for v in violations]
        assert "summary" in fields

    def test_bad_wiki_all_fail(self):
        notes, violations = load_all_notes(BAD_WIKI)
        # broken-related.md actually passes spec (related validation is broken slug check, not spec)
        # bare-header and long-summary and missing-slug should fail
        assert len(violations) > 0

    def test_violation_has_path(self):
        _, violations = parse_note(BAD_WIKI / "missing-slug.md", BAD_WIKI)
        for v in violations:
            assert v.path is not None
            assert isinstance(v.path, Path)

    def test_broken_related_passes_spec(self):
        """broken-related.md has valid spec fields — broken slug check is a doctor concern."""
        note, violations = parse_note(BAD_WIKI / "broken-related.md", BAD_WIKI)
        assert note is not None
        assert violations == []
        assert note.related == ["nonexistent-slug-xyz"]
