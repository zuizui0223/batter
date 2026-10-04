#!/usr/bin/env python3
"""Post-primary route-axis decomposition diagnostics."""
from __future__ import annotations
import importlib.util,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

def transformed(traj,kind):
    out=[]
    for r in traj:
        q=dict(r)
        if r["route_valid"]:
            x=np.asarray(r["route101"],float)
            if kind=="xy":
                y=x[:,:2]
            elif kind=="z":
                y=x[:,2:3]
            elif kind=="centroid":
                y=np.mean(x,axis=0,keepdims=True)
            elif kind=="centroid_centered":
                y=x-np.mean(x,axis=0,keepdims=True)
            else:raise ValueError(kind)
            q["route101"]=y
        out.append(q)
    return out

def run(traj,kind,seed):
    old=P.A_SEED
    try:
        P.A_SEED=seed
        return P.primary_a(transformed(traj,kind))
    finally:P.A_SEED=old

def main():
    t=P.load_rhino()
    out={
      "contract":"POST_PRIMARY_ROUTE_AXIS_CONTRACT_V1.md",
      "status":"POST_PRIMARY_DIAGNOSTIC_NOT_CONFIRMATORY",
      "species":"Rhinolophus nippon",
      "X1_absolute_XY":run(t,"xy",202610042241),
      "X2_absolute_Z":run(t,"z",202610042242),
      "X3_route_centroid":run(t,"centroid",202610042243),
      "X4_centroid_centered_route":run(t,"centroid_centered",202610042244),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
