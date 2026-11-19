"""Source-audit receipt checks; no biological effect regression is authorized."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
FILE=ROOT/"H1_COMBINE_GROUPSIZE_REPORTED_COVERAGE_V1.json"

class TestCombineBatSocialGroupCoverage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x=json.loads(FILE.read_text(encoding="utf-8"))

    def test_original_vs_mirror_authentication_status(self):
        a=self.x
        self.assertEqual(a["source_rows"],6263)
        self.assertEqual(a["source_columns"],60)
        self.assertEqual(a["mirror_git_blob_sha"],"7e274bac17eba845d93cdd27c1357605af3d710e")
        self.assertFalse(a["original_source_md5_verified"])

    def test_taxon_key_fallback_and_completeness(self):
        a=self.x
        self.assertEqual(a["chiroptera_rows"],1342)
        self.assertEqual(a["iucn_recognized_unique_labels"],1335)
        self.assertEqual(a["unrecognized_iucn_labels"],7)
        self.assertEqual(a["social_group_n_nonimputed_reported_bats"],45)
        self.assertEqual(a["group_size_missing_bats"],1297)
        self.assertAlmostEqual(a["group_size_nonimputed_coverage_percent"],100*45/1342)
        self.assertEqual(a["group_size_one"],33)
        self.assertEqual(a["group_size_greater_than_one"],12)
        self.assertEqual(a["group_size_greater_than_five"],3)
        self.assertEqual(sum(a["group_size_value_histogram"].values()),45)

    def test_family_diet_aliased(self):
        a=self.x
        self.assertEqual(a["pteropodidae_reported_n"],30)
        self.assertEqual(a["reported_bat_plant_diet_gt50_n"],30)
        self.assertTrue(a["plant_gt50_all_pteropodidae"])
        self.assertFalse(a["family_fixed_effect_plus_plant_diet_parameter_identified"])
        self.assertEqual(sum(t["recorded"] for t in a["family_source_coverage"].values()),45)
        self.assertEqual(a["recorded_group_size_families"],6)
        self.assertAlmostEqual(a["pteropodidae_vs_other_reporting_odds_ratio"],(30*1128)/(169*15))
        self.assertFalse(a["primary_H1_information_transfer_measured"])
        self.assertFalse(a["male_group_formation_measured"])
        self.assertFalse(a["causal_or_phylogenetic_inference_authorized"])

if __name__=="__main__":
    unittest.main()
