#!/usr/bin/env python3
"""Synthetic-only test for raw Movebank green turtle 2018 cohort X estimator."""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from reproduce_turtle_X_source_v1 import calculate


class SourceXYTest(unittest.TestCase):
    def test_equal_positions_yield_one_and_do_not_export_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            base=Path(tmp)
            p=base/"reference.csv"
            e=base/"gps.csv"
            with p.open("w",newline="",encoding="utf8") as stream:
                write=csv.writer(stream)
                write.writerow(["animal-id","animal-taxon","study-site","deploy-on-date"])
                for i in range(12):
                    write.writerow([f"synthetic_{i}","Chelonia mydas","Diego Garcia","2018-07-01 00:00:00.000"])
            start=datetime(2018,7,1)
            with e.open("w",newline="",encoding="utf8") as stream:
                write=csv.writer(stream)
                write.writerow(["individual-local-identifier","timestamp","location-long","location-lat","sensor-type","visible"])
                for i in range(12):
                    n=231 if i<2 else 230
                    for k in range(n):
                        at=start+timedelta(days=k%30,hours=k//30)
                        write.writerow([f"synthetic_{i}",at.strftime("%Y-%m-%d %H:%M:%S.000"),"72.4","-7.3","gps","true"])
            out=calculate(p,e)
            self.assertEqual(out["source_animals"],12)
            self.assertEqual(out["original_gps_positions_first30days"],2762)
            self.assertEqual(out["dependent_animal_pairs"],66)
            for grid in out["source_overlap_X_by_grid_km"].values():
                self.assertEqual(grid["n_pairs_positive"],66)
                self.assertAlmostEqual(grid["mean"],1.0,places=9)
            self.assertFalse(out["original_animal_ids_or_locations_exported"])


if __name__=="__main__":
    unittest.main()
