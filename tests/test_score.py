"""Tests for logslice.score."""

import pytest
from logslice.score import (
    filter_min_score,
    score_by_fn,
    score_record,
    score_records,
    top_scored,
)


RECORDS = [
    {"level": "error", "service": "auth", "status": "500"},
    {"level": "error", "service": "api",  "status": "500"},
    {"level": "info",  "service": "auth", "status": "200"},
    {"level": "warn",  "service": "db",   "status": "200"},
]


class TestScoreRecord:
    def test_full_match(self):
        r = score_record({"level": "error", "service": "auth"}, {"level": "error", "service": "auth"})
        assert r["_score"] == 2.0

    def test_partial_match(self):
        r = score_record({"level": "error", "service": "api"}, {"level": "error", "service": "auth"})
        assert r["_score"] == 1.0

    def test_no_match(self):
        r = score_record({"level": "info"}, {"level": "error"})
        assert r["_score"] == 0.0

    def test_weight_applied(self):
        r = score_record({"level": "error"}, {"level": "error"}, weight=2.5)
        assert r["_score"] == 2.5

    def test_does_not_mutate_original(self):
        original = {"level": "error"}
        score_record(original, {"level": "error"})
        assert "_score" not in original

    def test_missing_criterion_field(self):
        r = score_record({"level": "error"}, {"level": "error", "service": "auth"})
        assert r["_score"] == 1.0


class TestScoreRecords:
    def test_scores_all_records(self):
        results = score_records(RECORDS, {"level": "error"})
        assert len(results) == len(RECORDS)
        assert all("_score" in r for r in results)

    def test_correct_scores(self):
        results = score_records(RECORDS, {"level": "error", "service": "auth"})
        scores = [r["_score"] for r in results]
        assert scores == [2.0, 1.0, 1.0, 0.0]

    def test_empty_input(self):
        assert score_records([], {"level": "error"}) == []


class TestScoreByFn:
    def test_uses_callable(self):
        r = score_by_fn({"latency": 200}, fn=lambda rec: rec.get("latency", 0) / 100)
        assert r["_score"] == 2.0

    def test_custom_field_name(self):
        r = score_by_fn({"x": 3}, fn=lambda rec: 7.0, field="relevance")
        assert r["relevance"] == 7.0
        assert "_score" not in r


class TestTopScored:
    def test_returns_n(self):
        records = [{"_score": i} for i in range(10)]
        assert len(top_scored(records, 3)) == 3

    def test_highest_first(self):
        records = [{"_score": i} for i in range(5)]
        result = top_scored(records, 2)
        assert result[0]["_score"] == 4
        assert result[1]["_score"] == 3

    def test_n_larger_than_input(self):
        records = [{"_score": 1}, {"_score": 2}]
        assert len(top_scored(records, 100)) == 2


class TestFilterMinScore:
    def test_keeps_records_at_threshold(self):
        records = [{"_score": 1.0}, {"_score": 2.0}, {"_score": 0.0}]
        result = filter_min_score(records, 1.0)
        assert len(result) == 2

    def test_excludes_below_threshold(self):
        records = [{"_score": 0.5}]
        assert filter_min_score(records, 1.0) == []

    def test_empty_input(self):
        assert filter_min_score([], 1.0) == []
