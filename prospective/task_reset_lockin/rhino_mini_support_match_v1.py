#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, itertools, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(L)

B=9999
BATS=["A","B","C","D","E"]

def base_rows():
    rows,envs=L.standardized_rows()
    for r in rows:
        r["flight_intensity"]=float(np.mean(np.asarray(r["z8"],float)[:4]))
    return rows,envs

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def idmap(rows,envs):
    return {(e,b):b for e in envs for b in sorted(set(r["bat"] for r in rows if r["env"]==e))}

def permap(ls,rng):
    out={}
    for e,labs in ls.items():
        if not labs: continue
        q=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,q): out[(e,old)]=str(new)
    return out

def assigned(r,mp):
    return mp[(r["env"],r["bat"])]

def pca_coords(rows,envs):
    out={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        X=np.vstack([r["z8"] for r in train]).astype(float)
        mu=X.mean(axis=0); Xc=X-mu
        _,_,Vt=np.linalg.svd(Xc,full_matrices=False)
        v=Vt[0]
        out[e0]=np.asarray([(np.asarray(r["z8"],float)-mu)@v for r in rows],float)
    return out

def scalar_coords(rows,envs):
    x=np.asarray([r["flight_intensity"] for r in rows],float)
    return {e:x.copy() for e in envs}

def cluster_values(rows,coords,envs,mp,target_env):
    # assigned label -> environment -> trajectory scalar values
    out=collections.defaultdict(lambda:collections.defaultdict(list))
    for i,r in enumerate(rows):
        e=r["env"]
        if e==target_env: continue
        lab=assigned(r,mp)
        out[lab][e].append(float(coords[i]))
    return out

def one_traj_two_env_centroids(envvals):
    es=sorted(envvals)
    if len(es)<2: return []
    cent=[]
    for e1,e2 in itertools.combinations(es,2):
        for a in envvals[e1]:
            for b in envvals[e2]:
                cent.append(0.5*(a+b))
    return cent

def stat(rows,envs,coords_by_fold,mp):
    per=collections.defaultdict(list)
    for e0 in envs:
        coords=coords_by_fold[e0]
        cv=cluster_values(rows,coords,envs,mp,e0)
        cents={lab:one_traj_two_env_centroids(d) for lab,d in cv.items()}
        cents={lab:v for lab,v in cents.items() if v}
        if len(cents)<3: continue
        for i,r in enumerate(rows):
            if r["env"]!=e0: continue
            lab=assigned(r,mp)
            if lab not in cents: continue
            donors=[b for b in cents if b!=lab]
            if len(donors)<2: continue
            z=float(coords[i])
            ds=float(np.mean([abs(z-c) for c in cents[lab]]))
            dmean=[]
            for b in donors:
                dmean.append(float(np.mean([abs(z-c) for c in cents[b]])))
            do=float(np.mean(dmean))
            per[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in per.items() if v}
    if len(bm)<3: return None,bm
    return float(np.mean(list(bm.values()))),bm

def calibrate(rows,envs,coords,seed):
    ls=labelsets(rows,envs)
    obs,bm=stat(rows,envs,coords,idmap(rows,envs))
    if obs is None: raise RuntimeError("observed support failure")
    rng=np.random.default_rng(seed)
    null=np.empty(B,float)
    for q in range(B):
        k,_=stat(rows,envs,coords,permap(ls,rng))
        if k is None: raise RuntimeError("invalid permutation")
        null[q]=k
    p=float((1+np.sum(null>=obs))/(B+1))
    pos=sum(v>0 for v in bm.values())
    return {
      "K":float(obs),"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
      "p_one_sided":p,"null_mean":float(null.mean()),
      "null_q025":float(np.quantile(null,.025)),"null_q975":float(np.quantile(null,.975)),
      "valid_permutations":B,"seed":seed,
      "supported":bool(obs>0 and p<=.05 and pos>=3)
    }

def main():
    allrows,allenvs=base_rows()
    result={}
    for ix,omit in enumerate(BATS,1):
        rows=[dict(r) for r in allrows if r["bat"]!=omit]
        envs=sorted(set(r["env"] for r in rows))
        pcoords=pca_coords(rows,envs)
        fcoords=scalar_coords(rows,envs)
        p=calibrate(rows,envs,pcoords,20261007920+ix)
        f=calibrate(rows,envs,fcoords,20261007930+ix)
        result[omit]={
          "n_trajectories":len(rows),
          "environments":envs,
          "PCA1":p,
          "FlightIntensity":f
        }
    out={
      "status":"POST_PRIMARY_SUPPORT_STRESS_DIAGNOSTIC",
      "contract":"RHINO_MINI_SUPPORT_MATCH_CONTRACT_V1.md",
      "species":"Rhinolophus nippon",
      "subsets":result,
      "summary":{
        "PCA1_supported_subsets":sum(v["PCA1"]["supported"] for v in result.values()),
        "FlightIntensity_supported_subsets":sum(v["FlightIntensity"]["supported"] for v in result.values()),
        "subset_count":len(result),
        "PCA1_robust_all":all(v["PCA1"]["supported"] for v in result.values()),
        "FlightIntensity_robust_all":all(v["FlightIntensity"]["supported"] for v in result.values())
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
