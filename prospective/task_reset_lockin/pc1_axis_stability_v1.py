#!/usr/bin/env python3
"""Observed foldwise stability of the Rhino one-dimensional PC1 policy axis."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

FEATURES=P.FEATURES
FI=np.array([.5,.5,.5,.5,0,0,0,0],float)

def rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    out=[]
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):raise RuntimeError(e)
        for r in rr:
            q=dict(r);q["z"]=(r["features"]-mu)/sd;out.append(q)
    return out,envs

def main():
    rr,envs=rows()
    load={}
    for e0 in envs:
        M=np.vstack([r["z"] for r in rr if r["env"]!=e0])
        M=M-M.mean(axis=0,keepdims=True)
        _,_,vt=np.linalg.svd(M,full_matrices=False)
        v=vt[0].astype(float)
        if np.sum(v[:4])<0:v=-v
        load[e0]=v
    pairs=[]
    for i,e1 in enumerate(envs):
        for e2 in envs[i+1:]:
            c=float(np.dot(load[e1],load[e2])/(np.linalg.norm(load[e1])*np.linalg.norm(load[e2])))
            pairs.append({"fold1":e1,"fold2":e2,"cosine":c})
    fi={str(e):float(np.dot(v,FI)/(np.linalg.norm(v)*np.linalg.norm(FI))) for e,v in load.items()}
    V=np.vstack([load[e] for e in envs])
    disp={}
    for k,n in enumerate(FEATURES):
        disp[n]={"median":float(np.median(V[:,k])),"min":float(np.min(V[:,k])),
                 "max":float(np.max(V[:,k])),"sd":float(np.std(V[:,k],ddof=1))}
    cs=np.array([x["cosine"] for x in pairs],float)
    fis=np.array(list(fi.values()),float)
    out={
      "contract":"PC1_AXIS_STABILITY_CONTRACT_V1.md",
      "status":"POST_PRIMARY_INTERPRETABILITY_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "fold_loadings":{str(e):load[e].tolist() for e in envs},
      "pairwise_cosines":pairs,
      "A1":{"min":float(cs.min()),"median":float(np.median(cs)),"mean":float(cs.mean())},
      "A2_FlightIntensity_alignment":{"by_fold":fi,"min":float(fis.min()),"median":float(np.median(fis)),"max":float(fis.max())},
      "A3_loading_dispersion":disp
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
