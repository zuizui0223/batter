#!/usr/bin/env python3
from __future__ import annotations

import itertools
import json
from collections import defaultdict
from pathlib import Path
import importlib.util
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location(
    "F", HERE/"flight_intensity_scalar_v1.py"
)
F=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(F)

B=9999
SEED=20261007601
MIN_TRAIN=3
MS=(1,2,3)

def centroid_table():
    rows,envs=F.load_scalar_rows()
    cm={}
    for e in envs:
        bats=sorted(set(r["bat"] for r in rows if r["env"]==e))
        for b in bats:
            vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==b]
            cm[(e,b)]=float(np.mean(vals))
    bats=sorted(set(b for _,b in cm))
    return cm,envs,bats

def target_records(cm,envs,bats):
    rec=[]
    for b in bats:
        observed=[e for e in envs if (e,b) in cm]
        for e0 in observed:
            train=[e for e in observed if e!=e0]
            if len(train)<MIN_TRAIN:
                continue
            y=float(cm[(e0,b)])
            full=float(np.mean([cm[(e,b)] for e in train]))
            q={
                "bat":b,"target_env":e0,"target":y,
                "n_training_envs":len(train),
                "full_pred":full,
                "zero_sq":y*y,
                "full_sq":(y-full)**2,
                "full_abs":abs(y-full),
                "m":{}
            }
            for m in MS:
                preds=[]
                for ss in itertools.combinations(train,m):
                    preds.append(float(np.mean([cm[(e,b)] for e in ss])))
                a=np.asarray(preds,float)
                err=y-a
                q["m"][str(m)]={
                    "n_subsets":len(preds),
                    "mean_sq":float(np.mean(err*err)),
                    "mean_abs":float(np.mean(np.abs(err))),
                    "theta_subset_sd":float(np.std(a,ddof=0)),
                    "theta_subset_min":float(np.min(a)),
                    "theta_subset_max":float(np.max(a)),
                }
            rec.append(q)
    return rec

def aggregate(records, sampled_bats=None):
    if sampled_bats is None:
        sampled_bats=sorted(set(r["bat"] for r in records))
    # sampled_bats may contain duplicates in bootstrap.
    per_instance=[]
    for b in sampled_bats:
        rr=[r for r in records if r["bat"]==b]
        if not rr:
            continue
        d={
            "zero_mse":float(np.mean([r["zero_sq"] for r in rr])),
            "full_mse":float(np.mean([r["full_sq"] for r in rr])),
            "full_mae":float(np.mean([r["full_abs"] for r in rr])),
        }
        for m in MS:
            k=str(m)
            d[f"mse_{m}"]=float(np.mean([r["m"][k]["mean_sq"] for r in rr]))
            d[f"mae_{m}"]=float(np.mean([r["m"][k]["mean_abs"] for r in rr]))
            d[f"theta_sd_{m}"]=float(np.mean([r["m"][k]["theta_subset_sd"] for r in rr]))
        per_instance.append(d)
    if not per_instance:
        raise RuntimeError("no bootstrap support")
    keys=per_instance[0].keys()
    out={k:float(np.mean([d[k] for d in per_instance])) for k in keys}
    for m in MS:
        out[f"r2_{m}"]=1.0-out[f"mse_{m}"]/out["zero_mse"]
        out[f"excess_{m}"]=out[f"mse_{m}"]-out["full_mse"]
    out["r2_full"]=1.0-out["full_mse"]/out["zero_mse"]
    out["delta_1to3"]=out["mse_1"]-out["mse_3"]
    denom=out["mse_1"]-out["full_mse"]
    for m in (2,3):
        out[f"fraction_to_full_{m}"]=(1.0-(out[f"mse_{m}"]-out["full_mse"])/denom) if denom>0 else float("nan")
    return out

def bootstrap(records,bats):
    rng=np.random.default_rng(SEED)
    observed=aggregate(records,bats)
    keys=[
        "mse_1","mse_2","mse_3",
        "r2_1","r2_2","r2_3",
        "delta_1to3",
        "fraction_to_full_2","fraction_to_full_3"
    ]
    vals={k:[] for k in keys}
    for _ in range(B):
        sample=list(rng.choice(np.asarray(bats,dtype=object),size=len(bats),replace=True))
        q=aggregate(records,sample)
        for k in keys:
            vals[k].append(q[k])
    cis={}
    for k in keys:
        a=np.asarray(vals[k],float)
        a=a[np.isfinite(a)]
        cis[k]={
            "observed":observed[k],
            "ci95_low":float(np.quantile(a,.025)),
            "ci95_high":float(np.quantile(a,.975)),
            "valid":int(len(a))
        }
    return observed,cis

def main():
    cm,envs,bats=centroid_table()
    rec=target_records(cm,envs,bats)
    retained=sorted(set(r["bat"] for r in rec))
    if len(retained)<4:
        raise RuntimeError(f"insufficient bats: {retained}")
    obs,cis=bootstrap(rec,retained)

    per_bat={}
    for b in retained:
        per_bat[b]=aggregate(rec,[b])

    theta_full={}
    for b in retained:
        vals=[cm[(e,b)] for e in envs if (e,b) in cm]
        theta_full[b]={
            "all_environment_mean":float(np.mean(vals)),
            "between_environment_sd":float(np.std(vals,ddof=1)) if len(vals)>1 else None,
            "n_environments":len(vals)
        }

    out={
        "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
        "contract":"THETA_CONVERGENCE_CONTRACT_V1.md",
        "species":"Rhinolophus nippon",
        "n_bats":len(retained),
        "bats":retained,
        "n_target_bat_environments":len(rec),
        "target_counts_by_bat":{b:sum(r["bat"]==b for r in rec) for b in retained},
        "environment_counts_by_bat":{b:sum((e,b) in cm for e in envs) for b in retained},
        "observed":obs,
        "bootstrap":cis,
        "per_bat":per_bat,
        "theta_descriptive":theta_full,
        "rapid_convergence_m3":bool(np.isfinite(obs["fraction_to_full_3"]) and obs["fraction_to_full_3"]>=.80),
        "delta_1to3_supported":bool(cis["delta_1to3"]["ci95_low"]>0),
        "full_training_beats_zero":bool(obs["r2_full"]>0),
        "interpretation_category":(
            "FINITE_SCALAR_RAPID_CONVERGENCE"
            if obs["r2_full"]>0 and cis["delta_1to3"]["ci95_low"]>0 and np.isfinite(obs["fraction_to_full_3"]) and obs["fraction_to_full_3"]>=.80
            else "SCALAR_TRANSFER_WITHOUT_RAPID_CONVERGENCE"
            if obs["r2_full"]>0
            else "NO_POSITIVE_SCALAR_PREDICTION"
        )
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
