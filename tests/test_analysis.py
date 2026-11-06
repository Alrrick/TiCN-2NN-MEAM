"""Regression checks against archived bulk results and malformed-log handling.

Run from the repository root: MPLBACKEND=Agg python -m unittest discover -s tests
"""

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "bulk_analysis", ROOT / "Temp_Stab" / "analyze_stability.py"
)
bulk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bulk)


class ArchivedAnalysisTests(unittest.TestCase):
    def test_bulk_statistics_match_archived_results(self):
        reference = (ROOT / "Temp_Stab" / "Resultados.txt").read_text()
        rows = reference.replace(",", ".").splitlines()[1:]
        cases = sorted(p for p in (ROOT / "Temp_Stab").iterdir() if p.is_dir() and "-Ti(" in p.name)
        self.assertEqual(len(cases), len(rows))
        for case, row in zip(cases, rows, strict=True):
            expected = [float(value) for value in row.split()][1:]
            with self.subTest(case=case.name), contextlib.redirect_stdout(io.StringIO()):
                actual = bulk.analyze_folder(str(case), "temp_v")
                for value, reference_value in zip(actual, expected, strict=True):
                    self.assertAlmostEqual(value, reference_value, places=9)

    def test_missing_header_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "missing.log"
            log.write_text("No thermo output\n")
            with self.assertRaisesRegex(ValueError, "missing thermo block"):
                bulk.data_reader(log)

    def test_truncated_archived_surface_log_fails(self):
        log = ROOT / "Surfaces" / "1k (110)" / "B-Ti(C0.75,N0.25)" / "temp_v1.log"
        with self.assertRaisesRegex(ValueError, "incomplete thermo block 2"):
            bulk.data_reader(log)


if __name__ == "__main__":
    unittest.main()
