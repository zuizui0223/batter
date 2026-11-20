"""Known-truth checks for strict match gate; no original animal outcomes."""
import json
import unittest
from pathlib import Path
from source_join_gate_v2 import FIELDS, READY, audit_registry, gate_source


class SourceJoinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(Path(__file__).with_name(
            "source_join_registry_v2.json").read_text(encoding="utf-8"))

    def test_every_real_candidate_fails_at_least_one_unverified_input(self):
        result = audit_registry(self.registry)
        self.assertEqual(result["candidate_count"], 7)
        self.assertEqual(result["strict_ready_count"], 0)
        self.assertIsNone(result["claimed_ecological_gain"])
        self.assertTrue(all(r["all_stop_reasons"] for r in result["decisions"]))

    def test_congo_cameroon_same_species_never_joined(self):
        x = self.registry["forbidden_cross_source_pair"]
        self.assertEqual(x["left"], "hmon_congo_2020")
        self.assertEqual(x["right"], "hmon_cameroon_lidar_2022_2023")
        self.assertIn("Different countries", x["reason"])

    def test_nyctalus_matched_habitat_is_not_measured_food(self):
        row = next(r for r in self.registry["sources"] if r["id"] == "nyctalus_noctula_rsf")
        self.assertTrue(row["flags"]["verified_same_event_join"])
        self.assertTrue(row["flags"]["vertical_height_verified"])
        self.assertFalse(row["flags"]["independent_time_aligned_food_supply"])
        self.assertIn("STOP_NO_INDEPENDENT_FOOD_SUPPLY", gate_source(row)["all_stop_reasons"])

    def test_new_cactus_candidate_is_source_blocked_and_height_visit_leakage_stops(self):
        row = next(x for x in self.registry["sources"]
                   if x["id"]=="leptonycteris_cactus_goldshtein_2020")
        self.assertTrue(row["flags"]["same_population"])
        self.assertFalse(row["flags"]["original_bat_rows_authenticated_and_opened"])
        self.assertFalse(row["flags"]["behavior_label_independent_of_height"])
        self.assertIn("STOP_NO_INDEPENDENT_BEHAVIOR_LABEL",
                      gate_source(row)["all_stop_reasons"])
        self.assertIn("STOP_NO_VERIFIED_HEIGHT",
                      gate_source(row)["all_stop_reasons"])

    def test_missing_or_non_boolean_flags_stop(self):
        c = {"id":"toy", "flags": {name:True for name,_ in FIELDS}}
        self.assertEqual(gate_source(c)["status"], READY)
        c["flags"]["same_population"] = "yes"
        with self.assertRaises(TypeError):
            gate_source(c)
        del c["flags"]["same_population"]
        with self.assertRaises(ValueError):
            gate_source(c)

    def test_duplicate_sources_and_promoted_gain_rejected(self):
        x = dict(self.registry)
        x["sources"] = self.registry["sources"] + [self.registry["sources"][0]]
        with self.assertRaises(ValueError):
            audit_registry(x)
        x = dict(self.registry)
        x["real_joint_3d_resource_effect"] = 0.10
        with self.assertRaises(ValueError):
            audit_registry(x)

    def test_prior_evidence_kinematic_gates_are_not_food_gains(self):
        evidence=json.loads(Path(__file__).with_name(
            "behavioral_positive_extension_v2.json").read_text(encoding="utf-8"))
        claims={e["id"]:e for e in evidence["evidence"]}
        self.assertEqual(claims["SPEED_TURN_5"]["positive"], 5)
        self.assertEqual(claims["FINE_PLACE_SPEED_TURN_4"]["positive"], 4)
        self.assertEqual(claims["PHASE_SPEED_TURN_4"]["positive"], 3)
        self.assertEqual(claims["PATCH_FIDELITY_FAIL"]["positive"], 0)
        self.assertIsNone(evidence["primary_ecological_5d_resource_gain"])


if __name__=="__main__":
    unittest.main()
