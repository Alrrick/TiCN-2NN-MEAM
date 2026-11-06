# Check that the analysis works

I include a small test suite so you can check the Python analysis after setting
up the repository or changing the code. A **test** runs a known case and compares
the result with an expected answer.

Start in the repository root with the Python environment from the README active:

```bash
MPLBACKEND=Agg python -m unittest discover -s tests -v
```

You should see three tests finish with `ok`, followed by `OK`.
The test command reads saved data; it does not launch a LAMMPS simulation.

## What the three tests check

| Test | What it checks |
| --- | --- |
| Bulk statistics | All five bulk compositions match the saved `Resultados.txt` values. |
| Missing log header | A file without the expected data table gives a clear error. |
| Unfinished surface log | The incomplete (110) case gives an error instead of a misleading result. |

Passing these tests shows that these behaviors work. It does not prove that the
potential predicts every physical property correctly or that all paper tables
can be rebuilt from the saved logs.

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
