#!/usr/bin/env python3
"""Audits mechanical convergence and tests genuine identity-labelled held-out prediction."""
from __future__ import annotations

import collections
import importlib.util
import itertools
import json
import math
from pathlib import Path

import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("LP",HERE/"latent_policy_dimensionality_v1.py")
LP=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(LP)

B=9999
SEED=202610081011
BOOT=4999
BOOT_SEED=202610081012
AXES=("I","M")

def subset_identity_check():
    x=np.array([-2.0,0.3,1.6,4.1,8.3])
    y=2.71
    N=len(x)
    for m in (1,2,3,4,5):
        enumeration=np.mean([(y-np.mean(q))**2 for q in itertools.combinations(x,m)])
        analytic=(y-x.mean())**2+(1/m-1/N)*np.var(x,ddof=1)
        if not math.isclose(enumeration,analytic,rel_tol=0,abs_tol=1e-12):
            raise AssertionError((m,enumeration,analytic))
    return True

def cluster_centroids():
    rows,envs=LP.standardized_rows()
    if len(rows)!=45:
        raise RuntimeError(f"45 original trajectories required, found {len(rows)}")
    grp=collections.defaultdict(list)
    for r in rows:
        z=np.asarray(r["z8"],float)
        if z.shape!=(8,) or not np.isfinite(z).all():
            raise RuntimeError("z8 input not finite 8-vector")
        grp[(int(r["env"]),str(r["bat"]))].append((
            float(np.mean(z[:4])),
            float(np.mean(np.array([-z[0],z[4],z[5],z[6],z[7]])))
        ))
    cent={k:np.mean(np.array(v,float),axis=0) for k,v in grp.items()}
    labelsets={e:sorted(k[1] for k in cent if k[0]==e) for e in envs}
    bats=sorted({k[1] for k in cent})
    if len(bats)!=5 or any(len(v)==0 for v in labelsets.values()):
        raise RuntimeError("identity / environment structure drift")
    return cent,sorted(int(e) for e in envs),bats,labelsets

def assigned_centroids(cent,labelsets,rng=None):
    if rng is None:
        return cent
    out={}
    for e,labels in labelsets.items():
        perm=list(rng.permutation(np.asarray(labels,dtype=object)))
        for old,new in zip(labels,perm):
            out[(e,str(new))]=cent[(e,old)]
    return out

def errors_by_bat(cent,envs,bats):
    values=collections.defaultdict(lambda:collections.defaultdict(list))
    target_count=0
    for b in bats:
        present=[e for e in envs if (e,b) in cent]
        for target in present:
            train=[cent[(e,b)] for e in present if e!=target]
            if len(train)<3:
                continue
            target_count+=1
            tr=np.array(train,float)
            y=cent[(target,b)]
            n=tr.shape[0]
            mean=np.mean(tr,axis=0)
            variance=np.var(tr,axis=0,ddof=1)
            for a,idx in (("I",0),("M",1)):
                zero=float(y[idx]**2)
                full=float((y[idx]-mean[idx])**2)
                item={"zero":zero,"full":full}
                for m in (1,2,3):
                    item[str(m)]=full+float((1/m-1/n)*variance[idx])
                values[b][a].append(item)
    if target_count!=25:
        raise RuntimeError(f"target support drift {target_count} != 25")
    return values

