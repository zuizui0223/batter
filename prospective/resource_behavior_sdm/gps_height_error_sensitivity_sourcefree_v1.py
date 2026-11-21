"""Produce pinned source-free GPS AGL uncertainty sensitivity results.

No wild animal or publication original rows. Worlds and sigma grid are
fixed in advance, so signs cannot be selected after observing outcomes.
"""
from __future__ import annotations
import argparse
import json
import pathlib

from gps_height_error_likelihood_v1 import evaluate_error_noise
from test_gps_height_error_likelihood_v1 import noisy_observations

GRID=(
    ("true_resource_height", "resource_agl", .5, False),
    ("true_resource_height", "resource_agl", 11.0, False),
    ("true_resource_height", "resource_agl", 25.0, False),
    ("no_resource_effect", "null", 11.0, False),
    ("true_resource_height_heterogeneous_observation_sd",
     "resource_agl", 11.0, True),
)
N_BATS=6
STEPS_PER_BAT_NIGHT=5
SENSOR_NOISE_RANDOM_SEED=20261121
HELDOUT="site"


def run():
    trials=[]
    for tag,world,sigma,heterogeneous in GRID:
        events=noisy_observations(
            world=world,sigma=sigma,n_bats=N_BATS,
            steps=STEPS_PER_BAT_NIGHT,
            seed=SENSOR_NOISE_RANDOM_SEED,heterogeneous=heterogeneous)
        receipt=evaluate_error_noise(events,holdout=HELDOUT)
        if receipt["n_holdout_groups"]!=2:
            raise AssertionError("STOP_EXPECTED_TWO_WHOLE_SOURCE_SITES")
        m2="M2_resource_by_height"
        naive_vs_aware=[
            fold["per_model_scores"][m2]["sensor_aware"]["joint"]-
            fold["per_model_scores"][m2]["hard_bin_naive"]["joint"]
            for fold in receipt["fold_aggregates_without_identifying_keys"]]
        dg="M2_resource_by_height_minus_M1_add_resource_xy"
        trials.append({
            "scenario":tag,
            "synthetic_true_causal_resource_height_effect":
                world=="resource_agl",
            "nominal_sensor_sigma_m":sigma,
            "heterogeneous_by_xy":heterogeneous,
            "n_bats":receipt["n_fictional_or_source_bats"],
            "n_observed_events":receipt["n_observed_events"],
            "n_disjoint_site_folds":receipt["n_holdout_groups"],
            "sensor_sigma_used_m":receipt["sensor_sd_values_m"],
            "m2_minus_m1":receipt["group_equal_gains_nats_per_recorded_fix"][dg],
            "m2_sensor_aware_minus_hard_bin_joint_score_equal_site":
                sum(naive_vs_aware)/len(naive_vs_aware),
            "fold_scores_without_source_ids":naive_vs_aware,
        })
    return {
        "schema":"batter.source_free_gps_height_uncertainty_sensitivity.v1",
        "status":"PREDECLARED_FIVE_KNOWN_TRUTH_SCENARIOS_NO_FIELD_BAT_DATA",
        "scenario_count":len(trials),
        "original_source_animal_rows_opened":False,
        "goldshtein_same_night_resource_height_join_verified":False,
        "source_gps_sensor_sd_calibrated_from_publisher":False,
        "is_original_bat_field_result":False,
        "is_q_sampled_3d_ssf_integrated":False,
        "height_error_sd_11m_is_ILLUSTRATIVE_not_verified_sensor_calibration":True,
        "holdout_unit":HELDOUT,
        "primary_estimand":"same noisy XY+AGL observed density, M2-M1 conditional height score",
        "tested_sensor_sd_m":[.5,11,25],
        "scenarios":trials,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",required=True)
    opt=ap.parse_args()
    receipt=run()
    dest=pathlib.Path(opt.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",
                    encoding="utf-8")
    print("GPS_NOISE_SCENARIOS",receipt["scenario_count"])
    for trial in receipt["scenarios"]:
        g=trial["m2_minus_m1"]
        print("SCENARIO",trial["scenario"],
              "sigma_m",trial["nominal_sensor_sigma_m"],
              "delta_height_aware",round(g["sensor_aware"]["height_given_horizontal"],6),
              "delta_height_naive",round(g["hard_bin_naive"]["height_given_horizontal"],6),
              "aware_vs_naive",round(trial["m2_sensor_aware_minus_hard_bin_joint_score_equal_site"],6))
    print("SOURCE_OUTCOMES_OPENED",receipt["original_source_animal_rows_opened"])


if __name__=="__main__":
    main()
