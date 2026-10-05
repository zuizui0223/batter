#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,itertools,json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"personal_bias_retention_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

def get_vals():
    outer=P.zipfile.ZipFile(P.io.BytesIO(P.fetch()))
    vals={}
    for b in P.BATS:
        z=P.zipfile.ZipFile(P.io.BytesIO(outer.read(P.FILES[b])))
        ss=P.shared(z);pp=P.paths(z)
        vals[b]={}
        for key,sheet in P.P1_SHEETS.items():
            vals[b][key]=P.extract_mean(z,pp[sheet],ss)["mean_angle"]
    return vals

def calc(vals,perm=None):
    base=np.array([vals[b]["baseline"] for b in P.BATS],float)
    y30=np.array([vals[b]["mask30"] for b in P.BATS],float)
    y10=np.array([vals[b]["mask10"] for b in P.BATS],float)
    th=base-base.mean();a30=y30-y30.mean();a10=y10-y10.mean()
    if perm is not None:th=th[np.asarray(perm,int)]
    k30=P.p1_metrics(vals,perm)["K_mask30"]
    k10=P.p1_metrics(vals,perm)["K_mask10"]
    den=float(th@th)
    b30=float((th@a30)/den)
    b10=float((th@a10)/den)
    def r2(y):
        d=float(y@y)
        return float(1-np.sum((y-th)**2)/d) if d>0 else None
    return {
      "K30":float(k30),"K10":float(k10),"D_K":float(k30-k10),
      "alpha30":b30,"alpha10":b10,"D_alpha":float(b30-b10),
      "sd_baseline":float(np.std(th,ddof=1)),
      "sd_30":float(np.std(a30,ddof=1)),
      "sd_10":float(np.std(a10,ddof=1)),
      "sd_ratio_30":float(np.std(a30,ddof=1)/np.std(th,ddof=1)),
      "sd_ratio_10":float(np.std(a10,ddof=1)/np.std(th,ddof=1)),
      "r2_unscaled_30":r2(a30),"r2_unscaled_10":r2(a10),
    }

def main():
    vals=get_vals();obs=calc(vals)
    ndk=[];nda=[]
    for p in itertools.permutations(range(6)):
        q=calc(vals,p);ndk.append(q["D_K"]);nda.append(q["D_alpha"])
    ndk=np.asarray(ndk,float);nda=np.asarray(nda,float)
    out={
      "contract":"MASKER_STRENGTH_EXPRESSION_DIAGNOSTIC_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_MECHANISM_DIAGNOSTIC",
      "observed":obs,
      "D_K_exact":{
        "permutations":720,
        "p_one_sided":float(np.mean(ndk>=obs["D_K"]-1e-15)),
        "null_mean":float(ndk.mean()),
        "null_q025":float(np.quantile(ndk,.025)),
        "null_q975":float(np.quantile(ndk,.975))
      },
      "D_alpha_exact":{
        "permutations":720,
        "p_one_sided":float(np.mean(nda>=obs["D_alpha"]-1e-15)),
        "null_mean":float(nda.mean()),
        "null_q025":float(np.quantile(nda,.025)),
        "null_q975":float(np.quantile(nda,.975))
      }
    }
    print(json.dumps(out,indent=2))

if __name__=="__main__":main()
