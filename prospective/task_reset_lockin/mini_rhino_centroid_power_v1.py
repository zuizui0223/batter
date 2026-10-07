#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, itertools, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("M",HERE/"cross_species_policy_axis_v1.py")
M=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(M)
P=M.P

MINI_MIN,MINI_MAX=M.MINI_MIN,M.MINI_MAX
RHINO_MIN,RHINO_MAX=P.RHINO_MIN,P.RHINO_MAX
NMINI_PERM=9999
NMAP_PERM=1999
MIN_VALID_MINI=9500
MIN_VALID_MAP=1900

def species_rows(raw):
    ft=[r for r in raw if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    X=np.vstack([r["features"] for r in ft]).astype(float)
    env=np.asarray([r["env"] for r in ft])
    resid=np.empty_like(X)
    for e in envs:
        ix=np.where(env==e)[0]
        resid[ix]=X[ix]-X[ix].mean(axis=0,keepdims=True)
    sd=resid.std(axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0):
        raise RuntimeError(f"bad pooled residual SD {sd}")
    Z=resid/sd
    rows=[]
    for i,r in enumerate(ft):
        q=dict(r); q["z8"]=Z[i]; rows.append(q)
    return rows,envs

def cell_centroids(rows):
    out={}
    by=collections.defaultdict(list)
    for r in rows:
        by[(int(r["env"]),str(r["bat"]))].append(np.asarray(r["z8"],float))
    for k,v in by.items():
        out[k]=np.mean(np.vstack(v),axis=0)
    return out

def mini_template(mcent):
    cells=sorted(mcent)
    bats=sorted(set(b for e,b in cells))
    envs=sorted(set(e for e,b in cells))
    if len(cells)!=12 or len(bats)!=4 or len(envs)!=7:
        raise RuntimeError(f"Mini centroid drift cells={len(cells)} bats={bats} envs={envs}")
    return cells,bats,envs

def feasible_maps(mcells,rcent,mbats,menvs):
    rbats=sorted(set(b for e,b in rcent))
    renvs=sorted(set(e for e,b in rcent))
    rcells=set(rcent)
    feasible=[]
    for chosen in itertools.permutations(rbats,4):
        bmap=dict(zip(mbats,chosen))
        for eperm in itertools.permutations(renvs,7):
            emap=dict(zip(menvs,eperm))
            if all((emap[e],bmap[b]) in rcells for e,b in mcells):
                feasible.append((tuple(chosen),tuple(eperm)))
    feasible=sorted(feasible)
    if len(feasible)!=4212:
        raise RuntimeError(f"feasible mapping drift {len(feasible)}")
    return feasible

def rows_from_centroids(cent,cells):
    return [{"env":int(e),"bat":str(b),"z8":np.asarray(cent[(e,b)],float)} for e,b in cells]

def mapped_rhino_rows(rcent,mcells,mbats,menvs,mapping):
    chosen,eperm=mapping
    bmap=dict(zip(mbats,chosen)); emap=dict(zip(menvs,eperm))
    rows=[]
    for e,b in mcells:
        rows.append({"env":int(e),"bat":str(b),"z8":np.asarray(rcent[(emap[e],bmap[b])],float)})
    return rows

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def identity_mapping(ls):
    return {(e,b):b for e,labs in ls.items() for b in labs}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm): mp[(e,old)]=str(new)
    return mp

