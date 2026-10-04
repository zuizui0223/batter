#!/usr/bin/env python3
"""Held-out magnitude calibration of the one-dimensional Rhino FlightIntensity parameter."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)

NPERM=9999
SEED=202610042341

def cluster_centroids(rows,envs):
    cm={}
    for e in envs:
        for b in sorted(set(r["bat"] for r in rows if r["env"]==e)):
            vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==b]
            cm[(e,b)]=float(np.mean(vals))
    return cm

def calibration(cm,envs,mapping):
    # Assigned centroid table after within-environment relabeling.
    assigned={}
    presence=collections.defaultdict(set)
    for (e,old),v in cm.items():
        lab=mapping[(e,old)]
        assigned[(e,lab)]=v
        presence[lab].add(e)

    xs=[];ys=[];pair_sign=collections.defaultdict(list);detail=[]
    for e in envs:
        present=sorted([b for b in presence if (e,b) in assigned])
        theta={}
        for b in present:
            train=[assigned[(ee,b)] for ee in sorted(presence[b]) if ee!=e and (ee,b) in assigned]
            if len(train)>=2:
                theta[b]=float(np.mean(train))
        eligible=sorted(theta)
        for ii in range(len(eligible)):
            for jj in range(ii+1,len(eligible)):
                i,j=eligible[ii],eligible[jj]
                x=theta[i]-theta[j]
                y=assigned[(e,i)]-assigned[(e,j)]
                xs.append(x);ys.append(y)
                if x==0 or y==0: acc=.5
                else: acc=1.0 if math.copysign(1.0,x)==math.copysign(1.0,y) else 0.0
                pair=tuple(sorted((i,j)))
                pair_sign[pair].append(acc)
                detail.append({"environment":e,"pair":"-".join(pair),"predicted_difference":x,"observed_difference":y,"sign_accuracy":acc})
    x=np.asarray(xs,float);y=np.asarray(ys,float)
    if len(x)<3 or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)) or float(np.sum(x*x))<=0:
        return None
    beta=float(np.sum(x*y)/np.sum(x*x))
    if np.std(x,ddof=1)<=0 or np.std(y,ddof=1)<=0:
        r=math.nan
    else:
        r=float(np.corrcoef(x,y)[0,1])
    pair_acc={"-".join(k):float(np.mean(v)) for k,v in sorted(pair_sign.items())}
    equal_pair=float(np.mean(list(pair_acc.values()))) if pair_acc else math.nan
    return {
      "beta_through_origin":beta,
      "pearson_r":r,
      "raw_pair_environment_sign_accuracy":float(np.mean([d["sign_accuracy"] for d in detail])),
      "equal_pair_sign_accuracy":equal_pair,
      "n_pair_environment_points":len(detail),
      "n_pairs":len(pair_acc),
      "pair_accuracy":pair_acc,
      "points":detail,
    }

def main():
    rows,envs=F.load_scalar_rows()
    cm=cluster_centroids(rows,envs)
    ls=F.labelsets(rows,envs)
    obsmap=F.observed_mapping(rows,envs)
    obs=calibration(cm,envs,obsmap)
    if obs is None:
        raise RuntimeError("observed calibration support failed")

    rng=np.random.default_rng(SEED)
    beta_null=np.empty(NPERM,float); r_null=np.empty(NPERM,float)
    sign_null=np.empty(NPERM,float)
    for k in range(NPERM):
        mp=F.perm_mapping(ls,rng)
        q=calibration(cm,envs,mp)
        if q is None or not math.isfinite(q["pearson_r"]):
            raise RuntimeError("unexpected invalid permutation")
        beta_null[k]=q["beta_through_origin"]
        r_null[k]=q["pearson_r"]
        sign_null[k]=q["equal_pair_sign_accuracy"]

    p_beta=float((1+np.sum(beta_null>=obs["beta_through_origin"]))/(NPERM+1))
    p_r=float((1+np.sum(r_null>=obs["pearson_r"]))/(NPERM+1))
    p_sign=float((1+np.sum(sign_null>=obs["equal_pair_sign_accuracy"]))/(NPERM+1))
    supported=bool(obs["beta_through_origin"]>0 and obs["pearson_r"]>0 and p_beta<=.05 and p_r<=.05)

    out={
      "contract":"ONE_PARAMETER_CALIBRATION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "observed":obs,
      "permutations":NPERM,
      "seed":SEED,
      "beta_null_mean":float(beta_null.mean()),
      "beta_null_q025":float(np.quantile(beta_null,.025)),
      "beta_null_q975":float(np.quantile(beta_null,.975)),
      "p_beta_one_sided":p_beta,
      "r_null_mean":float(r_null.mean()),
      "r_null_q025":float(np.quantile(r_null,.025)),
      "r_null_q975":float(np.quantile(r_null,.975)),
      "p_r_one_sided":p_r,
      "sign_null_mean":float(sign_null.mean()),
      "sign_null_q025":float(np.quantile(sign_null,.025)),
      "sign_null_q975":float(np.quantile(sign_null,.975)),
      "p_equal_pair_sign_one_sided":p_sign,
      "diagnostic_verdict":"SUPPORTED_ONE_PARAMETER_MAGNITUDE_TRANSFER" if supported else "UNSUPPORTED_ONE_PARAMETER_MAGNITUDE_TRANSFER"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
