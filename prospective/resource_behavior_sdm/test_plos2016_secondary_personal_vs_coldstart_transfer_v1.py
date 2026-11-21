"""Synthetic-only secondary personal vs other-bat PLOS height transfer tests."""
from __future__ import annotations
import math
import unittest
from unittest.mock import patch

import plos2016_secondary_personal_vs_coldstart_transfer_v1 as secondary
from test_plos2016_three_paired_bats_exploratory_transfer_v1 import mock_trials


class SecondaryPLOS3Tests(unittest.TestCase):
    def test_sourcefree_pairing_and_heldout_trial_integrity(self):
        rows=mock_trials(target_z_effect=0.6,seed=401)
        with patch.object(secondary,"_source_rows_after_gate",return_value=rows):
            out=secondary.secondary_within_vs_other_bats_original(
                b"SYNTHETIC",enforce_frozen_coldstart=False)
        self.assertEqual(out["real_source_paired_bats"],3)
        self.assertEqual(out["real_source_heldout_trial_sequences"],24)
        self.assertEqual(out["personal_model_training_other_trials_of_same_bat"],7)
        self.assertEqual(out["cold_start_training_trials_from_two_other_bats"],16)
        self.assertEqual(len(out["bat_level_results_without_real_source_ids"]),3)
        self.assertTrue(out["same_heldout_target_events_between_models"])
        self.assertTrue(out["different_training_sample_sizes_cannot_isolate_personal_mechanism"])
        self.assertFalse(out["not_population_inference"] is False)
        self.assertIsNone(out["real_wild_bat_resource_height_gain"])
        self.assertNotIn("fake",str(out))
        metrics=out["mean_bat_equal_target_equal_deltas_nats_per_frame"]
        for value in metrics.values():
            self.assertTrue(math.isfinite(value))
        self.assertAlmostEqual(
            metrics["personal_trial_target_increment"]-
            metrics["other_bats_target_increment"],
            metrics["personal_minus_other_bat_target_increment"],places=11)

    def test_original_frozen_crossbat_check_must_block_unrelated_source(self):
        rows=mock_trials(target_z_effect=0.6,seed=401)
        with patch.object(secondary,"_source_rows_after_gate",return_value=rows):
            with self.assertRaisesRegex(ValueError,"PRIOR_ORIGINAL_COLD_START_RESULT_NOT_REPRODUCED"):
                secondary.secondary_within_vs_other_bats_original(b"FAKE")

    def test_source_mismatch_and_missing_trial_never_promote(self):
        rows=mock_trials(target_z_effect=0.6)
        bad=rows[:-1]
        with patch.object(secondary,"_source_rows_after_gate",return_value=bad):
            with self.assertRaisesRegex(ValueError,"THREE_BAT_STRUCTURE_DRIFT"):
                secondary.secondary_within_vs_other_bats_original(
                    b"SYNTHETIC",enforce_frozen_coldstart=False)


if __name__=="__main__":
    unittest.main()
