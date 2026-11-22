"""Frozen two-world source-free q-stratified noisy AGL sensitivity receipt.

All source trajectories are synthetic. No original Goldshtein source bytes.
The two worlds have the SAME observed-target setup and q sampling protocol;
only the simulated resource×altitude data-generating relation differs.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

from q_stratified_noisy_height_bridge_v1 import compare_q_noise
from test_q_stratified_noisy_height_bridge_v1 import q_sampled_noisy

FROZEN=(
    ("no_true_resource_effect","null"),
    ("true_resource_by_height","resource_agl"),
)
N_BATS=6
N_NIGHTS=2
STEPS_PER_NIGHT=4
Q_CONTROLS_PER_XY=24
Q_SEED=889
Q_SITE_TILT=1.7
GPS_OBS_SD_M=11.0

def run():
    scenarios=[]
    for name,world in FROZEN:
        rows=q_sampled_noisy(world=world,n_bats=N_BATS,
                             steps=STEPS_PER_NIGHT,
                             n_per_xy=Q_CONTROLS_PER_XY,
                             seed=Q_SEED,source_q_shift=Q_SITE_TILT)
        model=compare_q_noise(rows,heldout="site")
        scores=model["per_model_group_equal_scores"]
        gains=model["nested_group_equal_gains"]
        m2="M2_resource_by_height"
        both={mode:{"joint":scores[m2][mode]["joint"],
                    "horizontal":scores[m2][mode]["horizontal"],
                    "height_given_horizontal":
                        scores[m2][mode]["height_given_horizontal"]}
              for mode in ("corrected_importance","uncorrected_q_sampling")}
        scenarios.append({
            "world":name,
            "simulated_direct_resource_height_coefficient_nonzero":
                world=="resource_agl",
            "source_free_number_of_bats":model["n_bats"],
            "source_free_recorded_xy_noisy_agl_events":model["n_source_free_events"],
            "heldout_entire_sites":model["n_folds"],
            "minimum_q_effective_sample_fraction":
                model["min_importance_effective_sample_fraction"],
            "minimum_z_support_coverage":
                model["min_sampled_z_support_fraction"],
            "m2_joint_observation_log_scores":both,
            "m2_minus_m1_paired_gains":
                gains["M2_resource_by_height_minus_M1_add_resource_xy"],
            "source_original_animals_or_tracks_reported":False,
        })
    return {
        "schema":"batter.q_stratified_noisy_AGL_known_truth_receipt.v1",
        "status":"SOURCE_FREE_TWO_WORLD_BAT_PSEUDODATA_ONLY",
        "fixed_model_family":"nested M0 M1 M2 source-free ridge height measurement density",
        "observed_likelihood":"Normal(noisyAGL | trueZ,knownSigma), XY exact",
        "q_integration":"stratified Monte Carlo mu_xy*(mu_z/q_z)/n_draws_xy",
        "not_case_control_selected_label_likelihood":True,
        "not_continuous_ssf3d":True,
        "n_fictional_bats":N_BATS,
        "n_fictional_nights":N_BATS*N_NIGHTS,
        "n_fictional_event_steps":N_BATS*N_NIGHTS*STEPS_PER_NIGHT,
        "n_independent_source_studies":0,
        "known_noise_std_m_not_real_sensor_calibration":GPS_OBS_SD_M,
        "proposal_q_controls_per_xy":Q_CONTROLS_PER_XY,
        "site_proposal_tilt_positive_negative":Q_SITE_TILT,
        "q_seed":Q_SEED,
        "original_goldshtein_mendeley_archive_read":False,
        "original_dated_bloom_x_gps_height_join_verified":False,
        "empirical_bat_3d_resource_effect":None,
        "scenarios":scenarios
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    a=p.parse_args()
    obj=run()
    target=Path(a.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n")
    print("SOURCE_FREE_Q_GPS_NOISE_TWO_WORLDS",len(obj["scenarios"]))
    for x in obj["scenarios"]:
        print(x["world"],"q_ESS_min",
              round(x["minimum_q_effective_sample_fraction"],3),
              "M2_corrected_joint",
              round(x["m2_joint_observation_log_scores"]
                    ["corrected_importance"]["joint"],6),
              "M2_uncorrected_joint",
              round(x["m2_joint_observation_log_scores"]
                    ["uncorrected_q_sampling"]["joint"],6),
              "M2-M1_height_corrected",
              round(x["m2_minus_m1_paired_gains"]
                    ["corrected_importance"]["height_given_horizontal"],6))
    print("ORIGINAL_BAT_RESULTS_ESTIMATED",obj["empirical_bat_3d_resource_effect"])

if __name__=="__main__":
    main()
