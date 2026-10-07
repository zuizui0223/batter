#!/usr/bin/env python3
from __future__ import annotations
import collections, importlib.util, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(L)

spec=importlib.util.spec_from_file_location("M",HERE/"cross_species_policy_axis_v1.py")
M=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(M)

BATS=["A","B","C","D","E"]
N_VALID_PER_SUBSET=1000
SEED=20261007941
MAX_PROPOSALS=500000
MINI_PCA1=-0.16875692138998233

def mini_structure():
    rows=M.mini_standardized()
    envs=sorted(set(r["env"] for r in rows))
    env_n={e:sum(r["env"]==e for r in rows) for e in envs}
    env_b={e:len(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}
    return {"total":len(rows),"env_counts":env_n,"env_bats":env_b,"envs":envs}

def rhino_raw():
    traj=L.P.load_rhino()
    rows=[]
    for r in traj:
        if r["feature_valid"]:
            rows.append({"env":int(r["env"]),"bat":str(r["bat"]),
                         "features":np.asarray(r["features"],float),"name":r["name"]})
    if len(rows)!=45: raise RuntimeError(f"Rhino row drift {len(rows)}")
    return rows

def standardize_sample(rows):
    envs=sorted(set(r["env"] for r in rows))
    X=np.vstack([r["features"] for r in rows])
    resid=np.empty_like(X)
    for e in envs:
        ix=[i for i,r in enumerate(rows) if r["env"]==e]
        mu=X[ix].mean(axis=0)
        resid[ix]=X[ix]-mu
    sd=resid.std(axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0): return None
    Z=resid/sd
    out=[]
    for i,r in enumerate(rows):
        q=dict(r); q["z8"]=Z[i]; q["fi"]=float(np.mean(Z[i,:4])); out.append(q)
    return out

def eligible_four(rows):
    envs=sorted(set(r["env"] for r in rows))
    bats=sorted(set(r["bat"] for r in rows))
    if len(bats)!=4 or len(envs)!=7: return False
    for b in bats:
        if len(set(r["env"] for r in rows if r["bat"]==b))<3: return False
    return True

def sample_one(source,keep,struct,rng):
    chosen=[]
    for e in struct["envs"]:
        pool=[r for r in source if r["bat"] in keep and r["env"]==e]
        need=int(struct["env_counts"][e])
        minb=int(struct["env_bats"][e])
        if len(pool)<need: return None
        ok=None
        for _ in range(100):
            ix=rng.choice(len(pool),size=need,replace=False)
            cand=[pool[int(i)] for i in ix]
            if len(set(r["bat"] for r in cand))>=minb:
                ok=cand;break
        if ok is None:return None
        chosen.extend(ok)
    if len(chosen)!=struct["total"]: return None
    if not eligible_four(chosen): return None
    return standardize_sample(chosen)

def mapping_identity(rows):
    return {(r["env"],r["bat"]):r["bat"] for r in rows}

def pca_scores(rows):
    envs=sorted(set(r["env"] for r in rows))
    folds={}
    for e0 in envs:
        train=[r for r in rows if r["env"]!=e0]
        X=np.vstack([r["z8"] for r in train])
        mu=X.mean(axis=0); Xc=X-mu
        _,_,Vt=np.linalg.svd(Xc,full_matrices=False)
        v=Vt[0]
        folds[e0]=np.asarray([(np.asarray(r["z8"])-mu)@v for r in rows],float)
    return folds

def fi_scores(rows):
    x=np.asarray([r["fi"] for r in rows],float)
    return {e:x.copy() for e in sorted(set(r["env"] for r in rows))}

def stat(rows,folds):
    envs=sorted(set(r["env"] for r in rows))
    bats=sorted(set(r["bat"] for r in rows))
    per=collections.defaultdict(list)
    for e0 in envs:
        scores=folds[e0]
        cent={}
        for b in bats:
            perenv=[]
            for e in envs:
                if e==e0:continue
                ix=[i for i,r in enumerate(rows) if r["env"]==e and r["bat"]==b]
                if ix: perenv.append(float(np.mean(scores[ix])))
            if len(perenv)>=2:cent[b]=float(np.mean(perenv))
        if len(cent)<3:continue
        for i,r in enumerate(rows):
            if r["env"]!=e0 or r["bat"] not in cent:continue
            donors=[b for b in cent if b!=r["bat"]]
            if len(donors)<2:continue
            z=float(scores[i])
            ds=abs(z-cent[r["bat"]])
            do=float(np.mean([abs(z-cent[b]) for b in donors]))
            per[r["bat"]].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in per.items() if v}
    if len(bm)<4:return None,{}
    return float(np.mean(list(bm.values()))),bm

