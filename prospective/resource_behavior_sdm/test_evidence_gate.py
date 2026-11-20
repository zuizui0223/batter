"""Evidence classification tests; metadata checks, NOT biological replay."""
import json
import pathlib
import unittest


class ResourceBehaviorClaimGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = pathlib.Path(__file__).with_name("evidence_ledger_v1.json")
        cls.data = json.loads(path.read_text(encoding="utf-8"))
        cls.claims = {c["id"]: c for c in cls.data["claims"]}

    def test_unestimated_effects_stay_null(self):
        self.assertGreaterEqual(len(self.data["strict_unestimated"]), 5)
        self.assertTrue(all(v is None for v in self.data["strict_unestimated"].values()))
        self.assertEqual(self.data["claim_gate"], "UNVALIDATED_HIGHDIMENSIONAL_RESOURCE_SDM_PROTOTYPE")

    def test_positive_source_rank_not_promoted_to_resource_ecology(self):
        botanical = self.claims["BOTANICAL_RECORD_RANK"]
        self.assertIn("OBSERVATION_RANK", botanical["tier"])
        self.assertEqual(botanical["n_evaluable"], 647)
        self.assertEqual(botanical["n_candidate"], 1802)
        self.assertIn("bat species", botanical["not_claim"])

    def test_shadow_no_partner_gain_is_preserved(self):
        shadow = self.claims["SHADOW_LINKED_FRUIT_IDENTITY"]
        self.assertLess(shadow["mean_linked_minus_generic_auc"], 0.0)
        self.assertLess(shadow["mean_linked_minus_rewired_auc"], 0.0)
        self.assertEqual(shadow["n_fitted"], 49)

    def test_bat_individuality_not_called_spatial_partition(self):
        bat = self.claims["WILD_VERTICAL_IDENTITY"]
        self.assertEqual(bat["n_tropical_terrain_positive"], 4)
        self.assertEqual(bat["n_spatial_excess_positive"], 0)
        self.assertIn("true physical separation", bat["not_claim"])

    def test_no_frozen_manuscript_or_parent_main_overwrite(self):
        self.assertFalse(self.data["changes_to_frozen_bat_manuscripts"])
        self.assertFalse(self.data["changes_to_esdm_main"])


if __name__ == "__main__":
    unittest.main()
