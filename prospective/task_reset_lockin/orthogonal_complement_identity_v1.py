#!/usr/bin/env python3
"""Cross-environment identity after removing the dominant policy axis."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
SEED_PC1=202610050921
SEED_FI=202610050922
FI=np.array([.5,.5,.5,.5,0,0,0,0],float)

def std_rows():
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
            q=dict(r);q["z"]=(r["features"]-mu)/sd;rows.append(q)
    return rows,envs

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def obsmap(rows,envs):
    return {(e,b):b for e,labs in labelsets(rows,envs).items() for b in labs}

def permmap(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):mp[(e,old)]=str(new)
    return mp

def pc1_axes(rows,envs):
    out={}
    for e0 in envs:
        M=np.vstack([r["z"] for r in rows if r["env"]!=e0])
        M=M-M.mean(axis=0,keepdims=True)
        _,_,vt=np.linalg.svd(M,full_matrices=False)
        v=vt[0].astype(float)
        out[e0]=v/np.linalg.norm(v)
    return out

def residual(z,v):
    return z-v*float(np.dot(v,z))

def stat(rows,envs,mapping,mode,axes=None):
    perbat=collections.defaultdict(list)
    target_rows=[]
    for e0 in envs:
        v=FI if mode=="FI" else axes[e0]
        # cluster centroids under assigned labels in each training environment
        cent=collections.defaultdict(dict)
        presence=collections.defaultdict(set)
        for e in envs:
            if e==e0:continue
            groups=collections.defaultdict(list)
            for r in rows:
                if r["env"]!=e:continue
                lab=mapping[(e,r["bat"])]
                groups[lab].append(residual(r["z"],v))
            for lab,vals in groups.items():
                cent[lab][e]=np.mean(np.vstack(vals),axis=0)
                presence[lab].add(e)
        train={}
        for b,d in cent.items():
            if len(d)>=2:
                train[b]=np.mean(np.vstack([d[e] for e in sorted(d)]),axis=0)
        if len(train)<3:continue

        # target trajectory-level advantages
        for r in [x for x in rows if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train:continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2:continue
            z=residual(r["z"],v)
            ds=float(np.linalg.norm(z-train[lab]))
            do=float(np.mean([np.linalg.norm(z-train[b]) for b in donors]))
            k=do-ds
            perbat[lab].append(k)
            target_rows.append((e0,lab,k))
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None
    return float(np.mean(list(bm.values()))),bm,target_rows

def run(rows,envs,mode,axes,seed):
    ls=labelsets(rows,envs);om=obsmap(rows,envs)
    obs=stat(rows,envs,om,mode,axes)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    kval,bm,tr=obs
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        mp=permmap(ls,rng)
        q=stat(rows,envs,mp,mode,axes)
        if q is not None:null.append(q[0])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=kval))/(1+len(a)))
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    return {
      "status":"DONE","K":float(kval),"bat_means":bm,
      "positive_bats":pos,"n_bats":len(bm),"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_RESIDUAL_IDENTITY" if (kval>0 and p<=.05 and frac>=.70) else "UNSUPPORTED_RESIDUAL_IDENTITY"
    }

def main():
    rows,envs=std_rows();axes=pc1_axes(rows,envs)
    out={
      "contract":"ORTHOGONAL_COMPLEMENT_IDENTITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_DIMENSIONALITY_FALSIFICATION_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "O1_training_PC1_removed":run(rows,envs,"PC1",axes,SEED_PC1),
      "O2_transparent_FlightIntensity_removed":run(rows,envs,"FI",axes,SEED_FI),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
