#!/usr/bin/env python3
"""Cross-fitted transparent I/M -> scale-free geometry residual identity."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEED=202610061601

def rows_raw():
    traj=G.P.load_rhino()
    rows=[]
    for r in traj:
        gf=G.geometry_features(r)
        if gf is None or not r.get("feature_valid",False): continue
        rows.append({**r,"gfeat":np.asarray(gf,float),"mfeat":np.asarray(r["features"],float)})
    return rows,sorted(set(r["env"] for r in rows))

def idmap(rows):
    return {(e,b):b for e,b in sorted(set((r["env"],r["bat"]) for r in rows))}

def permmap(rows,rng):
    out={}
    for e in sorted(set(r["env"] for r in rows)):
        labs=sorted(set(r["bat"] for r in rows if r["env"]==e))
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p): out[(e,old)]=str(new)
    return out

def fold_residuals(rows,e0):
    tr=[r for r in rows if r["env"]!=e0]
    if not tr:return None
    M=np.vstack([r["mfeat"] for r in tr])
    Gm=np.vstack([r["gfeat"] for r in tr])
    mm=M.mean(0); ms=M.std(0,ddof=1)
    gm=Gm.mean(0); gs=Gm.std(0,ddof=1)
    if np.any(~np.isfinite(ms)) or np.any(ms<=0) or np.any(~np.isfinite(gs)) or np.any(gs<=0):
        return None
    def trans(r):
        mz=(r["mfeat"]-mm)/ms
        gz=(r["gfeat"]-gm)/gs
        I=float(np.mean(mz[:4]))
        Man=float(np.mean(np.array([-mz[0],mz[4],mz[5],mz[6],mz[7]],float)))
        return I,Man,gz
    X=[];Y=[]
    for r in tr:
        I,Man,gz=trans(r);X.append([1.0,I,Man]);Y.append(gz)
    X=np.asarray(X,float);Y=np.vstack(Y)
    B=np.linalg.lstsq(X,Y,rcond=None)[0]
    out=[]
    for r in rows:
        I,Man,gz=trans(r)
        resid=gz-np.array([1.0,I,Man])@B
        q=dict(r);q["resid"]=np.asarray(resid,float)
        out.append(q)
    return out

def stat(rows,envs,mapping):
    vals=collections.defaultdict(list)
    for e0 in envs:
        rr=fold_residuals(rows,e0)
        if rr is None:continue
        cent=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rr:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            cent[lab][r["env"]].append(r["resid"])
        train={}
        for b,d in cent.items():
            envc=[np.mean(np.vstack(v),0) for _,v in sorted(d.items()) if v]
            if len(envc)>=2: train[b]=np.mean(np.vstack(envc),0)
        if len(train)<3:continue
        for r in [x for x in rr if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train:continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2:continue
            ds=float(np.linalg.norm(r["resid"]-train[lab]))
            do=float(np.mean([np.linalg.norm(r["resid"]-train[b]) for b in donors]))
            vals[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,envs=rows_raw()
    if envs!=list(range(1,8)):raise RuntimeError(f"environment drift {envs}")
    obs,bm=stat(rows,envs,idmap(rows))
    if obs is None:raise RuntimeError("observed support failed")
    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        s,_=stat(rows,envs,permmap(rows,rng))
        if s is not None and math.isfinite(s):null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:raise RuntimeError(f"randomization support {len(a)}")
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    support=bool(obs>0 and p<=.05 and pos>=4)
    print(json.dumps({
      "contract":"GEOMETRY_CROSSFIT_IM_EXPRESSION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_FALSIFICATION_DIAGNOSTIC",
      "n_trajectories":len(rows),"environments":envs,
      "residual_geometry_identity":{
        "K":float(obs),"bat_means":bm,"positive_bats":int(pos),
        "n_bats":len(bm),"positive_fraction":float(pos/len(bm)),
        "requested_permutations":NPERM,"valid_permutations":len(a),"seed":SEED,
        "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
        "verdict":"SUPPORTED_GEOMETRY_BEYOND_CROSSFIT_IM" if support else "UNSUPPORTED_GEOMETRY_BEYOND_CROSSFIT_IM"
      }
    },indent=2))

if __name__=="__main__":main()
