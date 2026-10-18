#!/usr/bin/env python3
"""Synthetic-only tests for source GPS preflight. Not Movebank animal results."""
from __future__ import annotations
import csv
import gzip
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from preflight_movebank_events_v1 import preflight, detect_columns, STATUS, interval_bucket

class MovebankPreflightTests(unittest.TestCase):
    def csvfile(self, directory, animals=9, sensor="GPS",
                timezone_suffix=True, id_column=True,
                missing_one_coordinate=False, compressed=False):
        path = Path(directory)/("mock_events.csv.gz" if compressed else "mock_events.csv")
        openf = gzip.open if compressed else open
        fields = ["timestamp", "location-long", "location-lat",
                  "individual-local-identifier" if id_column else "tag-local-identifier",
                  "sensor-type", "eobs:horizontal-accuracy"]
        with openf(path, "wt", encoding="utf-8", newline="") as h:
            w=csv.DictWriter(h, fieldnames=fields)
            w.writeheader()
            for a in range(animals):
                for day in (0,3,6,9):
                    for tick in range(50):
                        dt=datetime(2026,6,1,tzinfo=timezone.utc)+timedelta(days=day,minutes=tick*5)
                        stamp=dt.isoformat().replace("+00:00","Z") if timezone_suffix else dt.strftime("%Y-%m-%dT%H:%M:%S")
                        lat=42.0 + (a%3)*0.001 + tick/100000
                        if missing_one_coordinate and a==0 and day==0 and tick==0:
                            lat=110.0
                        row={fields[0]:stamp,fields[1]:20.0+a/100,
                             fields[2]:lat, fields[3]:f"PRIVATE_ID_{a:04d}",
                             fields[4]:sensor,fields[5]:"8.5"}
                        w.writerow(row)
        return path

    def test_complete_synthetic_GPS_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.csvfile(tmp)
            result=preflight(p,"10.5441/synthetic/test-only")
            self.assertEqual(result["preflight_status"],STATUS["PASS"])
            self.assertEqual(result["valid_GPS_like_events"],9*4*50)
            self.assertEqual(result["n_repeated_animals_passing_simple_day_and_span_gate"],9)
            self.assertEqual(result["n_source_dates_with_2_or_more_passing_animals"],4)
            self.assertTrue(result["GPS_event_sensor_type_verified"])
            self.assertTrue(result["accuracy_measure_column_present"])
            self.assertEqual(result["accuracy_populated_fixes"],1800)
            self.assertEqual(result["time_step_histogram"]["<= 5 minutes"],9*4*49)
            self.assertNotIn("PRIVATE_ID",json.dumps(result))
            self.assertFalse(result["real_individuality_or_partition_effect_estimated"])

    def test_complete_gzip(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=preflight(self.csvfile(tmp,compressed=True),"test-only")
            self.assertEqual(r["preflight_status"],STATUS["PASS"])
            self.assertEqual(r["observations_scanned"],1800)

    def test_animal_n_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=preflight(self.csvfile(tmp,animals=7),"test-only")
            self.assertEqual(r["preflight_status"],STATUS["NOT_ENOUGH_ANIMALS"])
            self.assertEqual(r["n_distinct_animal_id_strings"],7)

    def test_nonGPS_events_do_not_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=preflight(self.csvfile(tmp,sensor="Accelerometer"),"test-only")
            self.assertEqual(r["preflight_status"],STATUS["NO_EVENTS"])
            self.assertEqual(r["row_exclusion_counts"]["non_GPS_sensor_excluded"],1800)

    def test_no_animal_identity_cannot_be_substituted_by_tag(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=preflight(self.csvfile(tmp,id_column=False),"test-only")
            self.assertEqual(r["preflight_status"],STATUS["NO_ID"])
            self.assertTrue(r["tag_only_id_not_accepted"])

    def test_timezone_naive_stop_without_explicit_operator_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.csvfile(tmp,timezone_suffix=False)
            r=preflight(p,"test-only")
            self.assertEqual(r["preflight_status"],STATUS["NO_EVENTS"])
            self.assertEqual(r["row_exclusion_counts"]["timestamp_invalid_or_timezone_unresolved"],1800)
            allowed=preflight(p,"test-only",assume_utc=True)
            self.assertEqual(allowed["preflight_status"],STATUS["PASS"])
            self.assertTrue(allowed["timestamp_timezone_assumption_enabled"])

    def test_bad_coords_flag_and_biological_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=self.csvfile(tmp,missing_one_coordinate=True)
            r=preflight(p,"test-only")
            self.assertEqual(r["preflight_status"],STATUS["PASS"])
            self.assertEqual(r["row_exclusion_counts"]["coordinates_invalid"],1)
            self.assertEqual(r["valid_GPS_like_events"],1799)

    def test_partial_read_can_never_claim_eligibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=preflight(self.csvfile(tmp),"test-only",max_rows=600)
            self.assertEqual(r["preflight_status"],"PARTIAL_SCAN_UNDECIDED_NOT_ELIGIBLE")
            self.assertEqual(r["observations_scanned"],600)

    def test_column_aliases_and_intervals(self):
        aliases=detect_columns(["Event Timestamp","Location.Long","location_lat","animal-id","Sensor Type"])
        self.assertEqual(aliases["timestamp"],"Event Timestamp")
        self.assertEqual(aliases["animal"],"animal-id")
        self.assertEqual(aliases["lat"],"location_lat")
        self.assertEqual(aliases["lon"],"Location.Long")
        self.assertEqual(interval_bucket(61),"<= 180 minutes")

if __name__=="__main__":
    unittest.main()
