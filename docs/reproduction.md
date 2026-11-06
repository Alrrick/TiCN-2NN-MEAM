# Reproduction and analysis guide

## Scope and software

These instructions reproduce the **archived workflow**, whose differences from
the article are listed in [the audit](archive-audit.md). They do not claim that
running the current inputs will regenerate all published tables.

Use Python 3, NumPy, Matplotlib, and SciPy (`requirements.txt`). Exact historical
Python dependency versions are unavailable. For simulations, use LAMMPS with
MEAM support, and MPI if running in parallel. Archived `log.lammps` files include
LAMMPS **23 Jun 2022 – Update 1**. Bundled `lmp_mpi` binaries are ignored by Git;
install a build appropriate for your machine.

The historical inputs use `pair_style meam/c`. Current LAMMPS documents
`pair_style meam`; check your executable's `-h` output. If `meam/c` is unsupported,
change it to `meam` in a **copy** of the input or `potential.mod`, record the
LAMMPS version, and compare results before assuming equivalence. The order in
`pair_coeff * * library.meam Ti C N TiCN.meam Ti C N` matters: it associates
potential indices and atom types with Ti, C, N. See the official
[MEAM documentation](https://docs.lammps.org/pair_meam.html).

LAMMPS `metal` units here mean Å, eV, ps, K, and bar. The MD timestep is 0.001 ps
(1 fs). The charge-style data records contain `id type q x y z`; their presence
does not imply a charge-equilibration model.

## Preserve reference data when rerunning

Run LAMMPS **inside a case directory**, where relative `read_data`, `include`,
and potential paths resolve. Logs and dumps are overwritten by LAMMPS. From the
repository root, make a small working copy instead of copying archived binaries
and trajectories:

```bash
mkdir -p runs/bulk-TiC
cp 'Temp_Stab/A-Ti(C1.0,N0.0)/temp_code.inp' runs/bulk-TiC/
cp 'Temp_Stab/A-Ti(C1.0,N0.0)/Ti(C1.0,N0.0)_v1.data' runs/bulk-TiC/
cp 'Temp_Stab/A-Ti(C1.0,N0.0)/library.meam' runs/bulk-TiC/
cp 'Temp_Stab/A-Ti(C1.0,N0.0)/TiCN.meam' runs/bulk-TiC/
cd runs/bulk-TiC
# Adjust pair_style in this copy if required by your installation.
lmp -in temp_code.inp
# Alternatively, with an MPI-enabled executable:
# mpirun -np 4 lmp -in temp_code.inp
```

Replace `lmp` with your installed executable. These are full simulations, not
short tests. Check the final log for completed stages, atom conservation,
minimization convergence, and any warnings. Inputs currently use
`thermo_modify lost ignore`; completion alone does not establish atom
conservation. Preserve the run's inputs, version, and settings with its outputs.
The top-level `corredor` runs surfaces and bulk, **not Elastic**; case runners
use hard-coded process counts and assume `lmp_mpi` is on PATH.

## Bulk stability and lattice parameter

Each `Temp_Stab/A…E` directory contains a 4096-atom, 8 × 8 × 8 conventional-cell
B1 structure. The inputs minimize the initial structure and run two 50,000-step
NPT stages at **1 K and 0 bar**, the first with drag 0.2. Outputs include
`temp_v1.log` (thermodynamics) and `TiCN.anim` (atom trajectory, excluded from Git).
The seed expression evaluates to 733438 for i = 1.

From `Temp_Stab`, run `python analyze_stability.py`. It reads all five
`temp_v1.log` files. For each sampled volume V, it calculates
`a = (V / 512) ** (1/3)`, then reports the sample mean and standard deviation.
The plotted reference is `a(x) = 0.0857*x + 4.2417`; a linear fit to the simulated
values is calculated but not reported.

**Retained historical sampling:** `data_reader(curve_number=3)` concatenates
the first **two** thermo blocks, including the minimization block. It then uses
rows `[150:-1]` of the concatenated data. It does not analyze the final 50 ps
production stage. The row number is not an absolute timestep or a time in ps.
This is preserved to make the English translation numerically comparable.
For a new scientific analysis, explicitly choose the equilibrated production
block, inspect its stationarity, and use block averaging or independent runs
when estimating uncertainty. Changing that selection changes the results.

The energy column is not formation enthalpy. To calculate an energy of formation
per atom, use `(E - N_Ti*e_Ti - N_C*e_C - N_N*e_N)/N_total`, with compatible
reference phases and the same potential. The workbook contains reference values
for bulk Ti, diamond C, and diatomic N, but their generating calculations are
not included. Include pressure/volume and thermal conventions if calling the
quantity an enthalpy.

## Static elastic properties

For each `Elastic/A…E` composition, the input set is:

- `in_v1.elastic` through `in_v4.elastic`: orchestration and output.
- `init_v1.mod` through `init_v4.mod`: structure, strain, units, and tolerances.
- `potential.mod`: interaction and neighbor/minimization settings.
- `displace.mod`: positive/negative strain perturbations.
- Corresponding `_v1.data` through `_v4.data` structures.

Copy the `.elastic`, `.mod`, `.data`, and `.meam` files for one case to a fresh
`runs/` subdirectory and run `lmp -in in_v1.elastic` there. Other versions can be
run sequentially with their matching inputs; they share `restart.equil`, so
concurrent versions need separate working directories. The existing case
runner runs only v1. Availability of v2–v4 logs varies by composition.

The routines relax the cell, displace atoms slightly, apply strain in six Voigt
directions, relax atomic coordinates, and calculate stress derivatives. Default
strain is `up = 1e-6`; pressure-to-GPa conversion is `cfac = 1e-4`. Inspect the
reported tensor components and averages near the end of each composition log.
The cubic bulk modulus is `(C11 + 2*C12)/3`, using the script's cubic averages.
Do not infer finite-temperature elastic constants from this static calculation.
The original LAMMPS example credits Aidan Thompson; see
[the official elastic-constant guide](https://docs.lammps.org/Howto_elastic.html).

Converge strain magnitude, minimization tolerances, and cell size before using
new results. Table 6's caption has an inconsistent unit conversion:
`10^12 dyn/cm² = 100 GPa`; a tabulated value 2.59 means 259 GPa. The workbook
explicitly divides GPa values by 100.

## Slab simulations and surface energy

The four `Surfaces/1k …` directories each contain A–E compositions. `X` denotes
the C/N sublattice termination. The current main-case inputs minimize the slab,
heat 1→50 K for 20 ps, cool 50→1 K for 20 ps, and run at 1 K for 5 ps. They use
periodic boundaries with vacuum in the structure and pressure control in x/y
only. Inspect the actual input and geometry rather than interpreting the folder
name as a complete temperature protocol. Copy each case's input, referenced
`.data`, and both `.meam` files to a separate run directory, then execute
`lmp -in temp_code.inp` as for bulk.

Run `python analyze_stability.py` from the orientation directory to analyze its
five logs. The (100) script concatenates the first **three** thermo blocks;
the other surface scripts concatenate the first **two**. All retain `[150:-1]`.
Thus these outputs are not averages over the final 1 K stage. The (110), x=0.75
log is truncated and the analyzer will raise a descriptive error; rerun that
case before analyzing the complete set. It must not silently produce a result
from the partial heating stage.

The inherited `a = (V/512)^(1/3)` calculation is **not a physical slab lattice
parameter**, because V includes vacuum and slab cell geometries differ. The
surface `results.txt` and lattice plots are retained legacy diagnostics. The
scripts do **not** calculate surface energies automatically.

For the paper's slab convention (Eq. 6), calculate
`gamma = (E_slab - N_slab*e_bulk)/(2*A)` with energies in eV and one-face area A
in Å². Multiply eV/Å² by **16.02176634** for J/m². Use a bulk energy **per atom**,
the slab atom count, and the corresponding surface area (e.g. Lx*Ly for a
rectangular xy surface). Use actual box vectors for other orientations or
triclinic cells. Match potential, composition, temperature, and relaxation state;
do not substitute total bulk energy for e_bulk. Report how area changes under
in-plane relaxation. Obtain equilibrated area from the trajectory or add box
lengths to thermo output in a new run; these logs report volume only.

For nonstoichiometric polar terminations, a bulk-only reference is a convention;
a general surface thermodynamic calculation needs species chemical potentials.
Check whether the two slab faces are equivalent before interpreting the factor
of two as a single-face surface energy. The workbook's `Energias Superficiales`
sheet contains historical energy/area calculations; some values differ from
current logs, so it is not a verified automated bridge to Table 7.

## (100) layer relaxation and rippling

Run from `Surfaces/100 Atomic Surface Analisis/`:

```bash
python analyze_surface_layers.py
```

This appends to `TiCresult.txt` and `TiNresult.txt`. To preserve those historical
files, copy the two material directories and the script to a new directory
under `runs/` and run there. Repeated execution appends repeated reports.

The active path reads `TiC/z1/z1_400.dat` etc. for layers z1–z4 and TiC/TiN.
Each export has two header lines, then `atom_type z_position` pairs (Å). It uses
indices **400 through 450 inclusive**; index 451 is present but excluded by the
end-exclusive range. The original export procedure and index-to-timestep mapping
are not provided. Type 1 is Ti; all other types are pooled as X. The script
pools positions across files, reports species means/standard deviations,
`r = abs(mean(z_Ti)-mean(z_X))`, and differences between layer midpoints.

The historical width-error expression is preserved. It depends on absolute z
coordinates and is not a translation-invariant uncertainty estimate. The unused
`analyze_rippling` helper also reports Ti standard deviation for its X output;
this historical issue is retained rather than changing a scientific result
within a language translation. Optional Gaussian/histogram helpers require
`coor_*.txt`, `r*coord.txt`, or `r*data.txt` files that are absent.

To reproduce interlayer percentages, calculate the relevant species-to-species
separation and compare it with the bulk nearest-neighbor spacing:
`100*(d - d_bulk)/d_bulk`. Preserve the surface-normal orientation and layer
ordering. The workbook's `SupAnalys` sheet contains these combinations; the
script does not export the complete published Table 8 automatically.
