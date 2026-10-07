#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, itertools, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(L)

spec2=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec2); assert spec2.loader is not None; spec2.loader.exec_module(F)

NPERM=9999

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def obsmap(rows,envs):
    return {(e,b):b for e in envs for b in sorted(set(r["bat"] for r in rows if r["env"]==e))}

def permmap(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p): mp[(e,old)]=str(new)
    return mp

def assigned(r,mp):
    return mp[(r["env"],r["bat"])]

def two_env_centroids(rows,envs,target_env,coords,mp):
    by=collections.defaultdict(dict)
    for e in envs:
        if e==target_env: continue
        labs=sorted(set(assigned(r,mp) for r in rows if r["env"]==e))
        for lab in labs:
            ix=[i for i,r in enumerate(rows) if r["env"]==e and assigned(r,mp)==lab]
            if ix:
                by[lab][e]=float(np.mean([coords[i] for i in ix]))
    out={}
    for lab,d in by.items():
        es=sorted(d)
        if len(es)<2: continue
        vals=[]
        for a,b in itertools.combinations(es,2):
            vals.append(0.5*(d[a]+d[b]))
        out[lab]=vals
    return out

def stat(rows,envs,coord_by_fold,mp):
    per=collections.defaultdict(list)
    for e0 in envs:
        coords=np.asarray(coord_by_fold[e0],float)
        cents=two_env_centroids(rows,envs,e0,coords,mp)
        if len(cents)<3: continue
        for i,r in enumerate(rows):
            if r["env"]!=e0: continue
            lab=assigned(r,mp)
            if lab not in cents: continue
            donors=[b for b in cents if b!=lab]
            if len(donors)<2: continue
            z=float(coords[i])
            ds=float(np.mean([abs(z-c) for c in cents[lab]]))
            donor_means=[float(np.mean([abs(z-c) for c in cents[b]])) for b in donors]
            do=float(np.mean(donor_means))
            per[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in per.items() if v}
    if len(bm)<3: return None,bm
    return float(np.mean(list(bm.values()))),bm

def calibrate(rows,envs,coord_by_fold,seed):
    ls=labelsets(rows,envs)
    obs,bm=stat(rows,envs,coord_by_fold,obsmap(rows,envs))
    if obs is None: raise RuntimeError("observed support")
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(NPERM):
        q,_=stat(rows,envs,coord_by_fold,permmap(ls,rng))
        if q is None: raise RuntimeError("invalid permutation")
        null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(NPERM+1))
    pos=sum(v>0 for v in bm.values())
    return {
        "K":float(obs),"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
        "p_one_sided":p,"null_mean":float(a.mean()),
        "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
        "valid_permutations":NPERM,"seed":seed,
        "supported":bool(obs>0 and p<=.05 and pos>=4)
    }

def main():
    # PCA1
    rows,envs=L.standardized_rows()
    folds=L.project_pca_folds(rows,envs)
    pca_coords={e:[float(x[0]) for x in folds[e]["scores"]] for e in envs}
    pca=calibrate(rows,envs,pca_coords,20261007911)

    # Transparent scalar
    srows,senvs=F.load_scalar_rows()
    if senvs!=envs: raise RuntimeError("environment mismatch")
    scalar=np.asarray([r["flight_intensity"] for r in srows],float)
    scalar_coords={e:scalar.copy() for e in envs}
    fi=calibrate(srows,envs,scalar_coords,20261007912)

    out={
      "status":"POST_PRIMARY_SUPPORT_MATCHING_DIAGNOSTIC",
      "contract":"RHINO_TWO_ENV_SUPPORT_CONTRACT_V1.md",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),
      "PCA1_exactly_two_training_environments":pca,
      "FlightIntensity_exactly_two_training_environments":fi,
      "reference":{
        "Miniopterus_n_trajectories":19,
        "Miniopterus_training_environments_per_bat":3,
        "Miniopterus_PCA1_K":-0.16875692138998233
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
