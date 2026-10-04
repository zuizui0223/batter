#!/usr/bin/env python3
"""Species-specific Miniopterus PCA1 cross-configuration identity diagnostic."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("M",HERE/"cross_species_policy_axis_v1.py")
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

NPERM=9999
SEED=202610042331
MIN_VALID=9500

def prepare():
    rows=M.mini_standardized()
    envs=sorted(set(r["env"] for r in rows))
    scores={}
    var1={}
    loadings={}
    for target in envs:
        train_idx=[i for i,r in enumerate(rows) if r["env"]!=target]
        X=np.vstack([rows[i]["z8"] for i in train_idx]).astype(float)
        mu=X.mean(axis=0)
        Xc=X-mu
        _,s,Vt=np.linalg.svd(Xc,full_matrices=False)
        v=Vt[0].copy()
        total=float(np.sum(s*s))
        var1[target]=float((s[0]*s[0])/total) if total>0 else math.nan
        loadings[target]=v.tolist()
        scores[target]=np.asarray([(np.asarray(r["z8"])-mu)@v for r in rows],float)
    return rows,envs,scores,var1,loadings

def env_labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def identity_mapping(labelsets):
    return {(e,b):b for e,labs in labelsets.items() for b in labs}

def perm_mapping(labelsets,rng):
    mp={}
    for e,labs in labelsets.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm):
            mp[(e,old)]=str(new)
    return mp

def stat(rows,envs,scores,mapping):
    perbat=collections.defaultdict(list)
    for target in envs:
        sc=scores[target]
        # Build equal-environment training centroid for each assigned label.
        cent={}
        assigned_labels=sorted(set(
            mapping[(e,r["bat"])]
            for e in envs if e!=target
            for r in rows if r["env"]==e
        ))
        for lab in assigned_labels:
            env_means=[]
            for e in envs:
                if e==target: continue
                idx=[i for i,r in enumerate(rows) if r["env"]==e and mapping[(e,r["bat"])]==lab]
                if idx:
                    env_means.append(float(np.mean(sc[idx])))
            if len(env_means)>=2:
                cent[lab]=float(np.mean(env_means))
        if len(cent)<3:
            continue
        for old in sorted(set(r["bat"] for r in rows if r["env"]==target)):
            lab=mapping[(target,old)]
            if lab not in cent: continue
            donors=[b for b in cent if b!=lab]
            if len(donors)<2: continue
            idx=[i for i,r in enumerate(rows) if r["env"]==target and r["bat"]==old]
            for i in idx:
                x=float(sc[i])
                ds=abs(x-cent[lab])
                do=float(np.mean([abs(x-cent[b]) for b in donors]))
                perbat[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:
        return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,envs,scores,var1,loadings=prepare()
    ls=env_labelsets(rows,envs)
    obs,bm=stat(rows,envs,scores,identity_mapping(ls))
    if obs is None:
        raise RuntimeError("observed support failed")
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        q,_=stat(rows,envs,scores,perm_mapping(ls,rng))
        if q is not None:
            null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else math.nan
    pos=sum(v>0 for v in bm.values())
    frac=pos/len(bm)
    supported=bool(len(a)>=MIN_VALID and obs>0 and p<=.05 and pos>=3)
    sq=np.asarray([np.asarray(loadings[e])**2 for e in envs])
    out={
      "contract":"MINI_SPECIES_SPECIFIC_PCA1_CONTRACT_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_DIAGNOSTIC",
      "species":"Miniopterus fuliginosus",
      "n_trajectories":len(rows),
      "K_PCA1":float(obs),
      "bat_means":bm,
      "positive_bats":pos,
      "n_bats":len(bm),
      "positive_fraction":frac,
      "requested_permutations":NPERM,
      "valid_permutations":int(len(a)),
      "seed":SEED,
      "null_mean":float(a.mean()) if len(a) else None,
      "null_q025":float(np.quantile(a,.025)) if len(a) else None,
      "null_q975":float(np.quantile(a,.975)) if len(a) else None,
      "p_one_sided":p,
      "training_PC1_variance_by_target_env":{str(e):var1[e] for e in envs},
      "median_training_PC1_variance":float(np.median([var1[e] for e in envs])),
      "median_squared_loadings_PC1":np.median(sq,axis=0).tolist(),
      "diagnostic_verdict":"SUPPORTED_SPECIES_SPECIFIC_PCA1" if supported else "UNSUPPORTED_SPECIES_SPECIFIC_PCA1",
      "references":{
        "failed_full8_K":-0.013597525318187484,
        "failed_full8_p":0.1687,
        "fixed_Rhino_FlightIntensity_p":0.2508,
        "fixed_Rhino_PC1_p":0.1593
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
