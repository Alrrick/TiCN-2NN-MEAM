# Run the code and understand the results

I use two kinds of programs here. Python reads saved data and makes plots.
LAMMPS runs new simulations of atoms. I recommend finishing the
[README example](../README.md) before starting a new simulation.

The instructions below run the files I have shared. Some are working versions
from the research, so their outputs can differ from my final workbook.
I list those differences in [the archive notes](archive-audit.md).

## Before you start

For Python, use the environment set up in the README. For new simulations,
install LAMMPS with **MEAM support**. MEAM is the interaction model used by the
potential files. Check your installation with:

```bash
lmp -h
```

I use `lmp` as the program name in this guide. Your installation may call it
`lmp_mpi` or something else; replace `lmp` in the commands if needed. My saved
logs include LAMMPS **23 Jun 2022 – Update 1**. I do not include an installer or
compiled program in this repository.

My original inputs contain `pair_style meam/c`. Newer LAMMPS versions document
`pair_style meam`. If your version rejects `meam/c`, change that line to
`pair_style meam` **in your working copy**. For elastic runs, the line is in
`potential.mod`. Record the version and compare the results after this change.
See the [LAMMPS MEAM guide](https://docs.lammps.org/pair_meam.html) for details.

I use this line to link the potential files to the atom types:

```text
pair_coeff * * library.meam Ti C N TiCN.meam Ti C N
```

Keep the element order. The first `Ti C N` gives the order of elements in the
potential settings. The last `Ti C N` maps atom types 1, 2, and 3 to those elements.

## Units I use

| Quantity | Unit | Meaning |
| --- | --- | --- |
| Distance | Å | Ångström; one ten-billionth of a metre |
| Energy | eV | Electronvolt; a unit suited to atomic energies |
| Time | ps | Picosecond; one trillionth of a second |
| Temperature | K | Kelvin, measured from absolute zero |
| Pressure | bar | A pressure unit; 1 bar is close to atmospheric pressure |
| Elastic stiffness | GPa | Gigapascal; one billion pascals |

These are LAMMPS `metal` units. The time step is 0.001 ps, or 1 femtosecond.
Each step advances the simulated clock by that amount; it does not describe
how long the computer takes to run it.

## Run a bulk TiC simulation

**Bulk** means a crystal without an exposed surface. The simulation repeats the
box in every direction to represent the interior of a larger crystal.

I run new cases in `runs/` so their output cannot replace the saved research
logs. Start in the repository root and copy these files:

```bash
mkdir -p runs/bulk-TiC
cp 'Temp_Stab/A-Ti(C1.0,N0.0)/temp_code.inp' runs/bulk-TiC/
cp 'Temp_Stab/A-Ti(C1.0,N0.0)/Ti(C1.0,N0.0)_v1.data' runs/bulk-TiC/
cp TiCN.meam library.meam runs/bulk-TiC/
cd runs/bulk-TiC
```

The `.data` file gives the starting atom positions. The `.inp` file gives the
instructions for the run. The two `.meam` files describe the atomic interactions.
Check the `pair_style` line as explained above, then run:

```bash
lmp -in temp_code.inp
```

This starts a full simulation. Its running time depends on your computer and
LAMMPS build. It writes `temp_v1.log` with the measured values and `TiCN.anim`
with atom positions over time. Running the same case again replaces its outputs.

The input starts with 4096 atoms in an 8 × 8 × 8 array of cubic cells. It first
adjusts the atom positions to lower the energy. This step is called
**minimization**. It then runs two stages of 50,000 steps each at 1 K and 0 bar.
Together, these stages cover 100 ps of simulated time.

I use **NPT** conditions: the number of atoms stays fixed while temperature and
pressure are controlled. The box can change size. The first stage also uses a
`drag` setting of 0.2 to damp fluctuations. The velocity seed is 733438 for this
case. A seed sets the starting point for a random-number calculation.

After the run, check the log for errors, completed stages, and the atom count.
My inputs contain `thermo_modify lost ignore`, so the program may keep running
if atoms are lost. Check the count yourself before accepting a result.

To use several CPU processes, you need an MPI-enabled LAMMPS build and MPI:

```bash
mpirun -np 4 lmp -in temp_code.inp
```

MPI lets the processes share the calculation. Start with one process if you
have not set it up. The old scripts named `corredor` also launch runs, but they
have fixed process counts. I recommend the explicit commands above while
learning. The root `corredor` launches surface and bulk cases, not elastic cases.

## Analyze bulk results

The README example reads all five saved bulk logs. My script calculates the
size of a cubic cell from each saved box volume:

```text
a = (V / 512) ** (1/3)
```

Here, `V` is the box volume. There are 512 cells because 8 × 8 × 8 = 512.
The cube root converts the volume of one cell into its side length.
The script then finds the average and standard deviation of those lengths.
It also plots the reference line `a(x) = 0.0857*x + 4.2417`.

**My script keeps the original sample selection.** A LAMMPS log contains
separate tables, called *thermo blocks*, for different stages. The bulk analyzer
joins the first two blocks, including minimization. It then uses Python's
`[150:-1]` slice: skip the first 150 rows and the last row.

This selection does not use the final 50 ps stage. The row numbers are not
times. I kept this behavior so the translated script gives the same results
as the original. For new research, choose a settled part of the run after
checking the temperature, pressure, and energy over time.

The script expects all five composition folders under its current folder.
To analyze new runs, create a separate analysis folder under `runs/`. With the local package installed as described in the README, copy
`analyze_stability.py` there, keep the same A–E folder names, and put each new
log in its matching folder as `temp_v1.log`. Then run the script from that
analysis folder. A single TiC run is not enough for its five-composition plot.

### Understand the energy values

`en_pot` is the total potential energy of all atoms. To find the energy needed
to form a compound from reference materials, I need another calculation:

```text
formation energy per atom =
    (E - N_Ti*e_Ti - N_C*e_C - N_N*e_N) / N_total
```

`E` is the compound's total energy. Each `N` is an atom count, and each lowercase
`e` is a reference energy per atom. My workbook uses references for bulk Ti,
diamond C, and nitrogen molecules. Their generating runs are not included.
Use the same potential and compatible conditions for all terms. Formation
**enthalpy** also needs a stated treatment of pressure, volume, and temperature.

## Measure elastic stiffness

Elastic stiffness describes how strongly a material resists small changes in
shape. I use LAMMPS scripts that slightly stretch or shear the crystal, relax
the atom positions, and measure the change in stress.

Start in the repository root:

```bash
mkdir -p runs/elastic-TiC
cp 'Elastic/A-Ti(C1.0,N0.0)/'*.elastic runs/elastic-TiC/
cp 'Elastic/A-Ti(C1.0,N0.0)/'*.mod runs/elastic-TiC/
cp 'Elastic/A-Ti(C1.0,N0.0)/'*.data runs/elastic-TiC/
cp TiCN.meam library.meam runs/elastic-TiC/
cd runs/elastic-TiC
```

Check the pair style in `potential.mod`, then run:

```bash
lmp -in in_v1.elastic
```

I split this workflow across several files:

| File | Its job |
| --- | --- |
| `in_v1.elastic` | Runs the calculation and prints the results |
| `init_v1.mod` | Selects the structure, units, and size of the deformation |
| `potential.mod` | Sets the atomic interaction model |
| `displace.mod` | Applies positive and negative deformations |
| The matching `_v1.data` file | Supplies the starting structure |

Look near the end of `Ti(C1.0,N0.0)_v1.log` for `Elastic Constant` and
`Bulk Modulus`. The constants describe different stretching and shear responses.
The bulk modulus measures resistance to a change in volume. For the cubic
averages used here, `B = (C11 + 2*C12)/3`.

I also include v2–v4 inputs. Run them one at a time, or in separate folders:
they share the file `restart.equil`. The old launcher runs only v1, and saved
logs for the other versions are not available for every case.

These calculations use minimized structures. They do not measure stiffness
at a chosen nonzero temperature. Before using a new result, vary the deformation
size and relaxation settings to check that the result is stable. The starting
strain is `up = 1e-6`; `cfac = 1e-4` converts bar to GPa.

I kept Aidan Thompson's credit in the scripts adapted from the LAMMPS example.
See the [LAMMPS elastic guide](https://docs.lammps.org/Howto_elastic.html).
For Table 6 in my paper, use `10^12 dyn/cm² = 100 GPa`: a table value of 2.59
means 259 GPa. The caption's conversion is inconsistent; the workbook divides
GPa values by 100.

## Run and analyze a surface case

I model a surface with a slab and a region of empty space, called **vacuum**.
The crystal has exposed faces next to that space.

Start in the repository root. This example uses the TiC (100) surface:

```bash
mkdir -p runs/surface-100-TiC
cp 'Surfaces/1k (100) Real/A-Ti(C1.0,N0.0)/temp_code.inp' runs/surface-100-TiC/
cp 'Surfaces/1k (100) Real/A-Ti(C1.0,N0.0)/Ti(C1.0,N0.0)_surf_v1.data' runs/surface-100-TiC/
cp TiCN.meam library.meam runs/surface-100-TiC/
cd runs/surface-100-TiC
```

Check the pair style, then run `lmp -in temp_code.inp`.
My main surface inputs minimize the structure, heat it from 1 to 50 K over
20 ps, cool it back to 1 K over 20 ps, and hold it at 1 K for 5 ps.
Pressure control acts along x and y, leaving the vacuum direction unchanged.

To inspect the saved (100) logs, start at the repository root and run:

```bash
cd 'Surfaces/1k (100) Real'
MPLBACKEND=Agg python analyze_stability.py
```

This writes `results.txt`, `lattice_parameter.png`, and `provenance.json` in that folder. My (100)
analyzer joins the first three thermo blocks; the other surface analyzers join
the first two. All use `[150:-1]`. These averages do not describe only the final
1 K stage.

The surface script inherits the bulk cell-size formula, but slab volume includes
empty space. Its reported `a` is therefore **not a physical lattice parameter**.
I keep it as an old analysis output. The compatibility script does not calculate surface energy. The new
`ticn-analyze surface-energy` command evaluates the formula below from explicit
energy, atom-count, and area inputs; it does not infer them from the logs.

The saved (110) log for `B-Ti(C0.75,N0.25)` stops during heating. Its analyzer
reports `incomplete thermo block 2`. Rerun that case in a working copy before
analyzing a full new set. Do not treat the partial log as a finished run.

### Calculate surface energy

Surface energy describes the energy cost of making a surface. I use this
convention in Eq. 6 of my paper:

```text
gamma = (E_slab - N_slab*e_bulk) / (2*A)
```

| Symbol | Meaning |
| --- | --- |
| `E_slab` | Total potential energy of the slab, in eV |
| `N_slab` | Number of atoms in the slab |
| `e_bulk` | Energy per atom of the matching bulk material, in eV |
| `A` | Area of one slab face, in Å² |
| `gamma` | Surface energy, in eV/Å² |

Multiply the result by **16.02176634** to convert it to J/m². Match the bulk and
slab composition, potential, temperature, and relaxation state.
For a rectangular xy face, the area is `Lx*Ly`. Use the actual face geometry
for tilted boxes. The logs give volume only; get the settled area from a
trajectory or add box lengths to the output of a new run.

The factor of two accounts for two faces. Check that the faces are equivalent
before reporting one surface's energy. If a slab has excess atoms of one element
or a polar surface, a broader treatment needs **chemical potentials**: reference
energy costs for adding or removing each species. State the convention you use.
My workbook's `Energias Superficiales` sheet contains the surface calculations;
the Python script does not rebuild that sheet automatically.

## Measure surface-layer rippling

Atoms near a surface can shift by different amounts. I call the height
difference between Ti and C/N atoms in the same layer **rippling**.

I recommend running this analysis in a copy because it adds text to its result
files each time. Start in the repository root with the Python environment active:

```bash
mkdir -p runs/layer-analysis
cp -r 'Surfaces/100 Atomic Surface Analisis/TiC' runs/layer-analysis/
cp -r 'Surfaces/100 Atomic Surface Analisis/TiN' runs/layer-analysis/
cp 'Surfaces/100 Atomic Surface Analisis/analyze_surface_layers.py' runs/layer-analysis/
cd runs/layer-analysis
python analyze_surface_layers.py
```

Read `TiCresult.txt` and `TiNresult.txt`. The script also prints distances between
layer centres. If you run it again in this folder, it adds another report to
each text file.

I provide four layers, z1–z4, for TiC and TiN. Each `.dat` file has two header
lines followed by atom type and z position in Å. The script reads file indices
400–450 inclusive. Files ending in 451 are present but are not read.
The original mapping from these indices to simulation times is not included.

Type 1 is Ti; all other types are grouped as X. The script averages positions
across the files and calculates `abs(mean(z_Ti) - mean(z_X))` for each layer.
To express a spacing change as a percentage, use
`100*(d - d_bulk)/d_bulk`, where `d_bulk` is the matching bulk spacing.
My workbook's `SupAnalys` sheet contains these comparisons.

I kept the original error formula, which depends on absolute z positions.
Moving the coordinate origin can change that error estimate, so do not treat
it as a reliable confidence interval. The optional `analyze_rippling` helper previously printed the Ti spread for
its X field; the shared implementation now reports the anion spread correctly. Other optional helpers need
`coor_*.txt`, `r*coord.txt`, or `r*data.txt` files that are not included.
The main command above uses the supplied `.dat` files instead.
