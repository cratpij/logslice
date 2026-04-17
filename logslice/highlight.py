"""Terminal highlighting utilities for logslice output."""

from typing import Any

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_CYAN = "\033[36m"
ANSI_GRAY = "\033[90m"

LEVEL_COLORS = {
    "error": ANSI_RED,
    "err": ANSI_RED,
    "warn": ANSI_YELLOW,
    "warning": ANSI_YELLOW,
    "info": ANSI_GREEN,
    "debug": ANSI_GRAY,
}

TIMESTAMP_FIELDS = ("timestamp", "time", "ts", "@timestamp")
LEVEL_FIELDS = ("level", "severity", "lvl")
MESSAGE_FIELDS = ("message", "msg")


def colorize(text: str, color: str) -> str:
    return f"{color}{text}{ANSI_RESET}"


def highlight_record(record: dict[str, Any]) -> str:
    """Format a log record with ANSI color highlights."""
    parts = []

    for tf in TIMESTAMP_FIELDS:
        if tf in record:
            parts.append(colorize(str(record[tf]), ANSI_CYAN))
            break

    level_str = None
    for lf in LEVEL_FIELDS:
        if lf in record:
            level_str = str(record[lf])
            color = LEVEL_COLORS.get(level_str.lower(), ANSI_BOLD)
            parts.append(colorize(level_str.upper(), color))
            break

    for mf in MESSAGE_FIELDS:
        if mf in record:
            parts.append(str(record[mf]))
            break

    skip = set(TIMESTAMP_FIELDS) | set(LEVEL_FIELDS) | set(MESSAGE_FIELDS)
    extras = [
        f"{colorize(k, ANSI_BOLD)}={v}"
        for k, v in record.items()
        if k not in skip
    ]
    if extras:
        parts.append(" ".join(extras))

    return " ".join(parts)


def highlight_records(records: list[dict[str, Any]]) -> list[str]:
    """Return highlighted string for each record."""
    return [highlight_record(r) for r in records]
