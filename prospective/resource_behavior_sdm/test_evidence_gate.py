"""Evidence classification tests; metadata checks, NOT biological replay."""
import json
import pathlib
import unittest


class ResourceBehaviorClaimGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = pathlib.Path(__file__).with_name("evidence_ledger_v1.json")
        cls.data = json.loads(path.read_text(encoding="utf-8"))
        cls.claims = {c["id"]: c for c in cls.data["claims"]}

    def test_unestimated_effects_stay_null(self):
        self.assertGreaterEqual(len(self.data["strict_unestimated"]), 5)
        self.assertTrue(all(v is None for v in self.data["strict_unestimated"].values()))
        self.assertEqual(self.data["claim_gate"], "UNVALIDATED_HIGHDIMENSIONAL_RESOURCE_SDM_PROTOTYPE")

    def test_positive_source_rank_not_promoted_to_resource_ecology(self):
        botanical = self.claims["BOTANICAL_RECORD_RANK"]
        self.assertIn("OBSERVATION_RANK", botanical["tier"])
        self.assertEqual(botanical["n_evaluable"], 647)
        self.assertEqual(botanical["n_candidate"], 1802)
        self.assertIn("bat species", botanical["not_claim"])

    def test_shadow_no_partner_gain_is_preserved(self):
        shadow = self.claims["SHADOW_LINKED_FRUIT_IDENTITY"]
        self.assertLess(shadow["mean_linked_minus_generic_auc"], 0.0)
        self.assertLess(shadow["mean_linked_minus_rewired_auc"], 0.0)
        self.assertEqual(shadow["n_fitted"], 49)

    def test_bat_individuality_not_called_spatial_partition(self):
        bat = self.claims["WILD_VERTICAL_IDENTITY"]
        self.assertEqual(bat["n_tropical_terrain_positive"], 4)
        self.assertEqual(bat["n_spatial_excess_positive"], 0)
        self.assertIn("true physical separation", bat["not_claim"])

    def test_independent_external_originals_do_not_become_5d_ecology(self):
        a=self.data["independent_external_evidence_progress_20261120"]
        self.assertEqual(len(a["candidates"]),2)
        self.assertFalse(a["live_source_crossstudy_join_allowed"])
        self.assertIsNone(a["real_highdimensional_resource_behavior_height_effect"])
        self.assertTrue(all(x["original_metadata_verified"] for x in a["candidates"]))
        self.assertTrue(all(not x["original_file_content_read"] for x in a["candidates"]))
        self.assertTrue(all(x["original_file_http_error"]==401 for x in a["candidates"]))

    def test_ducke_food_positive_is_only_source_local_guild(self):
        d={r["id"]:r for r in self.data["claims"]}["DUCKE_MEASURED_FOOD_LOCAL_GUILD_PREDICTION"]
        self.assertEqual(d["n_matched_plots"],46)
        self.assertEqual(d["n_same_site_same_day_nights"],103)
        self.assertGreater(d["heldout_food_12_minus_baseline_nats_per_capture"],0)
        self.assertIn("SOURCE_LOCAL_EXPLORATORY",d["tier"])
        self.assertIn("not occupancy",d["response"])
        self.assertTrue(d["source_anomalies"]["missing_vegetation_clutter"])
        self.assertIsNone(self.data["strict_unestimated"]["ecological_partner_m3_minus_m1"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_ducke_specificity_v2_never_promotes_to_causal_resource_height(self):
        d={r["id"]:r for r in self.data["claims"]}["DUCKE_MEASURED_FOOD_LOCAL_GUILD_PREDICTION"]
        r=d["source_specificity_v2"]
        self.assertGreater(r["frugivore"]["both_separate_fruit_axes_minus_baseline"],0)
        self.assertGreater(r["frugivore"]["food12_given_remaining10"],0)
        self.assertGreater(r["gleaning_animalivore"]["remaining10_given_food12"],0)
        self.assertFalse(r["true_independent_nonfood_negative_control"])
        self.assertFalse(r["adjusted_for_paper_vegetation_clutter"])
        self.assertFalse(r["independent_external_replication"])
        self.assertIsNone(r["causal_plant_diet_selection_effect"])
        self.assertIsNone(r["empirical_resource_conditioned_flight_height_gain"])
        self.assertIsNone(self.data["strict_unestimated"]["ecological_partner_m3_minus_m1"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_ducke_joint_four_guild_v3_is_multivariate_but_not_validated_5d(self):
        d={r["id"]:r for r in self.data["claims"]}["DUCKE_MEASURED_FOOD_LOCAL_GUILD_PREDICTION"]
        v=d["joint_four_guild_composition_v3"]
        self.assertEqual(v["four_guild_captures"],809)
        self.assertEqual(v["excluded_single_sanguivore_captures"],1)
        self.assertGreater(v["seven_source_blocks"]["split12plus10_minus_baseline"],0)
        self.assertEqual(v["seven_source_blocks"]["positive_split_vs_baseline"],6)
        self.assertEqual(v["six_L3_L8_only"]["positive_split_vs_baseline"],6)
        self.assertFalse(v["actual_plant_food_consumption_established"])
        self.assertFalse(v["resource_vertical_GPS_event_join_available"])
        self.assertIsNone(v["empirical_resource_conditional_3D_height_gain"])
        self.assertIsNone(self.data["strict_unestimated"]["ecological_partner_m3_minus_m1"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_ducke_v4_abundance_matched_null_does_not_support_unique_food_identity(self):
        c={x["id"]:x for x in self.data["claims"]}["DUCKE_MEASURED_FOOD_LOCAL_GUILD_PREDICTION"]
        v=c["plant_partition_label_null_v4"]
        self.assertEqual(v["n_original_plant_categories"],22)
        self.assertEqual(v["n_named_genera"],21)
        self.assertEqual(v["n_unidentified_observed_fruiting_plant_entries"],52)
        self.assertEqual(v["n_original_matched_rows_for_unidentified_source_category"],12)
        self.assertTrue(v["unidentified_count_value_is_sum_of_original_Amount_field"])
        self.assertAlmostEqual(v["random_12_of_22_null"]["exploratory_plus_one_fraction"],.025)
        self.assertAlmostEqual(v["abundance_quartile_matched_12_of_22_null"]["exploratory_plus_one_fraction"],.055)
        self.assertFalse(v["label_specific_food_causal_effect_established"])
        self.assertFalse(v["real_individual_bat_GPS_height_resource_join_estimated"])
        self.assertIsNone(v["new_ecological_species_SDM"])
        self.assertIsNone(v["new_5d_resource_height_gain"])
        self.assertIsNone(self.data["strict_unestimated"]["ecological_partner_m3_minus_m1"])

    def test_hendel_original_upload_within_source_not_geographic_or_3d(self):
        x=self.data["independent_prey_transfer_20261121"]
        self.assertEqual(x["source_sites_published"],64)
        self.assertTrue(x["original_publisher_metadata_version_and_two_file_inventory_verified"])
        self.assertFalse(x["original_publisher_content_available"])
        self.assertEqual(x["original_publisher_dataset_download_http_status"],401)
        self.assertTrue(x["user_uploaded_original_xlsx_opened"])
        self.assertEqual(x["new_external_test_outcome"]["n_unique_forest_plots"],65)
        self.assertEqual(x["source_sites_published"],64)
        gain=x["new_external_test_outcome"]["gains"]
        self.assertLess(gain["SRE"]["moth_abundance"],0)
        self.assertGreater(gain["MRE"]["moth_abundance"],0)
        self.assertGreater(gain["Ppip"]["moth_abundance"],0)
        self.assertGreater(gain["LRE"]["beetle_richness"],0)
        self.assertFalse(x["new_external_test_outcome"]["independent_geographic_holdout"])
        self.assertIsNone(x["new_external_test_outcome"]["height_3d_gain"])
        self.assertIsNone(x["external_resource_conditional_height_gain"])
        self.assertTrue(x["cannot_compare_numeric_scores_to_ducke_fruit_capture_guild"])
        self.assertFalse(x["raw_source_bytes_or_location_rows_uploaded_to_batter"])
        self.assertIsNone(self.data["strict_unestimated"]["external_resource_sdm_confirmation"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_goldshtein_source_access_and_true_resource_join_remain_stop(self):
        x=self.data["goldshtein_source_audit_20261121"]
        self.assertEqual(x["official_metadata_http_status"],401)
        self.assertFalse(x["source_file_inventory_verified"])
        self.assertEqual(x["gps_bats_in_mapped_cactus_field"],8)
        self.assertEqual(x["directly_monitored_open_flower_cacti"],414)
        self.assertFalse(x["same_night_mapped_cactus_flower_bat_gps_join_verified"])
        self.assertTrue(x["using_author_visit_labels_to_predict_height_is_response_leakage"])
        self.assertIsNone(x["true_resource_conditioned_height_holdout_gain"])
        self.assertIsNone(x["cactus_location_conditional_height_holdout_gain"])
        self.assertFalse(x["source_rows_committed"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_3d_forest_bird_prior_art_narrows_novelty_without_promotion(self):
        p=self.data["prior_art_novelty_audit_20261121"]
        self.assertEqual(p["seabird_3d_2026_n_taxa"],44)
        self.assertTrue(p["behavior_hmm_ssf_simulated_utilization_distribution"])
        self.assertEqual(p["direct_2026_3d_ssf_method_doi"], "10.1111/ele.70414")
        self.assertTrue(p["direct_2026_3d_ssf_3d_crw_movement_habitat_selection_joint"])
        self.assertFalse(p["direct_2026_3d_ssf_empirical_resource_state_individual_combination_demonstrated"])
        self.assertEqual(p["forest_bat_micarray_lidar_joint_3d_prior_art"],
                         "10.1186/s40462-023-00387-0")
        self.assertIsNone(p["original_joint_measured_resource_state_bat_individual_agl_gain"])
        self.assertEqual(p["number_of_hmm_ssf_simulated_tracks"],5)
        self.assertIn("10.1002/ece3.11138",p["forest_bird_18_sector_binomial_model"])
        self.assertIn("10.1016/j.foreco.2022.120668",
                      p["forest_detection_adjusted_four_strata"])
        self.assertFalse(p["empirical_joint_5d_model_fitted"])
        self.assertFalse(p["source_3d_joint_data_verified"])
        self.assertIsNone(p["new_resource_height_out_of_group_gain"])
        self.assertTrue(p["horizontal_marginal_conservation_is_probability_identity_not_discovery"])
        self.assertFalse(p["main_branch_or_frozen_article_changed"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_paired_3d_ssf_known_truth_cannot_become_empirical_field_result(self):
        v=self.data["paired_3d_ssf_known_truth_20261121"]
        self.assertEqual(v["evidence_tier"],"SOURCE_FREE_SIMULATION_ONLY_NOT_EMPIRICAL_3D_SDM")
        self.assertEqual(v["fictional_bats"],8)
        self.assertEqual(v["fictional_observed_risksets"],240)
        self.assertTrue(v["exact_discrete_joint_horizontal_vertical_log_score_identity"])
        self.assertFalse(v["is_reproduction_of_ssf3d_R_package"])
        self.assertFalse(v["is_species_occupancy_or_3d_resource_sdm"])
        self.assertFalse(v["source_original_real_goldshtein_files_read"])
        self.assertFalse(v["real_resource_height_night_bat_joint_model_fitted"])
        self.assertIsNone(v["ecological_joint_height_outcome_gain"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])
        s=v["simulation_8_bat_holdout_gains_nats_per_step"]
        self.assertLess(s["no_resource_effect"]["M1_minus_M0"]["joint"],0)
        self.assertGreater(s["only_horizontal_resource"]["M1_minus_M0"]["horizontal"],0)
        self.assertGreater(s["resource_by_height"]["M2_minus_M1"]["conditional_height"],0)
        self.assertGreater(s["resource_height_by_height_blind_behavior"]["M3_minus_M2"]["conditional_height"],0)
        proxy=s["unmeasured_habitat_proxy_with_zero_resource_causal_effect"]
        self.assertFalse(v["resource_conditioned_height_prediction_identifies_causal_resource_mechanism"])
        self.assertGreater(proxy["M1_minus_M0"]["horizontal"],0)
        self.assertAlmostEqual(proxy["M2_minus_M1"]["conditional_height"],
                               0.1541523358834193,places=5)
        for world in s.values():
            for contrast in world.values():
                if not isinstance(contrast,dict) or not {"joint","horizontal","conditional_height"}.issubset(contrast):
                    continue
                self.assertAlmostEqual(contrast["joint"],
                                       contrast["horizontal"]+contrast["conditional_height"],
                                       places=10)

    def test_proposal_correction_3d_known_truth_is_not_field_evidence(self):
        a=self.data["proposal_density_bias_known_truth_20261121"]
        self.assertEqual(a["synthetic_n_fictional_bats"],16)
        self.assertEqual(a["synthetic_n_observed_steps"],1120)
        self.assertAlmostEqual(
            a["null_site_equal_mean_corrected_minus_naive_nats_per_step"],
            2.424102403912198, places=9)
        self.assertLess(abs(a["null_pooled_corrected_beta"]), .15)
        self.assertAlmostEqual(a["true_0_95_world_pooled_corrected_beta"],
                               .998684342795897, places=9)
        self.assertEqual(a["mathematical_choice_offset"],
                         "log(reference_mass) - log(proposal_mass)")
        self.assertTrue(a["not_full_ssf3d_reference_implementation"])
        self.assertFalse(a["original_source_authenticity_verified_by_boolean_flags"])
        self.assertFalse(a["real_goldshtein_bat_resource_height_data_opened"])
        self.assertIsNone(a["real_bat_vertical_resource_effect"])
        self.assertIsNone(a["comparison_3d_ssf_original_bat_holdout_gain"])
        self.assertIsNone(self.data["strict_unestimated"]
                          ["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_known_q_sampled_3d_m0_m3_bridge_is_only_methodology(self):
        x=self.data["paired_3d_known_q_bridge_20261121"]
        self.assertEqual(x["supported_modes"],
                         ["enumerated_xy_z","known_q_sampled_controls"])
        self.assertEqual(x["known_q_logit_offset"],
                         "log(reference mass) - log(proposal mass)")
        self.assertTrue(x["exact_backward_compatibility_under_reference_equals_q"])
        self.assertTrue(x["zero_or_missing_or_unverified_q_stopped"])
        self.assertTrue(x["horizontal_component_scored_on_sampled_riskset_not_true_horizontal_sdm"])
        self.assertTrue(x["vertical_component_scored_on_sampled_riskset_not_true_z_given_xy_area_density"])
        self.assertFalse(x["independent_fitted_ssf3d_continuous_competitor_completed"])
        self.assertFalse(x["original_goldshtein_source_raw_file_headers_verified"])
        self.assertFalse(x["real_individual_tracked_resource_join_estimated"])
        self.assertIsNone(x["original_measured_resource_height_heldout_gain"])
        self.assertIsNone(x["original_ecological_m3_minus_m1_n1"])
        self.assertIsNone(self.data["strict_unestimated"]
                          ["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_gps_height_error_11m_is_simulation_not_a_verified_field_result(self):
        a=self.data["gps_height_error_known_truth_20261121"]
        self.assertEqual(a["number_of_precommitted_simulation_scenarios"],5)
        self.assertEqual(a["synthetic_bats"],6)
        self.assertEqual(a["synthetic_recorded_steps"],60)
        self.assertFalse(a["actual_goldshtein_sensor_sigma_verified"])
        self.assertFalse(a["known_q_sampled_control_correction_integrated"])
        self.assertTrue(a["target_height_leakage_prohibited"])
        self.assertTrue(a["same_recorded_observation_scored_for_sensor_aware_and_hard_binned_models"])
        self.assertFalse(a["original_goldshtein_bat_flower_agl_join_verified"])
        self.assertIsNone(a["empirical_wild_bat_resource_conditioned_height_gain"])
        self.assertIsNone(self.data["strict_unestimated"]
                          ["higher_dim_resource_conditional_bat_logscore_gain"])
        s=a["source_free_true_resource_height_sensitivities"]
        self.assertGreater(s[1]["conditional_height_M2_minus_M1_sensor_aware"],0)
        self.assertGreater(s[2]["sensor_aware_M2_joint_minus_hard_bin"],0)
        self.assertLess(a["source_free_true_no_resource_effect_sigma_11_height_gain"],0.001)

    def test_q_noisy_height_combined_likelihood_sourcefree_and_MonteCarlo_ceiling(self):
        x=self.data["q_noisy_observation_integration_20261121"]
        self.assertTrue(x["latent_z_integrated_out_using_independent_q_stratified_controls"])
        self.assertTrue(x["complete_xy_z_reference_reproduced_at_q_equal_reference"])
        self.assertTrue(x["finite_MC_importance_estimator_biased"])
        self.assertEqual(x["sourcefree_number_of_GPS_observations"],48)
        self.assertEqual(x["true_resource_height_K_grid"],[12,24,96,384,1536])
        self.assertGreater(
            x["sourcefree_two_world_M2_minus_M1_height_gain"]["true_resource_height_effect"]["corrected"],0)
        self.assertLess(
            x["true_resource_height_corrected_mae_nats"][-1],
            x["true_resource_height_corrected_mae_nats"][0])
        self.assertLess(
            x["true_resource_height_corrected_mae_nats"][-1],
            x["true_resource_height_uncorrected_mae_nats"][-1])
        self.assertTrue(x["no_general_K_threshold_established"])
        self.assertFalse(x["source_original_q_or_height_sensor_calibrated"])
        self.assertTrue(x["no_source_Goldshtein_raw_GPS_or_dated_flowers_opened"])
        self.assertIsNone(x["empirical_source_resource_height_gain"])
        self.assertFalse(x["continuous_full_ssf3d_reproduction_estimated"])
        self.assertFalse(x["regional_ecological_species_occupancy_estimated"])
        self.assertIsNone(self.data["strict_unestimated"]["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_real_plos_source_three_paired_bat_height_transfer_remains_exploratory(self):
        a=self.data["plos2016_original_three_paired_bat_exploratory_20261121"]
        self.assertEqual(a["n_source_bats_all"],5)
        self.assertEqual(a["n_bats_full_both_targets"],3)
        self.assertEqual(a["n_distinct_eligible_source_trials"],24)
        self.assertEqual(a["n_real_three_dimensional_recorded_frames_eligible"],2671)
        self.assertEqual(a["n_positive_animal_folds"],0)
        self.assertAlmostEqual(
            a["equal_bat_mean_target_class_height_gain_nats_per_frame"],
            -0.02970719061394642,places=12)
        self.assertTrue(all(g<0 for g in
            a["cross_bat_fold_gains_nats_per_recorded_frame"]))
        self.assertEqual(a["original_five_bat_completely_paired_protocol_status"],
                         "STOP_UNPAIRED_SOURCE")
        self.assertTrue(a["changed_hypothesis_support_after_original_failure_exploratory_only"])
        self.assertFalse(a["any_population_general_or_confirmatory_0_05_claim"])
        self.assertTrue(a["real_source_target_class_not_local_food_abundance"])
        self.assertIsNone(a["actual_wild_resource_height_gain_estimated"])
        self.assertFalse(a["raw_original_XYZ_or_bat_ids_committed"])
        self.assertIsNone(self.data["strict_unestimated"]
                          ["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_hermans_2023_dataverse_is_restricted_and_not_food(self):
        x=self.data["hermans_lidar_original_source_audit_20261121"]
        self.assertEqual(x["publisher_original_files_listed"],9)
        self.assertEqual(x["officially_restricted_file_count"],9)
        self.assertFalse(x["original_source_bat_xyz_files_accessible_in_this_session"])
        self.assertFalse(x["source_plant_food_amount_measured"])
        self.assertTrue(x["request_access_needed_to_open"])
        self.assertTrue(x["not_a_direct_true_resource_height_source"])

    def test_plos_three_bat_secondary_personal_vs_other_bats_negative_and_not_confirmatory(self):
        x=self.data["plos2016_real_secondary_personal_vs_coldstart_20261121"]
        self.assertEqual(x["independent_bat_clusters"],3)
        self.assertEqual(x["original_eligible_target_trials"],24)
        self.assertEqual(x["original_eligible_3d_frames"],2671)
        self.assertTrue(x["exact_frozen_previous_coldstart_value_reproduced_within_1e11"])
        self.assertAlmostEqual(x["equal_bat_personal_target_gain"],
                               -0.013035798777869817,places=12)
        self.assertAlmostEqual(x["equal_bat_coldstart_target_gain"],
                               -0.029707190613945514,places=12)
        self.assertAlmostEqual(x["personal_minus_coldstart_increment"],
                                0.0166713918360757,places=12)
        self.assertEqual(x["n_personal_target_gain_positive_bats"],0)
        self.assertEqual(x["n_coldstart_target_gain_positive_bats"],0)
        self.assertTrue(all(v<0 for v in x["personal_target_increments_by_bat_nats_per_frame"]))
        self.assertTrue(all(v<0 for v in x["coldstart_target_increments_by_bat_nats_per_frame"]))
        self.assertTrue(x["unequal_training_trial_counts_prevent_causal_mechanism_attribution"])
        self.assertTrue(x["post_outcome_exploration_closed_after_this_fixed_comparison"])
        self.assertTrue(x["original_5_bat_confirmatory_paired_support_gate_still_stop"])
        self.assertFalse(x["not_new_independent_study"] is False)
        self.assertFalse(x["not_true_food_nectar_resource_quantity"] is False)
        self.assertIsNone(x["field_resource_conditioned_3d_height_gain"])
        self.assertFalse(x["real_animal_xyz_or_trial_ids_committed"])
        self.assertIsNone(self.data["strict_unestimated"]
                          ["higher_dim_resource_conditional_bat_logscore_gain"])

    def test_goldshtein_uploaded_original_xy_is_only_spatial_eligibility_not_resource_height(self):
        r=self.data["goldshtein_uploaded_source_xy_audit_20261122"]
        self.assertEqual(r["n_tracking_animal_folders"],17)
        self.assertEqual(r["n_cactus_map_files"],8)
        self.assertEqual(r["n_cactus_map_rows"],2483)
        self.assertEqual(r["n_valid_rmc_fixes_raw"],205166)
        self.assertEqual(r["n_mapped_bat_time_xy_deduplicated"],105580)
        self.assertEqual(r["n_mapped_bat_fixes_in_cactus_convex_hull"],42562)
        self.assertTrue(r["convex_hull_NOT_original_survey_polygon"])
        self.assertFalse(r["publisher_digest_verified"])
        self.assertFalse(r["terrain_relative_AGL_and_uncertainty_independently_validated"])
        self.assertFalse(r["original_legacy_open_flowers_xls_schema_decoded"])
        self.assertFalse(r["source_video_bat_and_cactus_keys_joined"])
        self.assertFalse(r["any_new_fitted_wild_resource_height_gain"])
        self.assertIsNone(r["empirical_resource_height_gain"])
        self.assertIsNone(r["regional_species_SDM_gain"])
        self.assertIsNone(self.data["strict_unestimated"]
                          ["higher_dim_resource_conditional_bat_logscore_gain"])
        self.assertTrue(r["no_original_xy_or_height_values_or_animal_ids_committed"])

    def test_no_frozen_manuscript_or_parent_main_overwrite(self):
        self.assertFalse(self.data["changes_to_frozen_bat_manuscripts"])
        self.assertFalse(self.data["changes_to_esdm_main"])


if __name__ == "__main__":
    unittest.main()
