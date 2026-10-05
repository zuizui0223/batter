#!/usr/bin/env python3
"""Held-out transparent two-parameter policy law for Rhinolophus nippon."""
from __future__ import annotations

import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("T",HERE/"transparent_two_axis_policy_v1.py")
T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)

NPERM=9999
MIN_VALID=9500
SEEDS={"P1":202610051001,"P2I":202610051002,"P2M":202610051003,"P3":202610051004}

def centroid_table(rows,envs):
    out={}
    for e in envs:
        for b in sorted(set(r["bat"] for r in rows if r["env"]==e)):
            vals=np.array([[r["I"],r["M"]] for r in rows if r["env"]==e and r["bat"]==b],float)
            out[(e,b)]=vals.mean(axis=0)
    return out

def labelsets(cm,envs):
    return {e:sorted(b for ee,b in cm if ee==e) for e in envs}

def observed_mapping(cm,envs):
    return {(e,b):b for e in envs for b in labelsets(cm,envs)[e]}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):
            mp[(e,old)]=str(new)
    return mp

def metrics(cm,envs,mapping):
    assigned={}
    presence=collections.defaultdict(set)
    for (e,old),v in cm.items():
        lab=mapping[(e,old)]
        assigned[(e,lab)]=np.asarray(v,float)
        presence[lab].add(e)

    obs=[];pred=[];pairs=[]
    for e0 in envs:
        present=sorted([b for b in presence if (e0,b) in assigned])
        theta={}
        for b in present:
            tr=[assigned[(e,b)] for e in sorted(presence[b]) if e!=e0 and (e,b) in assigned]
            if len(tr)>=2:
                theta[b]=np.mean(np.vstack(tr),axis=0)
        eligible=sorted(theta)

        for b in eligible:
            obs.append(assigned[(e0,b)])
            pred.append(theta[b])

        for ii in range(len(eligible)):
            for jj in range(ii+1,len(eligible)):
                i,j=eligible[ii],eligible[jj]
                dh=theta[i]-theta[j]
                do=assigned[(e0,i)]-assigned[(e0,j)]
                pairs.append((dh,do,e0,i,j))

    if len(obs)<3 or len(pairs)<3:
        return None

    O=np.vstack(obs);H=np.vstack(pred)
    sse=float(np.sum((O-H)**2)); zero=float(np.sum(O**2))
    if zero<=0:return None
    r2=float(1-sse/zero)
    rmse=float(np.sqrt(np.mean((O-H)**2)))
    mederr=float(np.median(np.linalg.norm(O-H,axis=1)))
    cos=[]
    for o,h in zip(O,H):
        no=float(np.linalg.norm(o));nh=float(np.linalg.norm(h))
        if no>0 and nh>0:
            cos.append(float(np.dot(o,h)/(no*nh)))

    axis={}
    for k,name in enumerate(["I","M"]):
        den=float(np.sum(O[:,k]**2))
        axis[name]=float(1-np.sum((O[:,k]-H[:,k])**2)/den) if den>0 else math.nan

    Dhat=np.vstack([a for a,b,*_ in pairs])
    Dobs=np.vstack([b for a,b,*_ in pairs])
    denv=float(np.sum(Dobs**2))
    pr2=float(1-np.sum((Dobs-Dhat)**2)/denv) if denv>0 else math.nan
    pcos=[]
    for a,b in zip(Dhat,Dobs):
        na=float(np.linalg.norm(a));nb=float(np.linalg.norm(b))
        if na>0 and nb>0:
            pcos.append(float(np.dot(a,b)/(na*nb)))
    mdh=np.linalg.norm(Dhat,axis=1);mdo=np.linalg.norm(Dobs,axis=1)
    if len(mdh)>=3 and np.std(mdh,ddof=1)>0 and np.std(mdo,ddof=1)>0:
        rmag=float(np.corrcoef(mdh,mdo)[0,1])
    else:rmag=math.nan

    return {
      "P1_R2_2D":r2,
      "P1_RMSE_per_coordinate":rmse,
      "P1_median_euclidean_error":mederr,
      "P1_median_cosine":float(np.median(cos)) if cos else None,
      "P1_mean_cosine":float(np.mean(cos)) if cos else None,
      "P1_n_target_centroids":int(len(O)),
      "P2_R2_I":axis["I"],
      "P2_R2_M":axis["M"],
      "P3_pair_vector_R2":pr2,
      "P3_median_cosine":float(np.median(pcos)) if pcos else None,
      "P3_positive_cosine_fraction":float(np.mean(np.asarray(pcos)>0)) if pcos else None,
      "P3_pair_separation_magnitude_r":rmag,
      "P3_n_pair_environment_points":int(len(pairs)),
    }

def null_metric(cm,envs,ls,seed,key):
    rng=np.random.default_rng(seed);vals=[]
    for _ in range(NPERM):
        q=metrics(cm,envs,perm_mapping(ls,rng))
        if q is None:continue
        v=q[key]
        if v is not None and math.isfinite(v):vals.append(float(v))
    return np.asarray(vals,float)

def calibrate(value,null):
    return {
      "valid_permutations":int(len(null)),
      "null_mean":float(np.mean(null)),
      "null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "p_one_sided":float((1+np.sum(null>=value))/(1+len(null))),
    }

def main():
    rows,envs=T.standardized_rows()
    cm=centroid_table(rows,envs);ls=labelsets(cm,envs)
    obs=metrics(cm,envs,observed_mapping(cm,envs))
    if obs is None:raise RuntimeError("observed support failed")

    n1=null_metric(cm,envs,ls,SEEDS["P1"],"P1_R2_2D")
    ni=null_metric(cm,envs,ls,SEEDS["P2I"],"P2_R2_I")
    nm=null_metric(cm,envs,ls,SEEDS["P2M"],"P2_R2_M")
    n3=null_metric(cm,envs,ls,SEEDS["P3"],"P3_pair_vector_R2")

    out={
      "contract":"TWO_PARAMETER_POLICY_LAW_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "observed":obs,
      "P1_calibration":calibrate(obs["P1_R2_2D"],n1),
      "P2_I_calibration":calibrate(obs["P2_R2_I"],ni),
      "P2_M_calibration":calibrate(obs["P2_R2_M"],nm),
      "P3_calibration":calibrate(obs["P3_pair_vector_R2"],n3),
      "requested_permutations":NPERM,
      "seeds":SEEDS,
    }
    support=(len(n1)>=MIN_VALID and len(ni)>=MIN_VALID and len(nm)>=MIN_VALID and len(n3)>=MIN_VALID
             and obs["P1_R2_2D"]>0 and out["P1_calibration"]["p_one_sided"]<=.05
             and obs["P2_R2_I"]>0 and obs["P2_R2_M"]>0
             and obs["P3_pair_vector_R2"]>0 and out["P3_calibration"]["p_one_sided"]<=.05)
    out["diagnostic_verdict"]="SUPPORTED_TRANSPARENT_TWO_PARAMETER_LAW" if support else "PARTIAL_OR_UNSUPPORTED_TRANSPARENT_TWO_PARAMETER_LAW"
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
