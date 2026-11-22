"""Noisy GPS altitude + independently sampled q candidate integration tests.

All source data here are fictional. Latent chosen altitude is deleted before
q controls are sampled, and candidate proposals depend only on predeclared
world/XY/source-q—not the observed continuous GPS altitude.
"""
from __future__ import annotations

from copy import deepcopy
import math
import random
import unittest

from gps_height_error_likelihood_v1 import (
    evaluate_error_noise, score_observed
)
from paired_3d_ssf_resource_benchmark_v1 import LEVELS
from q_stratified_noisy_height_bridge_v1 import (
    attach_mc_log_weights, compare_q_noise, validate_q_noisy_events
)
from test_gps_height_error_likelihood_v1 import noisy_observations


def _pick(rng, probs):
    u = rng.random()
    for j, p in enumerate(probs):
        u -= p
        if u <= 0:
            return j
    return len(probs)-1


def q_sampled_noisy(world="resource_agl", n_bats=6, steps=4,
                    n_per_xy=24, seed=889, source_q_shift=1.7,
                    uniform_complete=False):
    records = noisy_observations(world=world, n_bats=n_bats,
                                 steps=steps, sigma=11., seed=20261121)
    rng = random.Random(seed)
    result = []
    for e in records:
        rows = {}
        for c in e["choices"]:
            rows.setdefault(c["xy_cell"], []).append(c)
        new = deepcopy(e)
        new["reference_xy_mass"] = {xy:1./len(rows) for xy in rows}
        new["z_support_by_xy"] = {}
        all_controls = []
        for xy, original in sorted(rows.items()):
            source_site = e["site"]
            sign = 1. if source_site == "s0" else -1.
            # q(z|xy) tilts toward resource×z; q is independent
            # of actual selected endpoint and measured noisy GPS y.
            f = [math.log1p(c["resource_count"]) * c["agl_m"]/50.
                 for c in original]
            if uniform_complete:
                q = [1./len(original)] * len(original)
            else:
                logits = [sign * source_q_shift * v for v in f]
                weights = [math.exp(v-max(logits)) for v in logits]
                q = [v/sum(weights) for v in weights]
            new["z_support_by_xy"][xy] = [
                {"z_level":c["z_level"],
                 "mu_z":1./len(original), "q_z":q[i]}
                for i,c in enumerate(original)]
            selected = (list(range(len(original))) if uniform_complete
                        else [_pick(rng, q) for _ in range(n_per_xy)])
            for k in selected:
                c = deepcopy(original[k])
                c["proposal_z_prob"] = q[k]
                c["reference_z_prob"] = 1./len(original)
                all_controls.append(c)
        new["choices"] = all_controls
        new["sampled_controls_independent_of_recorded_height_xy"] = True
        new["q_known_externally_or_fit_using_training_only"] = True
        new["reference_support_frozen_before_response"] = True
        result.append(new)
    return result


