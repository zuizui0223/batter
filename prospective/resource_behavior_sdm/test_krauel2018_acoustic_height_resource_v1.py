"""Behavioral and numerical contracts; all fixtures are artificial."""
import copy
import datetime as dt
import math
import unittest

import krauel2018_acoustic_height_resource_v1 as k


def fixture(world="null", n=12):
    rows = []
    for i in range(n):
        high = i % 4 in (1, 2)
        passes = [60, 30, 10]
        buzz = [6, 3, 1]
        if world == "height":
            passes = [10, 35, 55] if high else [90, 5, 5]
            buzz = [1, 3, 5] if high else [9, 0, 0]
        elif world == "buzz":
            buzz = [30, 15, 5] if high else [3, 1, 0]
        rows.append({"date": (dt.date(2020, 1, 1) + dt.timedelta(days=i)).isoformat(),
                     "trap_moths": 90 if high else 2,
                     "passes": passes, "buzz": buzz})
    return rows


class TestSourceStructure(unittest.TestCase):
    def test_missing_instrument_is_excluded_not_zero(self):
        rows = fixture(n=8)
        rows[1]["passes"][1] = None
        rows[1]["buzz"][1] = None
        complete, audit = k.validate_rows(rows)
        self.assertEqual(len(complete), 7)
        self.assertEqual(audit["missing_cells"], 1)
        self.assertEqual(audit["source_total_passes"], 770)
        self.assertEqual(audit["complete_total_passes"], 700)

    def test_true_zero_is_observed(self):
        rows = fixture(n=8)
        rows[0]["passes"][2] = 0
        rows[0]["buzz"][2] = 0
        complete, audit = k.validate_rows(rows)
        self.assertEqual(len(complete), 8)
        self.assertEqual(audit["missing_cells"], 0)

    def test_buzz_cannot_exceed_passes(self):
        rows = fixture()
        rows[0]["buzz"][2] = 11
        with self.assertRaises(ValueError):
            k.validate_rows(rows)

    def test_mismatched_missingness_rejected(self):
        rows = fixture()
        rows[0]["passes"][2] = None
        with self.assertRaises(ValueError):
            k.validate_rows(rows)

    def test_duplicate_date_rejected(self):
        rows = fixture()
        rows.append(copy.deepcopy(rows[0]))
        with self.assertRaises(ValueError):
            k.validate_rows(rows)

    def test_invalid_numeric_values_rejected(self):
        for bad in (-1, True, 1.5, float("nan"), "1"):
            with self.subTest(value=bad):
                rows = fixture()
                rows[0]["trap_moths"] = bad
                with self.assertRaises(ValueError):
                    k.validate_rows(rows)

    def test_no_pass_night_is_not_an_absence_record(self):
        rows = fixture()
        rows[0]["passes"] = [0, 0, 0]
        rows[0]["buzz"] = [0, 0, 0]
        with self.assertRaises(ValueError):
            k.validate_rows(rows)

    def test_source_receipt_rejects_unauthenticated_rows(self):
        with self.assertRaises(ValueError):
            k.source_receipt({"schema": "batter.krauel2018.table1_transcription.v1", "rows": fixture()})


class TestPredictions(unittest.TestCase):
    def test_constant_resource_has_zero_increment(self):
        rows = fixture("height")
        for row in rows:
            row["trap_moths"] = 17
        result = k.cross_validate(rows, "leave_night_out")
        self.assertAlmostEqual(result["mean_gains"]["height"], 0.0, places=10)
        self.assertAlmostEqual(result["mean_gains"]["buzz_given_height"], 0.0, places=10)

    def test_known_height_signal_generalizes(self):
        result = k.cross_validate(fixture("height"), "leave_night_out")
        self.assertGreater(result["mean_gains"]["height"], 0.10)

    def test_known_buzz_signal_does_not_create_height_gain(self):
        result = k.cross_validate(fixture("buzz"), "adjacent_pair_out")
        self.assertGreater(result["mean_gains"]["buzz_given_height"], 0.05)
        self.assertAlmostEqual(result["mean_gains"]["height"], 0.0, places=9)

    def test_multiplying_one_nights_counts_does_not_change_fit_or_score(self):
        original = fixture("height", n=8)
        scaled = copy.deepcopy(original)
        scaled[1]["passes"] = [n * 37 for n in scaled[1]["passes"]]
        scaled[1]["buzz"] = [n * 37 for n in scaled[1]["buzz"]]
        left = k.cross_validate(original, "adjacent_pair_out")
        right = k.cross_validate(scaled, "adjacent_pair_out")
        for name in ("height", "buzz_given_height", "joint"):
            self.assertAlmostEqual(left["mean_gains"][name], right["mean_gains"][name], places=10)

    def test_heldout_outcomes_are_not_prediction_inputs(self):
        rows = fixture("height")
        train, test = rows[:-1], copy.deepcopy(rows[-1])
        for factor in ("height", "buzz"):
            model = k.fit_factor(train, factor, True)
            first = k.predict_factor(model, test)
            test["passes"] = [100, 100, 100]
            test["buzz"] = [0, 100, 50]
            self.assertEqual(first, k.predict_factor(model, test))

    def test_both_factors_normalize_even_for_extreme_test_resource(self):
        rows = fixture("buzz")
        row = dict(rows[-1], trap_moths=10 ** 40)
        for factor in ("height", "buzz"):
            prediction = k.predict_factor(k.fit_factor(rows[:-1], factor, True), row)
            distributions = [prediction] if factor == "height" else prediction
            for logs in distributions:
                self.assertTrue(all(math.isfinite(v) for v in logs))
                self.assertAlmostEqual(sum(math.exp(v) for v in logs), 1.0, places=12)

    def test_hand_calculated_joint_score(self):
        row = {"passes": [2, 1, 1], "buzz": [1, 0, 1]}
        h = [math.log(p) for p in (.5, .25, .25)]
        b = [[math.log(.5), math.log(.5)]] * 3
        score = k.score_night(row, h, b)
        self.assertAlmostEqual(score["height"], -1.0397207708399179)
        self.assertAlmostEqual(score["buzz_given_height"], -0.6931471805599453)
        self.assertAlmostEqual(score["joint"], -1.7328679513998633)

    def test_four_joint_candidates_decompose_on_identical_support(self):
        result = k.cross_validate(fixture("height"), "leave_night_out")
        for fold in result["folds"]:
            self.assertAlmostEqual(fold["gains"]["joint"],
                                   fold["gains"]["height"] + fold["gains"]["buzz_given_height"], places=12)
            joint = fold["joint_model_scores"]
            self.assertAlmostEqual(joint["resource_both"] - joint["baseline"], fold["gains"]["joint"], places=12)

    def test_pair_folds_cover_all_nights_once(self):
        result = k.cross_validate(fixture(n=8), "adjacent_pair_out")
        self.assertEqual(result["n_folds"], 4)
        self.assertEqual([f["n_test_nights"] for f in result["folds"]], [2] * 4)
        self.assertEqual(sum(f["n_test_nights"] for f in result["folds"]), 8)
        self.assertFalse("date" in str(result))

    def test_odd_pair_design_stops_instead_of_dropping_a_night(self):
        with self.assertRaises(ValueError):
            k.cross_validate(fixture(n=9), "adjacent_pair_out")


if __name__ == "__main__":
    unittest.main()
