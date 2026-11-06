# 2NN MEAM simulations of TiCₓN₁₋ₓ

LAMMPS inputs, structures, potential files, archived logs, and Python analysis
for titanium carbonitride in the B1 (rock-salt) structure. The archive covers
five carbon fractions: x = 1, 0.75, 0.5, 0.25, and 0.

The reference article is A. Araya-Barr et al., **Second nearest neighbor modified
embedded atom method interatomic potentials for TiCₓN₁₋ₓ ternary systems**,
*Computational Materials Science* 231 (2024), 112615,
[doi:10.1016/j.commatsci.2023.112615](https://doi.org/10.1016/j.commatsci.2023.112615).
The publisher PDF is deliberately excluded from Git.

The author identifies **`Tablitas de datos BulkCorrected.xlsx` as the source of
final published results**. The root-level **`TiCN.meam` and `library.meam`** are
the potential files designated by the author for sharing. Copies are retained
inside simulation directories so the original relative paths continue to work.

The archive also contains intermediate simulation inputs and logs. Some differ
from the article and workbook; a complete automated reproduction of all final
results has not been verified. See the [archive audit](docs/archive-audit.md)
for those distinctions. Numerical settings were preserved during translation.

## Contents

| Location | Purpose |
| --- | --- |
| `TiCN.meam`, `library.meam` | Author-designated potential files for reuse |
| `Temp_Stab/` | Bulk NPT simulations and lattice/energy analysis |
| `Elastic/` | Static finite-strain elastic tensor calculations; v1–v4 inputs |
| `Surfaces/1k (100) Real/` | (100) slabs |
| `Surfaces/1k (110)/` | (110) slabs; one archived log is incomplete |
| `Surfaces/1k (111) Ti/` | Ti-terminated (111) slabs |
| `Surfaces/1k (111) X/` | C/N-terminated (111) slabs |
| `Surfaces/100 Atomic Surface Analisis/` | Exported TiC/TiN layer coordinates and rippling analysis |
| `Tablitas de datos BulkCorrected.xlsx` | Final published results, as confirmed by the author; calculations and reference comparisons |

Composition directories A–E correspond to decreasing carbon fraction. Atom types
are **1 = Ti, 2 = C, 3 = N**. Existing directory/data names are retained to keep
LAMMPS file references intact. `corredor` means “runner”; these are historical
shell scripts with fixed MPI process counts.

## Quick start: analyze existing data

Requires Python 3 and the packages in `requirements.txt`; LAMMPS is needed only
to rerun simulations.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cd Temp_Stab
MPLBACKEND=Agg python analyze_stability.py
```

This writes `results.txt` and `lattice_parameter.png` in `Temp_Stab/`. The results
retain decimal commas and the historical columns
`x a err_a en_pot err_en_pot`. Energies are total potential energies in eV;
`err_*` values are sample standard deviations, not uncertainties of the mean.
The lattice parameter is in Å. Omit `MPLBACKEND=Agg` for an interactive plot.

The historical script name `analizador_mk3.py` is now `analyze_stability.py` in
all five locations. `Surface dd analyzer.py` is now `analyze_surface_layers.py`.
Comments, descriptive identifiers, plot titles, and messages are in English.
The original result files remain as reference data.

## Guides

- [Reproduction and analysis](docs/reproduction.md): working directories,
  commands, units, outputs, formulas, and known sampling limitations.
- [Archive audit](docs/archive-audit.md): differences from the article, missing
  research stages, and publication preparation.
- [Adapting the workflows](docs/other-materials.md): what must change for a new
  material, composition, or geometry.

No license has been selected for this archive yet. An explicit reuse license
and the provenance/redistribution terms of inherited potential and LAMMPS
example files should be settled before public release. Original attribution
in the elastic scripts has been retained.
