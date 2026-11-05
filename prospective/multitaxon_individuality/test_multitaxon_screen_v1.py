#!/usr/bin/env python3
"""No third-party tracking files are included; small synthetic source-schema tests."""
from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from audit_source_events_v1 import summarize_csv


class TestSourceCoverageGate(unittest.TestCase):
    FIELDS = (
        "individual-local-identifier", "timestamp", "location-long",
        "location-lat", "sensor-type", "visible", "algorithm-marked-outlier"
    )

    def save(self, rows: list[tuple[str, ...]], folder: Path) -> Path:
        path = folder / "synthetic_movebank.csv"
        with path.open("w", newline="", encoding="utf8") as out:
            writer = csv.writer(out)
            writer.writerow(self.FIELDS)
            writer.writerows(rows)
        return path

    def cases(self, animals: int, sensor: str = "gps") -> list[tuple[str, ...]]:
        rows = []
        for animal in range(animals):
            for day in range(3):
                for t in range(10):
                    rows.append((
                        f"synthetic_animal_{animal}",
                        f"2026-06-{day+1:02d} 00:{t:02d}:00",
                        "14.2500", "38.4000", sensor, "true", ""
                    ))
        return rows

    def test_synthetic_nine_gps_individuals_have_multiple_days(self):
        with tempfile.TemporaryDirectory() as tmp:
            rows = self.cases(9)
            rows.append(rows[0])  # same animal/timestamp, not an extra unique position
            rows.append(("extra", "2026-06-01", "14", "38", "gps", "false", ""))
            r = summarize_csv(self.save(rows, Path(tmp)), "synthetic:test")
        self.assertEqual(r["raw_source_rows"], 272)
        self.assertEqual(r["visible_outlier_excluded"], 1)
        self.assertEqual(r["within_individual_same_timestamp_collisions"], 1)
        self.assertEqual(r["unique_individual_timestamp_positions"], 270)
        self.assertEqual(r["possible_individuals_with_ge_30_time_records_on_ge_3_days"], 9)
        self.assertEqual(
            r["stage3_precision_coverage_status"],
            "GPS_TEMPORAL_PREFLIGHT_POSSIBLE_NEEDS_COHORT_CONTEXT"
        )
        self.assertFalse(r["individual_identity_effect_fitted"])

    def test_synthetic_one_animal_cannot_measure_individuality(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = summarize_csv(self.save(self.cases(1), Path(tmp)), "synthetic:test")
        self.assertEqual(r["stage3_precision_coverage_status"], "FAIL_SINGLE_INDIVIDUAL")

    def test_synthetic_argos_not_equivalent_to_gps(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = summarize_csv(self.save(self.cases(11, "argos-doppler-shift"), Path(tmp)), "synthetic:test")
        self.assertEqual(r["possible_individuals_with_ge_30_time_records_on_ge_3_days"], 11)
        self.assertEqual(r["stage3_precision_coverage_status"], "ARGOS_ONLY_NOT_FINE_GPS_PRIMARY")


if __name__ == "__main__":
    unittest.main()
