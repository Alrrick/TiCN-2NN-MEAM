"""Pure calculations, independent of plotting and output files."""

from collections.abc import Sequence
from math import isfinite, prod
from statistics import mean, stdev

import numpy as np

from .models import BulkResult, LayerResult, ThermoBlock


def bulk_statistics(
    block: ThermoBlock, *, cells: tuple[int, int, int], geometry: str
) -> BulkResult:
    """Compute an equivalent cubic cell length for a declared cubic bulk cell.

    Caller must establish cubic geometry and equilibrated sampling from the
    simulation. Volume alone cannot establish either condition.
    """
    if geometry != "cubic-bulk":
        raise ValueError(
            "lattice analysis requires cubic-bulk geometry; slab volume includes vacuum"
        )
    if len(cells) != 3 or any(type(n) is not int or n <= 0 for n in cells):
        raise ValueError("cells must contain three positive integers")
    volumes = block.column("Volume")
    energies = block.column("PotEng")
    if len(volumes) < 2:
        raise ValueError("at least two selected samples are required")
    if not all(isfinite(v) and v > 0 for v in volumes):
        raise ValueError("volumes must be finite and positive")
    if not all(isfinite(e) for e in energies):
        raise ValueError("potential energies must be finite")
    # Preserve the archived elementwise transformation before averaging.
    lattice = (np.asarray(volumes) / prod(cells)) ** (1 / 3)
    return BulkResult(
        float(mean(lattice)), float(stdev(lattice)), mean(energies), stdev(energies), len(volumes)
    )


def layer_statistics(
    coordinates: Sequence[tuple[int, float]], *, legacy: bool = False
) -> LayerResult:
    """Pool species positions. Inputs must already be in a consistent image.

    For periodic coordinates, unwrap before calling. No confidence interval is
    inferred from pooled, potentially correlated atom/frame observations.
    """
    if any(kind not in (1, 2, 3) or not isfinite(z) for kind, z in coordinates):
        raise ValueError("invalid atom type or nonfinite coordinate")
    ti = [z for kind, z in coordinates if kind == 1]
    anions = [z for kind, z in coordinates if kind != 1]
    if min(len(ti), len(anions)) < 2:
        raise ValueError("at least two coordinates per species group are required")
    z_ti, sd_ti, z_anion, sd_anion = mean(ti), stdev(ti), mean(anions), stdev(anions)
    width = abs(z_ti - z_anion)
    error = None
    if legacy:
        if z_ti == 0 or z_anion == 0:
            raise ValueError("legacy width error is undefined at a zero species mean")
        error = abs(width * sd_ti / z_ti + width * sd_anion / z_anion)
    return LayerResult(z_ti, sd_ti, z_anion, sd_anion, width, len(ti), len(anions), error)


def surface_energy(
    *,
    slab_energy_ev: float,
    atom_count: int,
    bulk_energy_per_atom_ev: float,
    face_area_angstrom2: float,
    equivalent_faces: bool,
) -> float:
    """Return eV/Å² for two equivalent faces and a composition-matched bulk.

    Caller must establish compatible composition, reference state, and potential.
    This formula does not implement chemical-potential corrections for excess atoms.
    """
    if not equivalent_faces:
        raise ValueError("this surface-energy formula requires two equivalent faces")
    if type(atom_count) is not int or atom_count <= 0:
        raise ValueError("atom_count must be a positive integer")
    if not all(isfinite(v) for v in (slab_energy_ev, bulk_energy_per_atom_ev, face_area_angstrom2)):
        raise ValueError("surface-energy inputs must be finite")
    if face_area_angstrom2 <= 0:
        raise ValueError("face area must be positive")
    return (slab_energy_ev - atom_count * bulk_energy_per_atom_ev) / (2 * face_area_angstrom2)
