#!/usr/bin/env python3
"""Held-out relational stability of pairwise scale-free geometry."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEED=202610061901

def rank_average(a):
    a=np.asarray(a,float)
    o=np.argsort(a,kind="mergesort");r=np.empty(len(a),float)
    i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[o[j]]==a[o[i]]:j+=1
        rr=(i+j-1)/2+1
        r[o[i:j]]=rr;i=j
    return r

def corr(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if len(a)<3 or len(a)!=len(b):return math.nan
    aa=a-a.mean();bb=b-b.mean()
    den=float(np.sqrt(np.sum(aa*aa)*np.sum(bb*bb)))
    return float(np.sum(aa*bb)/den) if den>0 else math.nan

def spearman(a,b):
    return corr(rank_average(a),rank_average(b))

def centroids():
    traj=G.P.load_rhino()
    rows=[]
    for r in traj:
        f=G.geometry_features(r)
        if f is not None:rows.append({**r,"gfeat":np.asarray(f,float)})
    envs=sorted(set(r["env"] for r in rows))
    out={}
    for e in envs:
        rr=[r for r in rows if r["env"]==e]
        M=np.vstack([r["gfeat"] for r in rr]);mu=M.mean(0);sd=M.std(0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError(f"bad SD env {e}")
        tmp=collections.defaultdict(list)
        for r in rr:tmp[r["bat"]].append((r["gfeat"]-mu)/sd)
        for b,v in tmp.items():out[(e,b)]=np.mean(np.vstack(v),axis=0)
    return envs,out

def predictor(envs,gc,e0,i,j):
    vals=[]
    for e in envs:
        if e==e0:continue
        if (e,i) in gc and (e,j) in gc:
            vals.append(float(np.linalg.norm(gc[(e,i)]-gc[(e,j)])))
    if len(vals)<2:return None
    return float(np.mean(vals))

def records(envs,gc,maps=None):
    rec=[];counts={}
    for e0 in envs:
        obs={b:v for (e,b),v in gc.items() if e==e0}
        if maps is None:
            geom=obs
        else:
            geom={maps[e0][old]:v for old,v in obs.items()}
        bats=sorted(geom)
        n=0
        for a in range(len(bats)):
            for b in range(a+1,len(bats)):
                i,j=bats[a],bats[b]
                p=predictor(envs,gc,e0,i,j)
                if p is None:continue
                d=float(np.linalg.norm(geom[i]-geom[j]))
                rec.append({"env":e0,"i":i,"j":j,"pred":p,"target":d});n+=1
        counts[str(e0)]=n
    return rec,counts

def metrics(rec):
    if len(rec)<5:return None
    x=[r["pred"] for r in rec];y=[r["target"] for r in rec]
    s=spearman(x,y);p=corr(x,y)
    if not (math.isfinite(s) and math.isfinite(p)):return None
    by={}
    for e in sorted(set(r["env"] for r in rec)):
        q=[r for r in rec if r["env"]==e]
        ss=spearman([z["pred"] for z in q],[z["target"] for z in q]) if len(q)>=3 else math.nan
        pp=corr([z["pred"] for z in q],[z["target"] for z in q]) if len(q)>=3 else math.nan
        by[str(e)]={"n_pairs":len(q),"spearman":float(ss) if math.isfinite(ss) else None,
                    "pearson":float(pp) if math.isfinite(pp) else None}
    return {"spearman_rho":float(s),"pearson_r":float(p),
            "n_pair_environment_points":len(rec),"by_environment":by}

def perm_maps(envs,gc,rng):
    out={}
    for e in envs:
        labs=sorted(b for ee,b in gc if ee==e)
        pp=list(rng.permutation(np.asarray(labs,dtype=object)))
        out[e]={old:str(new) for old,new in zip(labs,pp)}
    return out

def main():
    envs,gc=centroids()
    rec,counts=records(envs,gc)
    obs=metrics(rec)
    if obs is None:raise RuntimeError("observed support failed")
    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        rr,_=records(envs,gc,perm_maps(envs,gc,rng))
        q=metrics(rr)
        if q is not None and math.isfinite(q["spearman_rho"]):null.append(q["spearman_rho"])
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:raise RuntimeError(f"null support {len(a)}")
    p=float((1+np.sum(a>=obs["spearman_rho"]))/(1+len(a)))
    print(json.dumps({
      "contract":"HELDOUT_GEOMETRY_RELATIONAL_STABILITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "environments":envs,"pair_counts":counts,"observed":obs,
      "permutation":{"requested":NPERM,"valid":int(len(a)),"seed":SEED,
        "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),"p_one_sided":p},
      "diagnostic_verdict":"SUPPORTED_HELDOUT_GEOMETRY_RELATIONAL_STABILITY"
          if (obs["spearman_rho"]>0 and p<=.05)
          else "UNSUPPORTED_HELDOUT_GEOMETRY_RELATIONAL_STABILITY"
    },indent=2))

if __name__=="__main__":main()
