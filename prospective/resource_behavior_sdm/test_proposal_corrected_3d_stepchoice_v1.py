"""Pure synthetic matched 3D proposal sampling audit; NO original bat rows."""
import math
import random
import unittest
from copy import deepcopy

from proposal_corrected_3d_stepchoice_v1 import (
    validate, crossvalidate, fit,
)


def _draw(rng, mass):
    u = rng.random()
    for i, p in enumerate(mass):
        u -= p
        if u <= 0:
            return i
    return len(mass) - 1


def simulate(n_bats=16, nights=2, steps=35, ncontrols=8,
             true_beta=0.0, seed=119, variable_proposals=True):
    rng = random.Random(seed)
    events = []
    for bat in range(n_bats):
        site = "A" if bat < n_bats // 2 else "B"
        alpha = (2.2 if site == "A" else -2.2) if variable_proposals else 2.2
        for night in range(nights):
            for step in range(steps):
                # 4 XY resource patches x 3 height bins in each patch.
                resources = [rng.uniform(.15, 2.5) for _ in range(4)]
                features = [math.log1p(resources[x]) * (z - 1)
                            for x in range(4) for z in range(3)]
                reference = [1.0 / len(features)] * len(features)
                praw = [math.exp(true_beta * f) for f in features]
                p = [v / sum(praw) for v in praw]
                qraw = [math.exp(alpha * f) for f in features]
                q = [v / sum(qraw) for v in qraw]
                observed = _draw(rng, p)
                # One actual simulated observation from target p, 8 controls
                # independently from proposal q. Tag observed index even when
                # a q-sampled control duplicates an endpoint's state.
                sampled = [(observed, 1)] + [(_draw(rng, q), 0)
                                             for _ in range(ncontrols)]
                rng.shuffle(sampled)
                idx = next(i for i, (_, flag) in enumerate(sampled) if flag)
                choices = [{
                    "resource_height_feature": features[k],
                    "reference_mass": reference[k],
                    "proposal_mass": q[k],
                } for k, _ in sampled]
                events.append({
                    "bat": "fictional_%d" % bat, "site": site,
                    "night": "night_%d" % night, "step": "step_%d" % step,
                    "choices": choices, "observed_choice": idx,
                    "proposal_fitted_on_training_only_or_external": True,
                    "controls_independent_of_observed_endpoint": True,
                    "reference_measure_prespecified": True,
                })
    return events


class KnownTruthProposalTests(unittest.TestCase):
    def test_per_source_validated_minimum(self):
        event = simulate(steps=4)
        self.assertEqual(len(validate(event)), 128)
        bad = deepcopy(event)
        bad[0]["controls_independent_of_observed_endpoint"] = False
        with self.assertRaisesRegex(ValueError, "PROPOSAL_PROVENANCE"):
            validate(bad)
        bad = deepcopy(event)
        bad[0]["choices"][0]["proposal_mass"] = 0.0
        with self.assertRaisesRegex(ValueError, "POSITIVE_PROPOSAL"):
            validate(bad)

    def test_different_proposals_make_naive_transfer_fail(self):
        r = crossvalidate(simulate(), holdout="site")
        self.assertEqual(r["n_folds"], 2)
        self.assertAlmostEqual(
            r["mean_corrected_minus_naive_log_score"], 2.424102403912198, places=5)
        self.assertFalse(r["is_full_ssf3d_reproduction"])
        self.assertFalse(r["resource_causality_or_field_bat_effect_estimated"])
        self.assertNotIn("fictional_", str(r))
        self.assertAlmostEqual(
            r["fold_aggregates_without_bat_site_IDs"][0][
                "corrected_minus_naive_log_score"], 2.3904026618006586, places=5)

    def test_proposal_biased_null_falsely_infers_effect(self):
        data = simulate(variable_proposals=False)
        corrected = fit(data, corrected=True)
        uncorrected = fit(data, corrected=False)
        self.assertLess(abs(corrected), .35)
        self.assertGreater(abs(uncorrected), 1.0)
        self.assertLess(abs(corrected), abs(uncorrected))

    def test_nonzero_real_simulated_effect_recovers_coefficient(self):
        data = simulate(true_beta=.95)
        corrected = fit(data, corrected=True)
        self.assertGreater(corrected, .35)
        self.assertLess(corrected, 1.6)
        r = crossvalidate(data, holdout="site")
        self.assertAlmostEqual(r["mean_corrected_minus_naive_log_score"],
                               2.1199348473405006, places=5)


if __name__ == "__main__":
    unittest.main()
