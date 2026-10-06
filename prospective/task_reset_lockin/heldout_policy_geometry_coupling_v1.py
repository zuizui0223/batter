#!/usr/bin/env python3
"""Held-out portable-policy distance to target geometry-distance coupling."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("T",HERE/"transparent_two_axis_policy_v1.py")
T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
spec2=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEED=202610061801

def rank_average(a):
    a=np.asarray(a,float)
    order=np.argsort(a,kind="mergesort")
    r=np.empty(len(a),float)
    i=0
    while i<len(a):
        j=i+1
        while j<len(a) and a[order[j]]==a[order[i]]:
            j+=1
        rank=(i+j-1)/2.0+1.0
        r[order[i:j]]=rank
        i=j
    return r

def corr(a,b):
    a=np.asarray(a,float);b=np.asarray(b,float)
    if len(a)<3 or len(b)!=len(a):return math.nan
    ac=a-a.mean();bc=b-b.mean()
    den=float(np.sqrt(np.sum(ac*ac)*np.sum(bc*bc)))
    return float(np.sum(ac*bc)/den) if den>0 else math.nan

def spearman(a,b):
    return corr(rank_average(a),rank_average(b))

def build_centroids():
    # Movement-policy rows use exactly the frozen within-environment
    # standardization and transparent I/M definitions.
    mrows,envs=T.standardized_rows()

    # Geometry is recalculated from the same authoritative Rhino trajectories
    # and standardized within target environment exactly as in the parent.
    traj=T.P.load_rhino()
    grows=[]
    for r in traj:
        gf=G.geometry_features(r)
        if gf is not None:
            grows.append({**r,"gfeat":np.asarray(gf,float)})

    gstd=[]
    genvs=sorted(set(r["env"] for r in grows))
    for e in genvs:
        rr=[r for r in grows if r["env"]==e]
        M=np.vstack([r["gfeat"] for r in rr])
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"geometry SD support failed env={e}")
        for r in rr:
            q=dict(r);q["gz"]=(r["gfeat"]-mu)/sd
            gstd.append(q)

    if envs!=genvs:
        raise RuntimeError(f"environment mismatch movement={envs} geometry={genvs}")

    mc=collections.defaultdict(list)
    for r in mrows:
        mc[(r["env"],r["bat"])].append(np.array([r["I"],r["M"]],float))
    mc={k:np.mean(np.vstack(v),axis=0) for k,v in mc.items()}

    gc=collections.defaultdict(list)
    for r in gstd:
        gc[(r["env"],r["bat"])].append(np.asarray(r["gz"],float))
    gc={k:np.mean(np.vstack(v),axis=0) for k,v in gc.items()}

    return envs,mc,gc

def heldout_theta(envs,mc,e0):
    bats=sorted(set(b for _,b in mc))
    out={}
    for b in bats:
        vals=[mc[(e,b)] for e in envs if e!=e0 and (e,b) in mc]
        if len(vals)>=2:
            out[b]=np.mean(np.vstack(vals),axis=0)
    return out

def observed_records(envs,mc,gc,geom_label_maps=None):
    records=[]
    pair_counts={}
    for e0 in envs:
        theta=heldout_theta(envs,mc,e0)
        geom_obs={b:v for (e,b),v in gc.items() if e==e0}
        if geom_label_maps is None:
            geom={b:v for b,v in geom_obs.items()}
        else:
            geom={}
            mp=geom_label_maps[e0]
            # old geometry cluster is reassigned to new biological label
            for old,v in geom_obs.items():
                geom[mp[old]]=v

        eligible=sorted(set(theta).intersection(geom))
        n=0
        for ii in range(len(eligible)):
            for jj in range(ii+1,len(eligible)):
                i,j=eligible[ii],eligible[jj]
                dt=float(np.linalg.norm(theta[i]-theta[j]))
                dg=float(np.linalg.norm(geom[i]-geom[j]))
                records.append({"env":e0,"i":i,"j":j,"d_theta":dt,"d_geometry":dg})
                n+=1
        pair_counts[str(e0)]=n
    return records,pair_counts

def metrics(records):
    x=np.asarray([r["d_theta"] for r in records],float)
    y=np.asarray([r["d_geometry"] for r in records],float)
    if len(x)<5:return None
    rho=spearman(x,y);pear=corr(x,y)
    if not (math.isfinite(rho) and math.isfinite(pear)):return None
    byenv={}
    for e in sorted(set(r["env"] for r in records)):
        rr=[r for r in records if r["env"]==e]
        if len(rr)>=3:
            sr=spearman([r["d_theta"] for r in rr],[r["d_geometry"] for r in rr])
            pr=corr([r["d_theta"] for r in rr],[r["d_geometry"] for r in rr])
        else:
            sr=pr=math.nan
        byenv[str(e)]={"n_pairs":len(rr),
                       "spearman":float(sr) if math.isfinite(sr) else None,
                       "pearson":float(pr) if math.isfinite(pr) else None}
    return {"spearman_rho":float(rho),"pearson_r":float(pear),
            "n_pair_environment_points":int(len(records)),
            "by_environment":byenv}

def perm_maps(envs,gc,rng):
    out={}
    for e in envs:
        labs=sorted(b for ee,b in gc if ee==e)
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        out[e]={old:str(new) for old,new in zip(labs,p)}
    return out

def main():
    envs,mc,gc=build_centroids()
    rec,pair_counts=observed_records(envs,mc,gc)
    obs=metrics(rec)
    if obs is None:raise RuntimeError("observed coupling support failed")

    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        rr,_=observed_records(envs,mc,gc,perm_maps(envs,gc,rng))
        q=metrics(rr)
        if q is not None and math.isfinite(q["spearman_rho"]):
            null.append(q["spearman_rho"])
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:
        raise RuntimeError(f"randomization support failed {len(a)}")
    p=float((1+np.sum(a>=obs["spearman_rho"]))/(1+len(a)))
    supported=bool(obs["spearman_rho"]>0 and p<=.05)

    print(json.dumps({
      "contract":"HELDOUT_POLICY_GEOMETRY_COUPLING_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MECHANISM_DIAGNOSTIC",
      "environments":envs,
      "pair_counts":pair_counts,
      "observed":obs,
      "permutation":{
        "requested":NPERM,"valid":int(len(a)),"seed":SEED,
        "null_mean":float(a.mean()),
        "null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),
        "p_one_sided":p
      },
      "diagnostic_verdict":"SUPPORTED_HELDOUT_POLICY_GEOMETRY_COUPLING" if supported
                           else "UNSUPPORTED_HELDOUT_POLICY_GEOMETRY_COUPLING"
    },indent=2))

if __name__=="__main__":main()
