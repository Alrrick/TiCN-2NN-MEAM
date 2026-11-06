# Check that the analysis works

I include a small test suite so you can check the Python analysis after setting
up the repository or changing the code. A **test** runs a known case and compares
the result with an expected answer.

Start in the repository root with the Python environment from the README active:

```bash
MPLBACKEND=Agg python -m unittest discover -s tests -v
```

The suite checks archived behavior and independently known numerical examples.
Install the package first; subprocess tests exercise the installed CLI from a
temporary working directory.

| Checks | Evidence |
| --- | --- |
| Archive regression | All 24 readable bulk/surface composition cases match the pre-refactor outputs; the incomplete (110) case fails explicitly. |
| Layer regression | All eight TiC/TiN layers match the pre-refactor species statistics and explicit legacy width-error values. |
| Independent calculations | Hand-calculated lattice means, sample SDs, layer widths, and surface energies. |
| Scientific invariants | Moving the coordinate origin preserves new-mode rippling and species spreads. |
| Input validation | Whitespace and column order, truncated/empty blocks, malformed/nonfinite values, invalid species, geometry and sampling bounds. |
| CLI integration | Execution outside the repository, JSON provenance, output protection, plot generation, layers, and surface-energy units. |
| Bug regression | The optional rippling helper reports the anion SD in its anion field. |

`tests/legacy_reference.json` was captured from the working Python scripts before
the package refactor, using the supplied logs and coordinate exports. It is a
compatibility baseline, not an independent proof of physical correctness. Do not
regenerate it simply to make a failing test pass.

For developer installation and automated formatting, lint, and type checks, see
[the package guide](python-package.md). CI runs these checks and the tests on
Python 3.10 and 3.12. The local refactor verification used Python 3.10.

Passing these tests does not establish equilibration, validate the potential,
or reproduce every published table. Molecular dynamics was not rerun.

## How I checked the English translation

During preparation on 2026-11-05, I compared the original and translated scripts
in temporary folders. I used the same saved inputs for both versions and kept
the research output files unchanged.

| Analysis | Result of the comparison |
| --- | --- |
| Bulk crystal | Same numerical output |
| (100) surface logs | Same numerical output |
| (111) Ti surface logs | Same numerical output |
| (111) X surface logs | Same numerical output |
| TiC and TiN surface layers | Same numerical values, with English field labels |
| (110) surface logs | The original crashes on the incomplete case; the translated version explains which block is unfinished. |

I also checked that the original numerical constants were unchanged and that
Python could parse every script. Importing the bulk script does not start a run.
A missing data header now produces an error instead of an endless search.

I used NumPy 2.2.6, SciPy 1.15.3, and Matplotlib 3.10.3 for these checks with
Python 3. These are the versions used to check the translation. I do not have a
record of the exact Python package versions used in the original research.

## What I have not tested here

I did not rerun the molecular dynamics or elastic simulations during this check.
LAMMPS was not available on the command path in that environment. I also did not
run optional layer-analysis helpers that need missing input exports.

I kept the original averaging windows and formulas. Matching the old output
therefore confirms the translation, but it does not resolve those methods'
limits. I explain them in the [run guide](reproduction.md) and list differences
from the final results in the [archive notes](archive-audit.md).

## Check the files shared through Git

I verified that the public repository includes the workbook and both root-level
potential files. It excludes the article PDF, `.anim` trajectories, and compiled
LAMMPS programs. From the repository root, you can inspect the local rules with:

```bash
git check-ignore -v paper1.pdf
git ls-files '*.pdf' '*.PDF' '*.anim' '**/lmp_mpi'
```

The first command should show the PDF ignore rule, even if you do not have the
PDF locally. The second should print nothing. I use `.gitignore` to keep these
files out of new commits; it does not erase a file from existing Git history.
