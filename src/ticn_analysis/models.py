"""Named results and explicit sampling settings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ThermoBlock:
    """One completed LAMMPS thermo table, with its original column names."""

    columns: tuple[str, ...]
    rows: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        if not self.columns or len(set(self.columns)) != len(self.columns):
            raise ValueError("thermo columns must be nonempty and unique")
        if any(len(row) != len(self.columns) for row in self.rows):
            raise ValueError("thermo row length does not match columns")

    def column(self, name: str) -> tuple[float, ...]:
        try:
            index = self.columns.index(name)
        except ValueError as exc:
            raise ValueError(f"missing required thermo column {name!r}") from exc
        return tuple(row[index] for row in self.rows)


@dataclass(frozen=True)
class Sampling:
    """Zero-based row slice within one explicitly selected thermo block."""

    start: int = 0
    stop: int | None = None
    stride: int = 1

    def __post_init__(self) -> None:
        if self.start < 0 or self.stride < 1:
            raise ValueError("start must be nonnegative and stride must be positive")
        if self.stop is not None and self.stop <= self.start:
            raise ValueError("stop must be greater than start")

    def select(self, block: ThermoBlock) -> ThermoBlock:
        if self.stop is not None and self.stop > len(block.rows):
            raise ValueError("stop exceeds the selected block's row count")
        rows = block.rows[self.start : self.stop : self.stride]
        if len(rows) < 2:
            raise ValueError("at least two selected samples are required")
        return ThermoBlock(block.columns, rows)


@dataclass(frozen=True)
class BulkResult:
    """Sample means and sample standard deviations, not standard errors."""

    lattice_mean_angstrom: float
    lattice_sd_angstrom: float
    potential_mean_ev: float
    potential_sd_ev: float
    sample_count: int

    def legacy_values(self) -> tuple[float, float, float, float]:
        return (
            self.lattice_mean_angstrom,
            self.lattice_sd_angstrom,
            self.potential_mean_ev,
            self.potential_sd_ev,
        )


@dataclass(frozen=True)
class LayerResult:
    """Pooled coordinate statistics; no independence of atoms/frames is assumed.

    The species SDs describe coordinate spread, not uncertainty of the mean.
    legacy_width_error_angstrom is only populated in explicit legacy mode.
    """

    titanium_mean_angstrom: float
    titanium_sd_angstrom: float
    anion_mean_angstrom: float
    anion_sd_angstrom: float
    width_angstrom: float
    titanium_count: int
    anion_count: int
    legacy_width_error_angstrom: float | None = None
