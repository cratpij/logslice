"""Tests for logslice.lookup."""

from __future__ import annotations

import json
import os
import tempfile
from typing import Dict, Any

import pytest

from logslice.lookup import load_lookup_table, lookup_join, lookup_filter

Record = Dict[str, Any]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_jsonl(rows, tmp_path):
    path = os.path.join(tmp_path, "lookup.jsonl")
    with open(path, "w") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    return path


# ---------------------------------------------------------------------------
# load_lookup_table
# ---------------------------------------------------------------------------

class TestLoadLookupTable:
    def test_indexes_by_key_field(self, tmp_path):
        path = _write_jsonl([{"id": "1", "name": "Alice"}, {"id": "2", "name": "Bob"}], str(tmp_path))
        table = load_lookup_table(path, "id")
        assert table["1"]["name"] == "Alice"
        assert table["2"]["name"] == "Bob"

    def test_skips_rows_without_key(self, tmp_path):
        path = _write_jsonl([{"name": "Alice"}, {"id": "2", "name": "Bob"}], str(tmp_path))
        table = load_lookup_table(path, "id")
        assert len(table) == 1

    def test_skips_invalid_json_lines(self, tmp_path):
        p = os.path.join(str(tmp_path), "lookup.jsonl")
        with open(p, "w") as fh:
            fh.write("not json\n")
            fh.write(json.dumps({"id": "3", "v": "ok"}) + "\n")
        table = load_lookup_table(p, "id")
        assert "3" in table

    def test_empty_file_returns_empty_table(self, tmp_path):
        path = _write_jsonl([], str(tmp_path))
        assert load_lookup_table(path, "id") == {}


# ---------------------------------------------------------------------------
# lookup_join
# ---------------------------------------------------------------------------

TABLE = {"1": {"id": "1", "city": "London", "tier": "gold"}, "2": {"id": "2", "city": "Paris", "tier": "silver"}}


class TestLookupJoin:
    def test_merges_all_fields_by_default(self):
        records = [{"user_id": "1", "event": "login"}]
        result = list(lookup_join(records, TABLE, on="user_id"))
        assert result[0]["city"] == "London"
        assert result[0]["event"] == "login"

    def test_subset_of_fields(self):
        records = [{"user_id": "1", "event": "login"}]
        result = list(lookup_join(records, TABLE, on="user_id", fields=["city"]))
        assert "city" in result[0]
        assert "tier" not in result[0]

    def test_prefix_applied_to_joined_fields(self):
        records = [{"user_id": "2", "event": "buy"}]
        result = list(lookup_join(records, TABLE, on="user_id", prefix="lu_"))
        assert "lu_city" in result[0]
        assert "city" not in result[0]

    def test_no_match_uses_missing_fallback(self):
        records = [{"user_id": "99", "event": "x"}]
        result = list(lookup_join(records, TABLE, on="user_id", fields=["city"], missing={"city": "Unknown"}))
        assert result[0]["city"] == "Unknown"

    def test_no_match_without_fallback_passes_through(self):
        records = [{"user_id": "99", "event": "x"}]
        result = list(lookup_join(records, TABLE, on="user_id"))
        assert result[0] == {"user_id": "99", "event": "x"}

    def test_does_not_mutate_original(self):
        original = {"user_id": "1", "event": "e"}
        list(lookup_join([original], TABLE, on="user_id"))
        assert "city" not in original


# ---------------------------------------------------------------------------
# lookup_filter
# ---------------------------------------------------------------------------

class TestLookupFilter:
    def test_keeps_matching_records(self):
        records = [{"user_id": "1"}, {"user_id": "99"}]
        result = list(lookup_filter(records, TABLE, on="user_id"))
        assert len(result) == 1
        assert result[0]["user_id"] == "1"

    def test_invert_keeps_non_matching(self):
        records = [{"user_id": "1"}, {"user_id": "99"}]
        result = list(lookup_filter(records, TABLE, on="user_id", invert=True))
        assert len(result) == 1
        assert result[0]["user_id"] == "99"

    def test_empty_input_returns_empty(self):
        assert list(lookup_filter([], TABLE, on="user_id")) == []
