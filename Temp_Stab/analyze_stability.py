"""Compatibility entry point: reproduce archived results in the working directory.

For explicit inputs, sampling, and output control, use ticn-analyze.
"""

import sys
from pathlib import Path

# Support a source checkout without duplicating analysis implementation.
for parent in Path(__file__).resolve().parents:
    if (parent / "src" / "ticn_analysis").is_dir():
        sys.path.insert(0, str(parent / "src"))
        break

from ticn_analysis.legacy import analyze_folder as _analyze_folder  # noqa: E402
from ticn_analysis.legacy import data_reader as _data_reader  # noqa: E402
from ticn_analysis.legacy import run_stability  # noqa: E402


def data_reader(archive_name, curve_number=3):
    return _data_reader(archive_name, curve_number)


def analyze_folder(folder_name, archive_name):
    return _analyze_folder(folder_name, archive_name, block_count=2)


def analyze_stability():
    print("Legacy analysis: historical sampling and formulas; existing outputs are replaced.")
    run_stability(Path.cwd(), Path.cwd(), kind="bulk", overwrite=True, show=True)


if __name__ == "__main__":
    analyze_stability()
