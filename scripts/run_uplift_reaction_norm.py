#!/usr/bin/env python3
from __future__ import annotations

import csv
from collections import defaultdict
import hashlib
import io
import json
import math
from pathlib import Path
import urllib.request

import numpy as np

URL = "https://datarepository.movebank.org/server/api/core/bitstreams/a6a6db33-0aca-4902-a58d-f32980c1a3e1/content"
EXPECTED_SIZE = 3630088
EXPECTED_MD5 = "e0f6faedfd1f21bac222d9da430ea5d8"
MIN_ROWS = 50
MIN_W_SD = 0.05
PERMUTATIONS = 9999
SEED = 220223


def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"batter-uplift-reaction-norm-v1/1.0"})
    with urllib.request.urlopen(req,timeout=120) as response:
        return response.read()


def finite_float(value):
    try:
        x=float(value)
    except (TypeError,ValueError):
        return None
    return x if math.isfinite(x) else None


def fit_ols(w, climb):
    w=np.asarray(w,dtype=float)
    y=np.asarray(climb,dtype=float)
    X=np.column_stack([np.ones(len(w)),w])
    beta=np.linalg.lstsq(X,y,rcond=None)[0]
    pred=X @ beta
    mse=float(np.mean((y-pred)**2))
    return float(beta[0]),float(beta[1]),mse


def mean_coeff(sessions):
    return (
        float(np.mean([s["intercept"] for s in sessions])),
        float(np.mean([s["slope"] for s in sessions])),
    )


def predict_mse(rows, coeff):
    intercept,slope=coeff
    errors=[(r["climb"]-(intercept+slope*r["w"]))**2 for r in rows]
    return float(np.mean(errors))


def permutation_repeatability(session_records, repeat_individuals):
    groups=[
        [s for s in session_records if s["individual"]==iid]
        for iid in repeat_individuals
    ]
    slopes=np.array([s["slope"] for group in groups for s in group],dtype=float)
    sizes=[len(g) for g in groups]

    def within_stat(values):
        pos=0
        total=0.0
        for n in sizes:
            block=values[pos:pos+n]
            pos+=n
            total+=float(np.sum((block-np.mean(block))**2))
        return total

    observed=within_stat(slopes)
    rng=np.random.default_rng(SEED)
    count=0
    for _ in range(PERMUTATIONS):
        shuffled=rng.permutation(slopes)
        if within_stat(shuffled) <= observed + 1e-15:
            count+=1
    p=(count+1)/(PERMUTATIONS+1)
    return observed,p,sizes


