#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("F",HERE/"flight_intensity_scalar_v1.py")
F=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(F)

B=9999
SEED=20261007901

def centroids(rows,envs,mapping):
    cm={}
    for e in envs:
        olds=sorted(set(r["bat"] for r in rows if r["env"]==e))
        for old in olds:
            lab=mapping[(e,old)]
            vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==old]
            cm[(e,lab)]=float(np.mean(vals))
    return cm

def obs_mapping(rows,envs):
    return {(e,b):b for e in envs for b in sorted(set(r["bat"] for r in rows if r["env"]==e))}

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm): mp[(e,old)]=str(new)
    return mp

def slopes(cm,envs):
    rows=[]
    bats=sorted(set(b for _,b in cm))
    for e0 in envs:
        xs=[]; ys=[]; used=[]
        for b in bats:
            if (e0,b) not in cm: continue
            train=[cm[(e,b)] for e in envs if e!=e0 and (e,b) in cm]
            if len(train)<2: continue
            xs.append(float(np.mean(train))); ys.append(float(cm[(e0,b)])); used.append(b)
        if len(xs)<3: continue
        x=np.asarray(xs,float); y=np.asarray(ys,float)
        X=np.column_stack([np.ones(len(x)),x])
        beta=np.linalg.lstsq(X,y,rcond=None)[0]
        r=float(np.corrcoef(x,y)[0,1]) if np.std(x)>0 and np.std(y)>0 else math.nan
        rows.append({"env":e0,"n":len(x),"bats":used,"intercept":float(beta[0]),"alpha":float(beta[1]),"pearson_r":r})
    return rows

def summary(sr):
    a=np.asarray([r["alpha"] for r in sr],float)
    return {"n_env":len(sr),"mean_alpha":float(np.mean(a)),"median_alpha":float(np.median(a)),
            "positive_envs":int(np.sum(a>0)),"positive_fraction":float(np.mean(a>0))}

def main():
    rows,envs=F.load_scalar_rows()
    ls=labelsets(rows,envs)
    cm=centroids(rows,envs,obs_mapping(rows,envs))
    sr=slopes(cm,envs); sm=summary(sr)
    target_n=sm["n_env"]

    rng=np.random.default_rng(SEED)
    null_mean=[]; null_pos=[]; invalid=0
    for _ in range(B):
        pcm=centroids(rows,envs,perm_mapping(ls,rng))
        ps=slopes(pcm,envs)
        if len(ps)!=target_n:
            invalid+=1; continue
        q=summary(ps)
        null_mean.append(q["mean_alpha"]); null_pos.append(q["positive_envs"])
    a=np.asarray(null_mean,float); p=np.asarray(null_pos,float)
    pmean=float((1+np.sum(a>=sm["mean_alpha"]))/(1+len(a)))
    ppos=float((1+np.sum(p>=sm["positive_envs"]))/(1+len(p)))
    out={"status":"POST_OUTCOME_MECHANISM_DIAGNOSTIC",
         "contract":"RHINO_CONFIGURATION_ALPHA_CONTRACT_V1.md",
         "environment_results":sr,"summary":sm,
         "null":{"B_requested":B,"valid":len(a),"invalid":invalid,"seed":SEED,
                 "mean_alpha_null_mean":float(a.mean()),"mean_alpha_q025":float(np.quantile(a,.025)),
                 "mean_alpha_q975":float(np.quantile(a,.975)),"p_mean_alpha_one_sided":pmean,
                 "positive_envs_null_mean":float(p.mean()),"p_positive_envs_one_sided":ppos}}
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
