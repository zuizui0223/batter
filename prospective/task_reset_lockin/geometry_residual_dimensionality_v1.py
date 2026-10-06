#!/usr/bin/env python3
"""Training-only PCA localization of held-out geometry identity beyond cross-fitted I/M."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("X",HERE/"geometry_crossfit_im_expression_v1.py")
X=importlib.util.module_from_spec(spec);spec.loader.exec_module(X)

NPERM=9999
MIN_VALID=9500
SEEDS={"PC1":202610061901,"PC12":202610061902,"RESID12":202610061903}

def build_folds(rows,envs):
    folds={};vf={}
    for e0 in envs:
        rr=X.fold_residuals(rows,e0)
        if rr is None:raise RuntimeError(f"fold residual support failed env={e0}")
        train=[r for r in rr if r["env"]!=e0]
        R=np.vstack([r["resid"] for r in train]).astype(float)
        mu=R.mean(axis=0)
        C=R-mu
        _,s,vt=np.linalg.svd(C,full_matrices=False)
        if len(s)<2:raise RuntimeError(f"<2 PCs env={e0}")
        # deterministic sign orientation
        V=vt.copy()
        for k in range(V.shape[0]):
            j=int(np.argmax(np.abs(V[k])))
            if V[k,j]<0:V[k]*=-1
        var=s*s
        frac=var/var.sum() if var.sum()>0 else np.full_like(var,np.nan)
        vf[str(e0)]={
          "PC1":float(frac[0]),
          "PC1_PC2":float(frac[:2].sum())
        }
        out=[]
        for r in rr:
            c=np.asarray(r["resid"],float)-mu
            score=c@V.T
            q=dict(r)
            q["PC1"]=np.asarray(score[:1],float)
            q["PC12"]=np.asarray(score[:2],float)
            q["RESID12"]=np.asarray(c-score[:2]@V[:2],float)
            out.append(q)
        folds[e0]=out
    return folds,vf

def idmap(rows):
    return {(e,b):b for e,b in sorted(set((r["env"],r["bat"]) for r in rows))}

def labelsets(rows):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e))
            for e in sorted(set(r["env"] for r in rows))}

def permmap(ls,rng):
    out={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):out[(e,old)]=str(new)
    return out

def stat(folds,envs,mapping,key):
    vals=collections.defaultdict(list)
    for e0 in envs:
        rr=folds[e0]
        cent=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rr:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            cent[lab][r["env"]].append(r[key])
        train={}
        for b,d in cent.items():
            envc=[np.mean(np.vstack(v),axis=0) for _,v in sorted(d.items()) if v]
            if len(envc)>=2:train[b]=np.mean(np.vstack(envc),axis=0)
        if len(train)<3:continue
        for r in [x for x in rr if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train:continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2:continue
            x=r[key]
            ds=float(np.linalg.norm(x-train[lab]))
            do=float(np.mean([np.linalg.norm(x-train[b]) for b in donors]))
            vals[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in vals.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def run(folds,rows,envs,key,seed):
    obs,bm=stat(folds,envs,idmap(rows),key)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    ls=labelsets(rows);rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        s,_=stat(folds,envs,permmap(ls,rng),key)
        if s is not None and math.isfinite(s):null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:return {"status":"STOP_RANDOMIZATION_SUPPORT","valid_permutations":len(a)}
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values())
    return {
      "status":"DONE","K":float(obs),"bat_means":bm,
      "positive_bats":int(pos),"n_bats":len(bm),
      "positive_fraction":float(pos/len(bm)),
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "supported":bool(obs>0 and p<=.05 and pos>=4)
    }

def main():
    rows,envs=X.rows_raw()
    if envs!=list(range(1,8)):raise RuntimeError(f"environment drift {envs}")
    folds,vf=build_folds(rows,envs)
    vals1=np.array([v["PC1"] for v in vf.values()],float)
    vals2=np.array([v["PC1_PC2"] for v in vf.values()],float)
    out={
      "contract":"GEOMETRY_RESIDUAL_DIMENSIONALITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_FALSIFICATION_DIAGNOSTIC",
      "n_trajectories":len(rows),"environments":envs,
      "variance_fraction_by_fold":vf,
      "variance_summary":{
        "PC1_min":float(vals1.min()),"PC1_median":float(np.median(vals1)),"PC1_max":float(vals1.max()),
        "PC12_min":float(vals2.min()),"PC12_median":float(np.median(vals2)),"PC12_max":float(vals2.max())
      },
      "D1_PC1":run(folds,rows,envs,"PC1",SEEDS["PC1"]),
      "D2_PC12":run(folds,rows,envs,"PC12",SEEDS["PC12"]),
      "D3_RESID12":run(folds,rows,envs,"RESID12",SEEDS["RESID12"])
    }
    a=out["D1_PC1"].get("supported",False)
    b=out["D2_PC12"].get("supported",False)
    c=out["D3_RESID12"].get("supported",False)
    if a and not c:verdict="LOW_DIMENSIONAL_RESIDUAL_CARRIER"
    elif (not a) and b and not c:verdict="TWO_PC_RESIDUAL_CARRIER"
    elif b and c:verdict="RESIDUAL_IDENTITY_EXTENDS_BEYOND_TWO_PCS"
    elif not b:verdict="NO_LEADING_TWO_PC_RESIDUAL_CARRIER"
    else:verdict="MIXED_RESIDUAL_DIMENSIONALITY"
    out["diagnostic_verdict"]=verdict
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
