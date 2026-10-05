#!/usr/bin/env python3
"""Held-out rank-one/rank-two reconstruction of Rhino movement policy."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
SEED1=202610050911
SEED2=202610050912
MIN_VALID=9500

def standardized_rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    rows=[]
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0); sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad SD env={e}")
        for r in rr:
            q=dict(r); q["z"]=(r["features"]-mu)/sd; rows.append(q)
    return rows,envs

def centroids(rows,envs):
    out={}
    for e in envs:
        bats=sorted(set(r["bat"] for r in rows if r["env"]==e))
        for b in bats:
            z=np.vstack([r["z"] for r in rows if r["env"]==e and r["bat"]==b])
            out[(e,b)]=z.mean(axis=0)
    return out

def fold_basis(rows,envs,d):
    bases={}
    for e0 in envs:
        M=np.vstack([r["z"] for r in rows if r["env"]!=e0])
        # pooled mean is approximately zero; center exactly as ordinary PCA.
        M=M-M.mean(axis=0,keepdims=True)
        _,_,vt=np.linalg.svd(M,full_matrices=False)
        bases[e0]=vt[:d].T.copy()
    return bases

def labelsets(cm,envs):
    return {e:sorted(b for ee,b in cm if ee==e) for e in envs}

def observed_map(cm,envs):
    return {(e,b):b for e in envs for b in labelsets(cm,envs)[e]}

def perm_map(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):mp[(e,old)]=str(new)
    return mp

def reconstruction(cm,envs,bases,mapping,d):
    # assigned centroid table after label permutation
    assigned={}
    presence=collections.defaultdict(set)
    for (e,old),v in cm.items():
        lab=mapping[(e,old)]
        assigned[(e,lab)]=v
        presence[lab].add(e)

    sq_model=[]; sq_zero=[]; cos=[]; detail=[]
    for e0 in envs:
        B=bases[e0]
        present=sorted([b for b in presence if (e0,b) in assigned])
        for b in present:
            train_envs=[e for e in sorted(presence[b]) if e!=e0 and (e,b) in assigned]
            if len(train_envs)<2:continue
            coords=[]
            for e in train_envs:
                coords.append(B.T@assigned[(e,b)])
            theta=np.mean(np.vstack(coords),axis=0)
            pred=B@theta
            obs=assigned[(e0,b)]
            em=float(np.sum((obs-pred)**2))
            ez=float(np.sum(obs**2))
            sq_model.append(em);sq_zero.append(ez)
            no=float(np.linalg.norm(obs));npred=float(np.linalg.norm(pred))
            cc=None
            if no>0 and npred>0:
                cc=float(np.dot(obs,pred)/(no*npred));cos.append(cc)
            detail.append({"environment":e0,"bat":b,"training_envs":train_envs,
                           "obs_norm":no,"pred_norm":npred,"sq_error":em,
                           "sq_zero":ez,"cosine":cc})
    if len(sq_model)<3 or sum(sq_zero)<=0:return None
    sse=float(sum(sq_model));zero=float(sum(sq_zero))
    return {
      "R2":float(1-sse/zero),
      "SSE_model":sse,"SSE_zero":zero,
      "RMSE_per_feature":float(math.sqrt(sse/(len(sq_model)*8))),
      "median_cosine":float(np.median(cos)) if cos else None,
      "mean_cosine":float(np.mean(cos)) if cos else None,
      "n_target_centroids":len(sq_model),
      "detail":detail,
    }

def null_for_d(cm,envs,bases,ls,d,seed):
    rng=np.random.default_rng(seed);vals=[]
    for _ in range(NPERM):
        mp=perm_map(ls,rng)
        q=reconstruction(cm,envs,bases,mp,d)
        if q is not None and math.isfinite(q["R2"]):vals.append(q["R2"])
    return np.asarray(vals,float)

def main():
    rows,envs=standardized_rows()
    cm=centroids(rows,envs);ls=labelsets(cm,envs);obsmap=observed_map(cm,envs)
    b1=fold_basis(rows,envs,1);b2=fold_basis(rows,envs,2)
    o1=reconstruction(cm,envs,b1,obsmap,1)
    o2=reconstruction(cm,envs,b2,obsmap,2)
    if o1 is None or o2 is None:raise RuntimeError("observed reconstruction failed")
    n1=null_for_d(cm,envs,b1,ls,1,SEED1)
    n2=null_for_d(cm,envs,b2,ls,2,SEED2)

    def cal(obs,null):
        return {
          **obs,
          "valid_permutations":int(len(null)),
          "null_mean":float(np.mean(null)),
          "null_q025":float(np.quantile(null,.025)),
          "null_q975":float(np.quantile(null,.975)),
          "p_one_sided":float((1+np.sum(null>=obs["R2"]))/(1+len(null))),
        }

    r1=cal(o1,n1);r2=cal(o2,n2)
    status="DONE" if len(n1)>=MIN_VALID and len(n2)>=MIN_VALID else "STOP_RANDOMIZATION_SUPPORT"
    out={
      "contract":"RANK_ONE_POLICY_RECONSTRUCTION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_MATHEMATICAL_STRUCTURE_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "rank1":r1,"rank2":r2,
      "DeltaR2_2minus1":float(o2["R2"]-o1["R2"]),
      "requested_permutations":NPERM,
      "seeds":{"rank1":SEED1,"rank2":SEED2},
      "diagnostic_status":status,
    }
    if status=="DONE":
        out["diagnostic_verdict"]=(
          "SUPPORTED_RANK_ONE_RECONSTRUCTION"
          if r1["R2"]>0 and r1["p_one_sided"]<=.05
          else "UNSUPPORTED_RANK_ONE_RECONSTRUCTION"
        )
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
