"""Tests for read and follow_related functionality."""

from pathlib import Path

import pytest

from wiki_pro.read import follow_related, read_note, read_section, slugify_header

GOOD_WIKI = Path(__file__).parent / "fixtures" / "good_wiki"


class TestSlugifyHeader:
    def test_basic(self):
        assert slugify_header("Binary Search") == "binary-search"

    def test_with_punctuation(self):
        assert slugify_header("O(n log n) Complexity!") == "on-log-n-complexity"

    def test_lowercase(self):
        assert slugify_header("HASH TABLE") == "hash-table"

    def test_spaces_to_hyphens(self):
        assert slugify_header("Merge Sort vs Quick Sort") == "merge-sort-vs-quick-sort"


class TestReadNote:
    def test_read_existing_note(self):
        content = read_note("binary-search", [GOOD_WIKI])
        assert content is not None
        assert "# Binary Search" in content
        assert "binary_search" in content or "binary search" in content.lower()

    def test_read_nonexistent_note(self):
        content = read_note("nonexistent-slug", [GOOD_WIKI])
        assert content is None

    def test_read_contains_frontmatter(self):
        content = read_note("hash-table", [GOOD_WIKI])
        assert content is not None
        assert "slug:" in content
        assert "hash-table" in content

    def test_read_merge_sort(self):
        content = read_note("merge-sort", [GOOD_WIKI])
        assert content is not None
        assert "Merge Sort" in content


class TestReadSection:
    def test_read_existing_section(self):
        # Section slug for "Binary Search Time Complexity"
        section = slugify_header("Binary Search Time Complexity")
        content = read_section("binary-search", section, [GOOD_WIKI])
        assert content is not None
        assert "Time Complexity" in content

    def test_read_section_includes_lead_paragraph(self):
        section = slugify_header("Binary Search Time Complexity")
        content = read_section("binary-search", section, [GOOD_WIKI])
        assert content is not None
        # Lead paragraph should be prepended
        assert "divide-and-conquer" in content.lower() or "sorted" in content.lower()

    def test_read_section_not_found(self):
        content = read_section("binary-search", "nonexistent-section", [GOOD_WIKI])
        assert content is None

    def test_read_section_wrong_slug(self):
        section = slugify_header("Binary Search Time Complexity")
        content = read_section("nonexistent-note", section, [GOOD_WIKI])
        assert content is None

    def test_read_hash_table_collision_section(self):
        section = slugify_header("Hash Table Collision Resolution")
        content = read_section("hash-table", section, [GOOD_WIKI])
        assert content is not None
        assert "Chaining" in content or "chaining" in content


class TestFollowRelated:
    def test_follow_related_binary_search(self):
        related = follow_related("binary-search", [GOOD_WIKI])
        assert len(related) >= 1
        slugs = [r["slug"] for r in related]
        assert "hash-table" in slugs

    def test_follow_related_returns_dicts(self):
        related = follow_related("binary-search", [GOOD_WIKI])
        for r in related:
            assert "slug" in r
            assert "title" in r
            assert "summary" in r
            assert "lead_paragraph" in r

    def test_follow_related_nonexistent_note(self):
        related = follow_related("nonexistent-slug", [GOOD_WIKI])
        assert related == []

    def test_follow_related_summary_present(self):
        related = follow_related("hash-table", [GOOD_WIKI])
        for r in related:
            assert r["summary"] != ""
