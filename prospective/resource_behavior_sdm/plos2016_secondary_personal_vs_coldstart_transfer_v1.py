"""Secondary POST-OUTCOME PLOS 2016 3 paired bats: same-trial heldout personal vs cold-start.

This deliberately does not change or rescue the earlier failed 5-bat
pre-outcome paired gate or the first 3-bat LOBO exploratory negative result.
No original XYZ/IDs/trial rows exported; all source read in Actions RAM only.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import math
from pathlib import Path
import sys

from plos2016_three_paired_bats_exploratory_transfer_v1 import (
    ALPHA, SHA, SOURCE, _source_rows_after_gate, _train, _bin, fetch_official
)

STATUS="PLOS_3_BAT_SECONDARY_POST_OUTCOME_WITHIN_VS_BETWEEN_ONLY"
FROZEN_CROSS_BAT_MEAN=-0.02970719061394642


def _single_test_trial_delta(trial,model):
    radii,heights,base,specific=model
    original=trial["target"]
    total=0.
    for radius,z in trial["frames"]:
        rb=_bin(radius,radii)
        zb=_bin(z,heights)
        a=base[rb]
        b=specific[rb,original]
        pbase=(a[zb]+ALPHA)/(math.fsum(a)+5*ALPHA)
        pspecific=(b[zb]+ALPHA)/(math.fsum(b)+5*ALPHA)
        total+=math.log(pspecific/pbase)
    return total/len(trial["frames"])


def secondary_within_vs_other_bats_original(payload, enforce_frozen_coldstart=True):
    trials=_source_rows_after_gate(payload)
    bats=sorted({trial["bat"] for trial in trials})
    if len(bats)!=3 or len(trials)!=24:
        raise ValueError("STOP_SECONDARY_THREE_BAT_STRUCTURE_DRIFT")
    bybat=defaultdict(lambda:defaultdict(lambda:defaultdict(list)))
    for heldout in trials:
        bat=heldout["bat"]
        personal=[a for a in trials if a["bat"]==bat and
                  a["group"]!=heldout["group"]]
        cold=[a for a in trials if a["bat"]!=bat]
        if (len(personal)!=7 or len(cold)!=16 or
            {x["target"] for x in personal}!={0,1} or
            {x["target"] for x in cold}!={0,1}):
            raise ValueError("STOP_SECONDARY_MISSING_SEEN_BAT_TARGET_TRAINING")
        within=_single_test_trial_delta(heldout,_train(personal))
        outgroup=_single_test_trial_delta(heldout,_train(cold))
        bybat[bat][heldout["target"]]["personal_trial"].append(within)
        bybat[bat][heldout["target"]]["other_bats"].append(outgroup)
    bat_rows=[]
    for ordinal,bat in enumerate(bats,1):
        model_values={}
        for mode in ("personal_trial","other_bats"):
            target_effects=[]
            for category in (0,1):
                values=bybat[bat][category][mode]
                if not values or len(values)<3:
                    raise ValueError("STOP_SECONDARY_HELDOUT_CELLS_TOO_SMALL")
                target_effects.append(math.fsum(values)/len(values))
            model_values[mode]=math.fsum(target_effects)/2
        bat_rows.append({
            "anonymous_bat_ordinal":ordinal,
            "heldout_trials":8,
            "personal_trial_target_increment":model_values["personal_trial"],
            "other_bats_target_increment":model_values["other_bats"],
            "personal_minus_other_bat_target_increment":
               model_values["personal_trial"]-model_values["other_bats"],
        })
    summary={field:math.fsum(row[field] for row in bat_rows)/len(bat_rows)
             for field in ("personal_trial_target_increment",
                           "other_bats_target_increment",
                           "personal_minus_other_bat_target_increment")}
    if (enforce_frozen_coldstart and
        abs(summary["other_bats_target_increment"]-FROZEN_CROSS_BAT_MEAN)>1e-11):
        raise ValueError("STOP_PRIOR_ORIGINAL_COLD_START_RESULT_NOT_REPRODUCED")
    return {
        "schema":"batter.PLOS2016_secondary_within_trial_vs_other_bats.v1",
        "status":STATUS,
        "original_PLOS_S1_sha256":SHA,
        "original_supplement_doi":SOURCE,
        "analysis_timing":"POST_FIRST_SOURCE_XYZ_OUTCOME_EXPLORATORY_ONLY",
        "precommitted_secondary_protocol":"PLOS2016_SECONDARY_WITHIN_VS_BETWEEN_TRIAL_FROZEN_20261121.md",
        "original_five_bat_fully_paired_gate":"STOP",
        "real_source_paired_bats":3,
        "real_source_heldout_trial_sequences":24,
        "real_source_recorded_3d_frames":sum(len(e["frames"]) for e in trials),
        "personal_model_training_other_trials_of_same_bat":7,
        "cold_start_training_trials_from_two_other_bats":16,
        "same_heldout_target_events_between_models":True,
        "mean_bat_equal_target_equal_deltas_nats_per_frame":summary,
        "n_positive_bat_folds":{
            mode:sum(row[mode]>0 for row in bat_rows)
            for mode in ("personal_trial_target_increment",
                         "other_bats_target_increment")},
        "bat_level_results_without_real_source_ids":bat_rows,
        "different_training_sample_sizes_cannot_isolate_personal_mechanism":True,
        "not_population_inference":True,
        "not_3d_wild_food_availability":True,
        "real_wild_bat_resource_height_gain":None,
        "raw_original_animal_ids_xyz_or_source_rows_committed":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",required=True)
    args=p.parse_args()
    try:
        out=secondary_within_vs_other_bats_original(fetch_official())
    except Exception as exc:
        out={
          "schema":"batter.PLOS2016_secondary_within_trial_vs_other_bats.v1",
          "status":"SECONDARY_SOURCE_OR_VALIDITY_STOP",
          "original_five_bat_fully_paired_gate":"STOP",
          "reason":(type(exc).__name__+":"+str(exc))[:200],
          "real_wild_bat_resource_height_gain":None,
          "raw_original_animal_ids_xyz_or_source_rows_committed":False,
        }
    target=Path(args.out)
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(out,indent=2)+"\n")
    print("PLOS3_SECONDARY",out["status"])
    if out["status"]==STATUS:
        print("PERSONAL_MINUS_CROSSBAT",
              out["mean_bat_equal_target_equal_deltas_nats_per_frame"]
                 ["personal_minus_other_bat_target_increment"])
        print("PERSONAL_TARGET_PREDICTION_GAINS",
              out["n_positive_bat_folds"]["personal_trial_target_increment"])
    else:
        print("SOURCE_STOP",out["reason"])
    return 0 if out["status"]==STATUS else 3


if __name__=="__main__":
    sys.exit(main())
