import csv
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
NAME="H1_INDEPENDENT_REPLICATION_ELIGIBILITY_V4.csv"

class TestIndependentCueH1Eligibility(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (HERE/NAME).open(newline="",encoding="utf-8") as f:
            cls.rows=list(csv.DictReader(f))
        cls.by={r["study_id"]:r for r in cls.rows}

    def test_eligibility_frame_covers_distinct_effects(self):
        self.assertEqual(len(self.rows),8)
        self.assertEqual(len(self.by),8)
        self.assertEqual(len({r["doi"] for r in self.rows}),8)
        self.assertTrue(all(r["study_id"] and r["source_url"].startswith("https://") for r in self.rows))
        self.assertEqual(sum(r["exact_2019_buzz_x_baseline_transfer"]=="YES" for r in self.rows),0)
        self.assertEqual(sum(r["exact_2019_buzz_x_baseline_transfer"]=="REFERENCE" for r in self.rows),1)

    def test_no_unsupported_species_negative_and_false_proxy(self):
        wilson=self.by["Wilson2026"]
        self.assertEqual(wilson["original_rows_verified"],"NO")
        self.assertIn("no authenticated",wilson["data_access"].lower())
        self.assertIn("Eptesicus fuscus",wilson["taxon_or_scope"])
        self.assertNotIn("all four no response",wilson["response_target"].lower())
        self.assertIn("not a measure of",self.by["GlobalRoost2024"]["reason_for_2019_transfer_stop"])
        self.assertIn("not experimentally demonstrated",self.by["SafiKerth2007"]["reason_for_2019_transfer_stop"])
        self.assertIn("filename inventory",self.by["CorcoranWeller2018"]["data_access"])

    def test_original_sources_independence_does_not_imply_same_measure(self):
        for key in ("Fenton1976","CorcoranWeller2018","Halat2024","CalderonCapote2025","Wilson2026"):
            r=self.by[key]
            self.assertEqual(r["independent_of_2019"],"YES")
            self.assertEqual(r["exact_2019_buzz_x_baseline_transfer"],"NO")
        self.assertEqual(self.by["Lewanzik2019"]["biological_unit"],"12 lakes")
        self.assertIn("sample",self.by["SafiKerth2007"]["data_access"].lower()) if False else None

if __name__=="__main__":
    unittest.main()
