#!/usr/bin/env python3
"""Held-out pair-vector stability in scale-free route-geometry space."""
from __future__ import annotations
import importlib.util,json,math,collections
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
SEED=202610061801

def centroids():
    traj=G.P.load_rhino()
    rows,support=G.build_rows(traj)
    if rows is None:raise RuntimeError(support)
    cm={}
    for e in support["usable_envs"]:
        for b in sorted(set(r["bat"] for r in rows if r["env"]==e)):
            M=np.vstack([r["z"] for r in rows if r["env"]==e and r["bat"]==b])
            cm[(e,b)]=M.mean(0)
    return cm,support["usable_envs"]

def labelsets(cm,envs):
    return {e:sorted(b for ee,b in cm if ee==e) for e in envs}

def obsmap(cm,envs):
    return {(e,b):b for e in envs for b in labelsets(cm,envs)[e]}

def permmap(ls,rng):
    out={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):out[(e,old)]=str(new)
    return out

def metrics(cm,envs,mapping):
    assigned={}
    presence=collections.defaultdict(set)
    for (e,old),v in cm.items():
        lab=mapping[(e,old)]
        assigned[(e,lab)]=np.asarray(v,float)
        presence[lab].add(e)

    pred=[];obs=[];meta=[]
    for e0 in envs:
        present=sorted(b for b in presence if (e0,b) in assigned)
        for ii in range(len(present)):
            for jj in range(ii+1,len(present)):
                i,j=present[ii],present[jj]
                shared=[e for e in envs if e!=e0 and (e,i) in assigned and (e,j) in assigned]
                if len(shared)<2:continue
                dh=np.mean(np.vstack([assigned[(e,i)]-assigned[(e,j)] for e in shared]),axis=0)
                do=assigned[(e0,i)]-assigned[(e0,j)]
                pred.append(dh);obs.append(do);meta.append((e0,i,j,len(shared)))
    if len(pred)<3:return None
    H=np.vstack(pred);O=np.vstack(obs)
    den=float(np.sum(O*O))
    if den<=0:return None
    r2=float(1-np.sum((O-H)**2)/den)
    cos=[]
    for h,o in zip(H,O):
        nh=float(np.linalg.norm(h));no=float(np.linalg.norm(o))
        if nh>0 and no>0:cos.append(float(np.dot(h,o)/(nh*no)))
    mh=np.linalg.norm(H,axis=1);mo=np.linalg.norm(O,axis=1)
    pr=None;sr=None
    if len(mh)>=3 and np.std(mh,ddof=1)>0 and np.std(mo,ddof=1)>0:
        pr=float(np.corrcoef(mh,mo)[0,1])
        # rank correlation without scipy
        def ranks(a):
            order=np.argsort(a,kind="mergesort");r=np.empty(len(a),float);k=0
            while k<len(a):
                q=k+1
                while q<len(a) and a[order[q]]==a[order[k]]:q+=1
                rv=(k+q-1)/2+1
                r[order[k:q]]=rv;k=q
            return r
        rh,ro=ranks(mh),ranks(mo)
        if np.std(rh,ddof=1)>0 and np.std(ro,ddof=1)>0:
            sr=float(np.corrcoef(rh,ro)[0,1])
    byenv=collections.Counter(e for e,_,_,_ in meta)
    return {
      "pair_vector_R2":r2,
      "median_cosine":float(np.median(cos)) if cos else None,
      "positive_cosine_fraction":float(np.mean(np.asarray(cos)>0)) if cos else None,
      "magnitude_pearson_r":pr,
      "magnitude_spearman_rho":sr,
      "n_pair_environment_points":len(meta),
      "by_target_environment":{str(e):int(byenv[e]) for e in sorted(byenv)}
    }

def main():
    cm,envs=centroids();ls=labelsets(cm,envs)
    obs=metrics(cm,envs,obsmap(cm,envs))
    if obs is None:raise RuntimeError("observed support failed")
    rng=np.random.default_rng(SEED);null=[]
    for _ in range(NPERM):
        q=metrics(cm,envs,permmap(ls,rng))
        if q is not None and math.isfinite(q["pair_vector_R2"]):
            null.append(float(q["pair_vector_R2"]))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:raise RuntimeError(f"randomization support {len(a)}")
    p=float((1+np.sum(a>=obs["pair_vector_R2"]))/(1+len(a)))
    print(json.dumps({
      "contract":"HELDOUT_GEOMETRY_PAIR_VECTOR_STABILITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_REPRESENTATION_COMPARISON_DIAGNOSTIC",
      "observed":obs,
      "calibration":{
        "requested_permutations":NPERM,"valid_permutations":len(a),"seed":SEED,
        "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
        "null_q975":float(np.quantile(a,.975)),"p_one_sided":p
      },
      "diagnostic_verdict":"SUPPORTED_GEOMETRY_PAIR_VECTOR_STABILITY"
        if obs["pair_vector_R2"]>0 and p<=.05 else
        "UNSUPPORTED_GEOMETRY_PAIR_VECTOR_STABILITY"
    },indent=2))

if __name__=="__main__":main()
