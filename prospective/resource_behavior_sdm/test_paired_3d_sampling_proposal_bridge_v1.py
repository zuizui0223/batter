"""Known-truth compatibility of M0–M3 with independent q-sampled 3D controls.

No actual bat, flower or GPS data. This audit tests the label likelihood
p_observed / q for a specific case-control riskset sampling protocol, not
Klappstein et al. 2026's entire continuous 3D-SSF proposal model.
"""
from __future__ import annotations
from copy import deepcopy
import math
import random
import unittest

from paired_3d_ssf_resource_benchmark_v1 import (
    LEVELS, evaluate, fit, score_event, validate_risksets
)
from test_paired_3d_ssf_resource_benchmark_v1 import simulated


FLAGS = (
    "controls_independently_sampled_from_q",
    "proposal_distribution_known_or_training_fitted",
    "reference_measure_source_supported",
    "proposal_positive_over_target_support_verified",
    "sampling_frozen_for_all_nested_models",
)


def _draw_index(rng, probs):
    cut = rng.random()
    for i, p in enumerate(probs):
        cut -= p
        if cut <= 0:
            return i
    return len(probs) - 1


def known_q_sampled(world="resource_agl", seed=2201, steps=15, q_strength=2.3):
    """Re-sample *controls* from known q, never modify an observed endpoint."""
    rng = random.Random(seed)
    originals = simulated(world=world, n_bats=8, steps=steps, seed=1834)
    records = []
    for e in originals:
        original_choices = e["choices"]
        site = e["site"]
        exponent = q_strength if site == "s0" else -q_strength
        # Site-specific known q over 6 original cells: q is NOT fit using test
        # labels, and its support includes all 6 target-eligible states.
        field = [math.log1p(c["resource_count"]) * c["agl_m"] / 50
                 for c in original_choices]
        logq = [exponent * f for f in field]
        q0 = [math.exp(x-max(logq)) for x in logq]
        q = [x / sum(q0) for x in q0]
        index = e["observed_choice"]
        entries = [(index, True)] + [
            (_draw_index(rng, q), False) for _ in range(8)]
        rng.shuffle(entries)
        choices = []
        observed = None
        for j, (which, is_observed) in enumerate(entries):
            item = deepcopy(original_choices[which])
            item["reference_mass"] = 1.0 / len(original_choices)
            item["proposal_mass"] = q[which]
            choices.append(item)
            if is_observed:
                observed = j
        out = deepcopy(e)
        out["choices"] = choices
        out["observed_choice"] = observed
        for flag in FLAGS:
            out[flag] = True
        records.append(out)
    return records


def uniform_q_enumerated(steps=5):
    """When q=mu, the offset is exactly zero, even without sampling."""
    rec = simulated(steps=steps)
    for e in rec:
        for c in e["choices"]:
            c["reference_mass"] = 1.0/len(e["choices"])
            c["proposal_mass"] = 1.0/len(e["choices"])
        for flag in FLAGS:
            e[flag] = True
    return rec


class Sampled3DProposalBridgeTests(unittest.TestCase):
    def test_uniform_reference_matches_old_exhaustive_likelihood(self):
        data = uniform_q_enumerated()
        a = evaluate(data, heldout="site")
        b = evaluate(data, heldout="site",
                     sampling_mode="known_q_sampled_controls")
        self.assertEqual(a["n_folds"], 2)
        for name in a["gains_equal_holdout_group_mean"]:
            for component in ("joint", "horizontal", "height_given_horizontal"):
                self.assertAlmostEqual(
                    a["gains_equal_holdout_group_mean"][name][component],
                    b["gains_equal_holdout_group_mean"][name][component],
                    places=12,
                )
        self.assertTrue(b["known_proposal_offset_in_all_nested_models"])
        self.assertFalse(b["vertical_height_marginalization_exact_on_discrete_XYxZ_riskset"])
        self.assertTrue(b["vertical_decomposition_exact_for_matched_sampled_candidate_labels"])

    def test_sampled_q_reuses_same_events_and_recovers_vertical_signal(self):
        data = known_q_sampled(steps=15)
        # Duplicate q-sampled endpoints are legal unlike exhaustive grid mode.
        self.assertTrue(validate_risksets(
            data, sampling_mode="known_q_sampled_controls"))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_XY_HEIGHT_CANDIDATE"):
            validate_risksets(data)
        result = evaluate(data, heldout="site",
                          sampling_mode="known_q_sampled_controls")
        m = result["gains_equal_holdout_group_mean"]
        dz = m["resource_height_M2_minus_M1"]
        self.assertGreater(dz["height_given_horizontal"], 0,
                           str(m))
        self.assertAlmostEqual(
            dz["joint"], dz["horizontal"]+dz["height_given_horizontal"],
            places=11)
        self.assertEqual(result["n_folds"], 2)
        self.assertFalse(result["empirical_resource_height_bat_gain_claim_allowed"])
        self.assertFalse(result["original_source_authenticity_verified_by_this_engine"])
        self.assertNotIn("b0", str(result))
        self.assertEqual(result["sampling_offset"],
                         "log(reference mass)-log(proposal mass)")

    def test_known_q_offset_is_not_redundant_for_selection_scores(self):
        data = known_q_sampled(steps=4)
        a = fit(data, LEVELS["M0_3d_movement_structure"],
                sampling_mode="known_q_sampled_controls")
        b = fit(data, LEVELS["M0_3d_movement_structure"],
                sampling_mode="enumerated_xy_z")
        # The q correction changes heldout conditional label log probability.
        delta = score_event(a, data[0])["joint"]-score_event(b, data[0])["joint"]
        self.assertGreater(abs(delta), .01)

    def test_missing_proposal_or_test_dependent_q_fails_closed(self):
        data = known_q_sampled(steps=4)
        a = deepcopy(data)
        a[0]["choices"][0]["proposal_mass"] = 0.
        with self.assertRaisesRegex(ValueError, "ZERO_Q_REFERENCE_MASS"):
            validate_risksets(a, sampling_mode="known_q_sampled_controls")
        a = deepcopy(data)
        del a[0]["choices"][0]["proposal_mass"]
        with self.assertRaisesRegex(ValueError, "ZERO_Q_REFERENCE_MASS"):
            validate_risksets(a, sampling_mode="known_q_sampled_controls")
        a = deepcopy(data)
        a[0]["proposal_distribution_known_or_training_fitted"] = False
        with self.assertRaisesRegex(ValueError, "STOP_SAMPLED_3D_PROPOSAL"):
            validate_risksets(a, sampling_mode="known_q_sampled_controls")
        with self.assertRaisesRegex(ValueError, "UNKNOWN_3D_CANDIDATE_SAMPLING_MODE"):
            validate_risksets(data, sampling_mode="some_invented_q")

    def test_q_is_not_source_authenticated_by_self_declared_flags(self):
        data = known_q_sampled(steps=3)
        result = evaluate(data, heldout="site",
                          sampling_mode="known_q_sampled_controls")
        self.assertTrue(result["horizontal_component_is_conditional_on_sampled_riskset"])
        self.assertFalse(result["is_regional_species_occupancy_sdm"])
        self.assertFalse(result["original_source_authenticity_verified_by_this_engine"])


if __name__ == "__main__":
    unittest.main()
