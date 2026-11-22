"""Counterexample known truth and no-biological-promotion regression guards."""
import unittest
from plos2016_target_confounding_counterexample import (
    CONSTRUCTED_DESIGN, calculate_counterexample,
    info_given_animal, observational_mutual_information
)

class ConfoundingTests(unittest.TestCase):
    def test_balanced_target_margins_allow_artificial_predictability(self):
        r=calculate_counterexample()
        self.assertEqual(r["status"],"SYNTHETIC_COUNTEREXAMPLE_VERIFIED")
        self.assertAlmostEqual(r["target_height_marginal_information_nats"],
                               0.1638965900335596,places=12)
        self.assertEqual(r["constructed_target_trial_counts_sorted"],[15,15])
        self.assertEqual(r["constructed_bat_trial_counts_sorted"],[3,3,8,8,8])
        self.assertEqual(r["constructed_bat_target_pair_count"],8)

    def test_target_has_no_effect_within_any_individual(self):
        self.assertAlmostEqual(info_given_animal(CONSTRUCTED_DESIGN),0,places=12)
        self.assertAlmostEqual(calculate_counterexample()[
           "true_target_effect_on_height_by_construction"],0,places=12)

    def test_three_paired_bats_have_no_05_signflip_power(self):
        r=calculate_counterexample()
        self.assertEqual(r["number_of_source_structurally_both_target_bats"],3)
        self.assertEqual(r["best_possible_one_sided_signflip_p_for_three_bats"],.125)
        self.assertIsNone(r["real_PLOS_target_height_coefficient"])
        self.assertTrue(r["constructed_no_real_biology_rows"])

    def test_empty_counterexample_stop(self):
        with self.assertRaises(ValueError):
            observational_mutual_information(())

if __name__=="__main__":
    unittest.main()
