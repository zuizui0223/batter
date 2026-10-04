#!/usr/bin/env python3
"""Movement-conditioned pulse identity sensitivities.

Contracts:
- MOVEMENT_CONDITIONED_PULSE_CONTRACT_V1.md
- MOVEMENT_CONDITIONED_PULSE_IMPLEMENTATION_V1.md
"""
from __future__ import annotations

import collections
import importlib.util
import json
import math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

P=load_module("movement_primary",HERE/"rhino_configuration_identity_primary_v1.py")
Q=load_module("pulse_identity",HERE/"rhino_pulse_identity_v1.py")

PULSE_NAMES=[
    "log_pulse_rate",
    "median_log_ipi",
    "p10_log_ipi",
    "p90_log_ipi",
    "iqr_log_ipi",
    "sd_log_ipi",
]
MOVE_NAMES=list(P.FEATURES)

C1_IDX=[0,1,2,3,7]
C2_IDX=list(range(8))
NPERM=9999
MIN_VALID=9500

def join_rows():
    move=P.load_rhino()
    pulse=Q.load_rows()
    mm={r["name"]:r for r in move if r["feature_valid"]}
    qq={r["name"]:r for r in pulse if r["valid"]}
    if len(mm)!=45 or len(qq)!=45 or set(mm)!=set(qq):
        raise RuntimeError(f"join mismatch movement={len(mm)} pulse={len(qq)} intersection={len(set(mm)&set(qq))}")
    rows=[]
    for name in sorted(mm):
        m=mm[name];q=qq[name]
        if m["env"]!=q["env"] or m["bat"]!=q["bat"]:
            raise RuntimeError(f"identity mismatch {name}")
        rows.append({
            "name":name,
            "env":m["env"],
            "bat":m["bat"],
            "move":np.asarray(m["features"],dtype=float),
            "pulse":np.asarray(q["features"],dtype=float),
        })
    return rows

def env_z(rows,key,nfeat):
    out=np.zeros((len(rows),nfeat),dtype=float)
    envs=sorted(set(r["env"] for r in rows))
    for e in envs:
        idx=[i for i,r in enumerate(rows) if r["env"]==e]
        mat=np.vstack([rows[i][key] for i in idx])
        mu=np.mean(mat,axis=0)
        sd=np.std(mat,axis=0,ddof=1)
        if not np.all(np.isfinite(sd)&(sd>0)):
            raise RuntimeError(f"first-stage {key} SD failure env={e}")
        out[idx]=(mat-mu)/sd
    return out,envs

def residualize(rows,predictor_idx):
    pulse_z,envs=env_z(rows,"pulse",6)
    move_z,_=env_z(rows,"move",8)

    X=np.column_stack([np.ones(len(rows),dtype=float),move_z[:,predictor_idx]])
    expected_rank=X.shape[1]
    rank=int(np.linalg.matrix_rank(X))
    cond=float(np.linalg.cond(X))
    if rank!=expected_rank:
        return None,{
            "status":"STOP_OLS_RANK",
            "rank":rank,
            "required_rank":expected_rank,
            "condition_number":cond,
        }

    # Six separate OLS fits, equivalently one multivariate least-squares fit.
    beta,_,rank2,_=np.linalg.lstsq(X,pulse_z,rcond=None)
    if int(rank2)!=expected_rank:
        return None,{
            "status":"STOP_OLS_RANK_LSTSQ",
            "rank":int(rank2),
            "required_rank":expected_rank,
            "condition_number":cond,
        }
    resid=pulse_z-X@beta

    keep=np.ones(6,dtype=bool)
    rz=np.full_like(resid,np.nan)
    # Determine species-wide feature support: any bad env SD drops feature.
    env_stats={}
    for e in envs:
        idx=np.array([i for i,r in enumerate(rows) if r["env"]==e],dtype=int)
        mu=np.mean(resid[idx],axis=0)
        sd=np.std(resid[idx],axis=0,ddof=1)
        env_stats[e]=(idx,mu,sd)
        keep &= np.isfinite(sd)&(sd>0)

    kept=np.where(keep)[0]
    if len(kept)<4:
        return None,{
            "status":"STOP_RESIDUAL_FEATURE_SUPPORT",
            "rank":rank,
            "required_rank":expected_rank,
            "condition_number":cond,
            "retained_feature_indices":kept.tolist(),
            "retained_features":[PULSE_NAMES[i] for i in kept],
        }

    for e,(idx,mu,sd) in env_stats.items():
        rz[np.ix_(idx,kept)]=(resid[np.ix_(idx,kept)]-mu[kept])/sd[kept]

    out=[]
    for i,r in enumerate(rows):
        out.append({
            **r,
            "z":rz[i,kept],
        })

    return out,{
        "status":"PASS_RESIDUALIZATION",
        "rank":rank,
        "required_rank":expected_rank,
        "condition_number":cond,
        "retained_feature_indices":kept.tolist(),
        "retained_features":[PULSE_NAMES[i] for i in kept],
        "predictor_indices":list(predictor_idx),
        "predictors":[MOVE_NAMES[i] for i in predictor_idx],
        "usable_envs":envs,
    }

