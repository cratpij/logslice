"""Tests for logslice.rollup."""

import pytest
from logslice.rollup import rollup, rollup_count_only, rollup_multi


RECORDS = [
    {"service": "api", "latency": 100},
    {"service": "api", "latency": 200},
    {"service": "api", "latency": 300},
    {"service": "db", "latency": 50},
    {"service": "db", "latency": 150},
]


class TestRollup:
    def test_groups_correctly(self):
        results = rollup(RECORDS, group_field="service", value_field="latency")
        keys = [r["service"] for r in results]
        assert "api" in keys
        assert "db" in keys

    def test_count_per_group(self):
        results = rollup(RECORDS, group_field="service", value_field="latency")
        by_key = {r["service"]: r for r in results}
        assert by_key["api"]["count"] == 3
        assert by_key["db"]["count"] == 2

    def test_sum_per_group(self):
        results = rollup(RECORDS, group_field="service", value_field="latency")
        by_key = {r["service"]: r for r in results}
        assert by_key["api"]["sum"] == 600.0
        assert by_key["db"]["sum"] == 200.0

    def test_avg_per_group(self):
        results = rollup(RECORDS, group_field="service", value_field="latency")
        by_key = {r["service"]: r for r in results}
        assert by_key["api"]["avg"] == pytest.approx(200.0)
        assert by_key["db"]["avg"] == pytest.approx(100.0)

    def test_min_max_per_group(self):
        results = rollup(RECORDS, group_field="service", value_field="latency")
        by_key = {r["service"]: r for r in results}
        assert by_key["api"]["min"] == 100.0
        assert by_key["api"]["max"] == 300.0
        assert by_key["db"]["min"] == 50.0
        assert by_key["db"]["max"] == 150.0

    def test_empty_input(self):
        results = rollup([], group_field="service", value_field="latency")
        assert results == []

    def test_non_numeric_value_excluded(self):
        records = [{"service": "api", "latency": "fast"}, {"service": "api", "latency": 100}]
        results = rollup(records, group_field="service", value_field="latency")
        assert results[0]["count"] == 1

    def test_missing_value_field_excluded(self):
        records = [{"service": "api"}, {"service": "api", "latency": 50}]
        results = rollup(records, group_field="service", value_field="latency")
        assert results[0]["count"] == 1

    def test_results_sorted_by_group(self):
        results = rollup(RECORDS, group_field="service", value_field="latency")
        keys = [r["service"] for r in results]
        assert keys == sorted(keys)


class TestRollupCountOnly:
    def test_returns_counts(self):
        results = rollup_count_only(RECORDS, group_field="service")
        by_key = {r["service"]: r for r in results}
        assert by_key["api"]["count"] == 3
        assert by_key["db"]["count"] == 2

    def test_no_sum_or_avg(self):
        results = rollup_count_only(RECORDS, group_field="service")
        for r in results:
            assert "sum" not in r
            assert "avg" not in r

    def test_empty_input(self):
        assert rollup_count_only([], group_field="service") == []

    def test_missing_group_field_uses_missing_key(self):
        records = [{"other": "x"}, {"service": "api"}]
        results = rollup_count_only(records, group_field="service")
        keys = [r["service"] for r in results]
        assert "__missing__" in keys


class TestRollupMulti:
    def test_multiple_value_fields(self):
        records = [
            {"svc": "api", "latency": 100, "errors": 1},
            {"svc": "api", "latency": 200, "errors": 0},
        ]
        results = rollup_multi(records, group_field="svc", value_fields=["latency", "errors"])
        assert len(results) == 1
        row = results[0]
        assert row["latency_count"] == 2
        assert row["latency_sum"] == 300.0
        assert row["errors_sum"] == 1.0

    def test_empty_input(self):
        results = rollup_multi([], group_field="svc", value_fields=["latency"])
        assert results == []

    def test_missing_value_field_gives_none(self):
        records = [{"svc": "api"}]
        results = rollup_multi(records, group_field="svc", value_fields=["latency"])
        assert results[0]["latency_count"] == 0
        assert results[0]["latency_sum"] is None
