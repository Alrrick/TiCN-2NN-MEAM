"""Strict readers that retain block boundaries and report input locations."""

from math import isfinite
from pathlib import Path

from .models import ThermoBlock


def read_thermo(path: str | Path, *, max_blocks: int | None = None) -> tuple[ThermoBlock, ...]:
    """Read completed thermo blocks, accepting arbitrary whitespace/column order.

    A table starts with a header containing Step and ends at 'Loop time'.
    Unexpected text, nonfinite values, and incomplete tables fail explicitly.
    max_blocks is used only when a caller intentionally wants an initial prefix.
    """
    path = Path(path)
    if max_blocks is not None and max_blocks < 1:
        raise ValueError("max_blocks must be positive")
    blocks: list[ThermoBlock] = []
    columns: tuple[str, ...] | None = None
    rows: list[tuple[float, ...]] = []
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            tokens = line.split()
            location = f"{path}:{line_number}"
            if columns is None:
                if "Step" in tokens and len(tokens) > 1:
                    if len(set(tokens)) != len(tokens):
                        raise ValueError(f"{location}: duplicate thermo column")
                    columns = tuple(tokens)
                    rows = []
                continue
            if line.lstrip().startswith("Loop time"):
                if not rows:
                    raise ValueError(f"{location}: empty thermo block {len(blocks) + 1}")
                blocks.append(ThermoBlock(columns, tuple(rows)))
                columns = None
                if max_blocks is not None and len(blocks) == max_blocks:
                    return tuple(blocks)
                continue
            if not tokens:
                continue
            if len(tokens) != len(columns):
                raise ValueError(
                    f"{location}: expected {len(columns)} thermo columns, got {len(tokens)}"
                )
            try:
                row = tuple(float(token.replace(",", ".")) for token in tokens)
            except ValueError as exc:
                raise ValueError(f"{location}: nonnumeric thermo row") from exc
            if not all(isfinite(value) for value in row):
                raise ValueError(f"{location}: nonfinite thermo value")
            rows.append(row)
    if columns is not None:
        raise ValueError(
            f"{path}: incomplete thermo block {len(blocks) + 1}; expected Loop terminator"
        )
    if not blocks or (max_blocks is not None and len(blocks) < max_blocks):
        raise ValueError(f"{path}: missing thermo block {len(blocks) + 1}")
    return tuple(blocks)


def read_coordinates(path: str | Path) -> tuple[tuple[int, float], ...]:
    """Read two-header-line type/z exports; supported types: Ti=1, C=2, N=3."""
    path = Path(path)
    rows: list[tuple[int, float]] = []
    with path.open(encoding="utf-8") as stream:
        for _ in range(2):
            if not stream.readline():
                raise ValueError(f"{path}: missing coordinate header")
        for line_number, line in enumerate(stream, 3):
            if not line.strip():
                continue
            tokens = line.split()
            if len(tokens) != 2:
                raise ValueError(f"{path}:{line_number}: expected type and z columns")
            try:
                kind, z = map(float, tokens)
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: nonnumeric coordinate") from exc
            if kind not in (1, 2, 3) or not isfinite(z):
                raise ValueError(f"{path}:{line_number}: invalid atom type or nonfinite coordinate")
            rows.append((int(kind), z))
    if not rows:
        raise ValueError(f"{path}: empty coordinate data")
    return tuple(rows)