def pca_scores(rows,envs):
    folds={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        X=np.vstack([r["z8"] for r in train])
        mu=X.mean(axis=0)
        Xc=X-mu
        _,_,Vt=np.linalg.svd(Xc,full_matrices=False)
        v=Vt[0]
        folds[e0]=np.asarray([(np.asarray(r["z8"])-mu)@v for r in rows],float)
    return folds

def k_stat(rows,envs,scores,mapping):
    perbat=collections.defaultdict(list)
    all_labels=sorted(set(mapping.values()))
    for e0 in envs:
        sc=scores[e0]
        cent={}
        for b in all_labels:
            per=[]
            for e in envs:
                if e==e0: continue
                ix=[i for i,r in enumerate(rows) if r["env"]==e and mapping.get((e,r["bat"]))==b]
                if ix: per.append(float(np.mean(sc[ix])))
            if len(per)>=2: cent[b]=float(np.mean(per))
        if len(cent)<3: continue
        for i,r in enumerate(rows):
            if r["env"]!=e0: continue
            b=mapping.get((e0,r["bat"]))
            if b not in cent: continue
            donors=[bb for bb in cent if bb!=b]
            if len(donors)<2: continue
            x=float(sc[i])
            ds=abs(x-cent[b])
            do=float(np.mean([abs(x-cent[bb]) for bb in donors]))
            perbat[b].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3: return None,bm
    return float(np.mean(list(bm.values()))),bm

def calibrate(rows,seed,nperm,minvalid):
    envs=sorted(set(r["env"] for r in rows))
    ls=labelsets(rows,envs)
    obsmap=identity_mapping(ls)
    scores=pca_scores(rows,envs)
    obs,bm=k_stat(rows,envs,scores,obsmap)
    if obs is None: return {"status":"STOP"}
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(nperm):
        q,_=k_stat(rows,envs,scores,perm_mapping(ls,rng))
        if q is not None:null.append(q)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a))) if len(a) else math.nan
    pos=sum(v>0 for v in bm.values())
    detected=bool(len(a)>=minvalid and obs>0 and p<=.05 and pos>=3)
    return {
        "K":float(obs),"bat_means":bm,"positive_bats":pos,"n_bats":len(bm),
        "valid_permutations":len(a),"requested_permutations":nperm,
        "p_one_sided":p,"null_mean":float(a.mean()) if len(a) else None,
        "null_q025":float(np.quantile(a,.025)) if len(a) else None,
        "null_q975":float(np.quantile(a,.975)) if len(a) else None,
        "detected":detected
    }

def observed_only(rows):
    envs=sorted(set(r["env"] for r in rows))
    ls=labelsets(rows,envs)
    scores=pca_scores(rows,envs)
    obs,bm=k_stat(rows,envs,scores,identity_mapping(ls))
    if obs is None:return None
    return {"K":float(obs),"positive_bats":sum(v>0 for v in bm.values()),"bat_means":bm}

def select_256(feasible):
    N=len(feasible); idx=[]; used=set()
    for j in range(256):
        k=int(math.floor(j*(N-1)/255))
        while k in used and k+1<N:k+=1
        if k in used:
            k=next(x for x in range(N) if x not in used)
        used.add(k); idx.append(k)
    return idx

def main():
    mraw=M.load_mini()
    rraw=P.load_rhino()
    if len(mraw)!=19 or len(rraw)!=45:
        raise RuntimeError(f"raw count drift Mini={len(mraw)} Rhino={len(rraw)}")
    mrows,_=species_rows(mraw)
    rrows,_=species_rows(rraw)
    mcent=cell_centroids(mrows); rcent=cell_centroids(rrows)
    mcells,mbats,menvs=mini_template(mcent)
    feasible=feasible_maps(mcells,rcent,mbats,menvs)

    mini_rows=rows_from_centroids(mcent,mcells)
    mini=calibrate(mini_rows,20261007951,NMINI_PERM,MIN_VALID_MINI)

    all_obs=[]
    for mp in feasible:
        q=observed_only(mapped_rhino_rows(rcent,mcells,mbats,menvs,mp))
        if q is None: raise RuntimeError("Rhino observed mapping support failed")
        all_obs.append(q["K"])
    A=np.asarray(all_obs,float)

    selected=select_256(feasible)
    cal=[]
    for rank,k in enumerate(selected):
        rr=mapped_rhino_rows(rcent,mcells,mbats,menvs,feasible[k])
        q=calibrate(rr,20261008000+rank,NMAP_PERM,MIN_VALID_MAP)
        q["mapping_index"]=int(k); q["rank"]=rank
        cal.append(q)
    det=sum(bool(q.get("detected")) for q in cal)
    frac=det/len(cal)
    if frac>=.80: category="ADEQUATE_FOR_RHINO_LIKE_SIGNAL"
    elif frac<.50: category="POWER_LIMITED"
    else: category="AMBIGUOUS"

    out={
        "status":"POST_PRIMARY_POWER_SUPPORT_DIAGNOSTIC",
        "contract":"MINI_RHINO_CENTROID_POWER_CONTRACT_V1.md",
        "mini":mini,
        "n_feasible_mappings":len(feasible),
        "rhino_all_mapping_K":{
            "median":float(np.median(A)),
            "q025":float(np.quantile(A,.025)),
            "q975":float(np.quantile(A,.975)),
            "min":float(np.min(A)),"max":float(np.max(A)),
            "fraction_gt_zero":float(np.mean(A>0)),
            "fraction_gt_mini_K":float(np.mean(A>float(mini["K"])))
        },
        "calibrated_mapping_count":len(cal),
        "rhino_detected_mappings":det,
        "rhino_detection_fraction":frac,
        "support_category":category,
        "calibrated_mappings":cal
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
