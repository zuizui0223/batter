import unittest
from h1_cue_interaction_known_truth_v1 import run

class TestCueInteractionKnownTruth(unittest.TestCase):
    def test_identification_and_artifact(self):
        r=run()
        self.assertEqual(r["status"],"SYNTHETIC_KNOWN_TRUTH_ONLY")
        null=r["results"]["null_no_cue_density_moderation"]
        alt=r["results"]["positive_true_cue_density_moderation"]
        self.assertEqual(null["repetitions"],128)
        self.assertAlmostEqual(null["mean_recovered_interaction"],0.0,delta=0.10)
        self.assertAlmostEqual(alt["mean_recovered_interaction"],0.8,delta=0.10)
        self.assertGreater(alt["estimates_positive"],120)
        self.assertLess(null["mean_naive_change_vs_pre_slope"],-0.25)
        self.assertLess(alt["mean_naive_change_vs_pre_slope"],-0.15)
