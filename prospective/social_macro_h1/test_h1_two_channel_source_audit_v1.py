import unittest
from h1_two_channel_source_audit_v1 import audit

class TestTwoChannelSourceGate(unittest.TestCase):
    def test_source_types_distinct_and_no_unmeasured_parameters_filled(self):
        a=audit()
        self.assertEqual(a["source_cases"],7)
        self.assertEqual(a["source_region_labels"],5)
        self.assertEqual(a["original_source_groups_with_all_required_direct_parameters"],0)
        self.assertEqual(a["original_source_groups_claimed_identified_VOI"],0)
        self.assertEqual(a["group_with_direct_individual_memory_and_social_CUE"],0)
        self.assertTrue(a["not_systematic_review"])
        self.assertFalse(a["model_globally_identified"])
        self.assertEqual(a["selected_responder_studies"],1)
        self.assertIn("when",a["cue_channel_counts"])
        self.assertIn("who",a["cue_channel_counts"])
        self.assertIn("risk",a["cue_channel_counts"])
    def test_no_false_external_h1_replication(self):
        a=audit()
        self.assertEqual(a["model_2019_buzz_pre_exact_external_replicates"],0)
        self.assertEqual(a["status"],"SOURCE_ELIGIBILITY_ONLY_NO_H1_EFFECT_FIT")

if __name__=="__main__":
    unittest.main()
