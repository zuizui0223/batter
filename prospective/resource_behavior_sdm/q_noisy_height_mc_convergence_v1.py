"""Precommitted source-free finite-importance K convergence vs exact XY×Z grid.

Not a new biological/causal resource effect. The evaluation coefficient and
K/seed/support grids are frozen in Q_NOISY_HEIGHT_MC_CONVERGENCE_FREEZE_V1.md.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
import math
from pathlib import Path

from gps_height_error_likelihood_v1 import score_observed
from paired_3d_ssf_resource_benchmark_v1 import LEVELS
from q_stratified_noisy_height_bridge_v1 import (
    attach_mc_log_weights, validate_q_noisy_events,
)
from test_q_stratified_noisy_height_bridge_v1 import q_sampled_noisy
from test_gps_height_error_likelihood_v1 import noisy_observations

K_GRID=(12,24,96,384,1536)
TRUE_WORLD="resource_agl"
N_BATS=6
STEPS_PER_NIGHT=4
SIGMA_M=11.0
NOISE_SEED=20261121
Q_SEED=889
SITE_TILT=1.7
FIELDS=LEVELS["M2_resource_by_height"]
BETA=(0.,0.,0.,0.,0.,-.08,.12,.45)


def _fixed_model():
    return {
        "fields":FIELDS,
        "center":[0.] * len(FIELDS),
        "scale":[1.] * len(FIELDS),
        "beta":list(BETA)
    }


def _equal_bat_mean(rows, field):
    buckets=defaultdict(lambda:defaultdict(list))
    for bat, night, metric in rows:
        buckets[bat][night].append(metric[field])
    return math.fsum(
        math.fsum(math.fsum(v)/len(v) for v in nights.values())/len(nights)
        for nights in buckets.values())/len(buckets)


def run():
    originals=noisy_observations(world=TRUE_WORLD,n_bats=N_BATS,
                                  steps=STEPS_PER_NIGHT,
                                  sigma=SIGMA_M,seed=NOISE_SEED)
    m=_fixed_model()
    reference=[score_observed(m,e) for e in originals]
    all_rows=[]
    for K in K_GRID:
        sampled=q_sampled_noisy(world=TRUE_WORLD,n_bats=N_BATS,
                                 steps=STEPS_PER_NIGHT,n_per_xy=K,
                                 seed=Q_SEED,source_q_shift=SITE_TILT)
        _,diag=validate_q_noisy_events(sampled)
        if any(any(e[col]!=originals[i][col] for col in
                   ("bat","site","night","step","observed_xy","observed_agl_m",
                    "sensor_sigma_m"))
               for i,e in enumerate(sampled)):
            raise AssertionError("STOP_DIFFERENT_OBSERVED_NOISY_TARGETS_BETWEEN_K")
        corrected=attach_mc_log_weights(sampled,True)
        naive=attach_mc_log_weights(sampled,False)
        compared={"corrected":[], "naive":[]}
        for i,orig in enumerate(originals):
            for label,rows in (("corrected",corrected),("naive",naive)):
                got=score_observed(m,rows[i])
                exact=reference[i]
                metrics={
                  "joint_log_density_abs_error":
                      abs(got["joint"]-exact["joint"]),
                  "joint_log_density_signed_error":
                      got["joint"]-exact["joint"],
                  "height_log_density_abs_error":
                      abs(got["height_given_horizontal"]-
                          exact["height_given_horizontal"]),
                  "horizontal_log_probability_abs_error":
                      abs(got["horizontal"]-exact["horizontal"]),
                }
                compared[label].append((orig["bat"],orig["night"],metrics))
        all_rows.append({
          "candidates_per_xy":K,
          "min_effective_proposal_sample_fraction":
             min(x["min_effective_sample_fraction"] for x in diag),
          "min_distinct_z_coverage_fraction":
             min(x["sampled_z_coverage_min"] for x in diag),
          "metrics":{
             method:{field:_equal_bat_mean(rows,field)
                     for field in (
                         "joint_log_density_abs_error",
                         "joint_log_density_signed_error",
                         "height_log_density_abs_error",
                         "horizontal_log_probability_abs_error")}
             for method,rows in compared.items()}
        })
    return {
      "schema":"batter.q_noisy_AGL_fixed_coeff_importance_convergence.v1",
      "status":"SOURCE_FREE_POST_PRIOR_RESULT_PRECOMMITTED_K_DIAGNOSTIC",
      "freeze":"Q_NOISY_HEIGHT_MC_CONVERGENCE_FREEZE_V1.md",
      "world":TRUE_WORLD,
      "K_per_XY_grid":list(K_GRID),
      "source_free_bats":N_BATS,
      "source_free_recorded_gps_events":len(originals),
      "noise_sigma_m_illustrative":SIGMA_M,
      "coefficient_vector_fixed_unfitted":list(BETA),
      "same_recorded_GPS_events_for_all_K":True,
      "reference_model":"fully enumerated 2 XY × 3 altitude cells, fixed beta",
      "q_controls_not_constructed_from_observed_endpoint":True,
      "importance_MC_estimator_finite_sample_biased":True,
      "is_full_ssf3d":False,
      "original_Goldshtein_animal_resource_rows_opened":False,
      "ecological_resource_height_gain_estimated":None,
      "scenarios":all_rows
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",required=True)
    args=parser.parse_args()
    receipt=run()
    dest=Path(args.out)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(receipt,indent=2)+"\n")
    print("K_DIAGNOSTIC_SCENARIOS",len(receipt["scenarios"]))
    for x in receipt["scenarios"]:
        print("K",x["candidates_per_xy"],"ESSmin",
              round(x["min_effective_proposal_sample_fraction"],3),
              "MAE_corrected",
              round(x["metrics"]["corrected"]["joint_log_density_abs_error"],6),
              "MAE_naive",
              round(x["metrics"]["naive"]["joint_log_density_abs_error"],6))
    print("REAL_GOLDSHTEIN_GAIN",receipt["ecological_resource_height_gain_estimated"])


if __name__=="__main__":
    main()