def main():
    data=download()
    if len(data)!=EXPECTED_SIZE:
        raise RuntimeError(f"source size mismatch {len(data)} != {EXPECTED_SIZE}")
    digest=hashlib.md5(data).hexdigest()
    if digest!=EXPECTED_MD5:
        raise RuntimeError(f"source md5 mismatch {digest}")

    reader=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    groups=defaultdict(list)
    total_rows=0
    finite_rows=0
    for row in reader:
        total_rows+=1
        individual=str(row.get("animal-id","")).strip()
        batday=str(row.get("BatDay","")).strip()
        w=finite_float(row.get("W.Component"))
        climb=finite_float(row.get("climb.rate"))
        agl=finite_float(row.get("height_true"))
        if not individual or not batday or w is None or climb is None:
            continue
        finite_rows+=1
        groups[(individual,batday)].append({"w":w,"climb":climb,"agl":agl})

    sessions=[]
    for (individual,batday),rows in sorted(groups.items()):
        w=[r["w"] for r in rows]
        if len(rows)<MIN_ROWS:
            status="too_few_rows"
        elif float(np.std(w,ddof=1))<MIN_W_SD:
            status="insufficient_w_variation"
        else:
            status="eligible"
        record={
            "individual":individual,
            "batday":batday,
            "session_id":f"{individual}::{batday}",
            "n":len(rows),
            "w_sd":float(np.std(w,ddof=1)) if len(rows)>1 else None,
            "status":status,
        }
        if status=="eligible":
            intercept,slope,mse=fit_ols(w,[r["climb"] for r in rows])
            agl_values=[r["agl"] for r in rows if r["agl"] is not None]
            record.update({
                "intercept":intercept,
                "slope":slope,
                "training_mse":mse,
                "median_agl_m":float(np.median(agl_values)) if agl_values else None,
                "rows":rows,
            })
        sessions.append(record)

    eligible=[s for s in sessions if s["status"]=="eligible"]
    by_individual=defaultdict(list)
    for s in eligible:
        by_individual[s["individual"]].append(s)

    repeat_individuals=sorted(i for i,v in by_individual.items() if len(v)>=2)
    target_results=[]
    for individual in repeat_individuals:
        for target in by_individual[individual]:
            self_train=[s for s in by_individual[individual] if s["session_id"]!=target["session_id"]]
            other_individuals=[i for i in sorted(by_individual) if i!=individual]
            other_mean_coeffs=[]
            other_mean_slopes=[]
            for other in other_individuals:
                coeff=mean_coeff(by_individual[other])
                other_mean_coeffs.append(coeff)
                other_mean_slopes.append(float(np.mean([s["slope"] for s in by_individual[other]])))
            if not other_mean_coeffs:
                continue
            self_coeff=mean_coeff(self_train)
            pop_coeff=(
                float(np.mean([x[0] for x in other_mean_coeffs])),
                float(np.mean([x[1] for x in other_mean_coeffs])),
            )
            self_slope=self_coeff[1]
            pop_slope=float(np.mean(other_mean_slopes))
            target_slope=target["slope"]
            slope_gain=abs(target_slope-pop_slope)-abs(target_slope-self_slope)
            self_mse=predict_mse(target["rows"],self_coeff)
            pop_mse=predict_mse(target["rows"],pop_coeff)
            target_results.append({
                "individual":individual,
                "session_id":target["session_id"],
                "target_slope":target_slope,
                "self_predicted_slope":self_slope,
                "population_predicted_slope":pop_slope,
                "slope_absolute_error_improvement":float(slope_gain),
                "self_target_mse":self_mse,
                "population_target_mse":pop_mse,
                "target_fix_mse_improvement":float(pop_mse-self_mse),
            })

    individual_results={}
    for individual in repeat_individuals:
        rows=[r for r in target_results if r["individual"]==individual]
        slope_gains=[r["slope_absolute_error_improvement"] for r in rows]
        mse_gains=[r["target_fix_mse_improvement"] for r in rows]
        individual_results[individual]={
            "eligible_sessions":len(by_individual[individual]),
            "mean_session_slope":float(np.mean([s["slope"] for s in by_individual[individual]])),
            "mean_slope_absolute_error_improvement":float(np.mean(slope_gains)),
            "positive_slope_error_session_fraction":float(np.mean(np.array(slope_gains)>0)),
            "mean_target_fix_mse_improvement":float(np.mean(mse_gains)),
            "positive_target_fix_mse_session_fraction":float(np.mean(np.array(mse_gains)>0)),
        }

    primary_values=[v["mean_slope_absolute_error_improvement"] for v in individual_results.values()]
    mse_values=[v["mean_target_fix_mse_improvement"] for v in individual_results.values()]
    observed_within,perm_p,group_sizes=permutation_repeatability(eligible,repeat_individuals)

    serializable_sessions=[]
    for s in sessions:
        serializable_sessions.append({k:v for k,v in s.items() if k!="rows"})

    payload={
        "study_id":"batter-uplift-reaction-norm-v1",
        "source":{"bytes":len(data),"md5":digest},
        "row_qc":{"total_rows":total_rows,"finite_primary_rows":finite_rows},
        "session_qc":{
            "session_count":len(sessions),
            "eligible_session_count":len(eligible),
            "repeat_individual_count":len(repeat_individuals),
            "repeat_individuals":repeat_individuals,
        },
        "primary":{
            "endpoint":"absolute slope error improvement: population error - self error",
            "equal_individual_mean_slope_absolute_error_improvement":float(np.mean(primary_values)) if primary_values else None,
            "positive_individual_fraction":float(np.mean(np.array(primary_values)>0)) if primary_values else None,
            "individual_results":individual_results,
            "target_session_results":target_results,
        },
        "secondary":{
            "equal_individual_mean_target_fix_mse_improvement":float(np.mean(mse_values)) if mse_values else None,
            "positive_mse_individual_fraction":float(np.mean(np.array(mse_values)>0)) if mse_values else None,
            "slope_identity_permutation":{
                "within_individual_sumsq":observed_within,
                "p_value":perm_p,
                "permutations":PERMUTATIONS,
                "seed":SEED,
                "group_sizes":group_sizes,
            },
        },
        "session_models":serializable_sessions,
        "claim_boundary":{
            "modeled_wind_not_experimental_manipulation":True,
            "foraging_not_verified":True,
            "individual_is_inference_unit_for_primary_summary":True,
            "post_primary_mechanism_analysis":True,
        },
    }
    out=Path("results/uplift_reaction_norm_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "row_qc":payload["row_qc"],
        "session_qc":payload["session_qc"],
        "primary":{
            "equal_individual_mean_slope_absolute_error_improvement":payload["primary"]["equal_individual_mean_slope_absolute_error_improvement"],
            "positive_individual_fraction":payload["primary"]["positive_individual_fraction"],
            "individual_results":individual_results,
        },
        "secondary":payload["secondary"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
