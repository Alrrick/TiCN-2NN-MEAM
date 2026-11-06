"""Command-line orchestration; all input/output paths are explicit."""

import argparse
import sys
from dataclasses import asdict
from pathlib import Path

from .analysis import bulk_statistics, surface_energy
from .io import read_thermo
from .layers import analyze_layer, layer_paths
from .legacy import run_stability
from .models import Sampling
from .reporting import provenance, write_json


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    commands = root.add_subparsers(dest="command", required=True)
    bulk = commands.add_parser(
        "bulk", help="analyze an explicitly selected cubic-bulk thermo block"
    )
    bulk.add_argument("input", type=Path)
    bulk.add_argument("--block", type=int, required=True, help="one-based thermo block number")
    bulk.add_argument("--cells", type=int, nargs=3, required=True, metavar=("NX", "NY", "NZ"))
    bulk.add_argument("--geometry", choices=("cubic-bulk", "slab"), required=True)
    bulk.add_argument(
        "--start", type=int, default=0, help="first row index within the selected block"
    )
    bulk.add_argument("--stop", type=int, help="exclusive row index (default: all remaining rows)")
    bulk.add_argument("--stride", type=int, default=1)
    layers = commands.add_parser(
        "layers", help="pooled species means and spreads from layer exports"
    )
    layers.add_argument("input", type=Path, help="material directory containing z1, z2, ...")
    layers.add_argument("--names", nargs="+", default=["z1", "z2", "z3", "z4"])
    layers.add_argument("--start", type=int, required=True, help="first export file index")
    layers.add_argument("--stop", type=int, required=True, help="exclusive export file index")
    layers.add_argument("--stride", type=int, default=1)
    layers.add_argument(
        "--legacy", action="store_true", help="also report the historical width error"
    )
    legacy = commands.add_parser(
        "legacy", help="reproduce archived five-composition tables and plots"
    )
    legacy.add_argument("input", type=Path)
    legacy.add_argument("--kind", choices=("bulk", "surface-100", "surface-other"), required=True)
    energy = commands.add_parser(
        "surface-energy", help="two equivalent faces, composition-matched bulk"
    )
    energy.add_argument("--slab-energy", type=float, required=True, help="eV")
    energy.add_argument("--atoms", type=int, required=True)
    energy.add_argument("--bulk-energy-per-atom", type=float, required=True, help="eV/atom")
    energy.add_argument("--area", type=float, required=True, help="one face's area in Å²")
    energy.add_argument("--equivalent-faces", action="store_true", required=True)
    for command in (bulk, layers, legacy, energy):
        command.add_argument(
            "--output", type=Path, required=True, help="output JSON file (legacy: output directory)"
        )
        command.add_argument("--overwrite", action="store_true")
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        settings = {
            key: str(value) if isinstance(value, Path) else value
            for key, value in vars(args).items()
        }
        if args.command == "legacy":
            run_stability(args.input, args.output, kind=args.kind, overwrite=args.overwrite)
        else:
            paths: list[Path] = []
            if args.command == "bulk":
                blocks = read_thermo(args.input)
                if not 1 <= args.block <= len(blocks):
                    raise ValueError(f"block must be between 1 and {len(blocks)}")
                selected = Sampling(args.start, args.stop, args.stride).select(
                    blocks[args.block - 1]
                )
                result = asdict(
                    bulk_statistics(selected, cells=tuple(args.cells), geometry=args.geometry)
                )
                paths = [args.input]
            elif args.command == "layers":
                if len(set(args.names)) != len(args.names):
                    raise ValueError("layer names must be unique")
                result = {}
                for name in args.names:
                    selected_paths = layer_paths(
                        args.input, name, args.start, args.stop, args.stride
                    )
                    result[name] = asdict(analyze_layer(selected_paths, legacy=args.legacy))
                    paths.extend(selected_paths)
            else:
                value = surface_energy(
                    slab_energy_ev=args.slab_energy,
                    atom_count=args.atoms,
                    bulk_energy_per_atom_ev=args.bulk_energy_per_atom,
                    face_area_angstrom2=args.area,
                    equivalent_faces=args.equivalent_faces,
                )
                result = {
                    "surface_energy_ev_per_angstrom2": value,
                    "surface_energy_j_per_m2": value * 16.02176634,
                }
            if args.output.resolve() in {path.resolve() for path in paths}:
                raise ValueError("output must not replace an input file")
            payload = {"provenance": provenance(paths, settings), "results": result}
            write_json(args.output, payload, overwrite=args.overwrite)
        print(f"Wrote {args.output}")
    except (OSError, ValueError) as exc:
        print(f"ticn-analyze: {exc}", file=sys.stderr)
        return 2
    return 0
