"""Rank records by a numeric field, optionally within groups."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

Record = Dict[str, Any]


def _get_numeric(record: Record, field: str) -> Optional[float]:
    """Return numeric value of field, or None if missing/non-numeric."""
    val = record.get(field)
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def rank_records(
    records: Iterable[Record],
    field: str,
    rank_field: str = "rank",
    ascending: bool = True,
    dense: bool = False,
) -> List[Record]:
    """Rank all records by *field*.

    Records where *field* is missing or non-numeric receive rank None.
    Ties share the same rank.  When *dense* is True consecutive ranks are
    used (1, 2, 2, 3); otherwise standard competition ranking is used
    (1, 2, 2, 4).
    """
    items = list(records)
    sortable = [(i, _get_numeric(r, field)) for i, r in enumerate(items)]
    ranked_indices = [(i, v) for i, v in sortable if v is not None]
    ranked_indices.sort(key=lambda x: x[1], reverse=not ascending)

    rank_map: Dict[int, Optional[int]] = {i: None for i in range(len(items))}
    rank = 1
    for pos, (i, v) in enumerate(ranked_indices):
        if dense:
            if pos > 0 and v != ranked_indices[pos - 1][1]:
                rank += 1
        else:
            rank = pos + 1
            if pos > 0 and v == ranked_indices[pos - 1][1]:
                # find the rank assigned to the previous equal value
                rank = rank_map[ranked_indices[pos - 1][0]]  # type: ignore[assignment]
        rank_map[i] = rank

    result = []
    for i, record in enumerate(items):
        result.append({**record, rank_field: rank_map[i]})
    return result


def rank_within_group(
    records: Iterable[Record],
    field: str,
    group_field: str,
    rank_field: str = "rank",
    ascending: bool = True,
    dense: bool = False,
) -> List[Record]:
    """Rank records by *field* independently within each *group_field* value."""
    from collections import defaultdict

    groups: Dict[Any, List[int]] = defaultdict(list)
    items = list(records)
    for i, record in enumerate(items):
        key = record.get(group_field, None)
        groups[key].append(i)

    rank_map: Dict[int, Optional[int]] = {}
    for key, indices in groups.items():
        group_records = [items[i] for i in indices]
        ranked = rank_records(group_records, field, rank_field, ascending, dense)
        for original_i, ranked_record in zip(indices, ranked):
            rank_map[original_i] = ranked_record.get(rank_field)

    return [{**items[i], rank_field: rank_map[i]} for i in range(len(items))]


def top_ranked(
    records: Iterable[Record], rank_field: str = "rank", n: int = 1
) -> Iterator[Record]:
    """Yield records whose *rank_field* value is <= *n*."""
    for record in records:
        v = record.get(rank_field)
        if v is not None and v <= n:
            yield record
