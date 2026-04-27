"""Tests for logslice.lineage."""

import pytest
from logslice.lineage import (
    add_lineage_step,
    get_lineage,
    lineage_steps,
    start_lineage,
    strip_lineage,
    tag_records,
)


# ---------------------------------------------------------------------------
# start_lineage
# ---------------------------------------------------------------------------

def test_start_lineage_adds_lineage_key():
    r = start_lineage({"msg": "hello"})
    assert "_lineage" in r


def test_start_lineage_first_entry_has_source():
    r = start_lineage({"msg": "hello"}, source="file.log")
    assert r["_lineage"][0]["step"] == "file.log"
    assert r["_lineage"][0]["action"] == "read"


def test_start_lineage_does_not_mutate_original():
    original = {"msg": "hello"}
    start_lineage(original)
    assert "_lineage" not in original


# ---------------------------------------------------------------------------
# add_lineage_step
# ---------------------------------------------------------------------------

def test_add_step_appends_entry():
    r = start_lineage({"x": 1})
    r2 = add_lineage_step(r, "filter", "time_range", start="2024-01-01")
    steps = get_lineage(r2)
    assert len(steps) == 2
    assert steps[1]["step"] == "filter"
    assert steps[1]["action"] == "time_range"
    assert steps[1]["start"] == "2024-01-01"


def test_add_step_does_not_mutate_original():
    r = start_lineage({"x": 1})
    add_lineage_step(r, "sort", "asc")
    assert len(get_lineage(r)) == 1


def test_add_step_works_without_existing_lineage():
    r = add_lineage_step({"x": 1}, "enrich", "constant")
    assert get_lineage(r)[0]["step"] == "enrich"


# ---------------------------------------------------------------------------
# strip_lineage
# ---------------------------------------------------------------------------

def test_strip_lineage_removes_key():
    r = start_lineage({"msg": "hi"})
    stripped = strip_lineage(r)
    assert "_lineage" not in stripped


def test_strip_lineage_preserves_other_fields():
    r = start_lineage({"msg": "hi", "level": "info"})
    stripped = strip_lineage(r)
    assert stripped == {"msg": "hi", "level": "info"}


def test_strip_lineage_noop_when_absent():
    r = {"msg": "hi"}
    assert strip_lineage(r) == {"msg": "hi"}


# ---------------------------------------------------------------------------
# lineage_steps
# ---------------------------------------------------------------------------

def test_lineage_steps_returns_names():
    r = start_lineage({"x": 1}, source="input")
    r = add_lineage_step(r, "filter", "field")
    r = add_lineage_step(r, "sort", "asc")
    assert lineage_steps(r) == ["input", "filter", "sort"]


def test_lineage_steps_empty_when_no_lineage():
    assert lineage_steps({"x": 1}) == []


# ---------------------------------------------------------------------------
# tag_records
# ---------------------------------------------------------------------------

def test_tag_records_applies_to_all():
    records = [{"a": 1}, {"a": 2}]
    tagged = tag_records(records, "dedupe", "by_field", field="id")
    assert all("_lineage" in r for r in tagged)


def test_tag_records_with_source_initialises_lineage():
    records = [{"a": 1}]
    tagged = tag_records(records, "sort", "asc", source="stdin")
    steps = lineage_steps(tagged[0])
    assert steps == ["stdin", "sort"]


def test_tag_records_empty_input():
    assert tag_records([], "sort", "asc") == []
