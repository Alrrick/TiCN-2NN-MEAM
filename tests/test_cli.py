"""Exercise the installed CLI in an unrelated working directory."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def run_cli(self, directory, *arguments):
        return subprocess.run(
            [sys.executable, "-m", "ticn_analysis", *map(str, arguments)],
            cwd=directory,
            text=True,
            capture_output=True,
            env=os.environ | {"MPLBACKEND": "Agg"},
            check=False,
        )

    def test_bulk_provenance_and_explicit_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.log"
            source.write_text("Step Volume PotEng\n0 8 -10\n1 64 -14\nLoop time done\n")
            output = Path(directory) / "result.json"
            args = (
                "bulk",
                source,
                "--block",
                1,
                "--cells",
                1,
                1,
                1,
                "--geometry",
                "cubic-bulk",
                "--output",
                output,
            )
            run = self.run_cli(directory, *args)
            self.assertEqual(run.returncode, 0, run.stderr)
            payload = json.loads(output.read_text())
            self.assertAlmostEqual(payload["results"]["lattice_mean_angstrom"], 3)
            self.assertEqual(len(payload["provenance"]["inputs"][0]["sha256"]), 64)
            before = output.read_bytes()
            self.assertEqual(self.run_cli(directory, *args).returncode, 2)
            self.assertEqual(output.read_bytes(), before)
            self.assertEqual(self.run_cli(directory, *args, "--overwrite").returncode, 0)

    def test_input_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "input.log"
            source.write_text("Step Volume PotEng\n0 8 -10\n1 64 -14\nLoop time done\n")
            before = source.read_bytes()
            run = self.run_cli(
                directory,
                "bulk",
                source,
                "--block",
                1,
                "--cells",
                1,
                1,
                1,
                "--geometry",
                "cubic-bulk",
                "--output",
                source,
                "--overwrite",
            )
            self.assertEqual(run.returncode, 2)
            self.assertIn("must not replace an input", run.stderr)
            self.assertEqual(source.read_bytes(), before)

    def test_incomplete_legacy_case_writes_no_partial_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "reports"
            run = self.run_cli(
                directory,
                "legacy",
                ROOT / "Surfaces/1k (110)",
                "--kind",
                "surface-other",
                "--output",
                output,
            )
            self.assertEqual(run.returncode, 2)
            self.assertIn("incomplete thermo block 2", run.stderr)
            self.assertFalse(output.exists())

    def test_invalid_selection_produces_no_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "result.json"
            run = self.run_cli(
                directory,
                "bulk",
                ROOT / "Temp_Stab/A-Ti(C1.0,N0.0)/temp_v1.log",
                "--block",
                99,
                "--cells",
                8,
                8,
                8,
                "--geometry",
                "cubic-bulk",
                "--output",
                output,
            )
            self.assertEqual(run.returncode, 2)
            self.assertIn("block must be", run.stderr)
            self.assertFalse(output.exists())

    def test_legacy_table_plot_and_metadata(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "reports"
            run = self.run_cli(
                directory, "legacy", ROOT / "Temp_Stab", "--kind", "bulk", "--output", output
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertTrue((output / "lattice_parameter.png").read_bytes().startswith(b"\x89PNG"))
            self.assertEqual(len((output / "results.txt").read_text().splitlines()), 6)
            metadata = json.loads((output / "provenance.json").read_text())
            self.assertEqual(metadata["settings"]["mode"], "legacy")
            self.assertEqual(len(metadata["inputs"]), 5)

    def test_layers_default_has_no_legacy_uncertainty(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "layers.json"
            run = self.run_cli(
                directory,
                "layers",
                ROOT / "Surfaces/100 Atomic Surface Analisis/TiC",
                "--names",
                "z1",
                "--start",
                400,
                "--stop",
                402,
                "--output",
                output,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_text())["results"]["z1"]
            self.assertIsNone(result["legacy_width_error_angstrom"])
            self.assertGreater(result["titanium_count"], 0)

    def test_surface_energy_units(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "energy.json"
            run = self.run_cli(
                directory,
                "surface-energy",
                "--slab-energy",
                -90,
                "--atoms",
                10,
                "--bulk-energy-per-atom",
                -10,
                "--area",
                5,
                "--equivalent-faces",
                "--output",
                output,
            )
            self.assertEqual(run.returncode, 0, run.stderr)
            result = json.loads(output.read_text())["results"]
            self.assertEqual(result["surface_energy_ev_per_angstrom2"], 1)
            self.assertAlmostEqual(result["surface_energy_j_per_m2"], 16.02176634)
