#!/usr/bin/env python3
"""Target-normalization sensitivity for scale-free Rhino route geometry."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEEDS={"S1":202610061201,"S2":202610061202}

def raw_rows():
    traj=G.P.load_rhino()
    rows=[]
    for k,r in enumerate(traj):
        x=G.geometry_features(r)
        if x is None:continue
        q=dict(r);q["row_id"]=k;q["x"]=np.asarray(x,float);rows.append(q)
    if len(rows)!=45:raise RuntimeError(f"expected 45 geometry-valid trajectories, got {len(rows)}")
    envs=sorted(set(r["env"] for r in rows))
    if envs!=[1,2,3,4,5,6,7]:raise RuntimeError(f"unexpected environments {envs}")
    return rows,envs

def precompute(rows,envs,variant):
    out={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        target=[r for r in rows if r["env"]==e0]
        if variant=="S1":
            emean={};res=[]
            for e in [z for z in envs if z!=e0]:
                X=np.vstack([r["x"] for r in train if r["env"]==e])
                mu=X.mean(axis=0);emean[e]=mu;res.append(X-mu)
            R=np.vstack(res);sd=R.std(axis=0,ddof=1)
            Xt=np.vstack([r["x"] for r in target]);tmean=Xt.mean(axis=0)
            if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError("bad S1 training SD")
            fold={}
            for r in train:fold[r["row_id"]]=(r["x"]-emean[r["env"]])/sd
            for r in target:fold[r["row_id"]]=(r["x"]-tmean)/sd
        elif variant=="S2":
            X=np.vstack([r["x"] for r in train])
            mu=X.mean(axis=0);sd=X.std(axis=0,ddof=1)
            if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError("bad S2 training SD")
            fold={r["row_id"]:(r["x"]-mu)/sd for r in rows}
        else:raise ValueError(variant)
        out[e0]=fold
    return out

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def observed_map(rows,envs):
    return {(e,b):b for e,labs in labelsets(rows,envs).items() for b in labs}

def perm_map(ls,rng):
    out={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):out[(e,old)]=str(new)
    return out

def stat(rows,envs,foldvec,mapping):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        groups=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rows:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            groups[lab][r["env"]].append(foldvec[e0][r["row_id"]])
        cent={}
        for b,d in groups.items():
            ec=[np.mean(np.vstack(d[e]),axis=0) for e in sorted(d)]
            if len(ec)>=2:cent[b]=np.mean(np.vstack(ec),axis=0)
        if len(cent)<3:continue
        for r in [q for q in rows if q["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in cent:continue
            donors=[b for b in cent if b!=lab]
            if len(donors)<2:continue
            x=foldvec[e0][r["row_id"]]
            ds=float(np.linalg.norm(x-cent[lab]))
            do=float(np.mean([np.linalg.norm(x-cent[b]) for b in donors]))
            perbat[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None,{}
    return float(np.mean(list(bm.values()))),bm

def run(rows,envs,variant):
    fv=precompute(rows,envs,variant)
    ls=labelsets(rows,envs);om=observed_map(rows,envs)
    obs,bm=stat(rows,envs,fv,om)
    if obs is None:raise RuntimeError(f"{variant} observed support fail")
    rng=np.random.default_rng(SEEDS[variant]);null=[]
    for _ in range(NPERM):
        q,_=stat(rows,envs,fv,perm_map(ls,rng))
        if q is not None and math.isfinite(q):null.append(float(q))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:raise RuntimeError(f"{variant} randomization support {len(a)}")
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    return {
      "K":float(obs),"bat_means":bm,"positive_bats":int(pos),"n_bats":int(len(bm)),
      "positive_fraction":float(frac),"requested_permutations":NPERM,
      "valid_permutations":int(len(a)),"seed":SEEDS[variant],
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "supported":bool(obs>0 and p<=.05 and frac>=.70)
    }

def main():
    rows,envs=raw_rows()
    s1=run(rows,envs,"S1");s2=run(rows,envs,"S2")
    if s1["supported"] and s2["supported"]:
        verdict="SUPPORTED_ABSOLUTE_TRAINING_SCALE_GEOMETRY_TRANSFER"
    elif s1["supported"]:
        verdict="SUPPORTED_RELATIVE_GEOMETRY_WITHOUT_TARGET_SCALING"
    else:
        verdict="TARGET_SCALING_MATERIAL_FOR_GEOMETRY_IDENTITY"
    print(json.dumps({
      "contract":"GEOMETRY_POLICY_TARGET_NORMALIZATION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_ROBUSTNESS_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "S1_target_centered_training_scaled":s1,
      "S2_fully_training_only_global_scaled":s2,
      "diagnostic_verdict":verdict
    },indent=2))

if __name__=="__main__":main()
