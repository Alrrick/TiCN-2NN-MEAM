"""Output and provenance helpers; scientific calculations live elsewhere."""

import hashlib
import json
import platform
from importlib.metadata import version
from pathlib import Path
from typing import Any

from . import __version__


def provenance(paths: list[Path], settings: dict[str, Any]) -> dict[str, Any]:
    """Record exact input content, settings, and runtime dependency versions."""
    return {
        "analysis_version": __version__,
        "python": platform.python_version(),
        "dependencies": {name: version(name) for name in ("numpy", "matplotlib", "scipy")},
        "settings": settings,
        "inputs": [
            {"path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in paths
        ],
    }


def write_json(path: Path, payload: dict[str, Any], *, overwrite: bool = False) -> None:
    """Write one complete JSON document; exclusive creation is the default."""
    text = json.dumps(payload, indent=2, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if overwrite else "x", encoding="utf-8") as stream:
        stream.write(text)


def plot_lattice(
    compositions: list[float],
    values: list[float],
    spreads: list[float],
    destination: Path,
    *,
    legacy_surface: bool = False,
    show: bool = False,
) -> None:
    """Render sample SD bars without changing global plotting configuration."""
    import matplotlib.pyplot as plt

    with plt.rc_context({"font.size": 12}):
        fig, ax = plt.subplots()
        ax.errorbar(compositions, values, yerr=spreads, fmt="o", label="Simulated (sample SD)")
        ax.plot(compositions, [0.0857 * x + 4.2417 for x in compositions], label="Reference")
        ax.set_xlabel("Carbon fraction x")
        ax.set_ylabel(
            "Legacy volume-derived length (Å)" if legacy_surface else "Lattice parameter (Å)"
        )
        ax.set_title(
            "Legacy slab diagnostic; includes vacuum" if legacy_surface else "Lattice parameter"
        )
        ax.spines[["right", "top"]].set_visible(False)
        ax.legend()
        try:
            fig.savefig(destination, bbox_inches="tight")
            if show:
                plt.show()
        finally:
            plt.close(fig)
