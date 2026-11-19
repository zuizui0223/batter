import unittest
from run_h1_feasibility import audit

class TestSourceFeasibility(unittest.TestCase):
    def setUp(self):
        self.result = audit()

    def test_review_unit_and_strategy_counts(self):
        s = self.result["review_table2"]
        self.assertEqual(s["cases"], 35)
        self.assertEqual(s["explicit_named_taxa"], 29)
        self.assertEqual(s["pooled_taxon_rows"], 1)
        self.assertEqual(s["resolved_strategy_cases"], 20)
        self.assertEqual(s["strategy_counts"]["local_enhancement"], 13)
        self.assertEqual(s["strategy_counts"]["group_facilitation"], 5)
        self.assertEqual(s["strategy_counts"]["following"], 1)
        self.assertEqual(s["strategy_counts"]["recruitment"], 1)

    def test_review_not_external_replication(self):
        s = self.result["review_table2"]
        self.assertEqual(s["persistence_and_location_known_cases"], 25)
        self.assertEqual(s["review_table_mismatches_to_published_framework"], 0)
        self.assertFalse(s["independent_outcome_validation"])

    def test_post2022_study_clustering_and_stop(self):
        s = self.result["post2022_targeted_evidence"]
        self.assertEqual(s["records_not_independent_effects"], 12)
        self.assertEqual(s["named_taxa"], 8)
        self.assertEqual(s["study_clusters"], 6)
        self.assertEqual(s["four_class_independently_coded_cases"], 0)
        self.assertEqual(s["unresolved_taxon_or_aggregate_rows"], 1)
        self.assertFalse(s["two_blinded_coders_completed"])
        self.assertIn("STOP", self.result["primary_phylogenetic_h1_strategy_model"])
        self.assertIn("STOP", self.result["primary_phylogenetic_h1_occurrence_model"])

if __name__ == "__main__":
    unittest.main()