class NoisyKnownQBridgeTests(unittest.TestCase):
    def test_complete_uniform_support_reproduces_gaussian_enumerated_model(self):
        complete = noisy_observations(n_bats=6,steps=3,sigma=11.)
        sampled = q_sampled_noisy(
            n_bats=6,steps=3,uniform_complete=True)
        self.assertTrue(validate_q_noisy_events(sampled)[0])
        a = evaluate_error_noise(complete,holdout="site")
        b = compare_q_noise(sampled,heldout="site")
        for model in b["model_names"]:
            old = [f["per_model_scores"][model]["sensor_aware"]
                   for f in a["fold_aggregates_without_identifying_keys"]]
            new = [f["scores"][model]["corrected_importance"]
                   for f in b["folds_without_original_group_keys"]]
            for x,y in zip(old,new):
                for field in ("joint","horizontal","height_given_horizontal"):
                    self.assertAlmostEqual(x[field],y[field],places=7)
        self.assertTrue(b["same_noisy_heldout_events_in_all_models"])
        self.assertFalse(b["empirical_bat_ecology_claim_allowed"])

    def test_nonuniform_q_controls_allow_duplicates_and_match_noisy_obs(self):
        sampled = q_sampled_noisy(n_bats=6,steps=4,n_per_xy=24)
        validated, d = validate_q_noisy_events(sampled)
        self.assertEqual(len(validated),48)
        self.assertGreater(min(x["min_effective_sample_fraction"] for x in d),0)
        result = compare_q_noise(sampled,heldout="site")
        self.assertEqual(result["n_folds"],2)
        self.assertEqual(result["n_source_free_events"],48)
        self.assertFalse(result["source_original_file_access_verified"])
        self.assertTrue(result["not_observed_choice_vs_controls_label_likelihood"])
        self.assertTrue(result["finite_mc_self_normalized_biased"])
        self.assertIsNone(result["real_resource_height_joint_bat_gain"])
        for model_scores in result["per_model_group_equal_scores"].values():
            for v in model_scores.values():
                self.assertAlmostEqual(v["joint"],
                    v["horizontal"]+v["height_given_horizontal"],places=9)
        changed = abs(result["per_model_group_equal_scores"]
                      ["M0_3d_movement_structure"]["corrected_importance"]["joint"]-
                      result["per_model_group_equal_scores"]
                      ["M0_3d_movement_structure"]["uncorrected_q_sampling"]["joint"])
        self.assertGreater(changed,1e-4)

    def test_large_q_sample_approaches_exact_grid_when_coefficients_fixed(self):
        e=noisy_observations(n_bats=6,steps=3,sigma=11.)[0]
        data=q_sampled_noisy(n_bats=6,steps=3,n_per_xy=1500)
        noisy=data[0]
        model={"fields":LEVELS["M0_3d_movement_structure"],
               "center":[0.]*len(LEVELS["M0_3d_movement_structure"]),
               "scale":[1.]*len(LEVELS["M0_3d_movement_structure"]),
               "beta":[0.]*len(LEVELS["M0_3d_movement_structure"])}
        truth=score_observed(model,e)
        correct=score_observed(model,attach_mc_log_weights([noisy],True)[0])
        naive=score_observed(model,attach_mc_log_weights([noisy],False)[0])
        self.assertLess(abs(correct["joint"]-truth["joint"]),.1)
        self.assertGreater(abs(naive["joint"]-truth["joint"]),.1)

    def test_q_zero_missing_support_and_response_leakage_fail_closed(self):
        base=q_sampled_noisy(n_bats=6,steps=3)
        bad=deepcopy(base)
        bad[0]["z_support_by_xy"]["0"][0]["q_z"]=0.
        with self.assertRaisesRegex(ValueError,"NO_POSITIVE_SUPPORT"):
            validate_q_noisy_events(bad)
        bad=deepcopy(base)
        bad[0]["choices"][0]["proposal_z_prob"]=0.
        with self.assertRaisesRegex(ValueError,"CANDIDATE_DENSITY_DISAGREES"):
            validate_q_noisy_events(bad)
        bad=deepcopy(base)
        bad[0]["observed_choice"]=3
        with self.assertRaisesRegex(ValueError,"LATENT_HEIGHT_OR_LABEL_LEAKAGE"):
            validate_q_noisy_events(bad)
        bad=deepcopy(base)
        bad[0]["sampled_controls_independent_of_recorded_height_xy"]=False
        with self.assertRaisesRegex(ValueError,"SOURCE_SENSOR_OR_PROPOSAL_PROVENANCE"):
            validate_q_noisy_events(bad)
        bad=deepcopy(base)
        bad[0]["choices"][0]["log_sampling_weight"]=0.
        with self.assertRaisesRegex(ValueError,"SUPPLIED_UNVERIFIED_WEIGHT"):
            validate_q_noisy_events(bad)
        bad=deepcopy(base)
        bad[0]["sensor_sigma_m"]=0
        with self.assertRaisesRegex(ValueError,"UNCALIBRATED_CONTINUOUS_AGL"):
            validate_q_noisy_events(bad)
        bad=deepcopy(base)
        bad[0]["resource_kind"]="dated_measured_flower"
        with self.assertRaisesRegex(ValueError,"NO_TRUE_DATED_FLOWER_SURVEY"):
            validate_q_noisy_events(bad)

    def test_q_method_is_not_mislabelled_as_animal_range_or_continuous_ssf(self):
        result=compare_q_noise(
            q_sampled_noisy(n_bats=6,steps=3,n_per_xy=16),
            heldout="site")
        self.assertFalse(result["not_reproduced_continuous_ssf3d"] is False)
        self.assertFalse(result["source_original_file_access_verified"])
        self.assertFalse(result["empirical_bat_ecology_claim_allowed"])


if __name__=="__main__":
    unittest.main()
