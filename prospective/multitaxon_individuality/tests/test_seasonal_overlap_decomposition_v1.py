"""Synthetic-only checks. No original tracking data or source-effect claims."""
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seasonal_overlap_decomposition_v1 import summarize

class TestSeasonalOverlapDecomposition(unittest.TestCase):
    def test_exact_incidence_strength_cancellation(self):
        w = {k: .544 if k < 6 else 0 for k in range(78)}
        s = {k: .232 if k < 14 else 0 for k in range(78)}
        r = summarize(w, s)
        self.assertEqual(r["states"]["both"], 6)
        self.assertEqual(r["states"]["summer_only"], 8)
        self.assertAlmostEqual(r["difference_winter_minus_summer"], .016 / 78)
        self.assertAlmostEqual(r["incidence_contribution"], -3.104 / 78)
        self.assertAlmostEqual(r["strength_contribution"], 3.120 / 78)
        self.assertAlmostEqual(r["decomposition_residual"], 0)
    def test_marginals_do_not_identify_pair_rewiring(self):
        w = {"a": .4, "b": 0, "c": 0, "d": 0}
        a = summarize(w, {"a": .2, "b": .2, "c": 0, "d": 0})
        b = summarize(w, {"a": 0, "b": .2, "c": .2, "d": 0})
        self.assertEqual(a["difference_winter_minus_summer"], b["difference_winter_minus_summer"])
        self.assertNotEqual(a["states"], b["states"])
    def test_different_risk_sets_or_invalid_observations(self):
        with self.assertRaises(ValueError): summarize({"a": 0}, {"b": 0})
        for x in (None, float("nan"), float("inf"), -1, 1.2, True):
            with self.subTest(value=x), self.assertRaises(ValueError):
                summarize({"a": x}, {"a": 0})
    def test_no_dyads_does_not_mean_zero(self):
        self.assertEqual(summarize({}, {})["status"], "NOT_ESTIMABLE_NO_COMMON_DYADS")
    def test_one_season_zero_positive_dyads_does_not_mean_zero_strength(self):
        r = summarize({"a": 0, "b": 0}, {"a": .5, "b": 0})
        self.assertIsNone(r["winter"]["positive_strength"])
        self.assertIsNone(r["incidence_contribution"])
        self.assertAlmostEqual(r["difference_winter_minus_summer"], -.25)
    def test_positive_incidence_can_coexist_with_negative_mean_difference(self):
        r = summarize({"a": .1, "b": .1}, {"a": 1, "b": 0})
        self.assertGreater(r["incidence_contribution"], 0)
        self.assertLess(r["strength_contribution"], 0)
        self.assertLess(r["difference_winter_minus_summer"], 0)

if __name__ == "__main__":
    unittest.main()
