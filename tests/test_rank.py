"""Tests for logslice.rank."""

import pytest
from logslice.rank import rank_records, rank_within_group, top_ranked


RECORDS = [
    {"id": "a", "score": 10},
    {"id": "b", "score": 30},
    {"id": "c", "score": 20},
    {"id": "d", "score": 30},
]


class TestRankRecords:
    def test_ascending_rank_order(self):
        result = rank_records(RECORDS, "score")
        by_id = {r["id"]: r["rank"] for r in result}
        assert by_id["a"] == 1
        assert by_id["c"] == 2

    def test_descending_rank_order(self):
        result = rank_records(RECORDS, "score", ascending=False)
        by_id = {r["id"]: r["rank"] for r in result}
        assert by_id["b"] == 1
        assert by_id["d"] == 1
        assert by_id["a"] == 4

    def test_ties_share_rank_standard(self):
        result = rank_records(RECORDS, "score")
        by_id = {r["id"]: r["rank"] for r in result}
        # b and d both have score 30 — should share rank 3
        assert by_id["b"] == by_id["d"] == 3

    def test_dense_ranking_no_gaps(self):
        result = rank_records(RECORDS, "score", dense=True)
        by_id = {r["id"]: r["rank"] for r in result}
        # scores: 10->1, 20->2, 30->3 (dense, no gap after tie)
        assert by_id["a"] == 1
        assert by_id["c"] == 2
        assert by_id["b"] == 3
        assert by_id["d"] == 3

    def test_missing_field_gets_none_rank(self):
        records = [{"id": "x"}, {"id": "y", "score": 5}]
        result = rank_records(records, "score")
        by_id = {r["id"]: r["rank"] for r in result}
        assert by_id["x"] is None
        assert by_id["y"] == 1

    def test_non_numeric_field_gets_none_rank(self):
        records = [{"id": "x", "score": "high"}, {"id": "y", "score": 5}]
        result = rank_records(records, "score")
        by_id = {r["id"]: r["rank"] for r in result}
        assert by_id["x"] is None

    def test_custom_rank_field_name(self):
        result = rank_records(RECORDS, "score", rank_field="position")
        assert "position" in result[0]
        assert "rank" not in result[0]

    def test_does_not_mutate_originals(self):
        originals = [{"id": "a", "score": 1}]
        rank_records(originals, "score")
        assert "rank" not in originals[0]

    def test_empty_input_returns_empty(self):
        assert rank_records([], "score") == []


class TestRankWithinGroup:
    def test_ranks_independently_per_group(self):
        records = [
            {"grp": "A", "val": 10},
            {"grp": "A", "val": 20},
            {"grp": "B", "val": 5},
            {"grp": "B", "val": 50},
        ]
        result = rank_within_group(records, "val", "grp")
        a_ranks = [r["rank"] for r in result if r["grp"] == "A"]
        b_ranks = [r["rank"] for r in result if r["grp"] == "B"]
        assert sorted(a_ranks) == [1, 2]
        assert sorted(b_ranks) == [1, 2]

    def test_missing_group_field_grouped_together(self):
        records = [{"val": 1}, {"val": 2}]
        result = rank_within_group(records, "val", "grp")
        ranks = [r["rank"] for r in result]
        assert sorted(ranks) == [1, 2]


class TestTopRanked:
    def test_filters_to_top_n(self):
        records = [{"rank": 1}, {"rank": 2}, {"rank": 3}]
        result = list(top_ranked(records, n=2))
        assert len(result) == 2
        assert all(r["rank"] <= 2 for r in result)

    def test_includes_tied_ranks(self):
        records = [{"rank": 1}, {"rank": 1}, {"rank": 2}]
        result = list(top_ranked(records, n=1))
        assert len(result) == 2

    def test_none_rank_excluded(self):
        records = [{"rank": None}, {"rank": 1}]
        result = list(top_ranked(records, n=1))
        assert len(result) == 1
