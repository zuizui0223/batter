"""Read-only structured H1 source unit and no-meta-pooling assertions.

This does NOT rerun the public individual bat trial dataset.
"""
import json
import csv
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent

class TestMolossusSourceReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d=json.loads((ROOT/"H1_EXTERNAL_MOLOSSUS_2020_RECEIPT_V1.json").read_text())
    def test_original_public_not_sha_authenticated(self):
        x=self.d
        self.assertFalse(x["original_file_bytes_verified"])
        self.assertEqual(x["transcribed_source_rows"],51)
        self.assertEqual(x["original_file_expected_md5"],"b4b9970eac190601b4a291725137c110")
    def test_observation_grain_and_roost_hierarchy(self):
        s=self.d["search"]
        self.assertEqual((s["n_trials"],s["n_subjects"],s["n_matched_bats"],s["n_matched_roosts"]),(34,19,12,5))
        self.assertEqual((s["n_test"],s["n_control"]),(20,14))
        self.assertEqual(sum(x["n"] for x in s["roosts"].values()),12)
        r=[v["mean"] for v in s["roosts"].values()]
        self.assertAlmostEqual(sum(r)/5,s["roost_equal_mean"],places=8)
        self.assertEqual(sum(v>0 for v in r),4)
        self.assertEqual(sum(v<0 for v in r),1)
        self.assertEqual(s["roost_signflip_p_two_sided"],0.25)
        self.assertLess(s["roost_bootstrap95"][0],0)
        self.assertGreater(s["roost_bootstrap95"][1],0)
    def test_approach_and_crossstudy_stop(self):
        x=self.d["approach"]
        self.assertEqual(x["n_matched_bats"],4)
        self.assertIn("STOP",x["status"])
        self.assertIn("not same estimand",self.d["interpretation"])
        with (ROOT/"H1_EXTERNAL_SOURCE_ELIGIBILITY_V1.csv").open(newline="") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),7)
        eligible=[x for x in rows if x["same_2019_buzz_x_baseline_estimand"]=="yes"]
        self.assertEqual(len(eligible),1)
        self.assertEqual(eligible[0]["year"],"2019")

if __name__=="__main__":
    unittest.main()
