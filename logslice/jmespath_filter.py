"""Filter and extract fields from log records using JMESPath expressions."""

from typing import Any, Dict, Iterable, Iterator, List, Optional

try:
    import jmespath
    _JMESPATH_AVAILABLE = True
except ImportError:  # pragma: no cover
    _JMESPATH_AVAILABLE = False


def _require_jmespath() -> None:
    if not _JMESPATH_AVAILABLE:  # pragma: no cover
        raise ImportError(
            "jmespath is required for JMESPath filtering. "
            "Install it with: pip install jmespath"
        )


def compile_expression(expr: str) -> Any:
    """Compile a JMESPath expression string, raising ValueError on invalid syntax."""
    _require_jmespath()
    try:
        return jmespath.compile(expr)
    except jmespath.exceptions.ParseError as exc:
        raise ValueError(f"Invalid JMESPath expression {expr!r}: {exc}") from exc


def evaluate(record: Dict[str, Any], expr: str) -> Any:
    """Evaluate a JMESPath expression against a single record."""
    _require_jmespath()
    compiled = compile_expression(expr)
    return compiled.search(record)


def filter_by_expression(
    records: Iterable[Dict[str, Any]],
    expr: str,
) -> Iterator[Dict[str, Any]]:
    """Yield records where the JMESPath expression evaluates to a truthy value."""
    compiled = compile_expression(expr)
    for record in records:
        result = compiled.search(record)
        if result:
            yield record


def extract_field(
    records: Iterable[Dict[str, Any]],
    expr: str,
    dest: str,
    overwrite: bool = True,
) -> Iterator[Dict[str, Any]]:
    """Add a new field *dest* to each record whose value is the result of *expr*.

    Records where the expression returns None are passed through unchanged
    unless *overwrite* is True and the destination field already exists.
    """
    compiled = compile_expression(expr)
    for record in records:
        value = compiled.search(record)
        if value is None and dest not in record:
            yield record
            continue
        if not overwrite and dest in record:
            yield record
            continue
        updated = {**record, dest: value}
        yield updated


def project(
    records: Iterable[Dict[str, Any]],
    expressions: Dict[str, str],
) -> Iterator[Dict[str, Any]]:
    """Build a new record from named JMESPath expressions.

    *expressions* maps output field name -> JMESPath expression string.
    Fields whose expression returns None are omitted from the output.
    """
    compiled = {name: compile_expression(expr) for name, expr in expressions.items()}
    for record in records:
        out: Dict[str, Any] = {}
        for name, compiled_expr in compiled.items():
            value = compiled_expr.search(record)
            if value is not None:
                out[name] = value
        yield out
