#!/usr/bin/env python3
"""Fast, algebraically equivalent 1-D PCA calibration.

Same contract/seed/statistic as latent_policy_pca1_calibration_v1.py.
Precomputes scalar bat×environment cluster means instead of rescanning rows.
"""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)

NPERM=9999
SEED=202610042282

def prepare():
    rows,envs=L.standardized_rows()
    folds=L.project_pca_folds(rows,envs)
    # For every target fold, precompute scalar PC1 coordinates and original clusters.
    folddata={}
    for e0 in envs:
        score=np.asarray([float(x[0]) for x in folds[e0]["scores"]])
        clusters={}
        for e in envs:
            labs=sorted(set(r["bat"] for r in rows if r["env"]==e))
            for b in labs:
                idx=[i for i,r in enumerate(rows) if r["env"]==e and r["bat"]==b]
                clusters[(e,b)]={
                    "mean":float(np.mean(score[idx])),
                    "target_values":score[idx].tolist(),
                }
        folddata[e0]={"score":score,"clusters":clusters}
    labelsets=L.env_label_sets(rows,envs)
    return rows,envs,folds,folddata,labelsets

def stat(rows,envs,folddata,mapping):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        d=folddata[e0]
        # assigned centroid from other environments, equal-environment weighting
        assigned_env=collections.defaultdict(list)
        for e in envs:
            if e==e0:continue
            for old in sorted(set(r["bat"] for r in rows if r["env"]==e)):
                new=mapping[(e,old)]
                assigned_env[new].append(d["clusters"][(e,old)]["mean"])
        cent={b:float(np.mean(v)) for b,v in assigned_env.items() if len(v)>=2}
        if len(cent)<3:return None,{}
        # targets in e0, preserve complete cluster reassignment
        for old in sorted(set(r["bat"] for r in rows if r["env"]==e0)):
            new=mapping[(e0,old)]
            if new not in cent:continue
            donors=[b for b in cent if b!=new]
            if len(donors)<2:continue
            for z in d["clusters"][(e0,old)]["target_values"]:
                ds=abs(z-cent[new])
                do=float(np.mean([abs(z-cent[b]) for b in donors]))
                perbat[new].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,envs,folds,folddata,labelsets=prepare()
    obsmap=L.observed_mapping(rows,envs)
    obs,bm=stat(rows,envs,folddata,obsmap)
    rng=np.random.default_rng(SEED)
    null=np.empty(NPERM,float)
    for p in range(NPERM):
        mp=L.perm_mapping(labelsets,rng)
        s,_=stat(rows,envs,folddata,mp)
        if s is None:raise RuntimeError("unexpected invalid permutation")
        null[p]=s
    pval=float((1+np.sum(null>=obs))/(NPERM+1))
    pos=sum(v>0 for v in bm.values());frac=pos/len(bm)
    cum=[float(folds[e]["ratio"][0]) for e in envs]
    sq=np.vstack([folds[e]["basis"][0]**2 for e in envs])
    out={
      "parent_contract":"LATENT_POLICY_DIMENSIONALITY_CONTRACT_V1.md",
      "implementation":"FAST_EQUIVALENT_D1_PCA1",
      "K":obs,"bat_means":bm,"positive_bats":pos,"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":NPERM,"seed":SEED,
      "null_mean":float(null.mean()),"null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),"p_one_sided":pval,
      "median_training_variance_explained_PC1":float(np.median(cum)),
      "range_training_variance_explained_PC1":[float(np.min(cum)),float(np.max(cum))],
      "median_squared_loadings_PC1":np.median(sq,axis=0).tolist(),
      "sufficient":bool(obs>0 and pval<=.05 and frac>=.70),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
