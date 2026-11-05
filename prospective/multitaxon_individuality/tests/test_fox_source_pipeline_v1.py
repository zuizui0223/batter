"""Synthetic regression tests; no original fox identifiers or coordinates."""
from __future__ import annotations

import csv
import importlib
import math
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_DIR))
try:
    pipeline = importlib.import_module("fox_source_pipeline_v1")
except ModuleNotFoundError:
    pipeline = None


def event_row(**overrides):
    row = {"timestamp": "2020-01-02 12:00:00.000", "location-lat": "0",
           "location-long": "0", "individual-local-identifier": "synthetic-a",
           "tag-local-identifier": "synthetic-tag", "manually-marked-outlier": "false",
           "gps:hdop": "1", "gps:satellite-count": "6", "activity-x": "2",
           "activity-y": "3", "sensor-type": "gps", "visible": "true"}
    row.update(overrides)
    return row


def reference_row(**overrides):
    row = {"animal-id": "synthetic-a", "tag-id": "synthetic-tag",
           "deploy-on-date": "2020-01-01 00:00:00.000",
           "deploy-off-date": "2020-02-01 00:00:00.000", "study-site": "Synthetic-site",
           "animal-sex": "f"}
    row.update(overrides)
    return row


def memory_event(when, animal="synthetic-a", tag="synthetic-tag", **overrides):
    dt = datetime.fromisoformat(when).replace(tzinfo=timezone.utc)
    result = {"animal": animal, "tag": tag, "deployment": 0,
              "site": "Synthetic-site", "year": 2020, "sex": "f", "dt": dt,
              "day": dt.date().isoformat(), "month": dt.strftime("%Y-%m"),
              "lat": 0.0, "lon": 0.0, "hdop": 1.0, "satellites": 6.0,
              "activity_x": 2.0, "activity_y": 3.0}
    result.update(overrides)
    return result


class SourcePipelineTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(pipeline, "source pipeline implementation is missing")

    def load_rows(self, events, references=None):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for name, rows in (("events.csv", events),
                               ("reference.csv", references or [reference_row()])):
                path = Path(directory) / name
                with path.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
                    writer.writeheader()
                    writer.writerows(rows)
                paths.append(path)
            return pipeline.load_source(*paths)

    def test_manual_outliers_are_removed_before_quality_gate(self):
        rows = [event_row(), event_row(**{"manually-marked-outlier": "TRUE", "gps:hdop": ""}),
                event_row(**{"gps:hdop": "5.1"}), event_row(**{"gps:satellite-count": "3"}),
                event_row(**{"gps:hdop": ""}), event_row(**{"gps:hdop": "NaN"}),
                event_row(**{"gps:hdop": "5", "gps:satellite-count": "4"})]
        events, audit, receipts = self.load_rows(rows)
        self.assertEqual(len(events), 2)
        self.assertEqual(audit["original_rows"], 7)
        self.assertEqual(audit["source_manual_outlier_removed"], 1)
        self.assertEqual(audit["additional_hdop_gt5_sat_below4_or_missing_removed"], 4)
        self.assertEqual(audit["after_quality"], 2)
        self.assertEqual(len(receipts["events"]["sha256"]), 64)
        self.assertEqual(events[0]["dt"].tzinfo, timezone.utc)

    def test_gps_and_visibility_guards_follow_outlier_and_quality_filters(self):
        rows = [event_row(), event_row(**{"sensor-type": "acceleration"}),
                event_row(**{"visible": "false"}), event_row(**{"sensor-type": ""}),
                event_row(**{"visible": ""}),
                event_row(**{"sensor-type": " GPS ", "visible": " TRUE "}),
                event_row(**{"manually-marked-outlier": "true", "sensor-type": "acceleration", "visible": "false"}),
                event_row(**{"gps:hdop": "10", "sensor-type": "acceleration", "visible": "false"}),
                event_row(**{"sensor-type": "acceleration", "visible": "false"})]
        events, audit, _ = self.load_rows(rows)
        self.assertEqual(len(events), 2)
        self.assertEqual(audit["source_manual_outlier_removed"], 1)
        self.assertEqual(audit["additional_hdop_gt5_sat_below4_or_missing_removed"], 1)
        self.assertEqual(audit["after_quality"], 7)
        self.assertEqual(audit["non_gps_after_quality_removed"], 3)
        self.assertEqual(audit["invisible_or_missing_visibility_after_quality_removed"], 2)
        self.assertEqual(audit["after_gps_visible"], 2)

    def test_reference_joins_animal_and_tag_with_deployment_interval(self):
        refs = [reference_row(), reference_row(**{"animal-id": "synthetic-b", "study-site": "Other-site"}),
                reference_row(**{"tag-id": "new-tag", "study-site": "Later-site",
                                 "deploy-on-date": "2021-01-01 00:00:00.000",
                                 "deploy-off-date": "2021-02-01 00:00:00.000", "animal-sex": "m"})]
        rows = [event_row(), event_row(**{"individual-local-identifier": "synthetic-b"}),
                event_row(**{"tag-local-identifier": "new-tag", "timestamp": "2021-01-02 00:00:00.000"})]
        events, _, _ = self.load_rows(rows, refs)
        self.assertEqual({(e["animal"], e["year"], e["site"], e["sex"]) for e in events},
                         {("synthetic-a", 2020, "Synthetic-site", "f"),
                          ("synthetic-b", 2020, "Other-site", "f"),
                          ("synthetic-a", 2021, "Later-site", "m")})

    def test_ambiguous_reference_mapping_fails_without_echoing_identifiers(self):
        refs = [reference_row(), reference_row(**{"study-site": "Contradictory-site"})]
        with self.assertRaisesRegex(ValueError, "[Aa]mbiguous") as caught:
            self.load_rows([event_row()], refs)
        self.assertNotIn("synthetic-a", str(caught.exception))

    def test_steps_are_sorted_and_use_same_date_inclusive_cadence(self):
        times = ["2020-01-01T00:00:00", "2020-01-01T00:09:00", "2020-01-01T00:24:00",
                 "2020-01-01T00:32:59", "2020-01-01T23:55:00", "2020-01-02T00:05:00",
                 "2020-01-02T00:15:00"]
        rows = [memory_event(t) for t in reversed(times)]
        steps, audit = pipeline.make_steps(rows)
        self.assertEqual(len(steps), 3)
        self.assertEqual([s["duration_minutes"] for s in steps], [9.0, 15.0, 10.0])
        self.assertEqual(audit["cross_utc_date_removed"], 1)
        self.assertEqual([s["dt"] for s in steps], sorted(s["dt"] for s in steps))
        self.assertTrue(all(s["day"] == s["dt_end"].date().isoformat() for s in steps))

    def test_steps_never_cross_tag_or_deployment(self):
        rows = [memory_event("2020-01-01T00:00:00"),
                memory_event("2020-01-01T00:10:00", tag="changed-tag"),
                memory_event("2020-01-01T00:20:00", tag="changed-tag", deployment=1),
                memory_event("2020-01-01T00:30:00", tag="changed-tag", deployment=1)]
        steps, audit = pipeline.make_steps(rows)
        self.assertEqual(len(steps), 1)
        self.assertEqual(audit["tag_or_deployment_boundary_removed"], 2)

    def test_origin_location_time_and_activity_are_preserved(self):
        origin = memory_event("2020-01-01T00:00:00", activity_x=0.0, activity_y=1.0)
        end = memory_event("2020-01-01T00:10:00", lon=0.0001, activity_x=5.0, activity_y=6.0)
        steps, _ = pipeline.make_steps([end, origin])
        self.assertEqual(steps[0]["lon"], origin["lon"])
        self.assertEqual(steps[0]["dt"], origin["dt"])
        self.assertEqual(steps[0]["activity_x"], 0.0)
        self.assertEqual(steps[0]["activity_x_end"], 5.0)
        self.assertNotIn("dt_end", origin)

    def test_nonpositive_times_and_implausible_speeds_are_removed(self):
        rows = [memory_event("2020-01-01T00:00:00"), memory_event("2020-01-01T00:00:00"),
                memory_event("2020-01-01T00:10:00", lon=1)]
        steps, audit = pipeline.make_steps(rows)
        self.assertEqual(steps, [])
        self.assertEqual(audit["nonpositive_duration_removed"], 1)
        self.assertEqual(audit["speed_gt10_kmh_removed"], 1)

    def test_speed_class_boundaries(self):
        self.assertEqual([pipeline.speed_mode(x) for x in (0, 0.049, 0.05, 0.499, 0.5, 10)],
                         [0, 0, 1, 1, 2, 2])

    def test_fixed_grid_uses_floor_for_negative_coordinates_and_utc_clock(self):
        step = memory_event("2020-01-01T13:00:00", lon=-0.01, lat=0.01)
        self.assertEqual(pipeline.context(step, 1, lat_cos=1), (-2, 1, 2))
        self.assertEqual(pipeline.context(step, 2, clock=False, lat_cos=1), (-1, 0))
        self.assertAlmostEqual(pipeline.source_lat_cos([step]), math.cos(math.radians(0.01)))

    def test_first_half_split_is_date_monotone_for_each_animal(self):
        rows = []
        for animal in ("synthetic-a", "synthetic-b"):
            for day in range(1, 8):
                for i in range(12):
                    row = memory_event(f"2020-01-{day:02d}T00:{i:02d}:00", animal=animal)
                    row["mode"] = 0 if animal.endswith("a") else 2
                    rows.append(row)
        train, test, eligible = pipeline.split_animal_days(rows)
        self.assertEqual(len(eligible), 2)
        self.assertEqual(len(train), 72)
        self.assertEqual(len(test), 96)
        for animal in eligible:
            self.assertLess(max(s["day"] for s in train if s["animal"] == animal),
                            min(s["day"] for s in test if s["animal"] == animal))

    def test_common_support_and_prediction_use_training_only(self):
        train, test = [], []
        for animal, mode in (("synthetic-a", 0), ("synthetic-b", 2)):
            for day in range(1, 6):
                for i in range(10):
                    row = memory_event(f"2020-01-{day:02d}T00:{i:02d}:00", animal=animal)
                    row["mode"] = mode
                    (train if day <= 2 else test).append(row)
        model = pipeline.fit(train, 1.0, lat_cos=1.0)
        report, internal = pipeline.score_heldout(model, test, return_internal=True)
        pooled, personal = pipeline.predict(model, test[0])
        self.assertGreater(personal, pooled)
        self.assertEqual(report["n_common_training_contexts"], 1)
        self.assertEqual(report["n_evaluable_holdout_animals"], 2)
        self.assertEqual(report["heldout_animal_days"], 6)
        self.assertGreater(report["gain_nats_per_step_equal_animal_day"], 0)
        self.assertEqual(len(internal["animal_day_gains"]), 2)
        self.assertNotIn("synthetic-a", str(report))


if __name__ == "__main__":
    unittest.main()
