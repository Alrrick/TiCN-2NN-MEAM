"""Independent numerical cases, parser failures, and archive-wide regressions."""

import contextlib
import io
import json
import math
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from ticn_analysis.analysis import bulk_statistics, layer_statistics, surface_energy
from ticn_analysis.io import read_coordinates, read_thermo
from ticn_analysis.layers import analyze_layer, layer_paths
from ticn_analysis.legacy import legacy_statistics
from ticn_analysis.legacy_helpers import analyze_rippling
from ticn_analysis.models import Sampling, ThermoBlock

ROOT = Path(__file__).resolve().parents[1]


class ReaderTests(unittest.TestCase):
    def read(self, text, **kwargs):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.log"
            path.write_text(text)
            return read_thermo(path, **kwargs)

    def test_whitespace_reordered_columns_and_block_boundaries(self):
        blocks = self.read(
            "LAMMPS\n PotEng\tVolume   Step\n-8  64 0\n\n-10\t125 1\nLoop time done\n"
            "Step Volume PotEng\n0 216 -12\n1 343 -14\nLoop time done\n"
        )
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].column("Volume"), (64, 125))
        self.assertEqual(blocks[1].column("Step"), (0, 1))

    def test_invalid_inputs_fail_with_context(self):
        for text, message in (
            ("nothing\n", "missing thermo block"),
            ("Step Volume\n0 1\n", "incomplete thermo block 1"),
            ("Step Volume\n0 1 2\n", "expected 2 thermo columns"),
            ("Step Volume\n0 nan\n", "nonfinite"),
            ("Step Volume\n0 inf\n", "nonfinite"),
            ("Step Volume\n0 broken\n", "nonnumeric"),
            ("Step Volume Volume\n", "duplicate"),
            ("Step Volume\nLoop time done\n", "empty thermo"),
        ):
            with self.subTest(text=text), self.assertRaisesRegex(ValueError, message):
                self.read(text)

    def test_selected_legacy_prefix_does_not_require_later_blocks(self):
        text = "Step Volume\n0 64\nLoop time done\nStep Volume\n0 125\n"
        self.assertEqual(len(self.read(text, max_blocks=1)), 1)
        with self.assertRaisesRegex(ValueError, "incomplete thermo block 2"):
            self.read(text)

    def test_coordinate_whitespace_and_validation(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "coords.dat"
            path.write_text("header\nheader\n1.0\t2.5\n\n2   3.5\n")
            self.assertEqual(read_coordinates(path), ((1, 2.5), (2, 3.5)))
            for row in ("4 2", "1 nan", "1 2 3", "1 wrong"):
                path.write_text(f"header\nheader\n{row}\n")
                with self.subTest(row=row), self.assertRaises(ValueError):
                    read_coordinates(path)


class NumericalTests(unittest.TestCase):
    def test_hand_calculated_bulk_and_sample_sd(self):
        block = ThermoBlock(("Volume", "PotEng"), ((8, -10), (64, -14)))
        result = bulk_statistics(block, cells=(1, 1, 1), geometry="cubic-bulk")
        self.assertAlmostEqual(result.lattice_mean_angstrom, 3)
        self.assertAlmostEqual(result.lattice_sd_angstrom, math.sqrt(2))
        self.assertEqual(result.potential_mean_ev, -12)
        self.assertAlmostEqual(result.potential_sd_ev, math.sqrt(8))
        self.assertEqual(result.sample_count, 2)

    def test_rejects_slab_invalid_volume_missing_column_and_short_sample(self):
        valid = ThermoBlock(("Volume", "PotEng"), ((8, -10), (64, -14)))
        with self.assertRaisesRegex(ValueError, "slab volume"):
            bulk_statistics(valid, cells=(1, 1, 1), geometry="slab")
        for block in (
            ThermoBlock(("Volume", "PotEng"), ((0, -10), (64, -14))),
            ThermoBlock(("PotEng",), ((-10,), (-14,))),
            ThermoBlock(("Volume", "PotEng"), ((8, -10),)),
        ):
            with self.subTest(block=block), self.assertRaises(ValueError):
                bulk_statistics(block, cells=(1, 1, 1), geometry="cubic-bulk")
        with self.assertRaises(ValueError):
            bulk_statistics(valid, cells=(1, 0, 1), geometry="cubic-bulk")

    def test_thermo_model_rejects_inconsistent_rows(self):
        with self.assertRaisesRegex(ValueError, "row length"):
            ThermoBlock(("Step", "Volume"), ((0,),))
        with self.assertRaisesRegex(ValueError, "unique"):
            ThermoBlock(("Step", "Step"), ((0, 1),))

    def test_sampling_uses_block_rows_and_validates_bounds(self):
        block = ThermoBlock(("Step",), tuple((float(i),) for i in range(8)))
        self.assertEqual(Sampling(2, 7, 2).select(block).column("Step"), (2, 4, 6))
        for settings in ((-1, None, 1), (2, 2, 1), (0, None, 0)):
            with self.assertRaises(ValueError):
                Sampling(*settings)
        for selection in (Sampling(7), Sampling(0, 9)):
            with self.assertRaises(ValueError):
                selection.select(block)

    def test_layer_values_and_translation_invariance(self):
        coordinates = [(1, 1.0), (1, 3.0), (2, 4.0), (3, 8.0)]
        result = layer_statistics(coordinates)
        shifted = layer_statistics([(kind, z + 100) for kind, z in coordinates])
        self.assertEqual(result.width_angstrom, 4)
        self.assertAlmostEqual(result.titanium_sd_angstrom, math.sqrt(2))
        self.assertAlmostEqual(result.anion_sd_angstrom, math.sqrt(8))
        self.assertIsNone(result.legacy_width_error_angstrom)
        for key in ("width_angstrom", "titanium_sd_angstrom", "anion_sd_angstrom"):
            self.assertAlmostEqual(getattr(result, key), getattr(shifted, key))
        with self.assertRaises(ValueError):
            layer_statistics([(1, 1.0), (1, 2.0)])

    def test_surface_energy_known_value_and_geometry_guard(self):
        inputs = dict(
            slab_energy_ev=-90,
            atom_count=10,
            bulk_energy_per_atom_ev=-10,
            face_area_angstrom2=5,
            equivalent_faces=True,
        )
        self.assertEqual(surface_energy(**inputs), 1)
        for change in (
            {"equivalent_faces": False},
            {"face_area_angstrom2": 0},
            {"atom_count": 0},
            {"slab_energy_ev": math.nan},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                surface_energy(**(inputs | change))

    def test_optional_rippling_reports_anion_spread(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "material"
            folder.mkdir()
            for index in range(1, 5):
                (folder / f"r{index}data.txt").write_text("h\nh\n1 1\n1 3\n2 4\n2 8\n")
            with contextlib.redirect_stdout(io.StringIO()):
                analyze_rippling(str(folder))
            report = Path(str(folder) + "result.txt").read_text()
            self.assertEqual(report.count(f"z_xs: 6.0 {math.sqrt(8)}"), 4)


class ArchiveRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reference = json.loads((ROOT / "tests/legacy_reference.json").read_text())

    def test_all_archived_stability_cases(self):
        for script, cases in self.reference.items():
            if not script.endswith(".py"):
                continue
            directory = ROOT / Path(script).parent
            count = 3 if directory.name == "1k (100) Real" else 2
            for case, expected in cases.items():
                path = directory / case / "temp_v1.log"
                with self.subTest(script=script, case=case):
                    if isinstance(expected, dict):
                        with self.assertRaisesRegex(ValueError, "incomplete thermo block 2"):
                            legacy_statistics(path, block_count=count)
                    else:
                        actual = legacy_statistics(path, block_count=count).legacy_values()
                        for value, reference in zip(actual, expected, strict=True):
                            self.assertAlmostEqual(value, reference, places=9)

    def test_all_archived_layers(self):
        directory = ROOT / "Surfaces/100 Atomic Surface Analisis"
        for material in ("TiC", "TiN"):
            for layer, expected in self.reference[material].items():
                with self.subTest(material=material, layer=layer):
                    result = analyze_layer(
                        layer_paths(directory / material, layer, 400, 451, 1), legacy=True
                    )
                    values = list(asdict(result).values())[:5] + [
                        result.legacy_width_error_angstrom
                    ]
                    for value, reference in zip(values, expected, strict=True):
                        self.assertAlmostEqual(value, reference, places=9)
