"""Tests for logslice.tail."""
import pytest
from logslice.tail import head_records, tail_records, skip_records, take_while, drop_while


RECORDS = [{"id": str(i), "status": "ok" if i < 3 else "err"} for i in range(6)]


class TestHeadRecords:
    def test_returns_first_n(self):
        result = head_records(RECORDS, 3)
        assert [r["id"] for r in result] == ["0", "1", "2"]

    def test_n_larger_than_input(self):
        result = head_records(RECORDS, 100)
        assert len(result) == len(RECORDS)

    def test_n_zero_returns_empty(self):
        assert head_records(RECORDS, 0) == []

    def test_empty_input(self):
        assert head_records([], 5) == []


class TestTailRecords:
    def test_returns_last_n(self):
        result = tail_records(RECORDS, 2)
        assert [r["id"] for r in result] == ["4", "5"]

    def test_n_larger_than_input(self):
        result = tail_records(RECORDS, 100)
        assert len(result) == len(RECORDS)

    def test_n_zero_returns_empty(self):
        assert tail_records(RECORDS, 0) == []

    def test_empty_input(self):
        assert tail_records([], 3) == []

    def test_exact_n(self):
        result = tail_records(RECORDS, len(RECORDS))
        assert result == RECORDS


class TestSkipRecords:
    def test_skips_first_n(self):
        result = list(skip_records(RECORDS, 2))
        assert [r["id"] for r in result] == ["2", "3", "4", "5"]

    def test_skip_zero_returns_all(self):
        result = list(skip_records(RECORDS, 0))
        assert result == RECORDS

    def test_skip_more_than_length(self):
        result = list(skip_records(RECORDS, 100))
        assert result == []

    def test_empty_input(self):
        assert list(skip_records([], 3)) == []


class TestTakeWhile:
    def test_yields_while_match(self):
        result = list(take_while(RECORDS, "status", "ok"))
        assert len(result) == 3
        assert all(r["status"] == "ok" for r in result)

    def test_stops_at_first_mismatch(self):
        result = list(take_while(RECORDS, "id", "0"))
        assert len(result) == 1

    def test_no_match_returns_empty(self):
        result = list(take_while(RECORDS, "status", "missing"))
        assert result == []


class TestDropWhile:
    def test_drops_while_match(self):
        result = list(drop_while(RECORDS, "status", "ok"))
        assert len(result) == 3
        assert all(r["status"] == "err" for r in result)

    def test_no_match_yields_all(self):
        result = list(drop_while(RECORDS, "status", "missing"))
        assert result == RECORDS

    def test_empty_input(self):
        assert list(drop_while([], "field", "val")) == []
