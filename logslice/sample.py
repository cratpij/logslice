"""Sampling utilities for log records."""
from typing import List, Dict, Any, Optional
import random


def sample_records(
    records: List[Dict[str, Any]],
    n: int,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return up to n randomly sampled records."""
    if n <= 0:
        return []
    if n >= len(records):
        return list(records)
    rng = random.Random(seed)
    return rng.sample(records, n)


def sample_rate(
    records: List[Dict[str, Any]],
    rate: float,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Return records kept with probability equal to rate (0.0–1.0)."""
    if rate <= 0.0:
        return []
    if rate >= 1.0:
        return list(records)
    rng = random.Random(seed)
    return [r for r in records if rng.random() < rate]


def every_nth(
    records: List[Dict[str, Any]],
    n: int,
) -> List[Dict[str, Any]]:
    """Return every nth record (1-based index)."""
    if n <= 0:
        raise ValueError("n must be a positive integer")
    return [r for i, r in enumerate(records) if i % n == 0]
