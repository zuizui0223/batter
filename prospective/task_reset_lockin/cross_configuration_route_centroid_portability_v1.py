#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(P)

NPERM=9999
SEED=20261007941
MIN_VALID=9500

def build_rows():
    traj=[r for r in P.load_rhino() if r["route_valid"]]
    raw=[]
    for r in traj:
        c=np.mean(np.asarray(r["route101"],float),axis=0)
        raw.append({"env":int(r["env"]),"bat":str(r["bat"]),"name":r["name"],"c":c})
    envs=sorted(set(r["env"] for r in raw))
    rows=[]
    for e in envs:
        rr=[r for r in raw if r["env"]==e]
        M=np.vstack([r["c"] for r in rr])
        mu=M.mean(axis=0); sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad centroid SD env={e}: {sd}")
        for r in rr:
            rows.append({**r,"z":(r["c"]-mu)/sd})
    return rows,envs

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def identity_map(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def perm_map(ls,rng):
    out={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for a,b in zip(labs,p):out[(e,a)]=str(b)
    return out

def stat(rows,envs,mapping):
    cell=collections.defaultdict(list)
    presence=collections.defaultdict(set)
    for r in rows:
        lab=mapping[(r["env"],r["bat"])]
        cell[(r["env"],lab)].append(r["z"])
        presence[lab].add(r["env"])
    cm={k:np.mean(np.vstack(v),axis=0) for k,v in cell.items()}
    candidates=sorted([b for b,es in presence.items() if len(es)>=3])
    perbat=collections.defaultdict(list)
    targets=[]
    for r in rows:
        e=r["env"]; b=mapping[(e,r["bat"])]
        if b not in candidates:continue
        own_envs=[ee for ee in sorted(presence[b]) if ee!=e and (ee,b) in cm]
        if len(own_envs)<2:continue
        own=np.mean(np.vstack([cm[(ee,b)] for ee in own_envs]),axis=0)
        donors=[]
        for j in candidates:
            if j==b:continue
            jes=[ee for ee in sorted(presence[j]) if ee!=e and (ee,j) in cm]
            if len(jes)>=2:
                donors.append((j,np.mean(np.vstack([cm[(ee,j)] for ee in jes]),axis=0)))
        if len(donors)<2:continue
        ds=float(np.linalg.norm(r["z"]-own))
        do=float(np.mean([np.linalg.norm(r["z"]-x) for _,x in donors]))
        k=do-ds
        perbat[b].append(k)
        targets.append({"env":e,"bat":b,"name":r["name"],"K":k,"D_self":ds,"D_other":do})
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None
    return float(np.mean(list(bm.values()))),bm,targets

def main():
    rows,envs=build_rows()
    ls=labelsets(rows,envs)
    obs=stat(rows,envs,identity_map(ls))
    if obs is None:raise RuntimeError("observed support")
    K,bm,targets=obs
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        q=stat(rows,envs,perm_map(ls,rng))
        if q is not None:null.append(q[0])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=K))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    support=bool(len(a)>=MIN_VALID and K>0 and p<=.05 and pos/len(bm)>=.70)
    out={
      "contract":"CROSS_CONFIGURATION_ROUTE_CENTROID_PORTABILITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),"environments":envs,
      "K_centroid":K,"bat_means":bm,
      "positive_bats":pos,"n_bats":len(bm),"positive_fraction":pos/len(bm),
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":SEED,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "targets":targets,
      "supported":support,
      "interpretation":"PORTABLE_RELATIVE_LANE_COORDINATE" if support else "CONFIGURATION_SPECIFIC_LANE_STATE"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