def summary(vals,mini_ref=None):
    K=np.asarray([x["K"] for x in vals],float)
    posfrac=np.asarray([x["positive_bats"]/4 for x in vals],float)
    out={
      "n":len(vals),
      "median_K":float(np.median(K)),
      "q05_K":float(np.quantile(K,.05)),
      "q95_K":float(np.quantile(K,.95)),
      "fraction_K_positive":float(np.mean(K>0)),
      "fraction_positive_bats_ge_3of4":float(np.mean(posfrac>=.75)),
      "fraction_both_directional":float(np.mean((K>0)&(posfrac>=.75)))
    }
    if mini_ref is not None:
      out["mini_reference_K"]=mini_ref
      out["mini_percentile_in_rhino_exactN"]=float(np.mean(K<=mini_ref))
    return out

def main():
    struct=mini_structure()
    if struct["total"]!=19:raise RuntimeError(f"Mini total drift {struct}")
    source=rhino_raw()
    rng=np.random.default_rng(SEED)
    byomit={o:{"PCA1":[],"FlightIntensity":[]} for o in BATS}
    proposals=0
    for omit in BATS:
        keep=[b for b in BATS if b!=omit]
        while len(byomit[omit]["PCA1"])<N_VALID_PER_SUBSET:
            proposals+=1
            if proposals>MAX_PROPOSALS:raise RuntimeError("proposal budget exhausted")
            rows=sample_one(source,keep,struct,rng)
            if rows is None:continue
            kp,bp=stat(rows,pca_scores(rows))
            kf,bf=stat(rows,fi_scores(rows))
            if kp is None or kf is None:continue
            byomit[omit]["PCA1"].append({"K":kp,"positive_bats":sum(v>0 for v in bp.values())})
            byomit[omit]["FlightIntensity"].append({"K":kf,"positive_bats":sum(v>0 for v in bf.values())})
    subset={}
    pooled={"PCA1":[],"FlightIntensity":[]}
    for omit in BATS:
        subset[omit]={
          "PCA1":summary(byomit[omit]["PCA1"],MINI_PCA1),
          "FlightIntensity":summary(byomit[omit]["FlightIntensity"])
        }
        pooled["PCA1"].extend(byomit[omit]["PCA1"])
        pooled["FlightIntensity"].extend(byomit[omit]["FlightIntensity"])
    ps=summary(pooled["PCA1"],MINI_PCA1)
    fs=summary(pooled["FlightIntensity"])
    p_robust=bool(ps["fraction_K_positive"]>=.90 and
                  ps["fraction_positive_bats_ge_3of4"]>=.80 and
                  ps["mini_percentile_in_rhino_exactN"]<.05)
    f_robust=bool(fs["fraction_K_positive"]>=.90 and
                  fs["fraction_positive_bats_ge_3of4"]>=.80)
    out={
      "status":"POST_PRIMARY_CROSS_SPECIES_SUPPORT_STRESS_DIAGNOSTIC",
      "contract":"RHINO_MINI_EXACT_N19_RESAMPLING_CONTRACT_V1.md",
      "mini_structure":struct,
      "valid_per_subset":N_VALID_PER_SUBSET,
      "total_valid":5*N_VALID_PER_SUBSET,
      "proposals_used":proposals,
      "seed":SEED,
      "subsets":subset,
      "pooled":{"PCA1":ps,"FlightIntensity":fs},
      "verdict":{
        "PCA1_robust_to_mini_totalN":p_robust,
        "FlightIntensity_robust_to_mini_totalN":f_robust
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
