#!/usr/bin/env python3
"""Sequential leave-one-environment PCA-subspace ablation for Rhino movement policy."""
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
MIN_VALID=9500
KS=list(range(8))

def standardized_rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    rows=[]
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad SD env={e}")
        for r in rr:
            q=dict(r);q["z"]=(r["features"]-mu)/sd;rows.append(q)
    return rows,envs

def fold_bases(rows,envs):
    bases={}; cumvar={}
    load_sq=collections.defaultdict(list)
    for e0 in envs:
        M=np.vstack([r["z"] for r in rows if r["env"]!=e0])
        M=M-M.mean(axis=0,keepdims=True)
        _,s,vt=np.linalg.svd(M,full_matrices=False)
        bases[e0]=vt.T.copy()
        v=s*s
        ev=v/v.sum()
        cumvar[e0]=np.concatenate([[0.0],np.cumsum(ev)]).tolist()
        for pc in range(4):
            load_sq[pc+1].append(vt[pc]**2)
    loading_summary={}
    for pc,arrs in load_sq.items():
        A=np.vstack(arrs)
        loading_summary[str(pc)]={
          "median_squared_loading":np.median(A,axis=0).tolist(),
          "min_squared_loading":np.min(A,axis=0).tolist(),
          "max_squared_loading":np.max(A,axis=0).tolist(),
        }
    return bases,cumvar,loading_summary

def residualized_by_k(rows,envs,bases,k):
    out=[]
    for r in rows:
        # A target trajectory will use the basis from its own held-out environment
        e=r["env"];V=bases[e]
        z=r["z"]
        if k==0:
            rr=z.copy()
        else:
            Q=V[:,:k]
            rr=z-Q@(Q.T@z)
        q=dict(r);q["r"]=rr;out.append(q)
    return out

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def observed_map(rows,envs):
    return {(e,b):b for e,labs in labelsets(rows,envs).items() for b in labs}

def perm_map(ls,rng):
    mp={}
    for e,labs in ls.items():
        p=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,p):mp[(e,old)]=str(new)
    return mp

def stat(rows,envs,mapping):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        # NOTE: vectors in rows were residualized by the basis of their own environment.
        # For the held-out architecture, training centroids must be represented in the
        # target fold basis too. Therefore this function expects rows carrying z and
        # the caller supplies target-fold residualization separately via fold_stat.
        raise RuntimeError("stat() should not be called")

def fold_stat(rows,envs,bases,k,mapping):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        V=bases[e0]
        def R(z):
            if k==0:return z
            Q=V[:,:k]
            return z-Q@(Q.T@z)

        # training centroids in target-fold residual coordinate system
        train_groups=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in rows:
            if r["env"]==e0:continue
            lab=mapping[(r["env"],r["bat"])]
            train_groups[lab][r["env"]].append(R(r["z"]))
        train={}
        for b,d in train_groups.items():
            envcent=[]
            for e in sorted(d):
                envcent.append(np.mean(np.vstack(d[e]),axis=0))
            if len(envcent)>=2:
                train[b]=np.mean(np.vstack(envcent),axis=0)
        if len(train)<3:continue

        for r in [x for x in rows if x["env"]==e0]:
            lab=mapping[(e0,r["bat"])]
            if lab not in train:continue
            donors=[b for b in train if b!=lab]
            if len(donors)<2:continue
            z=R(r["z"])
            ds=float(np.linalg.norm(z-train[lab]))
            do=float(np.mean([np.linalg.norm(z-train[b]) for b in donors]))
            perbat[lab].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None
    return float(np.mean(list(bm.values()))),bm

def run_k(rows,envs,bases,ls,k):
    om=observed_map(rows,envs)
    obs=fold_stat(rows,envs,bases,k,om)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    kval,bm=obs
    rng=np.random.default_rng(202610050930+k)
    null=[]
    for _ in range(NPERM):
        mp=perm_map(ls,rng)
        q=fold_stat(rows,envs,bases,k,mp)
        if q is not None:null.append(q[0])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=kval))/(1+len(a)))
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    supported=(kval>0 and p<=.05 and frac>=.70 and len(a)>=MIN_VALID)
    return {
      "status":"DONE","K":float(kval),"bat_means":bm,
      "positive_bats":pos,"n_bats":len(bm),"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":len(a),
      "seed":202610050930+k,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_RESIDUAL_IDENTITY" if supported else "UNSUPPORTED_RESIDUAL_IDENTITY"
    }

def main():
    rows,envs=standardized_rows()
    bases,cumvar,loads=fold_bases(rows,envs)
    ls=labelsets(rows,envs)
    results={}
    for k in KS:
        results[str(k)]=run_k(rows,envs,bases,ls,k)
    K0=results["0"].get("K")
    for k in KS:
        if K0 and "K" in results[str(k)]:
            results[str(k)]["K_over_K0"]=float(results[str(k)]["K"]/K0)
        cv=[cumvar[e][k] for e in envs]
        results[str(k)]["median_cumulative_variance_removed"]=float(np.median(cv))
        results[str(k)]["min_cumulative_variance_removed"]=float(np.min(cv))
        results[str(k)]["max_cumulative_variance_removed"]=float(np.max(cv))
    first=None
    for k in range(1,8):
        if results[str(k)].get("diagnostic_verdict")!="SUPPORTED_RESIDUAL_IDENTITY":
            first=k;break
    out={
      "contract":"SEQUENTIAL_POLICY_SUBSPACE_ABLATION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_DIMENSIONALITY_FALSIFICATION_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "feature_names":P.FEATURES,
      "dimensions_removed":results,
      "first_unsupported_complement_k":first,
      "pc1_to_pc4_loading_summary":loads,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
