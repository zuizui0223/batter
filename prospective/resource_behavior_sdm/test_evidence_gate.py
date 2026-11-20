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

    def test_independent_external_originals_do_not_become_5d_ecology(self):
        a=self.data["independent_external_evidence_progress_20261120"]
        self.assertEqual(len(a["candidates"]),2)
        self.assertFalse(a["live_source_crossstudy_join_allowed"])
        self.assertIsNone(a["real_highdimensional_resource_behavior_height_effect"])
        self.assertTrue(all(x["original_metadata_verified"] for x in a["candidates"]))
        self.assertTrue(all(not x["original_file_content_read"] for x in a["candidates"]))
        self.assertTrue(all(x["original_file_http_error"]==401 for x in a["candidates"]))

    def test_ducke_food_positive_is_only_source_local_guild(self):
        d={r["id"]:r for r in self.data["claims"]}["DUCKE_MEASURED_FOOD_LOCAL_GUILD_PREDICTION"]
        self.assertEqual(d["n_matched_plots"],46)
        self.assertEqual(d["n_same_site_same_day_nights"],103)
        self.assertGreater(d["heldout_food_12_minus_baseline_nats_per_capture"],0)
        self.assertIn("SOURCE_LOCAL_EXPLORATORY",d["tier"])
        self.assertIn("not occupancy",d["response"])
        self.assertTrue(d["source_anomalies"]["missing_vegetation_clutter"])
        self.assertIsNone(self.data["strict_unestimated"]["ecological_partner_m3_minus_m1"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_ducke_specificity_v2_never_promotes_to_causal_resource_height(self):
        d={r["id"]:r for r in self.data["claims"]}["DUCKE_MEASURED_FOOD_LOCAL_GUILD_PREDICTION"]
        r=d["source_specificity_v2"]
        self.assertGreater(r["frugivore"]["both_separate_fruit_axes_minus_baseline"],0)
        self.assertGreater(r["frugivore"]["food12_given_remaining10"],0)
        self.assertGreater(r["gleaning_animalivore"]["remaining10_given_food12"],0)
        self.assertFalse(r["true_independent_nonfood_negative_control"])
        self.assertFalse(r["adjusted_for_paper_vegetation_clutter"])
        self.assertFalse(r["independent_external_replication"])
        self.assertIsNone(r["causal_plant_diet_selection_effect"])
        self.assertIsNone(r["empirical_resource_conditioned_flight_height_gain"])
        self.assertIsNone(self.data["strict_unestimated"]["ecological_partner_m3_minus_m1"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_no_frozen_manuscript_or_parent_main_overwrite(self):
        self.assertFalse(self.data["changes_to_frozen_bat_manuscripts"])
        self.assertFalse(self.data["changes_to_esdm_main"])


if __name__ == "__main__":
    unittest.main()