def target_support(rows):
    bats=sorted(set(r["bat"] for r in rows))
    envs=sorted(set(r["env"] for r in rows))
    presence={b:sorted(set(r["env"] for r in rows if r["bat"]==b)) for b in bats}
    candidates=sorted([b for b,es in presence.items() if len(es)>=3])

    targets=[]
    support=collections.Counter()
    for i,r in enumerate(rows):
        b,e=r["bat"],r["env"]
        if b not in candidates:
            continue
        own=[ee for ee in presence[b] if ee!=e]
        donors=[]
        for j in bats:
            if j==b: continue
            jes=[ee for ee in presence[j] if ee!=e]
            if len(jes)>=2:
                donors.append(j)
        if len(own)>=2 and len(donors)>=2:
            targets.append(i)
            support[b]+=1

    if len(candidates)<3 or not targets:
        raise RuntimeError("conditioned pulse target support failed")

    return bats,envs,candidates,targets,dict(support)

def run_diag(rows,predictor_idx,seed,label):
    residual_rows,meta=residualize(rows,predictor_idx)
    if residual_rows is None:
        return {"label":label,**meta}

    bats,envs,candidates,targets,support=target_support(residual_rows)
    obs=P.b_stat(residual_rows,bats,targets,None)
    if obs is None:
        return {"label":label,**meta,"status":"STOP_OBSERVED_IDENTITY_SUPPORT"}

    Pobs,batmeans,target_vals=obs
    env_clusters={
        e:sorted(set(r["bat"] for r in residual_rows if r["env"]==e))
        for e in envs
    }

    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(NPERM):
        mapping={}
        for e,labs in env_clusters.items():
            perm=list(rng.permutation(np.asarray(labs,dtype=object)))
            for old,new in zip(labs,perm):
                mapping[(e,old)]=str(new)
        s=P.b_stat(residual_rows,bats,targets,mapping)
        if s is not None:
            null.append(float(s[0]))

    out={
        "label":label,
        **meta,
        "candidate_bats":candidates,
        "support_by_bat":support,
        "n_targets":len(targets),
        "P_residual_obs":float(Pobs),
        "bat_means":{k:float(v) for k,v in batmeans.items()},
        "positive_bats":int(sum(v>0 for v in batmeans.values())),
        "n_bats":len(batmeans),
        "positive_fraction":float(sum(v>0 for v in batmeans.values())/len(batmeans)),
        "requested_permutations":NPERM,
        "valid_permutations":len(null),
        "seed":seed,
    }
    if len(null)<MIN_VALID:
        out["verdict"]="STOP_RANDOMIZATION_SUPPORT"
        return out

    a=np.asarray(null,dtype=float)
    p=float((1+np.sum(a>=Pobs))/(1+len(a)))
    supported=Pobs>0 and p<=0.05 and out["positive_fraction"]>=0.70
    out.update({
        "null_mean":float(np.mean(a)),
        "null_q025":float(np.quantile(a,0.025)),
        "null_q975":float(np.quantile(a,0.975)),
        "p_one_sided":p,
        "verdict":"SUPPORTED_RESIDUAL_PULSE_IDENTITY" if supported else "UNSUPPORTED_RESIDUAL_PULSE_IDENTITY",
    })
    return out

def main():
    rows=join_rows()
    out={
        "contracts":[
            "MOVEMENT_CONDITIONED_PULSE_CONTRACT_V1.md",
            "MOVEMENT_CONDITIONED_PULSE_IMPLEMENTATION_V1.md",
        ],
        "status":"POST_PRIMARY_DIAGNOSTIC_SENSITIVITY",
        "species":"Rhinolophus nippon",
        "n_joined_trajectories":len(rows),
        "C1_performance_conditioned":run_diag(rows,C1_IDX,202610042251,"C1"),
        "C2_all_movement_conditioned":run_diag(rows,C2_IDX,202610042252,"C2"),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
