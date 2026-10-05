#!/usr/bin/env python3
"""Target-normalization sensitivity for transparent Rhino policy axes."""
from __future__ import annotations

import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
MIN_VALID=9500
SEEDS={"S1":202610051021,"S2":202610051022}

def raw_rows():
    traj=P.load_rhino()
    rr=[r for r in traj if r["feature_valid"]]
    if len(rr)!=45:raise RuntimeError(f"expected 45, got {len(rr)}")
    envs=sorted(set(r["env"] for r in rr))
    rows=[]
    for k,r in enumerate(rr):
        q=dict(r);q["row_id"]=k;q["x"]=np.asarray(r["features"],float);rows.append(q)
    return rows,envs

def axes(z):
    I=float(np.mean(z[:4]))
    M=float(np.mean(np.array([-z[0],z[4],z[5],z[6],z[7]],float)))
    return np.array([I,M],float)

def precompute(rows,envs,variant):
    out={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        target=[r for r in rows if r["env"]==e0]
        if variant=="S1":
            env_mean={}
            residuals=[]
            for e in [e for e in envs if e!=e0]:
                X=np.vstack([r["x"] for r in train if r["env"]==e])
                mu=X.mean(axis=0);env_mean[e]=mu
                residuals.append(X-mu)
            R=np.vstack(residuals)
            sd=R.std(axis=0,ddof=1)
            Xt=np.vstack([r["x"] for r in target])
            target_mean=Xt.mean(axis=0)
            if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError("bad S1 sd")
            fold={}
            for r in train:
                fold[r["row_id"]]=axes((r["x"]-env_mean[r["env"]])/sd)
            for r in target:
                fold[r["row_id"]]=axes((r["x"]-target_mean)/sd)
        elif variant=="S2":
            X=np.vstack([r["x"] for r in train])
            mu=X.mean(axis=0);sd=X.std(axis=0,ddof=1)
            if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError("bad S2 sd")
            fold={r["row_id"]:axes((r["x"]-mu)/sd) for r in rows}
        else:raise ValueError(variant)
        out[e0]=fold
    return out

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def observed_map(rows,envs):
    return {(e,b):b for e,labs in labelsets(rows,envs).items() for b in labs}

def perm_map(ls,rng):
    mp={}
    for e,labs in ls.items():
        vals=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,vals):mp[(e,old)]=str(new)
    return mp

def stat(rows,envs,foldvec,mapping,dims):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        train_groups=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rows:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            v=foldvec[e0][r["row_id"]][dims]
            train_groups[lab][r["env"]].append(np.atleast_1d(v).astype(float))
        cent={}
        for b,d in train_groups.items():
            ec=[]
            for e in sorted(d):
                ec.append(np.mean(np.vstack(d[e]),axis=0))
            if len(ec)>=2:cent[b]=np.mean(np.vstack(ec),axis=0)
        if len(cent)<3:continue
        for r in [x for x in rows if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in cent:continue
            donors=[b for b in cent if b!=lab]
            if len(donors)<2:continue
            x=np.atleast_1d(foldvec[e0][r["row_id"]][dims]).astype(float)
            ds=float(np.linalg.norm(x-cent[lab]))
            do=float(np.mean([np.linalg.norm(x-cent[b]) for b in donors]))
            perbat[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None,{}
    return float(np.mean(list(bm.values()))),bm

def run_variant(rows,envs,variant):
    fv=precompute(rows,envs,variant)
    ls=labelsets(rows,envs);om=observed_map(rows,envs)
    obs2,bm2=stat(rows,envs,fv,om,slice(0,2))
    obsi,bmi=stat(rows,envs,fv,om,slice(0,1))
    obsm,bmm=stat(rows,envs,fv,om,slice(1,2))
    if obs2 is None:raise RuntimeError(f"{variant} observed 2D support failed")
    rng=np.random.default_rng(SEEDS[variant]);null=[]
    for _ in range(NPERM):
        mp=perm_map(ls,rng)
        q,_=stat(rows,envs,fv,mp,slice(0,2))
        if q is not None and math.isfinite(q):null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs2))/(1+len(a)))
    pos=sum(v>0 for v in bm2.values());frac=pos/len(bm2)
    return {
      "twoD":{"K":obs2,"bat_means":bm2,"positive_bats":pos,"n_bats":len(bm2),
              "positive_fraction":frac,"valid_permutations":len(a),
              "requested_permutations":NPERM,"seed":SEEDS[variant],
              "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
              "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
              "supported":bool(obs2>0 and p<=.05 and frac>=.70 and len(a)>=MIN_VALID)},
      "FlightIntensity":{"K":obsi,"bat_means":bmi,
                         "positive_fraction":sum(v>0 for v in bmi.values())/len(bmi)},
      "ManeuveringExtent":{"K":obsm,"bat_means":bmm,
                           "positive_fraction":sum(v>0 for v in bmm.values())/len(bmm)},
    }

def main():
    rows,envs=raw_rows()
    s1=run_variant(rows,envs,"S1")
    s2=run_variant(rows,envs,"S2")
    if s1["twoD"]["supported"] and s2["twoD"]["supported"]:
        verdict="SUPPORTED_ABSOLUTE_TRAINING_SCALE_TRANSFER"
    elif s1["twoD"]["supported"]:
        verdict="SUPPORTED_RELATIVE_POLICY_WITHOUT_TARGET_SCALING"
    else:
        verdict="TARGET_SCALING_MATERIAL"
    out={
      "contract":"TARGET_NORMALIZATION_SENSITIVITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_ROBUSTNESS_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "S1_target_centered_training_scaled":s1,
      "S2_fully_training_only_global_scaled":s2,
      "diagnostic_verdict":verdict,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
