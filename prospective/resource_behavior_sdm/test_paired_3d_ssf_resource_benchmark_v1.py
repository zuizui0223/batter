"""Synthetic known-truth tests ONLY; no Goldshtein or other animal rows."""
import math
import random
import unittest
from copy import deepcopy
from paired_3d_ssf_resource_benchmark_v1 import (
    LEVELS, score_event, validate_risksets, evaluate, fit,
)


def simulated(world="resource_agl", n_bats=8, steps=15, seed=1834, dated=False):
    rng = random.Random(seed)
    result = []
    for bat in range(n_bats):
        for night in range(2):
            for step in range(steps):
                state = (step + night) % 2
                # Nuisance environment partly correlated with prey.
                if world == "unmeasured_habitat_proxy":
                    # Latent quality causes BOTH insect/plant proxy and true use.
                    latent = (rng.uniform(-1, 1), rng.uniform(-1, 1))
                    resources = tuple(
                        max(0.0, math.exp(0.9 + 1.1 * q + rng.uniform(-.15, .15)) - 1)
                        for q in latent
                    )
                else:
                    latent = (0.0, 0.0)
                    r0 = rng.uniform(0.0, 3.0)
                    r1 = rng.uniform(0.0, 3.0)
                    resources = (r0, r1)
                choices = []
                logits = []
                for xy in range(2):
                    for zi, z in enumerate((10.0, 40.0, 90.0)):
                        forest = (1.0 if xy else 0.0) + rng.uniform(-.15, .15)
                        move = 25 + xy * 5 + zi * 4 + rng.uniform(-4, 4)
                        c = {
                            "xy_cell": str(xy), "z_level": str(zi),
                            "step_m": move,
                            "cos_turn": 0.15 + xy * .3 + rng.uniform(-.2, .2),
                            "omega_delta": zi * .15,
                            "forest_structure": forest,
                            "agl_m": z,
                            "resource_count": resources[xy],
                            "is_control_built_from_test_endpoint": False,
                        }
                        choices.append(c)
                        score = 0.4 * forest - 0.012 * move - 0.10 * z / 50
                        if world == "resource_xy":
                            score += 2.0 * math.log1p(resources[xy])
                        elif world == "resource_agl":
                            score += 2.8 * math.log1p(resources[xy]) * z / 50
                        elif world == "resource_agl_state":
                            score += (3.5 if state == 1 else -3.5) * \
                                     math.log1p(resources[xy]) * z / 50
                        elif world == "unmeasured_habitat_proxy":
                            # World definition: hidden habitat -> resource proxy,
                            # hidden habitat -> horizontal and vertical selection;
                            # NO direct arrow resource -> animal behavior.
                            score += 2.0 * latent[xy] + 2.5 * latent[xy] * z / 50
                        elif world != "null":
                            raise ValueError("unknown test world")
                        logits.append(score)
                probs = [math.exp(v - max(logits)) for v in logits]
                threshold = rng.random() * sum(probs)
                obs = len(probs) - 1
                for j, weight in enumerate(probs):
                    threshold -= weight
                    if threshold <= 0:
                        obs = j
                        break
                result.append({
                    "bat": "b%d" % bat,
                    "night": "n%d" % night,
                    "site": "s%d" % (bat % 2),
                    "step": "k%d" % step,
                    "observed_choice": obs,
                    "choices": choices,
                    "original_fix": True,
                    "height_agl_verified": True,
                    "regular_interval_verified": True,
                    "riskset_outcome_independent": True,
                    "candidate_sampling_frozen": True,
                    "resource_independent_of_tracking": True,
                    "resource_kind": ("dated_measured_flower" if dated
                                      else "cactus_location_proxy"),
                    "state_context": state,
                    "state_annotation_height_blind": True,
                    "resource_same_night_observed": dated,
                    "resource_no_simulated_imputation": dated,
                    "resource_survey_effort_verified": dated,
                })
    return result


