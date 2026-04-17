"""Tests for logslice.highlight."""

import pytest
from logslice.highlight import (
    colorize,
    highlight_record,
    highlight_records,
    ANSI_RESET,
    ANSI_CYAN,
    ANSI_GREEN,
    ANSI_RED,
    ANSI_YELLOW,
    ANSI_GRAY,
    ANSI_BOLD,
)


def test_colorize_wraps_with_codes():
    result = colorize("hello", ANSI_RED)
    assert result.startswith(ANSI_RED)
    assert result.endswith(ANSI_RESET)
    assert "hello" in result


def test_highlight_record_timestamp():
    record = {"timestamp": "2024-01-01T00:00:00Z", "msg": "hi"}
    result = highlight_record(record)
    assert ANSI_CYAN in result
    assert "2024-01-01T00:00:00Z" in result


def test_highlight_record_level_error():
    record = {"level": "error", "msg": "boom"}
    result = highlight_record(record)
    assert ANSI_RED in result
    assert "ERROR" in result


def test_highlight_record_level_warn():
    record = {"level": "warn", "msg": "careful"}
    result = highlight_record(record)
    assert ANSI_YELLOW in result


def test_highlight_record_level_info():
    record = {"level": "info", "msg": "ok"}
    result = highlight_record(record)
    assert ANSI_GREEN in result


def test_highlight_record_level_debug():
    record = {"level": "debug", "msg": "trace"}
    result = highlight_record(record)
    assert ANSI_GRAY in result


def test_highlight_record_message_included():
    record = {"msg": "hello world"}
    result = highlight_record(record)
    assert "hello world" in result


def test_highlight_record_extra_fields():
    record = {"msg": "test", "request_id": "abc123"}
    result = highlight_record(record)
    assert "request_id" in result
    assert "abc123" in result


def test_highlight_record_no_known_fields():
    record = {"foo": "bar", "baz": 42}
    result = highlight_record(record)
    assert "foo" in result
    assert "bar" in result


def test_highlight_records_returns_list():
    records = [
        {"level": "info", "msg": "one"},
        {"level": "error", "msg": "two"},
    ]
    results = highlight_records(records)
    assert len(results) == 2
    assert all(isinstance(r, str) for r in results)


def test_highlight_records_empty():
    assert highlight_records([]) == []


def test_ts_alias_field():
    record = {"ts": "12:00:00", "msg": "ping"}
    result = highlight_record(record)
    assert ANSI_CYAN in result
