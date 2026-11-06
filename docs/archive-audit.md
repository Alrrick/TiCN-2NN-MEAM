# Archive audit and publication status

Inspection date: 2026-11-05. Source evidence: local article PDF, Python scripts,
LAMMPS inputs, thermodynamic logs, potential files, structure headers, exported
layer coordinates, and workbook cell values/formulas. Trajectories were
inventoried but not exhaustively analyzed. No simulation was rerun during this
preparation.

## Author-confirmed sources

The author confirms that `Tablitas de datos BulkCorrected.xlsx` contains the
final published results and designates `TiCN.meam` and `library.meam` as the
potential files to share. Both are now available at the repository root and
match the 31 original copies byte for byte. The observations below concern
the archived inputs/logs and their relation to the article; they do not replace
the workbook as the author-designated final-results source.

## Reference and research history

The author confirmed that the local article is the reference:
[10.1016/j.commatsci.2023.112615](https://doi.org/10.1016/j.commatsci.2023.112615).
The initially supplied Results in Engineering DOI is not used for this archive.

The article develops a C–N interaction using DFT reference structures, combines
it with Ti–C/Ti–N and ternary screening parameters, and evaluates bulk and surface
properties. This folder contains the downstream LAMMPS evaluation workflows and
some postprocessing. Its workbook, alternative structures, and differences from
the published tables suggest a working research snapshot; the precise revision
history cannot be recovered from the files alone.

## Differences that prevent claiming exact paper reproduction

| Item | Local evidence | Article / implication |
| --- | --- | --- |
| Bulk temperature | All five `Temp_Stab` inputs set 1 K | Section 4.2 describes 300 K |
| Pressure | Bulk uses `iso 0 0`; surfaces use x/y targets 0 bar | Article describes 1 bar |
| Surface preparation | Main cases contain 20 ps heating + 20 ps cooling + 5 ps hold | Section 4.3 also describes a preceding 100 ps stabilization; its full chain is not represented in these inputs |
| Ti–C parameters | `re(1,2)=2.165`, `alpha(1,2)=4.47129` | Table 2: 2.161 and 4.61286 |
| Ti–N parameters | `re(1,3)=2.121`, `alpha(1,3)=4.889` | Table 2: 2.1169 and 4.87483 |
| TiC elastic bulk modulus | `Elastic/A…/_v1.log`: 241.995013904074 GPa | Table 6: 259 GPa |
| TiC bulk lattice parameter | Archived `Temp_Stab/Resultados.txt`: 4.3300121285 Å | Table 5: 4.326 Å |
| (110), x=0.75 | `B-Ti(C0.75,N0.25)/temp_v1.log` ends at step 300 without a Loop terminator for heating | Incomplete simulation; no final production statistics can be obtained from it |
| Python sampling | Early concatenated thermo blocks, then `[150:-1]` | Does not isolate final equilibrium production data |
| Slab lattice output | Uses vacuum-containing volume divided by 512 | Not a physical slab lattice parameter |
| Workbook provenance | Some bulk/surface values differ from current logs | Manual intermediate calculations need reconciliation |

All 31 copies of `TiCN.meam` are byte-identical at inspection, as are all 31
copies of `library.meam`. Therefore, the published parameter revision is not
hidden in another case directory. The existing files were not changed to match
the table: individual edits would not establish the full intended potential.
The author has designated the existing potential files for sharing. Rerun
comparisons and reconcile the parameter/table differences before claiming
that every final workbook value is reproduced by the archived input sets. The article's cohesive-energy
expressions and unit labels also require careful sign/unit interpretation;
do not transcribe them mechanically over the working files.

The `(100)` directory also includes `A-Ti(C1.0,N0.0) Bad`. Its name suggests an
alternative/rejected case, but the reason is not recorded. It is preserved as
provenance and is not selected by the composition analyzer.

## What is missing for full reconstruction

- VASP inputs/outputs and energy–volume fitting for the hypothetical C–N
  reference structures (article Sections 2–3).
- A parameter optimization driver and its objective data/history.
- A verified mapping from the shared potential and archived run settings to all
  final workbook results.
- Generating scripts and substitution seeds for the existing structures.
- Complete reference-phase calculations for formation enthalpy and the C–N
  dimer/diamond-defect validation in Table 4.
- The complete surface preparation/export chain and a documented mapping of
  layer-file indices to simulation steps.
- Automated table/figure generation from raw calculations, including the
  spreadsheet's manual reference choices.

The saved structures allow reruns without their original generators. Existing
logs and layer exports allow postprocessing without LAMMPS. These are useful
starting points, but do not cover all of the paper's research stages.

## English translation and behavior

All six Python files were renamed to English and their Spanish comments,
descriptive names, messages, and plot titles translated. Existing directory,
structure, workbook, and historical output names remain intact. The five thermo
analyzers now write `results.txt` / `lattice_parameter.png`; the layer analyzer
still appends `TiCresult.txt` / `TiNresult.txt` with English field labels.

Numerical expressions, sample windows, reference values, and defaults were
preserved. Entry-point guards prevent analysis on import. A verbose (100)
row-by-row debug print was removed. Missing/incomplete thermo blocks now raise
`ValueError` rather than hanging at EOF or failing with an unexplained index
error. These small execution changes do not change complete-log statistics.
See [validation](validation.md) for the checks performed.

## Git preparation

The initial folder occupied approximately 7 GB. Most space was in `.anim`
trajectories (~4.54 GB) and repeated `lmp_mpi` binaries (~2.91 GB). `.gitignore`
now excludes those files, all PDF extensions (including uppercase), generated
`restart.equil`, Python environments/caches, new thermo-analysis outputs, and
`runs/`. Local files were not deleted. Logs, `.data` structures, `.meam`
parameters, layer `.dat` exports, the workbook, and historical summary/plot
outputs remain eligible for inclusion; they are evidence needed for reuse.

The folder was initialized as a new Git repository on branch `main` after Git
was installed. Git ignore and staged-file checks exclude PDFs, executables,
trajectories, restart files, and Python caches. The workbook and both root-level
potential files are included. Publication uses the author-designated files;
no potential parameters or workbook values were changed.

No reuse license has been selected. Original third-party attribution is
retained. The missing research stages and numerical discrepancies above remain
documented limitations of reproducing the full published workflow.
