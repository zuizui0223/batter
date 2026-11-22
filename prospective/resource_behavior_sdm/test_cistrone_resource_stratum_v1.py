"""Synthetic contracts for source-local, whole-plot stratum prediction."""
import copy
import math
import unittest

import cistrone_resource_stratum_v1 as c


def fixture(n=12, signal=True):
    rows = []
    for i in range(n):
        high = i % 2 == 0
        food = [3, 80] if high else [80, 3]
        passes = ([10, 90] if high else [90, 10]) if signal else [40, 60]
        rows.append({
            "plot_id": "artificial_%02d" % i,
            "passes": passes,
            "baseline": [0.0, 7.0, 40.0, 30.0, 20.0],
            "resources": {"total": food,
                          "lepidoptera": [x // 2 for x in food],
                          "diptera": [x // 3 for x in food]},
        })
    return rows


class SourceContracts(unittest.TestCase):
    def test_zero_pass_plot_retained_in_coverage_only(self):
        rows = fixture()
        rows[0]["passes"] = [0, 0]
        valid, audit = c.validate_plots(rows)
        self.assertEqual(len(valid), 11)
        self.assertEqual(audit["source_plots"], 12)
        self.assertEqual(audit["zero_pass_plots_excluded_from_conditional_score"], 1)

    def test_zero_resource_count_is_valid(self):
        rows = fixture()
        for name in rows[0]["resources"]:
            rows[0]["resources"][name][0] = 0
        valid, _ = c.validate_plots(rows)
        self.assertEqual(len(valid), len(rows))
        self.assertTrue(all(math.isfinite(x) for x in c.raw_features(rows[0], "orders")))

    def test_duplicate_plot_rejected(self):
        rows = fixture()
        rows.append(copy.deepcopy(rows[0]))
        with self.assertRaises(ValueError):
            c.validate_plots(rows)

    def test_bad_counts_and_covariates_rejected(self):
        for value in (-1, 1.2, True, None, float("nan"), "5"):
            for key in ("passes", "resources"):
                with self.subTest(value=value, field=key):
                    rows = fixture()
                    if key == "passes":
                        rows[0]["passes"][0] = value
                    else:
                        rows[0]["resources"]["total"][0] = value
                    with self.assertRaises(ValueError):
                        c.validate_plots(rows)
        for value in (None, True, float("inf"), float("nan"), "7"):
            rows = fixture()
            rows[0]["baseline"][1] = value
            with self.assertRaises(ValueError):
                c.validate_plots(rows)

    def test_subgroup_counts_cannot_exceed_total(self):
        rows = fixture()
        rows[0]["resources"]["diptera"][0] = rows[0]["resources"]["total"][0] + 1
        with self.assertRaises(ValueError):
            c.validate_plots(rows)

    def test_invalid_shapes_and_models_rejected(self):
        for key, bad in (("passes", [10]), ("baseline", [1, 2]), ("resources", {})):
            rows = fixture()
            rows[0][key] = bad
            with self.assertRaises(ValueError):
                c.validate_plots(rows)
        with self.assertRaises(ValueError):
            c.fit_model(fixture(), "post_outcome_variant")

    def test_fit_does_not_silently_drop_zero_plot(self):
        rows = fixture()
        rows[0]["passes"] = [0, 0]
        with self.assertRaises(ValueError):
            c.fit_model(rows, "baseline")


class PredictiveContracts(unittest.TestCase):
    def test_known_resource_signal_predicts_new_plots(self):
        result = c.cross_validate(fixture())
        self.assertGreater(result["summary"]["total"]["mean_gain"], 0.15)
        self.assertGreater(result["summary"]["orders"]["mean_gain"], 0.15)

    def test_constant_resource_adds_no_information(self):
        rows = fixture()
        for row in rows:
            row["resources"] = {"total": [5, 9], "lepidoptera": [2, 4], "diptera": [2, 3]}
        result = c.cross_validate(rows)
        for name in ("total", "orders"):
            self.assertAlmostEqual(result["summary"][name]["mean_gain"], 0.0, places=11)

    def test_one_plots_count_multiplier_does_not_change_weight(self):
        original = fixture()
        scaled = copy.deepcopy(original)
        scaled[0]["passes"] = [x * 100 for x in scaled[0]["passes"]]
        a, b = c.cross_validate(original), c.cross_validate(scaled)
        for name in c.MODELS:
            self.assertAlmostEqual(a["summary"][name]["mean_score"],
                                   b["summary"][name]["mean_score"], places=12)

    def test_scaling_uses_training_plots_only(self):
        rows = fixture()
        for i, row in enumerate(rows):
            row["baseline"][0] = float(i)
        model = c.fit_model(rows[:-1], "total")
        self.assertAlmostEqual(model["mean"][0], 5.0)
        self.assertAlmostEqual(model["scale"][0], math.sqrt(10))
        heldout = copy.deepcopy(rows[-1])
        heldout["baseline"][0] = 1e7
        c.predict_log_probabilities(model, heldout)
        self.assertAlmostEqual(model["mean"][0], 5.0)

    def test_heldout_response_is_not_a_prediction_input(self):
        rows = fixture()
        model = c.fit_model(rows[:-1], "orders")
        heldout = copy.deepcopy(rows[-1])
        first = c.predict_log_probabilities(model, heldout)
        heldout.pop("passes")
        self.assertEqual(first, c.predict_log_probabilities(model, heldout))

    def test_cv_holds_out_the_entire_plots_response(self):
        rows = fixture()
        original = c.cross_validate(rows)
        changed = copy.deepcopy(rows)
        changed[0]["passes"] = [3, 97]
        modified = c.cross_validate(changed)
        first = original["folds"][0]
        second = modified["folds"][0]
        self.assertEqual(first["heldout_plot_id"], rows[0]["plot_id"])
        for name in c.MODELS:
            self.assertEqual(first["models"][name]["fit"], second["models"][name]["fit"])
            self.assertEqual(first["models"][name]["logp"], second["models"][name]["logp"])
            self.assertEqual(first["models"][name]["fit"]["training_plots"], len(rows) - 1)

    def test_zero_pass_plot_changes_coverage_but_no_predictions(self):
        rows = fixture()
        original = c.cross_validate(rows)
        extra = copy.deepcopy(rows[0])
        extra["plot_id"] = "artificial_zero_plot"
        extra["passes"] = [0, 0]
        extra["baseline"][0] = 1000000.
        modified = c.cross_validate(rows + [extra])
        self.assertEqual(original["folds"], modified["folds"])
        self.assertEqual(original["summary"], modified["summary"])
        self.assertEqual(modified["coverage"]["source_plots"], len(rows) + 1)
        self.assertEqual(modified["coverage"]["zero_pass_plots_excluded_from_conditional_score"], 1)

    def test_source_row_order_does_not_change_predictions(self):
        rows = fixture()
        a, b = c.cross_validate(rows), c.cross_validate(list(reversed(rows)))
        self.assertEqual(a, b)

    def test_stratum_reversal_preserves_score(self):
        rows = fixture()
        flipped = copy.deepcopy(rows)
        for row in flipped:
            row["passes"].reverse()
            row["baseline"][0] *= -1
            for value in row["resources"].values():
                value.reverse()
        a, b = c.cross_validate(rows), c.cross_validate(flipped)
        for name in c.MODELS:
            self.assertAlmostEqual(a["summary"][name]["mean_score"],
                                   b["summary"][name]["mean_score"], places=11)

    def test_score_is_normalized_log_likelihood(self):
        self.assertAlmostEqual(c.score_plot([30, 70], [math.log(.4), math.log(.6)]),
                               .3 * math.log(.4) + .7 * math.log(.6))

    def test_score_rejects_invalid_counts_and_distributions(self):
        for counts in ([0, 0], [1], [1, None], [True, 2], [-1, 2]):
            with self.assertRaises(ValueError):
                c.score_plot(counts, [math.log(.5)] * 2)
        for logp in ([], [0], [.1, -.1], [-2, -2], [float("nan"), -1]):
            with self.assertRaises(ValueError):
                c.score_plot([1, 2], logp)

    def test_extreme_valid_log_probabilities_remain_finite(self):
        self.assertEqual(c.score_plot([1, 0], [-10000., -0.]), -10000.)

    def test_public_summary_omits_source_ids_and_observations(self):
        result = c.cross_validate(fixture())
        public = c.public_summary(result)
        self.assertNotIn("artificial_", str(public))
        self.assertNotIn("heldout_plot_id", str(public))
        self.assertEqual(public["n_heldout_plots"], 12)
        self.assertEqual(len(public["models"]["total"]["sorted_plot_gains"]), 12)


if __name__ == "__main__":
    unittest.main()
