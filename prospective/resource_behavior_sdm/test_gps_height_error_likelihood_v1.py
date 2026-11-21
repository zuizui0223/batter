"""Pure synthetic stress tests for GPS height error under 3D M0–M3.

The actual source's true height never enters the fitted models. The original
simulator's latent chosen endpoint is used ONLY to generate an independent
noisy GPS observation, and is then deleted before source admission.
"""
from __future__ import annotations
from copy import deepcopy
import math
import random
import unittest

from gps_height_error_likelihood_v1 import (
    validate_observed_noisy_events, fit_error_aware, score_observed,
    evaluate_error_noise,
)
from paired_3d_ssf_resource_benchmark_v1 import LEVELS
from test_paired_3d_ssf_resource_benchmark_v1 import simulated


def noisy_observations(world="resource_agl",sigma=11.,n_bats=6,steps=9,
                       seed=20261121,heterogeneous=False):
    rng=random.Random(seed)
    input_rows=simulated(world=world,n_bats=n_bats,steps=steps,seed=1834)
    output=[]
    for e in input_rows:
        d=deepcopy(e)
        idx=d.pop("observed_choice")
        chosen=d["choices"][idx]
        # Paired across sigma analyses: random standard-normal deviates have
        # the same deterministic order for all sigma values.
        local_sigma=(sigma*(1.7 if chosen["xy_cell"]=="1" else .6)
                     if heterogeneous else sigma)
        d["observed_xy"]=chosen["xy_cell"]
        d["observed_agl_m"]=chosen["agl_m"]+local_sigma*rng.gauss(0.,1.)
        d["sensor_sigma_m"]=float(local_sigma)
        d["sensor_agl_datum_verified"]=True
        d["sensor_sigma_from_independent_calibration"]=True
        d["candidate_grid_independent_of_test_height"]=True
        d["resource_measured_independently"]=True
        d["fixed_complete_xy_z_support"]=True
        # There is NO accessible latent endpoint or true observation in d.
        output.append(d)
    return output


class GPSKnownNoiseTests(unittest.TestCase):
    def test_observation_model_uses_no_latent_true_height(self):
        rows=noisy_observations(n_bats=4,steps=4)
        self.assertNotIn("observed_choice",str(rows))
        self.assertNotIn("latent_z_truth",str(rows))
        validated=validate_observed_noisy_events(rows)
        self.assertEqual(len(validated),32)
        m=fit_error_aware(rows,LEVELS["M1_add_resource_xy"])
        p=score_observed(m,rows[0])
        self.assertTrue(all(math.isfinite(v) for v in p.values()))
        self.assertAlmostEqual(
            p["joint"],p["horizontal"]+p["height_given_horizontal"],places=10)

    def test_same_continuous_gps_target_for_noise_aware_and_hard_bin(self):
        rows=noisy_observations(steps=8)
        result=evaluate_error_noise(rows,holdout="site")
        self.assertEqual(result["n_holdout_groups"],2)
        self.assertEqual(result["n_fictional_or_source_bats"],6)
        self.assertEqual(result["n_observed_events"],96)
        self.assertFalse(result["empirical_3d_resource_height_gain_claim_allowed"])
        self.assertFalse(result["q_sampled_control_correction_integrated"])
        self.assertFalse(result["true_regional_horizontal_species_sdm_estimated"])
        gains=result["group_equal_gains_nats_per_recorded_fix"]
        self.assertIn("M2_resource_by_height_minus_M1_add_resource_xy",gains)
        self.assertEqual(set(gains["M2_resource_by_height_minus_M1_add_resource_xy"]),
                         {"sensor_aware","hard_bin_naive"})
        for fold in result["fold_aggregates_without_identifying_keys"]:
            for values in fold["per_model_scores"].values():
                for d in values.values():
                    self.assertAlmostEqual(d["joint"],
                                           d["horizontal"]+d["height_given_horizontal"],
                                           places=10)

    def test_near_exact_sensor_gps_is_mathematically_well_defined(self):
        rows=noisy_observations(sigma=.5,steps=4)
        result=evaluate_error_noise(rows,holdout="site")
        self.assertEqual(result["sensor_sd_values_m"],[.5])
        g=result["group_equal_gains_nats_per_recorded_fix"]
        for pair in g.values():
            for method in pair.values():
                for value in method.values():
                    self.assertTrue(math.isfinite(value))

    def test_height_error_in_different_xy_cannot_be_relabelled_true_height(self):
        rows=noisy_observations(sigma=11.,heterogeneous=True,steps=4)
        result=evaluate_error_noise(rows,holdout="site")
        self.assertEqual(result["sensor_sd_values_m"],[6.6,18.7])
        self.assertFalse(result["empirical_3d_resource_height_gain_claim_allowed"])

    def test_source_gates_stop_missing_calibration_or_response_leakage(self):
        base=noisy_observations(n_bats=4,steps=4)
        def violates(change,pattern):
            d=deepcopy(base)
            change(d[0])
            with self.assertRaisesRegex(ValueError,pattern):
                validate_observed_noisy_events(d)
        violates(lambda x:x.update(sensor_sigma_m=0),
                 "UNCALIBRATED_HEIGHT_OBSERVATION")
        violates(lambda x:x.update(sensor_sigma_from_independent_calibration=False),
                 "UNVERIFIED_SENSOR")
        violates(lambda x:x.update(sensor_agl_datum_verified=False),
                 "UNVERIFIED_SENSOR")
        violates(lambda x:x.update(observed_choice=1),
                 "LATENT_TRUE_HEIGHT_LEAKS")
        violates(lambda x:x["choices"][0].update(is_control_built_from_test_endpoint=True),
                 "TEST_OBSERVED_HEIGHT_USED_FOR_CANDIDATES")
        violates(lambda x:x["choices"][1].update(resource_count=999),
                 "HEIGHT_DEFINED_RESOURCE_COVARIATE")
        d=deepcopy(base)
        d[0]["state_annotation_height_blind"]=False
        with self.assertRaisesRegex(ValueError,"STATE_USES_RESPONSE_HEIGHT"):
            validate_observed_noisy_events(d,include_state=True)


if __name__=="__main__":
    unittest.main()
