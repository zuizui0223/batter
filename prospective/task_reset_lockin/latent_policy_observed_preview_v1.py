#!/usr/bin/env python3
"""Observed-only preview for the frozen latent-policy dimensionality diagnostic."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("L",HERE/"latent_policy_dimensionality_v1.py")
L=importlib.util.module_from_spec(spec);spec.loader.exec_module(L)

def main():
    rows,envs=L.standardized_rows()
    obsmap=L.observed_mapping(rows,envs)
    pf=L.project_pca_folds(rows,envs)
    pca={}
    for d in L.PCA_DIMS:
        k,bm=L.k_stat(rows,envs,obsmap,{e:pf[e]["scores"] for e in envs},d)
        pca[str(d)]={"K":k,"bat_means":bm,"positive_bats":sum(v>0 for v in bm.values())}
    folds,loads=L.identity_coord_folds(rows,envs,obsmap)
    ident={}
    for d in L.ID_DIMS:
        k,bm=L.k_stat(rows,envs,obsmap,folds,d)
        ident[str(d)]={"K":k,"bat_means":bm,"positive_bats":sum(v>0 for v in bm.values())}
    out={"status":"OBSERVED_ONLY_PREVIEW_NO_NULL","PCA":pca,"identity_subspace":ident}
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
