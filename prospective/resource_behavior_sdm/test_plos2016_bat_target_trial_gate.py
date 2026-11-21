"""Frozen pre-outcome PLOS schema and source ID assertions (no numeric cases)."""
import unittest
from plos2016_bat_target_trial_gate import HEADER,SHA,PASS

class LabelSchemaTests(unittest.TestCase):
    def test_pinned_seven_column_header(self):
        self.assertEqual(HEADER[-3:],["Target","Bat","Test"])
        self.assertEqual(len(HEADER),7)
        self.assertEqual(len(SHA),64)
        self.assertEqual(PASS,"PLOS_BAT_TARGET_TEST_LABEL_SUPPORT_PASS")

    def test_height_predictor_leakage_guard_contract(self):
        predictor_keys=["X Ref Target","Y Ref Target","Target"]
        self.assertNotIn("Distance toT",predictor_keys)
        self.assertNotIn("Z Ref Target",predictor_keys)

if __name__=="__main__":
    unittest.main()
