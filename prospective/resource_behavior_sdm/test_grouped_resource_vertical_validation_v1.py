"""Known-truth heldout tests; synthetic rows do NOT represent bat ecology."""
import unittest
from grouped_resource_vertical_validation_v1 import score_group_heldout


def simulated_rows(with_food=False,all_interpolated=False):
    rows=[]
    for i in range(8):
        for night in range(2):
            for h in range(40):
                habitat="forest" if h<20 else "open"
                z="high" if habitat=="forest" else "low"
                r={
                    "individual":"toy_ind_"+str(i),
                    "night":"night_"+str(night),
                    "site":"site_a" if i<4 else "site_b",
                    "horizontal_cell":"coarse_XY_shared",
                    "height_datum_verified":True,
                    "state_annotation_outcome_blind":True,
                    "habitat_independently_measured":True,
                    "time_bin":"night",
                    "kinematic_state":"moving",
                    "height_bin":z,
                    "habitat_class":habitat,
                    "is_original_fix":not all_interpolated,
                    "is_interpolated":all_interpolated,
                }
                if with_food:
                    r["food_bin"]="more" if habitat=="forest" else "less"
                    r["independent_food_survey"]=True
                    r["food_time_matched"]=True
                rows.append(r)
    return rows


class GroupedVerticalTests(unittest.TestCase):
    def test_known_truth_habitat_raises_predictive_score(self):
        x=score_group_heldout(simulated_rows(),"individual")
        self.assertEqual(x["n_folds"],8)
        self.assertGreater(x["equal_heldout_group_mean_gain"]["habitat_minus_base"],0)
        self.assertEqual(x["n_unique_bats"],8)
        self.assertFalse(x["fixes_are_independent_replicates"])

    def test_site_heldout_and_not_storing_fix_effect_pvalues(self):
        x=score_group_heldout(simulated_rows(),"site")
        self.assertEqual(x["n_folds"],2)
        self.assertEqual(len(x["source_group_scores"]),2)
        self.assertNotIn("p_value",x)

    def test_food_model_does_not_alter_baseline_prediction_denominator(self):
        a=score_group_heldout(simulated_rows(),"individual",use_food=False)
        b=score_group_heldout(simulated_rows(with_food=True),"individual",use_food=True)
        self.assertEqual(a["n_folds"],b["n_folds"])
        for aa,bb in zip(a["source_group_scores"],b["source_group_scores"]):
            self.assertAlmostEqual(
                aa["matched_scores_nats_per_observed_fix"]["kinematic_time"],
                bb["matched_scores_nats_per_observed_fix"]["kinematic_time"],places=12)
            self.assertAlmostEqual(
                aa["matched_scores_nats_per_observed_fix"]["add_habitat"],
                bb["matched_scores_nats_per_observed_fix"]["add_habitat"],places=12)
            self.assertNotIn("heldout_block",aa)
            self.assertIn("heldout_block_ordinal",aa)

    def test_true_food_cannot_be_assumed_from_habitat(self):
        with self.assertRaisesRegex(ValueError,"NO_INDEPENDENT_TIME_MATCHED_FOOD"):
            score_group_heldout(simulated_rows(),use_food=True)
        x=score_group_heldout(simulated_rows(with_food=True),use_food=True)
        self.assertIn("true_food_minus_habitat",x["equal_heldout_group_mean_gain"])
        self.assertTrue(x["food_channel_is_directly_measured_and_time_matched"])

    def test_unsafe_annotation_provenance_never_enters_fit(self):
        for flag in ("height_datum_verified","state_annotation_outcome_blind",
                     "habitat_independently_measured"):
            sample=simulated_rows()
            sample[0][flag]=False
            with self.assertRaisesRegex(ValueError,"UNVERIFIED_HEIGHT_STATE_OR_HABITAT"):
                score_group_heldout(sample)

    def test_coarse_xy_must_be_prespecified_not_derived_from_target_height(self):
        data=simulated_rows()
        del data[0]["horizontal_cell"]
        with self.assertRaisesRegex(ValueError,"SOURCE_SCHEMA"):
            score_group_heldout(data)

    def test_interpolated_source_is_never_a_new_gps_fix(self):
        with self.assertRaisesRegex(ValueError,"NONORIGINAL_OR_INTERPOLATED_FIX"):
            score_group_heldout(simulated_rows(all_interpolated=True))

    def test_data_schema_and_classification_must_be_frozen(self):
        x=simulated_rows()
        x[0].pop("kinematic_state")
        with self.assertRaisesRegex(ValueError,"SOURCE_SCHEMA"):
            score_group_heldout(x)
        x=simulated_rows()
        x[0]["height_bin"]="unknown"
        with self.assertRaisesRegex(ValueError,"UNFROZEN_OR_MISSING_HEIGHT"):
            score_group_heldout(x)
        with self.assertRaisesRegex(ValueError,"HELDOUT_UNIT"):
            score_group_heldout(simulated_rows(),"not_a_holdout")

if __name__=="__main__":
    unittest.main()
