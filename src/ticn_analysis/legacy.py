"""Explicit compatibility with the archived selection and numerical formulas.

Legacy slab lengths and width errors are historical diagnostics, not validated
physical lattice parameters or confidence intervals.
"""

from dataclasses import asdict
from pathlib import Path
from typing import Any

from .analysis import bulk_statistics
from .io import read_thermo
from .models import BulkResult, ThermoBlock
from .reporting import plot_lattice, provenance, write_json

COMPOSITIONS = ("1.0", "0.75", "0.5", "0.25", "0.0")
COLUMNS = ("Step", "PotEng", "KinEng", "Temp", "Volume", "Press")


def legacy_block(path: str | Path, *, block_count: int = 2) -> ThermoBlock:
    blocks = read_thermo(path, max_blocks=block_count)
    rows: list[tuple[float, ...]] = []
    for block in blocks:
        columns = [block.column(name) for name in COLUMNS]
        rows.extend(zip(*columns, strict=True))
    return ThermoBlock(COLUMNS, tuple(rows))


def data_reader(path: str | Path, curve_number: int = 3) -> tuple[Any, ...]:
    """Historical six-value reader interface; prefer read_thermo for new code."""
    block = legacy_block(path, block_count=curve_number - 1)
    return (
        [list(row) for row in block.rows],
        *[list(block.column(name)) for name in ("Step", "Temp", "Volume", "Press", "PotEng")],
    )


def legacy_statistics(path: str | Path, *, block_count: int = 2) -> BulkResult:
    block = legacy_block(path, block_count=block_count)
    selected = ThermoBlock(block.columns, block.rows[150:-1])
    # This intentionally reproduces the archived formula even for slab cases.
    # Only the legacy entry point may use it without a physical bulk declaration.
    return bulk_statistics(selected, cells=(8, 8, 8), geometry="cubic-bulk")


def analyze_folder(
    folder_name: str | Path, archive_name: str, *, block_count: int = 2
) -> tuple[float, float, float, float]:
    result = legacy_statistics(Path(folder_name) / f"{archive_name}1.log", block_count=block_count)
    values = result.legacy_values()
    print(f"{folder_name}\n  a : {values[0]} {values[1]}\n pot: {values[2]} {values[3]}")
    return values


def run_stability(
    directory: Path,
    output: Path,
    *,
    kind: str = "bulk",
    overwrite: bool = False,
    show: bool = False,
) -> None:
    if kind not in ("bulk", "surface-100", "surface-other"):
        raise ValueError(f"unknown legacy case kind: {kind}")
    count = 3 if kind == "surface-100" else 2
    paths = [
        directory / f"{label}-Ti(C{x},N{COMPOSITIONS[::-1][i]})" / "temp_v1.log"
        for i, (label, x) in enumerate(zip("ABCDE", COMPOSITIONS, strict=True))
    ]
    destinations = [
        output / name for name in ("results.txt", "lattice_parameter.png", "provenance.json")
    ]
    if not overwrite:
        for destination in destinations:
            if destination.exists():
                raise FileExistsError(f"{destination} exists; use --overwrite to replace outputs")
    results = [legacy_statistics(path, block_count=count) for path in paths]
    metadata = provenance(
        paths,
        {
            "mode": "legacy",
            "kind": kind,
            "block_count": count,
            "slice": [150, -1],
            "cells": [8, 8, 8],
        },
    )
    metadata["results"] = [asdict(result) for result in results]
    metadata["limitations"] = [
        "Historical block selection and row slice; equilibration is not established.",
        "Spreads are sample standard deviations, not standard errors.",
    ]
    if kind != "bulk":
        metadata["limitations"].append(
            "Slab length includes vacuum and is not a physical lattice parameter."
        )
    output.mkdir(parents=True, exist_ok=True)
    lines = ["x a err_a en_pot err_en_pot"]
    for x, result in zip(COMPOSITIONS, results, strict=True):
        lines.append(" ".join(map(str, (float(x), *result.legacy_values()))).replace(".", ","))
    destinations[0].write_text("\n".join(lines) + "\n", encoding="utf-8")
    plot_lattice(
        [float(x) for x in COMPOSITIONS],
        [r.lattice_mean_angstrom for r in results],
        [r.lattice_sd_angstrom for r in results],
        destinations[1],
        legacy_surface=kind != "bulk",
        show=show,
    )
    write_json(destinations[2], metadata, overwrite=overwrite)