class Paired3DResourceSSFKnownTruthTests(unittest.TestCase):
    def test_frozen_null_world_rejects_automatic_resource_gain(self):
        out = evaluate(simulated("null"), heldout="bat")
        g = out["gains_equal_holdout_group_mean"]
        self.assertAlmostEqual(g["resource_main_M1_minus_M0"]["horizontal"],
                               -0.002508923738964247, places=5)
        self.assertLess(g["resource_height_M2_minus_M1"]["height_given_horizontal"], 0)

    def test_hidden_habitat_generates_false_causal_resource_height_conclusion(self):
        out = evaluate(simulated("unmeasured_habitat_proxy"), heldout="bat")
        gain = out["gains_equal_holdout_group_mean"]
        self.assertAlmostEqual(
            gain["resource_main_M1_minus_M0"]["horizontal"], 0.3116959335634489,
            places=5)
        self.assertAlmostEqual(
            gain["resource_height_M2_minus_M1"]["height_given_horizontal"],
            0.1541523358834193, places=5)
        # Fitted associations CAN predict but NEVER establish direct food use.
        self.assertFalse(out["empirical_resource_height_bat_gain_claim_allowed"])

    def test_discrete_horizontal_projection_is_exact(self):
        data = simulated(steps=4)
        model = fit(data[20:], LEVELS["M2_resource_by_height"])
        scores = score_event(model, data[0])
        self.assertAlmostEqual(scores["mass_sum"], 1.0, places=12)
        self.assertAlmostEqual(
            scores["joint"],
            scores["horizontal"] + scores["height_given_horizontal"],
            places=12,
        )

    def test_resource_height_world_improves_heldout_vertical_score(self):
        out = evaluate(simulated("resource_agl"), heldout="bat")
        gain = out["gains_equal_holdout_group_mean"]["resource_height_M2_minus_M1"]
        self.assertGreater(gain["height_given_horizontal"], 0)
        self.assertGreater(gain["joint"], 0)
        self.assertAlmostEqual(gain["height_given_horizontal"], 0.03901653396497237, places=5)
        self.assertAlmostEqual(
            gain["joint"], gain["horizontal"] + gain["height_given_horizontal"], places=11)
        self.assertFalse(out["empirical_resource_height_bat_gain_claim_allowed"])
        self.assertFalse(out["is_regional_species_occupancy_sdm"])
        self.assertEqual(out["n_unique_bats"], 8)
        self.assertNotIn("b0", str(out))

    def test_resource_xy_gives_horizontal_gain(self):
        out = evaluate(simulated("resource_xy"), heldout="bat")
        gain = out["gains_equal_holdout_group_mean"]["resource_main_M1_minus_M0"]
        self.assertGreater(gain["horizontal"], 0)
        self.assertGreater(gain["joint"], 0)
        self.assertAlmostEqual(gain["horizontal"], 0.09653327525365989, places=5)

    def test_state_change_only_if_height_blind(self):
        data = simulated("resource_agl_state")
        out = evaluate(data, heldout="bat", include_state=True)
        gain = out["gains_equal_holdout_group_mean"]["state_interactions_M3_minus_M2"]
        self.assertGreater(gain["joint"], 0)
        self.assertAlmostEqual(gain["height_given_horizontal"], 0.46475676298846086, places=5)
        bad = deepcopy(data)
        bad[0]["state_annotation_height_blind"] = False
        with self.assertRaisesRegex(ValueError, "STATE_DERIVED_FROM_HEIGHT"):
            evaluate(bad, heldout="bat", include_state=True)

    def test_direct_flowers_require_observed_matching_date(self):
        data = simulated(dated=False, steps=3)
        with self.assertRaisesRegex(ValueError, "DATED_DIRECT_FLOWER_SURVEY_JOIN"):
            evaluate(data, require_dated_flower=True)
        data = simulated(dated=True, steps=3)
        self.assertTrue(validate_risksets(data, require_dated_flower=True))
        out = evaluate(data, require_dated_flower=True)
        self.assertFalse(out["empirical_resource_height_bat_gain_claim_allowed"])
        data[0]["resource_no_simulated_imputation"] = False
        with self.assertRaisesRegex(ValueError, "DATED_DIRECT_FLOWER_SURVEY_JOIN"):
            evaluate(data, require_dated_flower=True)

    def test_unsafe_controls_and_xy_resource_height_leakage_fail(self):
        data = simulated(steps=3)
        bad = deepcopy(data)
        bad[0]["choices"][0]["is_control_built_from_test_endpoint"] = True
        with self.assertRaisesRegex(ValueError, "RESPONSE_LEAKING_CONTROL"):
            evaluate(bad)
        bad = deepcopy(data)
        del bad[0]["choices"][2]
        if bad[0]["observed_choice"] >= 2:
            bad[0]["observed_choice"] -= 1
        with self.assertRaisesRegex(ValueError, "UNBALANCED_XY_BY_Z"):
            evaluate(bad)
        bad = deepcopy(data)
        bad[0]["choices"][1]["resource_count"] += 5
        with self.assertRaisesRegex(ValueError, "XY_RESOURCE_CHANGES_WITH_CANDIDATE_HEIGHT"):
            evaluate(bad)
        bad = deepcopy(data)
        bad[0]["resource_independent_of_tracking"] = False
        with self.assertRaisesRegex(ValueError, "SOURCE_PROVENANCE"):
            evaluate(bad)

    def test_whole_night_and_site_holdouts(self):
        data = simulated(steps=3)
        by_night = evaluate(data, heldout="bat_night")
        self.assertEqual(by_night["n_folds"], 16)
        by_site = evaluate(data, heldout="site")
        self.assertEqual(by_site["n_folds"], 2)
        one_site = deepcopy(data)
        for row in one_site:
            row["site"] = "one_site"
        with self.assertRaisesRegex(ValueError, "FEWER_THAN_TWO_HELDOUT_BLOCKS"):
            evaluate(one_site, heldout="site")


if __name__ == "__main__":
    unittest.main()
