#!/usr/bin/env python3
"""Transparent two-axis Rhino movement-policy diagnostic."""
from __future__ import annotations

import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
MIN_VALID=9500

V_I=np.array([1,1,1,1,0,0,0,0],float)
V_M=np.array([-1,0,0,0,1,1,1,1],float)
V_I_UNIT=V_I/np.linalg.norm(V_I)
V_M_UNIT=V_M/np.linalg.norm(V_M)

def standardized_rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    rows=[]
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError(e)
        for r in rr:
            z=(r["features"]-mu)/sd
            q=dict(r)
            q["z8"]=z
            q["I"]=float(np.mean(z[:4]))
            q["M"]=float(np.mean(np.array([-z[0],z[4],z[5],z[6],z[7]],float)))
            rows.append(q)
    return rows,envs

def fold_pc2_alignment(rows,envs):
    out={}
    for e0 in envs:
        M=np.vstack([r["z8"] for r in rows if r["env"]!=e0])
        M=M-M.mean(axis=0,keepdims=True)
        _,_,vt=np.linalg.svd(M,full_matrices=False)
        v=vt[1].astype(float)
        if v[4]<0:v=-v
        out[str(e0)]=float(np.dot(v,V_M_UNIT)/(np.linalg.norm(v)*np.linalg.norm(V_M_UNIT)))
    a=np.asarray(list(out.values()),float)
    return {"by_fold":out,"min":float(a.min()),"median":float(np.median(a)),"max":float(a.max())}

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def observed_mapping(rows,envs):
    return {(e,b):b for e,labs in labelsets(rows,envs).items() for b in labs}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):
            mp[(e,old)]=str(new)
    return mp

def identity_stat(rows,envs,mapping,key):
    # key can map row -> vector-like np array
    # Build training environment-equal centroids for assigned labels.
    perbat=collections.defaultdict(list)
    for e0 in envs:
        train_groups=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rows:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            train_groups[lab][r["env"]].append(np.atleast_1d(key(r)).astype(float))
        train={}
        for b,d in train_groups.items():
            ec=[]
            for ee in sorted(d):
                ec.append(np.mean(np.vstack(d[ee]),axis=0))
            if len(ec)>=2:
                train[b]=np.mean(np.vstack(ec),axis=0)
        if len(train)<3:continue

        for r in [x for x in rows if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train:continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2:continue
            x=np.atleast_1d(key(r)).astype(float)
            ds=float(np.linalg.norm(x-train[lab]))
            do=float(np.mean([np.linalg.norm(x-train[b]) for b in donors]))
            perbat[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None
    return float(np.mean(list(bm.values()))),bm

def calibrate(rows,envs,key,seed):
    ls=labelsets(rows,envs);obsmap=observed_mapping(rows,envs)
    obs=identity_stat(rows,envs,obsmap,key)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    K,bm=obs
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        mp=perm_mapping(ls,rng)
        q=identity_stat(rows,envs,mp,key)
        if q is not None:null.append(q[0])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=K))/(1+len(a)))
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    return {
      "status":"DONE","K":K,"bat_means":bm,"positive_bats":pos,
      "n_bats":len(bm),"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "supported":bool(K>0 and p<=.05 and frac>=.70 and len(a)>=MIN_VALID)
    }

def main():
    rows,envs=standardized_rows()
    T1=fold_pc2_alignment(rows,envs)

    T2=calibrate(rows,envs,lambda r:np.array([r["M"]],float),202610050921)
    T3=calibrate(rows,envs,lambda r:np.array([r["I"],r["M"]],float),202610050922)

    # Fixed two-dimensional transparent span.
    V=np.column_stack([V_I,V_M])
    Q,_=np.linalg.qr(V)
    for r in rows:
        z=r["z8"]
        r["resid2"]=z-Q@(Q.T@z)
    T4=calibrate(rows,envs,lambda r:r["resid2"],202610050923)

    if "K" in T3:
        T3["K_over_full8"]=float(T3["K"]/0.9435600964999665)

    verdict="STOP_RANDOMIZATION_SUPPORT"
    if all(x.get("valid_permutations",0)>=MIN_VALID for x in [T2,T3,T4]):
        if T3.get("supported") and not T4.get("supported"):
            verdict="SUPPORTED_TRANSPARENT_TWO_AXIS_SPAN"
        else:
            verdict="INCOMPLETE_TRANSPARENT_TWO_AXIS_SPAN"

    out={
      "contract":"TRANSPARENT_TWO_AXIS_POLICY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_INTERPRETABILITY_AND_FALSIFICATION_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "definitions":{
        "FlightIntensity":"mean(z1,z2,z3,z4)",
        "ManeuveringExtent":"mean(-z1,z5,z6,z7,z8)"
      },
      "T1_PC2_alignment":T1,
      "T2_ManeuveringExtent_identity":T2,
      "T3_transparent_2D_identity":T3,
      "T4_residual_after_transparent_span":T4,
      "diagnostic_verdict":verdict
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
