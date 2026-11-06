"""Compatibility entry point; historical reports append to material result files.

Use ticn-analyze layers for explicit paths and structured, non-appending output.
"""

import sys
from pathlib import Path

for parent in Path(__file__).resolve().parents:
    if (parent / "src" / "ticn_analysis").is_dir():
        sys.path.insert(0, str(parent / "src"))
        break

from ticn_analysis.layers import analyze_all_layers, read_layer_info  # noqa: E402, F401
from ticn_analysis.legacy_helpers import (  # noqa: E402, F401
    analyze_rippling,
    analyze_rippling_coordinates,
    gauss,
    layer_analysis_basic,
    read_two_columns,
    surface_analysis,
)

if __name__ == "__main__":
    print("Legacy analysis: historical width-error formula; reports append to existing files.")
    analyze_all_layers("TiC", 400, 451, 1)
    analyze_all_layers("TiN", 400, 451, 1)