def aggregate(values,bats,normalizers=None):
    per={}
    for b in bats:
        per[b]={}
        for a in AXES:
            items=values[b][a]
            if not items:
                raise RuntimeError(f"missing bat/axis {b}/{a}")
            d={k:float(np.mean([r[k] for r in items])) for k in ("zero","1","2","3","full")}
            for m in ("1","2","3","full"):
                d["gain_"+m]=d["zero"]-d[m]
            per[b][a]=d
    stats={}
    for a in AXES:
        stats[a]={k:float(np.mean([per[b][a][k] for b in bats])) for k in per[bats[0]][a]}
        stats[a]["r2_3"]=1-stats[a]["3"]/stats[a]["zero"]
        stats[a]["r2_full"]=1-stats[a]["full"]/stats[a]["zero"]
        stats[a]["positive_bats_3"]=int(sum(per[b][a]["gain_3"]>0 for b in bats))
    if normalizers is None:
        normalizers={a:stats[a]["zero"] for a in AXES}
    if any(normalizers[a]<=0 for a in AXES):
        raise RuntimeError("bad zero normalization")
    stats["joint"]={
        k:float(np.mean([stats[a][k]/normalizers[a] for a in AXES]))
        for k in ("gain_1","gain_2","gain_3","gain_full")
    }
    stats["joint"]["positive_bats_3"]=int(sum(
        np.mean([per[b][a]["gain_3"]/normalizers[a] for a in AXES])>0
        for b in bats
    ))
    return stats,per

def bootstrap(values,bats,denoms):
    rng=np.random.default_rng(BOOT_SEED)
    keys=("I","M","joint")
    obs,_=aggregate(values,bats,denoms)
    samples={a:[] for a in keys}
    for _ in range(BOOT):
        sampled=list(rng.choice(np.asarray(bats,dtype=object),size=len(bats),replace=True))
        s,_=aggregate(values,sampled,denoms)
        for a in keys:
            samples[a].append(s[a]["gain_3"])
    return {a:{
        "ci95_low":float(np.quantile(samples[a],.025)),
        "ci95_high":float(np.quantile(samples[a],.975))
    } for a in keys}

def main():
    subset_identity_check()
    cent,envs,bats,labelsets=cluster_centroids()
    original=errors_by_bat(cent,envs,bats)
    orig_stats,_=aggregate(original,bats)
    denoms={a:orig_stats[a]["zero"] for a in AXES}
    orig_stats,per=aggregate(original,bats,denoms)

    rng=np.random.default_rng(SEED)
    nulls={a:{"gain_3":[],"gain_full":[]} for a in ("I","M","joint")}
    for _ in range(B):
        perm=assigned_centroids(cent,labelsets,rng)
        q=errors_by_bat(perm,envs,bats)
        stat,_=aggregate(q,bats,denoms)
        for a in nulls:
            for k in nulls[a]:
                nulls[a][k].append(stat[a][k])

    result={}
    for a in nulls:
        q={}
        for k,vals in nulls[a].items():
            v=np.asarray(vals,float)
            obs=float(orig_stats[a][k])
            q[k]={
                "observed":obs,
                "null_mean":float(v.mean()),
                "null_ci95":[float(np.quantile(v,.025)),float(np.quantile(v,.975))],
                "p_upper":float((1+np.sum(v>=obs-1e-12))/(B+1))
            }
        q["observed_scores"]=orig_stats[a]
        q["supported_at_m3"]=bool(
            q["gain_3"]["observed"]>0
            and q["gain_3"]["p_upper"]<=.05
            and orig_stats[a]["positive_bats_3"]>=4
        )
        result[a]=q

    out={
        "contract":"PERSONAL_POLICY_TRANSFER_NULL_CONTRACT_V1.md",
        "status":"POST_OUTCOME_NONTAUTOLOGICAL_AUDIT",
        "source":"same frozen 45 Rhino trajectories and within-environment normalization",
        "n_trajectories":45,"n_bats":len(bats),"n_envs":len(envs),
        "n_eligible_targets":25,
        "permutations":B,"seed":SEED,
        "subset_identity_check":"PASS",
        "axes":result,
        "bootstrap":bootstrap(original,bats,denoms),
        "per_bat":per,
        "interpretation_boundary":[
            "MSE_m-MSE_full is algebraically determined by finite-population sample variance; never cite its positivity as biological convergence",
            "Valid inference here is actual-labelled m=3 gain relative to an environment-wise label-disruption null",
            "Target-environment standardized inputs are transductive; strict label-free normalization requires the full target-environment sample"
        ]
    }
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
