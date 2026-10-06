#!/usr/bin/env python3
"""Cross-fitted residual identity between global-route and horizontal-maneuver geometry families."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEEDS={"H_after_G":202610061301,"G_after_H":202610061302}
GIDX=[0,1,2,3]
HIDX=[4,5]

def raw_rows():
    traj=G.P.load_rhino()
    rows=[]
    for r in traj:
        f=G.geometry_features(r)
        if f is None:continue
        rows.append({**r,"gfeat":np.asarray(f,float)})
    envs=sorted(set(r["env"] for r in rows))
    return rows,envs

def mapping_identity(rows):
    return {(e,b):b for e,b in sorted(set((r["env"],r["bat"]) for r in rows))}

def mapping_perm(rows,rng):
    mp={}
    envs=sorted(set(r["env"] for r in rows))
    for e in envs:
        labs=sorted(set(r["bat"] for r in rows if r["env"]==e))
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):mp[(e,old)]=str(new)
    return mp

def residualize_fold(rows,target_env,mode):
    train=[r for r in rows if r["env"]!=target_env]
    target=[r for r in rows if r["env"]==target_env]
    M=np.vstack([r["gfeat"][GIDX+HIDX] for r in train])
    mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0):
        return None

    def zfeat(r):
        return (r["gfeat"][GIDX+HIDX]-mu)/sd

    Ztr=np.vstack([zfeat(r) for r in train])
    Gtr=Ztr[:,:4];Htr=Ztr[:,4:]
    if mode=="H_after_G":
        X=np.column_stack([np.ones(len(Gtr)),Gtr])
        coef=np.linalg.lstsq(X,Htr,rcond=None)[0]
        def res(r):
            z=zfeat(r);g=z[:4];h=z[4:]
            return h-np.r_[1.0,g]@coef
    elif mode=="G_after_H":
        X=np.column_stack([np.ones(len(Htr)),Htr])
        coef=np.linalg.lstsq(X,Gtr,rcond=None)[0]
        def res(r):
            z=zfeat(r);g=z[:4];h=z[4:]
            return g-np.r_[1.0,h]@coef
    else:
        raise ValueError(mode)

    out=[]
    for r in rows:
        q=dict(r);q["resid"]=np.asarray(res(r),float)
        if np.all(np.isfinite(q["resid"])):out.append(q)
    return out

def stat(rows,envs,mode,mapping):
    vals=collections.defaultdict(list)
    for e0 in envs:
        rr=residualize_fold(rows,e0,mode)
        if rr is None:continue
        cent=collections.defaultdict(list)
        for r in rr:
            lab=mapping[(r["env"],r["bat"])]
            cent[(r["env"],lab)].append(r["resid"])
        cent={k:np.mean(np.vstack(v),axis=0) for k,v in cent.items()}
        bats=sorted(set(lab for _,lab in cent))
        presence=collections.defaultdict(set)
        for e,b in cent:presence[b].add(e)
        candidate=[b for b in bats if len(presence[b])>=3]
        for r in [x for x in rr if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in candidate:continue
            own_envs=[e for e in sorted(presence[lab]) if e!=e0 and (e,lab) in cent]
            if len(own_envs)<2:continue
            own=np.mean(np.vstack([cent[(e,lab)] for e in own_envs]),axis=0)
            donors=[]
            for b in candidate:
                if b==lab:continue
                ees=[e for e in sorted(presence[b]) if e!=e0 and (e,b) in cent]
                if len(ees)>=2:
                    donors.append(np.mean(np.vstack([cent[(e,b)] for e in ees]),axis=0))
            if len(donors)<2:continue
            ds=float(np.linalg.norm(r["resid"]-own))
            do=float(np.mean([np.linalg.norm(r["resid"]-d) for d in donors]))
            vals[lab].append(do-ds)
    indiv={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(indiv)<3:return None,indiv
    return float(np.mean(list(indiv.values()))),indiv

def run(rows,envs,mode,seed):
    obs,ind=stat(rows,envs,mode,mapping_identity(rows))
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        s,_=stat(rows,envs,mode,mapping_perm(rows,rng))
        if s is not None and math.isfinite(s):null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:return {"status":"STOP_RANDOMIZATION_SUPPORT","valid_permutations":int(len(a))}
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in ind.values())
    return {
      "status":"DONE","K":float(obs),"bat_means":ind,
      "positive_bats":int(pos),"n_bats":int(len(ind)),
      "positive_fraction":float(pos/len(ind)),
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "supported":bool(obs>0 and p<=.05 and pos>=4)
    }

def main():
    rows,envs=raw_rows()
    out={
      "contract":"GEOMETRY_FAMILY_CROSSFIT_RESIDUAL_CONTRACT_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_MECHANISM_DIAGNOSTIC",
      "n_trajectories":len(rows),"environments":envs,
      "H_after_G":run(rows,envs,"H_after_G",SEEDS["H_after_G"]),
      "G_after_H":run(rows,envs,"G_after_H",SEEDS["G_after_H"])
    }
    a=out["H_after_G"].get("supported",False);b=out["G_after_H"].get("supported",False)
    out["diagnostic_verdict"]=(
      "BOTH_RESIDUAL_FAMILIES_IDENTITY_BEARING" if a and b else
      "H_INCREMENTAL_ONLY" if a else
      "G_INCREMENTAL_ONLY" if b else
      "NEITHER_RESIDUAL_FAMILY_SUPPORTED")
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
