#!/usr/bin/env python3
"""Post-primary robustness diagnostics for Rhino dual PASS.

Imports the frozen primary implementation and changes only the representations
explicitly authorized by POST_PRIMARY_ROBUSTNESS_CONTRACT_V1.md.
"""
from __future__ import annotations

import collections
import copy
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
PRIMARY_PATH=HERE/"rhino_configuration_identity_primary_v1.py"

spec=importlib.util.spec_from_file_location("primary_v1",PRIMARY_PATH)
P=importlib.util.module_from_spec(spec)
spec.loader.exec_module(P)

NPERM=9999
B_MIN_VALID=9500

PERFORMANCE=[
    "median_speed",
    "p90_speed",
    "median_abs_vertical_speed",
    "p90_abs_vertical_speed",
    "vertical_range",
]
STEERING=[
    "median_abs_horizontal_turn_rate",
    "p90_abs_horizontal_turn_rate",
    "path_efficiency",
]


def transformed_a(traj, mode, seed):
    tt=[]
    grid=np.linspace(0.0,1.0,101)[:,None]
    for r in traj:
        q=dict(r)
        if r["route_valid"]:
            x=np.array(r["route101"],copy=True)
            if mode=="start":
                x=x-x[0]
            elif mode=="chord":
                chord=(1-grid)*x[0]+grid*x[-1]
                x=x-chord
            else:
                raise ValueError(mode)
            q["route101"]=x
        tt.append(q)
    oldseed=P.A_SEED
    try:
        P.A_SEED=seed
        res=P.primary_a(tt)
    finally:
        P.A_SEED=oldseed
    return res


def subset_rows(traj, feature_names):
    idx=[P.FEATURES.index(k) for k in feature_names]
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    usable=[]
    stats={}
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        bats=set(r["bat"] for r in rr)
        if len(rr)>=2 and len(bats)>=2:
            mat=np.vstack([r["features"][idx] for r in rr])
            mu=np.mean(mat,axis=0)
            sd=np.std(mat,axis=0,ddof=1)
            if not np.all(np.isfinite(sd)&(sd>0)):
                raise RuntimeError(f"subset SD failure env={e} features={feature_names}")
            usable.append(e)
            stats[e]=(mu,sd)

    rows=[]
    for r in ft:
        if r["env"] not in usable:
            continue
        mu,sd=stats[r["env"]]
        z=(r["features"][idx]-mu)/sd
        rows.append({**r,"z":z})

    bats=sorted(set(r["bat"] for r in rows))
    presence={b:sorted(set(r["env"] for r in rows if r["bat"]==b)) for b in bats}
    candidates=sorted([b for b,es in presence.items() if len(es)>=3])

    targets=[]
    for i,r in enumerate(rows):
        b,e=r["bat"],r["env"]
        if b not in candidates: continue
        own=[ee for ee in presence[b] if ee!=e]
        donors=[]
        for j in bats:
            if j==b: continue
            jes=[ee for ee in presence[j] if ee!=e]
            if len(jes)>=2: donors.append(j)
        if len(own)>=2 and len(donors)>=2:
            targets.append(i)

    # Frozen full-primary support yielded all 45; robustness subsets must not
    # silently change the target cohort.
    if len(targets)!=45 or len(candidates)!=5:
        raise RuntimeError(f"target drift: targets={len(targets)}, candidates={candidates}")
    return rows,bats,targets,usable


def observed_subset(traj, feature_names):
    rows,bats,targets,usable=subset_rows(traj,feature_names)
    obs=P.b_stat(rows,bats,targets,None)
    if obs is None: raise RuntimeError("observed subset support failed")
    K,batmeans,_=obs
    return {
        "features":feature_names,
        "usable_envs":usable,
        "K_obs":float(K),
        "bat_means":batmeans,
        "positive_bats":sum(v>0 for v in batmeans.values()),
        "n_bats":len(batmeans),
    }


def calibrated_subset(traj, feature_names, seed):
    rows,bats,targets,usable=subset_rows(traj,feature_names)
    obs=P.b_stat(rows,bats,targets,None)
    if obs is None: raise RuntimeError("observed subset support failed")
    Kobs,batmeans,_=obs

    env_clusters={}
    for e in usable:
        env_clusters[e]=sorted(set(r["bat"] for r in rows if r["env"]==e))

    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(NPERM):
        mapping={}
        for e,labels in env_clusters.items():
            perm=list(rng.permutation(np.array(labels,dtype=object)))
            for old,new in zip(labels,perm):
                mapping[(e,old)]=str(new)
        s=P.b_stat(rows,bats,targets,mapping)
        if s is not None:
            null.append(s[0])

    nvalid=len(null)
    out={
        "features":feature_names,
        "usable_envs":usable,
        "K_obs":float(Kobs),
        "bat_means":batmeans,
        "positive_bats":sum(v>0 for v in batmeans.values()),
        "n_bats":len(batmeans),
        "requested_permutations":NPERM,
        "valid_permutations":nvalid,
        "seed":seed,
    }
    if nvalid<B_MIN_VALID:
        out["verdict"]="STOP_RANDOMIZATION_SUPPORT"
        return out
    null=np.asarray(null,dtype=float)
    out.update({
        "null_mean":float(np.mean(null)),
        "null_q025":float(np.quantile(null,0.025)),
        "null_q975":float(np.quantile(null,0.975)),
        "p_one_sided":float((1+np.sum(null>=Kobs))/(1+nvalid)),
    })
    return out


def main():
    traj=P.load_rhino()

    a1=transformed_a(traj,"start",202610042211)
    a2=transformed_a(traj,"chord",202610042212)

    primary_K=0.9435600964999665
    lofo=[]
    for feature in P.FEATURES:
        subset=[x for x in P.FEATURES if x!=feature]
        r=observed_subset(traj,subset)
        lofo.append({
            "dropped_feature":feature,
            "K_without_feature":r["K_obs"],
            "ratio_to_primary_K":r["K_obs"]/primary_K,
            "bat_means":r["bat_means"],
        })

    b2=calibrated_subset(traj,PERFORMANCE,202610042213)
    b3=calibrated_subset(traj,STEERING,202610042214)

    out={
        "contract":"POST_PRIMARY_ROBUSTNESS_CONTRACT_V1.md",
        "status":"POST_PRIMARY_DIAGNOSTIC_NOT_CONFIRMATORY",
        "species":"Rhinolophus nippon",
        "primary_K_reference":primary_K,
        "A1_start_centered":a1,
        "A2_chord_residual":a2,
        "B1_leave_one_feature_out":lofo,
        "B2_performance_magnitude_only":b2,
        "B3_steering_style_only":b3,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
