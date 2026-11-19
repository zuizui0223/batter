import unittest
from published_contrast_and_change_score_audit_v1 import main_audit,simulate_stationary_null

class TestPublishedAggregatesAndKnownTruth(unittest.TestCase):
    def test_reported_counts_and_study_units(self):
        a=main_audit()
        self.assertEqual(a["published_2019"]["independent_studies"],1)
        self.assertEqual(a["published_2019"]["recipient_species"],3)
        self.assertEqual(a["published_2019"]["pooled_recipient_groups"],1)
        self.assertTrue(a["published_2019"]["all_four_baseline_coefficients_have_negative_reported_95cri"])
        self.assertEqual(a["published_2026"]["original_n_bats"],16)
        self.assertEqual(len(a["published_2026"]["rate_ratio_contrasts"]),4)
        self.assertIn("STOP",a["meta_analytic_eligibility"])

    def test_ratio_of_ratios_not_counted_as_new_independent_animals(self):
        a=main_audit()
        x={r["signal"]:r for r in a["published_2026"]["rate_ratio_contrasts"]}
        self.assertAlmostEqual(x["alert"]["female_vs_male_ratio_of_rate_ratios"],6.57/0.17,places=4)
        self.assertAlmostEqual(x["benign"]["female_vs_male_ratio_of_rate_ratios"],2.58/0.73,places=4)
        self.assertGreater(x["alert"]["female_vs_male_ratio_of_rate_ratios"],x["benign"]["female_vs_male_ratio_of_rate_ratios"])
        self.assertLess(x["alert"]["approx_wald_95_ci_if_sex_contrasts_independent"][0],x["alert"]["female_vs_male_ratio_of_rate_ratios"])

    def test_known_truth_null_mechanical_slope(self):
        a=main_audit()
        by_rho={r["stationary_pre_during_correlation"]:r for r in a["known_truth_null"]["simulations"]}
        for rho in (0.0,0.5,0.9):
            x=by_rho[rho]
            self.assertEqual(x["true_social_effect"],0)
            self.assertAlmostEqual(x["mean_within_site_slope_from_128_simulations"],rho-1,delta=0.045)
            self.assertGreater(x["number_of_negative_slopes"],90)
        self.assertLess(simulate_stationary_null(0.5,27011),0)

if __name__=="__main__":
    unittest.main()
