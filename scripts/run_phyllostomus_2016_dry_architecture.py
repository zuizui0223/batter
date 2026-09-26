#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

import numpy as np

import scripts.run_new_species_replications as core

CONTRACT_PATH=Path("contract/phyllostomus_2016_dry_architecture_v1.json")


def normalize(contract, field):
    c=copy.deepcopy(contract)
    c["vertical"]={
      "field":field,
      "primary_edges_m":contract["vertical"]["edges_m"],
    }
    return c


def architecture_counts(summary):
    vals=[
      v for v in summary["individual_results"].values()
      if v.get("mean_conditional_identity_gain") is not None
    ]
    marg=np.array([v["mean_marginal_identity_gain"] for v in vals],dtype=float)
    inter=np.array([v["mean_identity_x_location_increment"] for v in vals],dtype=float)
    return {
      "evaluable_individual_count":len(vals),
      "positive_marginal_individual_fraction":float(np.mean(marg>0)) if len(marg) else None,
      "negative_identity_x_location_individual_fraction":float(np.mean(inter<0)) if len(inter) else None,
      "median_marginal_identity_gain":float(np.median(marg)) if len(marg) else None,
      "median_identity_x_location_increment":float(np.median(inter)) if len(inter) else None,
    }


def checks(summary):
    extra=architecture_counts(summary)
    return {
      "minimum_evaluable_individuals":extra["evaluable_individual_count"]>=6,
      "mean_marginal_identity_positive":(summary["equal_individual_mean_marginal_identity_gain"] or -1e300)>0,
      "majority_marginal_positive":(extra["positive_marginal_individual_fraction"] or 0)>0.5,
      "mean_identity_x_location_negative":(summary["equal_individual_mean_identity_x_location_increment"] if summary["equal_individual_mean_identity_x_location_increment"] is not None else 1e300)<0,
      "majority_identity_x_location_negative":(extra["negative_identity_x_location_individual_fraction"] or 0)>0.5,
      "marginal_exceeds_conditional":(
        summary["equal_individual_mean_marginal_identity_gain"] is not None
        and summary["equal_individual_mean_conditional_identity_gain"] is not None
        and summary["equal_individual_mean_marginal_identity_gain"]>summary["equal_individual_mean_conditional_identity_gain"]
      ),
    }


def compact(summary):
    extra=architecture_counts(summary)
    return {
      "cell_size_m":summary["cell_size_m"],
      "evaluable_individual_count":summary["evaluable_individual_count"],
      "equal_individual_mean_conditional_identity_gain":summary["equal_individual_mean_conditional_identity_gain"],
      "equal_individual_mean_marginal_identity_gain":summary["equal_individual_mean_marginal_identity_gain"],
      "equal_individual_mean_identity_x_location_increment":summary["equal_individual_mean_identity_x_location_increment"],
      "positive_conditional_individual_fraction":summary["positive_conditional_individual_fraction"],
      **extra,
      "cohort_summaries":summary["cohort_summaries"],
    }


def main():
    contract=json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    ua=contract["study_id"]+"/1.0"
    gps=core.get(contract["source"]["gps"],ua)
    ref=core.get(contract["source"]["reference"],ua)
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)

    primary_contract=normalize(contract,contract["vertical"]["primary_field"])
    pre=core.build_pre_numeric(rows,headers,refs,primary_contract)
    if not pre["admitted_cohorts"]:
        payload={
          "study_id":contract["study_id"],
          "status":"structurally_unavailable",
          "numeric_height_opened":False,
          "pre_numeric_structure":core.compact_pre(pre),
        }
    else:
        primary=core.analyze(rows,pre,primary_contract,float(contract["horizontal"]["primary_cell_size_m"]))
        spatial={
          str(int(cs)):core.analyze(rows,pre,primary_contract,float(cs))
          for cs in contract["horizontal"]["sensitivity_cell_sizes_m"]
        }
        semantic_contract=normalize(contract,contract["vertical"]["semantic_sensitivity_field"])
        semantic=core.analyze(rows,pre,semantic_contract,float(contract["horizontal"]["primary_cell_size_m"]))
        rule=checks(primary)
        payload={
          "study_id":contract["study_id"],
          "status":"evaluated",
          "numeric_height_opened":True,
          "pre_numeric_structure":core.compact_pre(pre),
          "primary_msl":primary,
          "primary_architecture_summary":compact(primary),
          "spatial_sensitivities":{k:compact(v) for k,v in spatial.items()},
          "ellipsoid_semantic_sensitivity":compact(semantic),
          "prediction_rule_checks":rule,
          "prediction_supported":all(rule.values()),
          "claim_boundary":contract["claim_boundary"],
        }

    out=Path("results/phyllostomus_2016_dry_architecture_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":payload["status"],
      "admitted_cohorts":payload.get("pre_numeric_structure",{}).get("admitted_cohorts"),
      "primary_architecture_summary":payload.get("primary_architecture_summary"),
      "spatial_sensitivities":payload.get("spatial_sensitivities"),
      "ellipsoid_semantic_sensitivity":payload.get("ellipsoid_semantic_sensitivity"),
      "prediction_rule_checks":payload.get("prediction_rule_checks"),
      "prediction_supported":payload.get("prediction_supported"),
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
