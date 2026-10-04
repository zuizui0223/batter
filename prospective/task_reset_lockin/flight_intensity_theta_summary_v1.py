#!/usr/bin/env python3
"""Descriptive positions on the transparent FlightIntensity axis."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"flight_intensity_scalar_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

def main():
    rows,envs=S.load_scalar_rows()
    bats=sorted(set(r["bat"] for r in rows))
    env_cent={}
    for e in envs:
        for b in bats:
            vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==b]
            if vals:
                env_cent[(e,b)]=float(np.mean(vals))
    theta={}
    for b in bats:
        vals=[env_cent[(e,b)] for e in envs if (e,b) in env_cent]
        theta[b]={
          "theta_equal_environment_mean":float(np.mean(vals)),
          "between_environment_sd":float(np.std(vals,ddof=1)) if len(vals)>1 else None,
          "n_environments":len(vals),
          "min_environment_centroid":float(np.min(vals)),
          "max_environment_centroid":float(np.max(vals)),
          "environment_centroids":{str(e):env_cent[(e,b)] for e in envs if (e,b) in env_cent},
        }
    order=sorted(bats,key=lambda b:theta[b]["theta_equal_environment_mean"],reverse=True)
    pairs=[]
    for i,a in enumerate(bats):
        for b in bats[i+1:]:
            common=[e for e in envs if (e,a) in env_cent and (e,b) in env_cent]
            diffs=[env_cent[(e,a)]-env_cent[(e,b)] for e in common]
            global_diff=theta[a]["theta_equal_environment_mean"]-theta[b]["theta_equal_environment_mean"]
            expected=np.sign(global_diff)
            agree=sum(np.sign(d)==expected for d in diffs if d!=0)
            n=sum(d!=0 for d in diffs)
            pairs.append({
              "pair":f"{a}-{b}",
              "theta_difference":float(global_diff),
              "absolute_theta_difference":float(abs(global_diff)),
              "n_common_environments":len(common),
              "environment_differences":{str(e):env_cent[(e,a)]-env_cent[(e,b)] for e in common},
              "same_sign_as_global_fraction":float(agree/n) if n else None,
            })
    out={
      "status":"DESCRIPTIVE_POST_PRIMARY",
      "scalar_definition":"mean of four environment-z-scored speed/vertical-speed features",
      "theta_by_bat":theta,
      "theta_order_high_to_low":order,
      "pairwise":sorted(pairs,key=lambda x:x["absolute_theta_difference"]),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
