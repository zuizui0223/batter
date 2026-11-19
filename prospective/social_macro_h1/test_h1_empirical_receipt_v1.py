"""Provenance/claim guard for archived empirical aggregate receipt.

This checks internal consistency of saved results; it does NOT rerun the raw XLSX.
Actual animal-data execution requires the original SHA-pinned workbook.
"""
import json
import csv
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent

class TestEmpiricalResultReceipt(unittest.TestCase):
    def test_saved_source_and_study_boundary(self):
        r=json.loads((HERE/"H1_EMPIRICAL_LEWANZIK2019_RECEIPT_V1.json").read_text())
        self.assertEqual(r["original_xlsx_sha256"],"fbabb5021c613aa7033ad13bc1a357a68700a7d3683ec16ae1bcf4a65e121c86")
        self.assertEqual(r["input_rows"],1440)
        self.assertEqual(r["study_lakes"],12)
        self.assertEqual(len(r["results"]),4)
        self.assertFalse(r["user_raw_source_uploaded_to_github"])
        self.assertEqual({x["group"]:x["n"] for x in r["results"]},
                         {"Myotis":360,"NEV":360,"Pnat":330,"Ppip":360})

    def test_saved_claim_boundaries(self):
        r=json.loads((HERE/"H1_EMPIRICAL_LEWANZIK2019_RECEIPT_V1.json").read_text())
        for x in r["results"]:
            self.assertLess(x["delta_heldout"],0)
            self.assertLess(x["ci95"][0],0)
            self.assertGreater(x["ci95"][1],0)
            self.assertLessEqual(x["positive_lakes"],x["lakes"])
        self.assertEqual(next(x for x in r["results"] if x["group"]=="Pnat")["lakes"],11)
        self.assertGreater(next(x for x in r["results"] if x["group"]=="Pnat")["author_filter_delta"],0)

    def test_heldout_lake_receipt_reconciles(self):
        r=json.loads((HERE/"H1_EMPIRICAL_LEWANZIK2019_RECEIPT_V1.json").read_text())
        with (HERE/"H1_EMPIRICAL_LEWANZIK2019_LOLO_LAKES_V1.csv").open(newline="",encoding="utf-8") as fh:
            rows=list(csv.DictReader(fh))
        self.assertEqual(len(rows),47)
        for x in r["results"]:
            rr=[y for y in rows if y["recipient_group"]==x["group"]]
            self.assertEqual(len(rr),x["lakes"])
            self.assertEqual(sum(float(y["delta_mean_gaussian_logscore_interaction_vs_main"])>0 for y in rr),x["positive_lakes"])
            avg=sum(float(y["delta_mean_gaussian_logscore_interaction_vs_main"]) for y in rr)/len(rr)
            self.assertAlmostEqual(avg,x["delta_heldout"],places=7)
            self.assertEqual(sum(int(y["test_rows"]) for y in rr),x["n"])

if __name__=="__main__":
    unittest.main()
