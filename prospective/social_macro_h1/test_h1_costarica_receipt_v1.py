"""Read-only receipt guard; does NOT independently refit original 2025 bat rows."""
import csv
import json
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
NAME="H1_COSTARICA_2025_AUTHENTICATED_RESULT_V1.json"

class TestCostaRicaAuthenticatedReceipt(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a=json.loads((HERE/NAME).read_text(encoding="utf-8"))

    def test_source_authenticity_and_responder_selection(self):
        r=self.a
        self.assertEqual(r["original_author_git_blob_sha1"],"b8a119df0204ed0beb90b971c97f60cafbdb74cd")
        self.assertEqual(r["original_csv_sha256"],"11e281708be94ad76b0875d8cf43adf605e8095bb500ad43936f20a3c98d77d3")
        self.assertEqual(r["source_rows"],228)
        self.assertEqual((r["original_csv_individuals"],r["tested_animals_in_paper"],r["tested_social_groups_in_paper"]),(38,117,33))
        self.assertEqual(r["unrepresented_tested_animals"],79)
        self.assertFalse(r["all_117_tested_population_effect_available"])
        self.assertFalse(r["group_independent_uncertainty_available"])
        self.assertFalse(r["raw_subject_data_committed"])

    def test_matched_direction_and_ambiguous_groups(self):
        r=self.a
        a=r["primary"];g=r["group_identification"]
        self.assertEqual((a["negative_bats"],a["positive_bats"],a["zero_bats"]),(35,3,0))
        self.assertEqual(sum(s["n"] for s in r["stimulus_order"]),38)
        self.assertEqual(sum(s["n"] for s in r["nonpredator_class"]),38)
        self.assertAlmostEqual(a["mean"],-2.1652937703974704,places=8)
        self.assertEqual(g["extra_responders"],5)
        self.assertEqual(g["feasible_size_allocations"],7)
        self.assertTrue(g["sharp_possible_mean_interval"][0]<a["mean"]<g["sharp_possible_mean_interval"][1]<0)
        self.assertIn("NOT_SAMPLING_CONFIDENCE_INTERVAL",g["type"])
        self.assertIn("NOT_IDENTIFIED",g["group_cluster_p"])

    def test_independent_geography_not_matched_meta(self):
        r=self.a
        self.assertFalse(r["source_exactly_replicates_2019_buzz_density"])
        self.assertTrue(r["original_source_biological_result_already_published"])
        with (HERE/"H1_CROSS_STUDY_RESPONSE_COMPARABILITY_V3.csv").open(encoding="utf-8",newline="") as f:
            entries=list(csv.DictReader(f))
        self.assertEqual(len(entries),7)
        by={e["study_id"]:e for e in entries}
        self.assertEqual(by["GambaRios2025"]["exact_2019_buzz_by_baseline_replication"],"no")
        self.assertEqual(by["GambaRios2025"]["independent_external_region_from_2015_2016_BCI"],"yes")
        self.assertEqual(by["Eckenweber2016"]["independent_external_region_from_2015_2016_BCI"],"no")
        self.assertEqual(by["Carter2015"]["independent_external_region_from_2015_2016_BCI"],"no")

if __name__=="__main__":
    unittest.main()
