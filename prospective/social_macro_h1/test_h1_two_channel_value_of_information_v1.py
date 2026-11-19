import math
import unittest
from h1_two_channel_value_of_information_v1 import run, value,posterior, piecewise_thresholds,PARAMS

class TestTwoChannelInformationValue(unittest.TestCase):
    def test_bayes_identity_and_thresholds(self):
        o=posterior(PARAMS)
        self.assertAlmostEqual(o["P(cue_positive)"],0.43,places=9)
        self.assertAlmostEqual(o["P(available_given_positive)"],0.34/0.43,places=9)
        self.assertAlmostEqual(o["P(available_given_negative)"],0.06/0.57,places=9)
        th=piecewise_thresholds(PARAMS)
        self.assertAlmostEqual(th["positive_cue_visit"],0.37941176470588234)
        self.assertAlmostEqual(th["baseline_visit"],0.75)
        self.assertAlmostEqual(th["negative_cue_visit"],2.85)
    def test_non_monotone_social_timing_value(self):
        low=value(PARAMS,0.5)["net_value_if_cue_purchased"]
        middle=value(PARAMS,0.75)["net_value_if_cue_purchased"]
        high=value(PARAMS,1)["net_value_if_cue_purchased"]
        self.assertAlmostEqual(low,.31)
        self.assertAlmostEqual(middle,1.16)
        self.assertAlmostEqual(high,1.01)
        self.assertTrue(low<middle>high)
        self.assertTrue(value(PARAMS,0.25)["would_purchase_cue"] is False)
        self.assertTrue(value(PARAMS,0.5)["would_purchase_cue"] is True)
    def test_analytic_slopes_and_monte_grid(self):
        th=piecewise_thresholds(PARAMS)
        eps=0.00001
        for m,slope in ((0.6,3.4),(0.85,-0.6)):
            finite=(value(PARAMS,m+eps)["gross_value_of_information"]-
                    value(PARAMS,m-eps)["gross_value_of_information"])/(2*eps)
            self.assertAlmostEqual(finite,slope,places=6)
        self.assertAlmostEqual(th["none_to_positive_cue_slope"],3.4)
        self.assertAlmostEqual(th["baseline_visits_but_negative_cue_skips_slope"],-0.6)
    def test_known_theory_not_mislabelled_empirical(self):
        r=run()
        self.assertEqual(r["evidence_status"],"THEORETICAL_ILLUSTRATION_NOT_EMPIRICAL_BAT_FIT")
        self.assertFalse(r["scientific_conclusion"]["global_species_effect_estimated"])
        self.assertFalse(r["scientific_conclusion"]["real_bat_memory_m_measured"])
        self.assertEqual(r["scientific_conclusion"]["novelty_claim"][:4],"NONE")
        self.assertAlmostEqual(r["maximum_net_information_value_in_0_to_1"]["net_value_if_cue_purchased"],1.16)
    def test_invalid_parameters_not_accepted(self):
        x=dict(PARAMS);x["cue_false_positive_rate"]=0.9
        with self.assertRaises(ValueError):
            posterior(x)
        with self.assertRaises(ValueError):
            value(PARAMS,1.2)

if __name__=="__main__":unittest.main()
