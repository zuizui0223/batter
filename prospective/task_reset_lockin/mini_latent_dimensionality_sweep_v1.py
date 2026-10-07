#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("M",HERE/"cross_species_policy_axis_v1.py")
M=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(M)

D1=list(range(1,9))
D2=[1,2,3]
B=9999
SEED=20261007801

def prepare():
    rows=M.mini_standardized()
    envs=sorted(set(r["env"] for r in rows))
    return rows,envs

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def idmap(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def permap(ls,rng):
    out={}
    for e,labs in ls.items():
        q=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,q): out[(e,old)]=str(new)
    return out

def assigned(r,mp):
    return mp[(r["env"],r["bat"])]

def pca_folds(rows,envs):
    out={}
    for e0 in envs:
        idx=[i for i,r in enumerate(rows) if r["env"]!=e0]
        X=np.vstack([rows[i]["z8"] for i in idx])
        mu=X.mean(axis=0); Xc=X-mu
        _,s,Vt=np.linalg.svd(Xc,full_matrices=False)
        coords=np.vstack([(np.asarray(r["z8"])-mu)@Vt.T for r in rows])
        out[e0]={"coords":coords,"Vt":Vt,"ratio":(s*s)/np.sum(s*s)}
    return out

def kstat(rows,envs,coords_by_fold,mp,d):
    per=collections.defaultdict(list)
    for e0 in envs:
        C=coords_by_fold[e0]
        labs=sorted(set(assigned(r,mp) for r in rows))
        cent={}
        for b in labs:
            ev=[]
            for e in envs:
                if e==e0: continue
                ix=[i for i,r in enumerate(rows) if r["env"]==e and assigned(r,mp)==b]
                if ix: ev.append(np.mean(C[ix,:d],axis=0))
            if len(ev)>=2: cent[b]=np.mean(np.vstack(ev),axis=0)
        if len(cent)<3: continue
        for i,r in enumerate(rows):
            if r["env"]!=e0: continue
            b=assigned(r,mp)
            if b not in cent: continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2: continue
            z=C[i,:d]
            ds=float(np.linalg.norm(z-cent[b]))
            do=float(np.mean([np.linalg.norm(z-cent[bb]) for bb in donors]))
            per[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in per.items() if v}
    if len(bm)<3: return None,bm
    return float(np.mean(list(bm.values()))),bm

def identity_folds(rows,envs,mp):
    folds={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        labels=sorted(set(assigned(r,mp) for r in train))
        cent=[]
        used=[]
        for b in labels:
            ev=[]
            for e in envs:
                if e==e0: continue
                vals=[r["z8"] for r in train if r["env"]==e and assigned(r,mp)==b]
                if vals: ev.append(np.mean(np.vstack(vals),axis=0))
            if len(ev)>=2:
                cent.append(np.mean(np.vstack(ev),axis=0)); used.append(b)
        if len(used)<3: return None
        X=np.vstack(cent); grand=X.mean(axis=0)
        _,_,Vt=np.linalg.svd(X-grand,full_matrices=False)
        folds[e0]=np.vstack([(np.asarray(r["z8"])-grand)@Vt.T for r in rows])
    return folds

def observed(rows,envs):
    ls=labelsets(rows,envs); mp=idmap(ls)
    pf=pca_folds(rows,envs)
    pca={}
    coords={e:pf[e]["coords"] for e in envs}
    for d in D1:
        k,bm=kstat(rows,envs,coords,mp,d)
        pca[d]=(k,bm)
    idf=identity_folds(rows,envs,mp)
    ident={}
    for d in D2:
        k,bm=kstat(rows,envs,idf,mp,d)
        ident[d]=(k,bm)
    return pf,pca,ident

def main():
    rows,envs=prepare(); ls=labelsets(rows,envs)
    pf,pca_obs,id_obs=observed(rows,envs)
    coords={e:pf[e]["coords"] for e in envs}
    rng=np.random.default_rng(SEED)
    max_pca=np.empty(B,float); max_id=np.empty(B,float)
    valid_pca=np.ones((B,len(D1)),bool); valid_id=np.ones((B,len(D2)),bool)
    raw_pca=np.full((B,len(D1)),np.nan); raw_id=np.full((B,len(D2)),np.nan)

    for q in range(B):
        mp=permap(ls,rng)
        ks=[]
        for j,d in enumerate(D1):
            k,_=kstat(rows,envs,coords,mp,d)
            if k is None: valid_pca[q,j]=False
            else: raw_pca[q,j]=k; ks.append(k)
        max_pca[q]=max(ks) if ks else np.nan

        idf=identity_folds(rows,envs,mp)
        ks=[]
        if idf is not None:
            for j,d in enumerate(D2):
                k,_=kstat(rows,envs,idf,mp,d)
                if k is None: valid_id[q,j]=False
                else: raw_id[q,j]=k; ks.append(k)
        else:
            valid_id[q,:]=False
        max_id[q]=max(ks) if ks else np.nan

    out={"status":"POST_PRIMARY_EXPLORATORY_FAMILYWISE_SWEEP",
         "species":"Miniopterus fuliginosus","n_trajectories":len(rows),
         "permutations":B,"seed":SEED,
         "D1_PCA":{},"D2_identity_subspace":{}}

    mpca=max_pca[np.isfinite(max_pca)]
    mid=max_id[np.isfinite(max_id)]

    for d in D1:
        k,bm=pca_obs[d]
        pos=sum(v>0 for v in bm.values())
        padj=float((1+np.sum(mpca>=k))/(1+len(mpca)))
        out["D1_PCA"][str(d)]={
            "K":k,"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
            "adjusted_p_maxT":padj,
            "supported":bool(k>0 and padj<=.05 and pos>=3),
            "training_variance_median":float(np.median([np.sum(pf[e]["ratio"][:d]) for e in envs]))
        }

    for d in D2:
        k,bm=id_obs[d]
        pos=sum(v>0 for v in bm.values())
        padj=float((1+np.sum(mid>=k))/(1+len(mid)))
        out["D2_identity_subspace"][str(d)]={
            "K":k,"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
            "adjusted_p_maxT":padj,
            "supported":bool(k>0 and padj<=.05 and pos>=3)
        }

    out["minimal_supported_dimension_PCA"]=min([d for d in D1 if out["D1_PCA"][str(d)]["supported"]],default=None)
    out["minimal_supported_dimension_identity"]=min([d for d in D2 if out["D2_identity_subspace"][str(d)]["supported"]],default=None)
    out["interpretation_category"]=(
        "REGULARIZED_LOW_DIMENSIONAL_IDENTITY"
        if out["minimal_supported_dimension_PCA"] is not None or out["minimal_supported_dimension_identity"] is not None
        else "NO_STABLE_CROSS_CONFIGURATION_IDENTITY_AFTER_DIMENSION_SWEEP"
    )
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
