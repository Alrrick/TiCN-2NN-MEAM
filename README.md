# Learn to simulate titanium carbonitride

I share the code, potential files, and results from my research on titanium
carbonitride here. My goal is to help you run the analysis, explore how atoms
behave, and adapt the methods to your own research.

Titanium carbonitride contains titanium (Ti), carbon (C), and nitrogen (N).
I write its composition as **TiCₓN₁₋ₓ**. The number `x` tells you how much of the
carbon/nitrogen part is carbon. For example, `x = 1` gives TiC, `x = 0` gives
TiN, and `x = 0.5` gives equal amounts of carbon and nitrogen.

I use **LAMMPS** to simulate atoms and **Python** to read the results and draw
plots. The potential is the mathematical model that tells LAMMPS how the atoms
interact. My model uses **2NN MEAM**, short for *second nearest neighbor modified
embedded atom method*.

## Start here: make your first plot

I suggest starting with the saved data. You can make a plot without running a
new atom simulation or installing LAMMPS.

You need Git and Python 3, including Python's `venv` and `pip` tools. The commands
below use a **Bash terminal** on Linux, macOS, or Windows through WSL. A terminal
is a window where you type commands. Run each line in order in the same terminal.

### 1. Download the repository

```bash
git clone https://github.com/Alrrick/TiCN-2NN-MEAM.git
cd TiCN-2NN-MEAM
```

`git clone` downloads the files. `cd` changes the folder you are working in.
I call the folder containing this README the **repository root**.

### 2. Set up Python

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

I use a **virtual environment**, named `.venv`, to keep this project's Python
packages together. The last line installs NumPy for calculations, SciPy for
fitting curves, and Matplotlib for plots. You need internet access for this step.

### 3. Run the analysis

```bash
cd Temp_Stab
MPLBACKEND=Agg python analyze_stability.py
```

The script reads the saved logs for five compositions. It prints results and
creates two files in `Temp_Stab`:

| New file | What you get |
| --- | --- |
| `lattice_parameter.png` | A plot of crystal cell size against carbon content |
| `results.txt` | The values used in the analysis |

Open the PNG with an image viewer and the text file with a text editor.
`MPLBACKEND=Agg` saves the plot without opening a plot window. If your computer
supports plot windows, you can instead run `python analyze_stability.py`.
Running the script again replaces these two files.

### 4. Read the output

A crystal has a repeating pattern of atoms. The **lattice parameter**, `a`, is
the size of the repeating cubic cell. I measure it in ångströms (`Å`), where
1 Å = 0.0000000001 metres.

| Column in `results.txt` | Meaning |
| --- | --- |
| `x` | Carbon fraction, from 0 to 1 |
| `a` | Average lattice parameter in Å |
| `err_a` | Spread of the sampled lattice parameters |
| `en_pot` | Average total potential energy in electronvolts (eV) |
| `err_en_pot` | Spread of the sampled potential energies |

I kept the original number format: `4,33` means `4.33`. The `err_` columns are
**standard deviations**, which describe how much the samples vary. They do not
measure the accuracy of the whole model.

For the saved TiC bulk log, you should get `a` close to **4.3300 Å**. This is a
check that the saved-data analysis works. I explain its sampling limits in the
[run guide](docs/reproduction.md).

## Find my final results and potential files

My final published results are in **`Tablitas de datos BulkCorrected.xlsx`**.
You can open this workbook with Excel or LibreOffice Calc. I share the potential
in **`TiCN.meam` and `library.meam`**, both in the repository root. Use them
together. Copies inside the case folders keep the original inputs working.

I also include working inputs and logs from the research. Some differ from the
paper and final workbook. I have not verified a single command sequence that
recreates every published table. See [what the archive contains and what is
missing](docs/archive-audit.md) before comparing a new run with my final results.

## Choose your next step

| What you want to do | Where I explain it |
| --- | --- |
| Run a new LAMMPS simulation | [Run guide](docs/reproduction.md) |
| Study stiffness or surfaces | [Run guide](docs/reproduction.md) |
| Understand differences from the paper | [Archive notes](docs/archive-audit.md) |
| Work with another material | [Guide to other materials](docs/other-materials.md) |
| Check the Python analysis | [Validation guide](docs/validation.md) |

## Find your way around the files

| Folder or file | What I keep there |
| --- | --- |
| `Temp_Stab/` | Bulk crystal simulations and the first-plot example |
| `Elastic/` | Calculations of how the crystal responds to stretching and shear |
| `Surfaces/1k (100) Real/` | Slabs with a (100) surface |
| `Surfaces/1k (110)/` | Slabs with a (110) surface; one saved log is incomplete |
| `Surfaces/1k (111) Ti/` | (111) slabs with titanium on the outer surface |
| `Surfaces/1k (111) X/` | (111) slabs with carbon or nitrogen on the outer surface |
| `Surfaces/100 Atomic Surface Analisis/` | Positions of atoms in surface layers |

A **slab** is a thin piece of crystal with empty space around it. The numbers
(100), (110), and (111) describe different ways to cut a crystal surface.
In these files, `X` means carbon, nitrogen, or a mixture of both.

I label the five composition folders A–E: A has `x = 1`, B has `0.75`, C has
`0.5`, D has `0.25`, and E has `0`. Atom types are **1 = Ti, 2 = C, 3 = N**.
I kept the original folder names because the simulation inputs refer to them.

## If something goes wrong

| Message or problem | What to try |
| --- | --- |
| `python3: command not found` | Install Python 3, then open a new terminal. |
| `No module named venv` or an `ensurepip` error | Install your system's Python venv support, then repeat step 2. |
| `No module named numpy`, `scipy`, or `matplotlib` | Activate `.venv` and repeat the package-install command from the root. |
| `No such file or directory` | Check your current folder with `pwd`. Run the first analysis from `Temp_Stab`. |
| No plot window appears | With `MPLBACKEND=Agg`, open the saved PNG yourself. |
| `incomplete thermo block 2` in the (110) analysis | That saved case is unfinished. I explain how to handle it in the run guide. |

When you open a new terminal, return to the repository root and run
`source .venv/bin/activate` before using the Python scripts.

## Cite the research

If you use this work, please cite my paper with G. García, I. Arias-Camacho,
C. Espinoza, Byeong-Joo Lee, and E. Ramos-Moore:

A. Araya-Barr et al., **Second nearest neighbor modified embedded atom method
interatomic potentials for TiCₓN₁₋ₓ ternary systems**, *Computational Materials
Science* 231 (2024), 112615.
[Read the paper through its DOI](https://doi.org/10.1016/j.commatsci.2023.112615).

I exclude the publisher PDF, large atom trajectories, and compiled LAMMPS
programs from Git. I have not selected a reuse license yet. I keep the original
credits in files adapted from other work.
