"""Source-open Ducke post-hoc food-genera discrimination.

This code does NOT reopen original source, infer food absences, or store
original sample IDs. Expects hash-gated matched aggregate plot rows from
ducke_original_adapter_v1. Independent group heldout uses the existing
ridge-fractional-binomial scorer in ducke_guild_cv_engine_v1.
"""
from __future__ import annotations
import json
import math
from collections import Counter
from pathlib import Path
from ducke_guild_cv_engine_v1 import predict, _score

BASE=("elevation_m","design_added_riparian_plot","n_matched_nights")
MODELS={
 "baseline":BASE,
 "food12":BASE+("fruit_batfood_12",),
 "other10":BASE+("fruit_other",),
 "food12_and_other10":BASE+("fruit_batfood_12","fruit_other"),
 "all22_sum":BASE+("fruit_all",),
}
GUILDS=("frug","glean","nectar")


def _evaluate(rows, guild, leave_unit="block"):
    if leave_unit not in ("block","plot"):
        raise ValueError("STOP_UNSUPPORTED_FOLD_UNIT")
    if len(rows)<25 or len({r["plot"] for r in rows})!=len(rows):
        raise ValueError("STOP_SMALL_OR_DUPLICATED_PLOT_SOURCE")
    groups=sorted({r[leave_unit] for r in rows})
    if len(groups)<5:raise ValueError("STOP_TOO_FEW_SOURCE_GROUPS")
    folds=[]
    for g in groups:
        train=[r for r in rows if r[leave_unit]!=g]
        test=[r for r in rows if r[leave_unit]==g]
        # All model scores computed on IDENTICAL source observations.
        scores={name:_score(test,predict(train,test,cols,guild),guild)
                for name,cols in MODELS.items()}
        c={
            "food_given_other":scores["food12_and_other10"]-scores["other10"],
            "other_given_food":scores["food12_and_other10"]-scores["food12"],
            "food_vs_other":scores["food12"]-scores["other10"],
            "two_axes_vs_total":scores["food12_and_other10"]-scores["all22_sum"],
            "food_minus_baseline":scores["food12"]-scores["baseline"],
            "other_minus_baseline":scores["other10"]-scores["baseline"],
            "both_minus_baseline":scores["food12_and_other10"]-scores["baseline"],
        }
        folds.append({"fold_ordinal":len(folds)+1,"n_source_plots":len(test),"contrasts":c})
    keys=list(folds[0]["contrasts"])
    return {
        "n_source_plots":len(rows),"n_outer_groups":len(groups),
        "group_equal_mean":{k:math.fsum(f["contrasts"][k] for f in folds)/len(folds) for k in keys},
        "plot_equal_mean":{k:math.fsum(f["contrasts"][k]*f["n_source_plots"] for f in folds)/len(rows) for k in keys},
        "positive_fold_counts":{k:sum(f["contrasts"][k]>0 for f in folds) for k in keys},
        "fold_ordinal_only":folds if leave_unit=="block" else [],
        "source_ids_or_positions_stored":False,
    }


def run(plots):
    rows=[dict(r) for r in plots]
    if len(rows)!=46 or sum(r["captures"] for r in rows)!=810 or sum(r["frug"] for r in rows)!=573:
        raise ValueError("STOP_ORIGINAL_DUCKE_SOURCE_ELIGIBILITY_DRIFT")
    if len(set(r["block"] for r in rows))!=7 or sum(r["block"]=="PO" for r in rows)!=17:
        raise ValueError("STOP_RAPELD_SOURCE_DESIGN_CHANGED")
    l=[r for r in rows if r["block"]!="PO"]
    if len(l)!=29 or len(set(r["block"] for r in l))!=6:
        raise ValueError("STOP_SOURCE_DESIGN_RESTRICTION_CHANGED")
    analysis={}
    for guild in GUILDS:
        analysis[guild]={
            "seven_all_layout_blocks":_evaluate(rows,guild,"block"),
            "leave_plot_out_sensitivity":_evaluate(rows,guild,"plot"),
            "six_L3_L8_only_blocks":_evaluate(l,guild,"block"),
        }
    expected=0.016084661100832526
    actual=analysis["frug"]["seven_all_layout_blocks"]["group_equal_mean"]["food_minus_baseline"]
    if not math.isclose(actual,expected,rel_tol=0,abs_tol=1e-7):
        raise ValueError("STOP_ORIGINAL_V1_FOOD_GAIN_NOT_REPRODUCED")
    return {
        "schema":"batter.ducke.conditional_fruit_12_vs_other_10_source_local.v2",
        "status":"POST_OUTCOME_SOURCE_LOCAL_EXPLORATORY_ONLY",
        "input_source_doi":"10.5061/dryad.9rb48c5",
        "n_eligible_source_plots":46,
        "n_eligible_captures":810,
        "models":{k:list(v) for k,v in MODELS.items()},
        "responses":analysis,
        "publication_level_independence":False,
        "food10_is_true_negative_control":False,
        "vegetation_clutter_adjusted":False,
        "original_observation_rows_or_coordinates_committed":False,
        "measured_resource_conditional_3D_height_gain":None,
        "regional_species_occupancy_SDM_gain":None,
    }


def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--qualified-private-plots",required=True)
    ap.add_argument("--aggregate-output",required=True)
    args=ap.parse_args()
    plots=json.loads(Path(args.qualified_private_plots).read_text(encoding="utf-8"))
    receipt=run(plots)
    Path(args.aggregate_output).write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("DUCKE_12_VS_10_SOURCE_OPEN",receipt["status"],"ANALYZED_PLOTS",receipt["n_eligible_source_plots"])
    for k in GUILDS:
        x=receipt["responses"][k]["seven_all_layout_blocks"]
        print(k,"food_given_other",x["group_equal_mean"]["food_given_other"],
              "other_given_food",x["group_equal_mean"]["other_given_food"],
              "positive",x["positive_fold_counts"]["food_given_other"],
              "/",x["n_outer_groups"])

if __name__=="__main__":
    main()
