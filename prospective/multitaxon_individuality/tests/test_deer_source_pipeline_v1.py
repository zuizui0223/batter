"""Synthetic source-contract tests; no original deer tracking records."""
from __future__ import annotations

import csv
import importlib
import math
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
try:
    pipeline = importlib.import_module("deer_source_pipeline_v1")
except ModuleNotFoundError:
    pipeline = None


def source_row(**changes):
    row = {"event-id": "synthetic-event", "visible": "true", "timestamp": "2018-01-01 00:00:00.000",
           "location-long": "0", "location-lat": "0", "sensor-type": "gps",
           "individual-taxon-canonical-name": "Odocoileus hemionus",
           "individual-local-identifier": "synthetic-a", "tag-local-identifier": "synthetic-tag"}
    row.update(changes)
    return row


def reference_row(**changes):
    row = {"animal-id": "synthetic-a", "tag-id": "synthetic-tag", "animal-taxon": "Odocoileus hemionus",
           "deploy-on-date": "", "deploy-off-date": "", "animal-group-id": "synthetic-group",
           "animal-life-stage": "adult", "animal-sex": "f", "deployment-id": "synthetic-deployment"}
    row.update(changes)
    return row


class DeerSourceTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(pipeline, "deer source pipeline implementation is missing")

    def load_rows(self, rows, references=None, verify_receipts=False):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for filename, records in (("events.csv", rows), ("reference.csv", references or [reference_row()])):
                path = Path(directory) / filename
                fields = list(dict.fromkeys(key for row in records for key in row))
                with path.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.DictWriter(stream, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(records)
                paths.append(path)
            return pipeline.load_source(*paths, verify_receipts=verify_receipts)

    def event(self, when, **changes):
        values = {"animal": "synthetic-a", "tag": "synthetic-tag", "group": "synthetic-group",
                  "sex": "f", "life_stage": "adult", "deployment": 0, "dt": datetime.fromisoformat(when),
                  "lat": 0.0, "lon": 0.0}
        values.update(changes)
        return pipeline.Event(**values)

    def test_receipt_mismatch_is_rejected_by_default(self):
        with self.assertRaisesRegex(ValueError, "[Cc]hecksum|[Rr]eceipt"):
            self.load_rows([source_row()], verify_receipts=True)

    def test_source_filters_preserve_native_clock_and_declared_years(self):
        rows = [source_row(), source_row(**{"visible": "false"}), source_row(**{"visible": ""}),
                source_row(**{"sensor-type": "acceleration"}), source_row(**{"location-lat": "NaN"}),
                source_row(**{"location-long": "181"}), source_row(**{"timestamp": "invalid"}),
                source_row(**{"timestamp": "2021-01-01 00:00:00.000"}),
                source_row(**{"timestamp": "2018-01-01 02:00:00.000", "visible": "1"}),
                source_row(**{"individual-taxon-canonical-name": "Other taxon"})]
        events, audit, receipts = self.load_rows(rows)
        self.assertEqual(len(events), 2)
        self.assertIsNone(events[0].dt.tzinfo)
        self.assertEqual(events[0].day, datetime(2018, 1, 1).toordinal())
        self.assertEqual(audit["outside_2018_2020_removed"], 1)
        self.assertEqual(audit["not_explicitly_visible_removed"], 2)
        self.assertEqual(audit["non_gps_removed"], 1)
        self.assertEqual(audit["invalid_position_removed"], 2)
        self.assertEqual(audit["invalid_timestamp_removed"], 1)
        self.assertEqual(audit["unexpected_taxon_removed"], 1)
        self.assertEqual(len(receipts["events"]["sha256"]), 64)

    def test_present_source_outlier_flags_are_honored_without_speed_filter(self):
        rows = [source_row(), source_row(**{"manually-marked-outlier": "true"}),
                source_row(**{"algorithm-marked-outlier": "1"}),
                source_row(**{"timestamp": "2018-01-01 02:00:00.000", "location-long": "1"})]
        events, audit, _ = self.load_rows(rows)
        self.assertEqual(len(events), 2)
        self.assertEqual(audit["source_outlier_removed"], 2)
        steps, _ = pipeline.make_steps(events)
        self.assertEqual(len(steps), 1)
        self.assertGreater(steps[0].speed_kmh, 50)

    def test_animal_and_tag_reference_mismatch_is_not_silently_joined(self):
        for changes in ({"tag-local-identifier": "other-tag"},
                        {"individual-local-identifier": "other-animal"}):
            with self.subTest(changes=changes):
                with self.assertRaisesRegex(ValueError, "[Rr]eference") as caught:
                    self.load_rows([source_row(**changes)])
                self.assertNotIn("synthetic-a", str(caught.exception))
                self.assertNotIn("other-tag", str(caught.exception))

    def test_conflicting_reference_metadata_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "[Aa]mbiguous|[Cc]onflict"):
            self.load_rows([source_row()], [reference_row(), reference_row(**{"animal-group-id": "other-group"})])

    def test_group_and_missing_deployment_date_limits_are_audited(self):
        events, audit, _ = self.load_rows([source_row()])
        self.assertEqual(events[0].group, "synthetic-group")
        self.assertEqual(audit["reference"]["distinct_nonempty_groups"], 1)
        self.assertEqual(audit["reference"]["missing_deploy_on_date"], 1)
        self.assertEqual(audit["reference"]["missing_deploy_off_date"], 1)
        self.assertNotIn("synthetic-group", str(audit))

    def test_identical_duplicates_collapse_and_conflicting_times_remove_all_rows(self):
        rows = [source_row(), source_row(),
                source_row(**{"timestamp": "2018-01-01 02:00:00.000"}),
                source_row(**{"timestamp": "2018-01-01 02:00:00.000", "location-long": "0.1"}),
                source_row(**{"timestamp": "2018-01-01 04:00:00.000"})]
        events, audit, _ = self.load_rows(rows)
        self.assertEqual(len(events), 2)
        self.assertEqual(audit["identical_duplicate_rows_removed"], 1)
        self.assertEqual(audit["conflicting_timestamp_groups"], 1)
        self.assertEqual(audit["conflicting_timestamp_rows_removed"], 2)
        steps, _ = pipeline.make_steps(events)
        self.assertEqual(steps, [])

    def test_sorting_both_input_directions_yields_identical_steps(self):
        events = [self.event("2018-01-01T00:00:00"), self.event("2018-01-01T02:00:00", lon=0.001),
                  self.event("2018-01-01T04:00:00", lon=0.002)]
        forward, _ = pipeline.make_steps(events)
        reverse, _ = pipeline.make_steps(list(reversed(events)))
        self.assertEqual(forward, reverse)
        self.assertEqual(len(forward), 2)

    def test_two_hour_cadence_boundaries_are_inclusive(self):
        for minutes, expected in ((107.999, 0), (108, 1), (120, 1), (132, 1), (132.001, 0)):
            from datetime import timedelta
            with self.subTest(minutes=minutes):
                a = self.event("2018-01-01T00:00:00")
                b = self.event("2018-01-01T00:00:00", dt=a.dt + timedelta(minutes=minutes))
                steps, _ = pipeline.make_steps([a, b])
                self.assertEqual(len(steps), expected)

    def test_cross_midnight_month_year_and_tag_pairs_are_rejected(self):
        cases = [("2018-01-01T23:00:00", "2018-01-02T01:00:00", {}),
                 ("2018-01-31T23:00:00", "2018-02-01T01:00:00", {}),
                 ("2018-12-31T23:00:00", "2019-01-01T01:00:00", {}),
                 ("2018-01-01T00:00:00", "2018-01-01T02:00:00", {"tag": "changed-tag"}),
                 ("2018-01-01T00:00:00", "2018-01-01T02:00:00", {"deployment": 1})]
        for start, end, changes in cases:
            with self.subTest(start=start, end=end, changes=changes):
                steps, _ = pipeline.make_steps([self.event(start), self.event(end, **changes)])
                self.assertEqual(steps, [])

    def test_known_distance_and_origin_context_have_no_endpoint_location_leakage(self):
        a = self.event("2018-01-01T05:00:00")
        b = self.event("2018-01-01T07:00:00", lon=1.0)
        steps, _ = pipeline.make_steps([a, b])
        step = steps[0]
        self.assertAlmostEqual(step.distance_km, 6371 * math.pi / 180, places=9)
        self.assertAlmostEqual(step.speed_kmh, step.distance_km / 2, places=9)
        self.assertEqual((step.dt, step.lon, step.lat, step.hour_bin), (a.dt, a.lon, a.lat, 0))
        self.assertEqual(step.dt_end, b.dt)
        self.assertEqual(step.duration_minutes, 120)
        self.assertEqual((step.year, step.month), (2018, 1))

    def test_projection_and_month_groups_use_all_supplied_source_events(self):
        events = [self.event("2018-01-01T00:00:00", lat=0), self.event("2018-01-01T02:00:00", lat=60)]
        self.assertAlmostEqual(pipeline.source_lat_cos(events), math.cos(math.radians(30)))
        steps, _ = pipeline.make_steps(events)
        grouped = pipeline.group_steps_by_month(steps)
        self.assertEqual(list(grouped), [(2018, 1)])
        self.assertIs(grouped[(2018, 1)][0], steps[0])


if __name__ == "__main__":
    unittest.main()
