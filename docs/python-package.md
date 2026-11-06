# Python analysis package

The shared package is in `src/ticn_analysis`. The original script locations are
small compatibility entry points. Simulation inputs, archived logs, and published
workbooks retain their original roles.

## Install

From the repository root, in an activated Python 3.10+ virtual environment:

```bash
python -m pip install -c requirements-lock.txt -e '.[dev]'
```

`pyproject.toml` declares supported dependency ranges. `requirements-lock.txt`
pins the runtime and development dependencies used for verification; it is a
constraints file, used with `-c`. It does not pin the operating system, Python
patch version, or build-isolation tools. Update it deliberately and rerun checks.
The package wheel contains code; simulation data stays in the research repository.

## Select new bulk analysis explicitly

```bash
ticn-analyze bulk 'Temp_Stab/A-Ti(C1.0,N0.0)/temp_v1.log' \
  --block 3 --cells 8 8 8 --geometry cubic-bulk \
  --start 150 --output runs/bulk-tic.json
```

Block numbers are one-based. `--start`, `--stop`, and `--stride` select zero-based
rows **within that block**, with an exclusive stop. Omitting stop includes the
last row. The example is a selection demonstration, not an equilibration claim.
The reader checks all blocks and rejects truncated logs rather than silently
accepting a partial run. It supports whitespace and thermo-column reordering;
unexpected messages inside a table fail with file/line context.

The lattice calculation is `(volume / number_of_cells) ** (1/3)` per sample,
followed by the mean and sample SD (`ddof=1`). `--geometry cubic-bulk` declares
that the caller has verified cubic bulk geometry. Volume alone cannot verify
that declaration. Slabs are rejected because their volume includes vacuum.
Energy is total potential energy in eV, not energy per atom or formation energy.
SDs describe sample spread, not uncertainty of the mean.

## Analyze layer exports

```bash
ticn-analyze layers 'Surfaces/100 Atomic Surface Analisis/TiC' \
  --start 400 --stop 451 --output runs/layers-tic.json
```

This pools z1–z4 exports 400–450. Use `--names z1 z2` to select layers or
`--stride` to change the file increment. Atom type 1 is Ti; 2 and 3 form the
anion group. Unknown types, nonfinite positions, and insufficient samples fail.
Coordinates must already use a consistent periodic image; no unwrapping is done.

The new output gives species means, sample SDs, counts, and the absolute difference
of means. It deliberately leaves `legacy_width_error_angstrom` null: pooled atoms
and frames do not establish the independent samples needed for a confidence
interval. Add `--legacy` only to recover the historical, origin-dependent formula.
Computing a defensible uncertainty requires a separately justified treatment of
spatial/temporal correlation and sampling, which this refactor does not infer.

## Calculate surface energy

This numerical example illustrates units and interface, not a research result:

```bash
ticn-analyze surface-energy --slab-energy -90 --atoms 10 \
  --bulk-energy-per-atom -10 --area 5 --equivalent-faces \
  --output runs/surface-energy-example.json
```

The result is `(E_slab - N*e_bulk)/(2*A)` in eV/Å² and J/m². Area is for one face.
The required flag asserts two equivalent faces. The caller must also establish
matching composition, potential, temperature/reference state, and a suitable
surface convention. Excess-species chemical-potential corrections are not implemented.

## Reproduce historical analysis

```bash
MPLBACKEND=Agg ticn-analyze legacy Temp_Stab --kind bulk --output runs/legacy-bulk
MPLBACKEND=Agg ticn-analyze legacy 'Surfaces/1k (100) Real' \
  --kind surface-100 --output runs/legacy-100
```

Use `surface-other` for the other slab folders. Legacy mode concatenates the first
two blocks (three for surface-100), applies `[150:-1]`, and uses 8×8×8 cells.
It preserves the historical decimal-comma `results.txt` and creates a plot plus
`provenance.json`. Surface plots now label the length as a legacy diagnostic that
includes vacuum. The numerical table retains the historical column names.

The old scripts remain runnable from their case directories. Stability wrappers
replace their three generated outputs, while the layer wrapper retains its
historical append behavior. These entry points print those behaviors explicitly.
The new CLI never appends and requires `--overwrite` to replace outputs.

Optional histogram helpers live in `legacy_helpers.py`, and the old layer script
re-exports them. Their input exports are absent from the archive, so their fitting
methods remain historical and unvalidated. The repeated optional rippling code
was consolidated and its anion-spread output corrected. This is an intentional
bug fix, not a promise of byte-identical output for that helper.

## Use the Python API

```python
from pathlib import Path
from ticn_analysis.io import read_thermo
from ticn_analysis.models import Sampling
from ticn_analysis.analysis import bulk_statistics

blocks = read_thermo(Path("Temp_Stab/A-Ti(C1.0,N0.0)/temp_v1.log"))
samples = Sampling(start=150).select(blocks[2])
result = bulk_statistics(samples, cells=(8, 8, 8), geometry="cubic-bulk")
print(result.lattice_mean_angstrom)
```

Core functions return frozen dataclasses and have no printing, plotting, or file
writing side effects. Parsing, calculations, file selection, reporting, and CLI
orchestration are separate modules. Legacy behavior is isolated in `legacy.py`
and compatibility helpers; case differences are parameters rather than copied
analysis implementations.

## Validate changes

```bash
ruff check .
ruff format --check .
mypy
MPLBACKEND=Agg python -m unittest discover -s tests -v
python -m pip wheel --no-deps --wheel-dir dist .
```

All package modules are checked with strict mypy; external plotting/SciPy modules
without usable stubs are allowed missing imports. Tests use temporary output
locations and do not rerun simulations or modify archived results. The CI workflow
runs the same checks on Python 3.10 and 3.12. Keep both archive regression tests
and independent numerical tests: matching historical output alone can preserve a
historical mistake.

JSON reports contain input SHA-256 hashes, paths, analysis settings, package and
Python versions, and NumPy/SciPy/Matplotlib versions. Surface-energy inputs are
provided as CLI values and recorded in settings rather than as source files.
