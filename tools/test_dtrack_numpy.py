"""Offline fixture tests; no KoLmafia session or network needed."""

import tempfile
import unittest
from pathlib import Path

from dtrack_numpy import analyze


class DTrackNumpyTests(unittest.TestCase):
    def test_missing_inputs(self):
        with tempfile.TemporaryDirectory() as folder:
            result = analyze(Path(folder))
            self.assertEqual(result["count"], 0)
            self.assertEqual(result["intervals"], [])

    def test_deltas_gaps_and_zero_adventures(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "meat.txt").write_text(
                "20261101\tstart\t100\t2000\tBarf\t1000\n"
                "20261101\tmid\t105\t2500\tBarf\t2000\n"
                "20261101\tend\t105\t2400\tBarf\t3000\n"
                "20261102\tstart\t106\t3000\tBarf\t4000\n"
                "bad-date\tignored\t0\t0\tx\t0\n", encoding="utf-8")
            (p / "networth_checkpoints.txt").write_text(
                "20261101\tstart\t2000\t5000\n"
                "20261101\tmid\t2500\t5400\n"
                "20261102\tstart\t3000\t5500\n", encoding="utf-8")
            result = analyze(p)
            self.assertEqual(result["count"], 4)
            self.assertEqual(result["valued_count"], 3)
            self.assertEqual(result["intervals"][0]["total_delta"], 900)
            self.assertEqual(result["intervals"][0]["total_per_adventure"], 180.0)
            self.assertIsNone(result["intervals"][1]["total_delta"])
            self.assertIsNone(result["intervals"][1]["meat_per_adventure"])
            self.assertIsNone(result["intervals"][2]["total_delta"])
            self.assertEqual(result["intervals"][2]["meat_delta"], 600)

    def test_duplicate_key_latest_wins_and_safe_labels(self):
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder)
            (p / "meat.txt").write_text(
                "20261101\ta\t1\t10\tx\t1\n"
                "20261101\ta\t2\t20\tx\t2\n"
                "20261101\t../unsafe\t3\t30\tx\t3\n", encoding="utf-8")
            result = analyze(p)
            self.assertEqual(result["count"], 1)
            self.assertEqual(result["checkpoints"][0]["liquid_meat"], 20)


if __name__ == "__main__":
    unittest.main()
