# What I share, and what is still missing

I share this archive so you can learn from my research and run the saved
workflows. My final published results are in
**`Tablitas de datos BulkCorrected.xlsx`**. The potential files I share are
**`TiCN.meam` and `library.meam`** in the repository root.

I also keep earlier inputs, logs, and calculations. A **log** is the text record
of a program's run. Some logs and settings differ from the final results.
This page explains those differences so you can choose the right files and
understand what a new run can reproduce.

My reference paper is
[Araya-Barr et al., Computational Materials Science 231 (2024), 112615](https://doi.org/10.1016/j.commatsci.2023.112615).

## How the files fit into the research

In the paper, I develop the interaction model with my coauthors, then test bulk
crystals and surfaces. Part of that work uses **density functional theory
(DFT)**, a method for calculating material properties from their electrons.
Those calculations help set the parameters of the faster atom-based model.

This repository contains the later LAMMPS calculations and some of the analysis.
It does not contain every stage of model fitting. I keep the saved structures
so you can run them without the original structure-building programs.

## Differences to keep in mind

I checked the article, inputs, logs, potential files, structure headers, layer
data, and workbook during repository preparation on 2026-11-05. I did not rerun
the LAMMPS simulations or examine every frame of the large atom trajectories.

| What I checked | What is in the archive | What to keep in mind |
| --- | --- | --- |
| Bulk temperature | All five `Temp_Stab` inputs use 1 K | Paper Section 4.2 describes 300 K. |
| Pressure | Bulk and surface inputs target 0 bar | The paper describes 1 bar. |
| Surface run stages | 20 ps heating, 20 ps cooling, 5 ps hold | Section 4.3 also describes an earlier 100 ps stage. That full sequence is not in these inputs. |
| Ti–C potential settings | `re(1,2)=2.165`; `alpha(1,2)=4.47129` | Table 2 lists 2.161 and 4.61286. |
| Ti–N potential settings | `re(1,3)=2.121`; `alpha(1,3)=4.889` | Table 2 lists 2.1169 and 4.87483. |
| TiC bulk modulus | The saved elastic v1 log gives about 242 GPa | Table 6 gives 259 GPa. |
| TiC lattice parameter | `Temp_Stab/Resultados.txt` gives about 4.3300 Å | Table 5 gives 4.326 Å. |
| (110) case with `x=0.75` | The log ends at step 300 during heating | It is incomplete and cannot give a final average. |
| Python sample selection | The scripts use early parts of the logs | They do not select only the final settled stage. |
| Surface `a` output | The calculation includes empty space in the box | This value is not the crystal's physical lattice parameter. |
| Workbook and logs | Some values differ | The workbook is my final-results source; the saved logs do not rebuild all its values. |

In the parameter files, `re` sets a reference distance and `alpha` helps set the
shape of the energy curve. I leave their values unchanged in this release.
All 31 original copies of each potential file match, and the root copies match
them too. I do not have a different parameter set hidden in another case folder.

Before claiming that a new run recreates every final result, I need to resolve
these differences and check the calculation from input to workbook. Changing
only a few numbers to match a printed table would not establish that link.
The paper's energy signs and unit labels also need care when comparing values.

I keep `A-Ti(C1.0,N0.0) Bad` in the (100) folder as part of the working archive.
Its rejection reason is not recorded. The analysis script does not select it.

## Steps I cannot yet rebuild from this archive alone

| Missing part | Why it matters |
| --- | --- |
| VASP inputs, outputs, and energy–volume fits | These support the DFT work used to build the C–N model. |
| The fitting program and its full history | These show how the potential parameters were selected. |
| A checked path from every input to the final workbook | This is needed to reproduce all final values automatically. |
| Structure-building scripts and substitution seeds | These would recreate the starting atom arrangements from scratch. |
| Complete reference-material and defect calculations | These support formation energies and the checks in Table 4. |
| The full surface preparation and layer-export process | These would show how each saved layer file relates to the simulation. |
| Scripts that rebuild every final table and figure | Some analysis choices still live in the workbook. |

A **seed** is a number used to repeat a random calculation. The supplied atom
structures can still be used directly even though their building scripts and
seeds are missing.

## Changes I made for sharing

I translated all six Python analysis scripts into English. The old
`analizador_mk3.py` files are now `analyze_stability.py`.
`Surface dd analyzer.py` is now `analyze_surface_layers.py`.
I kept the original directory and data names so file references still work.

The thermo analyzers now write `results.txt` and `lattice_parameter.png`.
The layer analyzer still adds reports to `TiCresult.txt` and `TiNresult.txt`,
with English labels. I kept numerical formulas, sample ranges, and defaults.

I also made the scripts safe to import without starting an analysis and added
clear errors for missing or unfinished log sections. I removed a (100) debug
print that displayed every data row. The checks in my
[validation guide](validation.md) show that complete inputs give the same
numerical results as before translation.

## Files I leave out of Git

My original working folder was about 7 GB. Most of that space held atom
trajectories and repeated copies of a compiled LAMMPS program. I keep about
17 MB of code, structures, logs, layer data, and results in the public repository.

My `.gitignore` excludes PDFs, `lmp_mpi` programs, `.anim` trajectories,
`restart.equil`, Python environments and caches, new thermo-analysis outputs,
and the `runs/` folder. This keeps new experiments separate from the saved
research files. The ignored files can still exist on your computer.

I checked the public repository to confirm that the workbook and both potential
files are included, and that PDFs, trajectories, and compiled programs are not.
I have not selected a reuse license. I keep the existing credits for work adapted
from other sources.
