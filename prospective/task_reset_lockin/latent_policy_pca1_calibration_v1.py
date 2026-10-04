#!/usr/bin/env python3
"""Focused 1-D PCA null calibration from LATENT_POLICY_DIMENSIONALITY_CONTRACT_V1."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)

NPERM=9999
SEED=202610042282

def main():
    rows,envs=L.standardized_rows()
    folds=L.project_pca_folds(rows,envs)
    coords={e:folds[e]["scores"] for e in envs}
    obsmap=L.observed_mapping(rows,envs)
    obs,bm=L.k_stat(rows,envs,obsmap,coords,1)
    labelsets=L.env_label_sets(rows,envs)
    rng=np.random.default_rng(SEED)
    null=[]
    for _ in range(NPERM):
        mp=L.perm_mapping(labelsets,rng)
        s,_=L.k_stat(rows,envs,mp,coords,1)
        if s is not None:null.append(s)
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in bm.values()); frac=pos/len(bm)
    cum=[float(np.sum(folds[e]["ratio"][:1])) for e in envs]
    out={
      "parent_contract":"LATENT_POLICY_DIMENSIONALITY_CONTRACT_V1.md",
      "diagnostic":"D1_unsupervised_PCA_d1",
      "K":float(obs),"bat_means":bm,"positive_bats":pos,
      "n_bats":len(bm),"positive_fraction":frac,
      "requested_permutations":NPERM,"valid_permutations":len(a),"seed":SEED,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p,
      "median_training_variance_explained_PC1":float(np.median(cum)),
      "min_training_variance_explained_PC1":float(np.min(cum)),
      "max_training_variance_explained_PC1":float(np.max(cum)),
      "sufficient":bool(obs>0 and p<=.05 and frac>=.70 and len(a)>=9500),
      "pc1_squared_loadings_by_fold":{
        str(e):(folds[e]["basis"][0]**2).tolist() for e in envs
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
