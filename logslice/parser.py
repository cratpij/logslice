"""Parse structured log lines (JSON or key=value) into dicts."""

import json
import re
from typing import Optional


KV_PATTERN = re.compile(r'(\w+)=("[^"]*"|\S+)')


def parse_json_line(line: str) -> Optional[dict]:
    """Attempt to parse a line as JSON. Returns None on failure."""
    line = line.strip()
    if not line:
        return None
    try:
        obj = json.loads(line)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    return None


def parse_kv_line(line: str) -> Optional[dict]:
    """Attempt to parse a key=value log line. Returns None if no pairs found."""
    line = line.strip()
    if not line:
        return None
    matches = KV_PATTERN.findall(line)
    if not matches:
        return None
    result = {}
    for key, value in matches:
        # Strip surrounding quotes
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        result[key] = value
    return result if result else None


def parse_line(line: str) -> Optional[dict]:
    """Parse a log line, trying JSON first then key=value format."""
    parsed = parse_json_line(line)
    if parsed is not None:
        return parsed
    return parse_kv_line(line)


def parse_lines(lines) -> list[dict]:
    """Parse an iterable of log lines, skipping unparseable entries."""
    results = []
    for line in lines:
        entry = parse_line(line)
        if entry is not None:
            results.append(entry)
    return results
