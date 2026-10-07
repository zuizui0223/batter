#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from collections import defaultdict
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("R",HERE/"geometry_beyond_theta_v1.py")
R=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(R)

def main():
    rows,envs,support=R.prepare()
    X=np.asarray([[1.0,r["fi"]] for r in rows],float)
    G=np.vstack([r["z"] for r in rows]).astype(float)
    coef=np.linalg.lstsq(X,G,rcond=None)[0]
    resid=G-X@coef
    mu=resid.mean(axis=0)
    _,s,Vt=np.linalg.svd(resid-mu,full_matrices=False)
    v=Vt[0].copy()
    k=int(np.argmax(np.abs(v)))
    if v[k]<0:v=-v
    phi=(resid-mu)@v
    ratio=(s*s)/np.sum(s*s)

    by=defaultdict(lambda:defaultdict(list))
    for i,r in enumerate(rows):
        by[str(r["bat"])][int(r["env"])].append((float(r["fi"]),float(phi[i])))
    bats=sorted(by)
    coords={}
    for b in bats:
        envcent={}
        for e,vals in sorted(by[b].items()):
            envcent[str(e)]={
                "theta":float(np.mean([q[0] for q in vals])),
                "phi":float(np.mean([q[1] for q in vals])),
                "n_trajectories":len(vals)
            }
        tv=np.asarray([q["theta"] for q in envcent.values()],float)
        pv=np.asarray([q["phi"] for q in envcent.values()],float)
        coords[b]={
            "theta":float(tv.mean()),
            "phi":float(pv.mean()),
            "theta_between_environment_sd":float(tv.std(ddof=1)) if len(tv)>1 else None,
            "phi_between_environment_sd":float(pv.std(ddof=1)) if len(pv)>1 else None,
            "n_environments":len(envcent),
            "environment_centroids":envcent
        }
    theta=np.asarray([coords[b]["theta"] for b in bats],float)
    ph=np.asarray([coords[b]["phi"] for b in bats],float)
    corr=float(np.corrcoef(theta,ph)[0,1])
    out={
      "status":"DESCRIPTIVE_POST_PRIMARY_COORDINATE_EXTRACTION",
      "species":"Rhinolophus nippon",
      "coordinate_definition":{
        "theta":"equal-environment mean transparent FlightIntensity",
        "phi":"equal-environment mean full-data PCA1 score of geometry residuals after global linear FlightIntensity removal",
        "phi_sign_rule":"largest absolute loading forced positive",
        "phi_variance_explained":float(ratio[0])
      },
      "phi_loadings":{name:float(v[i]) for i,name in enumerate(support["retained_features"])},
      "theta_phi_correlation_across_five_bats":corr,
      "coordinates":coords,
      "theta_order_high_to_low":sorted(bats,key=lambda b:coords[b]["theta"],reverse=True),
      "phi_order_high_to_low":sorted(bats,key=lambda b:coords[b]["phi"],reverse=True)
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
