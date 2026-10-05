#!/usr/bin/env python3
"""Foldwise signed PC2 stability for Rhino movement policy."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

FI=np.array([.5,.5,.5,.5,0,0,0,0],float)

def standardized_rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    rows=[]
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError(e)
        for r in rr:
            q=dict(r);q["z"]=(r["features"]-mu)/sd;rows.append(q)
    return rows,envs

def main():
    rows,envs=standardized_rows()
    load={}
    for e0 in envs:
        M=np.vstack([r["z"] for r in rows if r["env"]!=e0])
        M=M-M.mean(axis=0,keepdims=True)
        _,_,vt=np.linalg.svd(M,full_matrices=False)
        v=vt[1].astype(float)
        # Orient by median absolute horizontal turn-rate loading (feature 5, index 4).
        if v[4]<0:v=-v
        load[e0]=v

    pairs=[]
    for i,e1 in enumerate(envs):
        for e2 in envs[i+1:]:
            c=float(np.dot(load[e1],load[e2])/(np.linalg.norm(load[e1])*np.linalg.norm(load[e2])))
            pairs.append({"fold1":e1,"fold2":e2,"cosine":c})
    cs=np.asarray([x["cosine"] for x in pairs],float)

    V=np.vstack([load[e] for e in envs])
    summary={}
    for k,n in enumerate(P.FEATURES):
        summary[n]={
          "median_loading":float(np.median(V[:,k])),
          "min_loading":float(np.min(V[:,k])),
          "max_loading":float(np.max(V[:,k])),
          "sd_loading":float(np.std(V[:,k],ddof=1)),
          "median_squared_loading":float(np.median(V[:,k]**2)),
        }

    fi=np.asarray([abs(float(np.dot(v,FI)/(np.linalg.norm(v)*np.linalg.norm(FI)))) for v in load.values()])
    out={
      "contract":"PC2_MANEUVERING_AXIS_STABILITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_INTERPRETABILITY_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "fold_loadings":{str(e):load[e].tolist() for e in envs},
      "M1_pairwise_cosines":pairs,
      "M1_summary":{"min":float(cs.min()),"median":float(np.median(cs)),"mean":float(cs.mean())},
      "M2_signed_loading_summary":summary,
      "M3_abs_cosine_with_FlightIntensity":{"min":float(fi.min()),"median":float(np.median(fi)),"max":float(fi.max())},
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
