# Validation of the English translation

Checked on 2026-11-05 with Python 3, NumPy 2.2.6, SciPy 1.15.3, and
Matplotlib 3.10.3. These versions describe the validation environment, not the
original research environment.

## Checks performed

Before editing, all six original scripts were saved outside the repository and
executed in temporary working directories containing copies or links to the
required archived inputs. After translation, the same procedure was repeated
with `MPLBACKEND=Agg`. Historical outputs in this repository were not overwritten.

| Script/workflow | Result |
| --- | --- |
| Bulk stability | Output text matches the original exactly, allowing the English output filename |
| (100) surface thermo analysis | Same numerical output as the original |
| (111) Ti surface thermo analysis | Same numerical output as the original |
| (111) X surface thermo analysis | Same numerical output as the original |
| TiC/TiN layer analysis | Same output values as the original, allowing translated field labels |
| (110) surface thermo analysis | Original crashes on the truncated x=0.75 log; translated script raises a descriptive incomplete-block error |

All original numerical constants were compared through Python syntax trees and
preserved. All Python files pass syntax parsing. Importing the bulk analysis
module does not run its entry point. A log without a thermo header raises an
error promptly instead of looping at end-of-file.

The reusable regression suite checks all five bulk compositions against the
archived `Resultados.txt`, the missing-header error, and the incomplete (110)
log. All three tests pass. Run it from the repository root after installing
`requirements.txt`:

```bash
MPLBACKEND=Agg python -m unittest discover -s tests -v
```

These checks establish preservation of the legacy postprocessing results.
They do not validate its sampling choices or establish agreement with the paper.
No LAMMPS executable was available on PATH, and no molecular dynamics or elastic
simulation was run. Optional layer-analysis helpers with missing input exports
were translated and syntax-checked but not exercised.

## Files and ignore rules

An inventory matched filenames against the new ignore patterns and confirmed
that `paper1.pdf`, bundled `lmp_mpi` binaries, `.anim` trajectories, and
`restart.equil` files are excluded. Approximately 17 MB of files remain eligible
for inclusion. Git was subsequently installed and the folder initialized as a new repository.
Git ignore and staged-file checks confirmed that the article PDF and generated
large files are excluded, while the workbook and root-level potential files
are included. No prior repository history was present in this folder.
