import csv
import io
import unittest
from datetime import datetime, timezone
from prospective.lunar_3d.lunar_source_gate_v1 import (
    as_utc, classify_fix, evaluate_source, local_solar_night, moon_sun_state,
)

class GateTests(unittest.TestCase):
    def test_night_boundary(self):
        t = datetime(2026, 11, 22, 1, tzinfo=timezone.utc)
        self.assertEqual(local_solar_night(t, -80), "2026-11-21")
    def test_utc_normalization(self):
        self.assertEqual(as_utc("2026-01-01T00:00:00Z").utcoffset().total_seconds(), 0)
    def test_illumination_and_horizon(self):
        t = datetime(2026, 11, 22, 12, tzinfo=timezone.utc)
        exposure, f = moon_sun_state(t, 35.6, 139.7)
        self.assertTrue(0 <= f <= 1)
        self.assertIn(exposure, {"bright", "dark", "intermediate", "twilight"})
        self.assertEqual(classify_fix(t, 35.6, 139.7, {}), "bright")
    def test_height_value_is_never_parsed(self):
        header = "timestamp,individual-local-identifier,location-lat,location-long,height-above-msl\n"
        record = "2026-11-22T12:00:00Z,b1,35.6,139.7,NOT_A_NUMBER\n"
        rows = csv.DictReader(io.StringIO(header + record * 40))
        r = evaluate_source({"doi": "synthetic", "title": "test", "checksum": "none"}, rows)
        self.assertEqual(r["usable_fix_presence_count"], 40)
        self.assertEqual(r["native_height_field"], "height_above_msl")
        self.assertFalse(r["outcome_opened"])
        self.assertFalse(r["supports_confirmatory_within_animal_test"])

if __name__ == "__main__":
    unittest.main()
