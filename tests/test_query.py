"""Tests for query/search functionality."""

from pathlib import Path

import pytest

from wiki_pro.query import query, QueryHit

GOOD_WIKI = Path(__file__).parent / "fixtures" / "good_wiki"


class TestQuery:
    def test_query_returns_hits(self):
        hits = query("binary search", [GOOD_WIKI])
        assert len(hits) > 0

    def test_query_top_hit_is_binary_search(self):
        hits = query("binary search sorted array", [GOOD_WIKI])
        assert hits[0].slug == "binary-search"

    def test_query_hit_fields(self):
        hits = query("binary search", [GOOD_WIKI])
        h = hits[0]
        assert isinstance(h.slug, str)
        assert isinstance(h.title, str)
        assert isinstance(h.summary, str)
        assert isinstance(h.snippet, str)
        assert isinstance(h.score, float)
        assert isinstance(h.tags, list)
        assert isinstance(h.header_chain, list)

    def test_query_limit(self):
        hits = query("sort algorithm", [GOOD_WIKI], limit=1)
        assert len(hits) <= 1

    def test_query_tag_filter(self):
        hits = query("sort", [GOOD_WIKI], tags=["sorting"])
        slugs = [h.slug for h in hits]
        assert "merge-sort" in slugs
        # binary-search does not have sorting tag
        assert "binary-search" not in slugs

    def test_query_tag_filter_intersective(self):
        # Both tags must be present
        hits = query("algorithm", [GOOD_WIKI], tags=["algorithms", "searching"])
        slugs = [h.slug for h in hits]
        assert "binary-search" in slugs
        assert "merge-sort" not in slugs  # merge-sort has algorithms but not searching

    def test_query_no_results_empty_query(self):
        hits = query("", [GOOD_WIKI])
        assert hits == []

    def test_query_no_match(self):
        hits = query("zxqwerty12345notarealterm", [GOOD_WIKI])
        assert hits == []

    def test_query_score_ordered(self):
        hits = query("binary search", [GOOD_WIKI])
        scores = [h.score for h in hits]
        assert scores == sorted(scores, reverse=True)

    def test_query_snippet_max_length(self):
        hits = query("hash", [GOOD_WIKI])
        for h in hits:
            assert len(h.snippet) <= 220  # allow for "..." padding

    def test_query_merge_sort_found(self):
        hits = query("merge sort divide conquer", [GOOD_WIKI])
        slugs = [h.slug for h in hits]
        assert "merge-sort" in slugs
