#!/usr/bin/env python3
"""Post-primary family ablation for scale-free route-geometry identity."""
from __future__ import annotations
import importlib.util,json,math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("G",HERE/"geometry_only_policy_v1.py")
G=importlib.util.module_from_spec(spec);spec.loader.exec_module(G)

NPERM=9999
MIN_VALID=9500
VARIANTS={
 "G_only":([0,1,2,3],202610061101),
 "H_only":([4,5],202610061102),
 "V_only":([6,7],202610061103),
 "drop_G":([4,5,6,7],202610061104),
 "drop_H":([0,1,2,3,6,7],202610061105),
 "drop_V":([0,1,2,3,4,5],202610061106),
}

def subrows(rows,idx):
    out=[]
    for r in rows:
        q=dict(r)
        q["z"]=np.asarray(r["z"],float)[idx]
        out.append(q)
    return out

def calibrate(rows,envs,seed):
    obs,ind=G.stat(rows)
    if obs is None:return {"status":"STOP_OBSERVED_SUPPORT"}
    env_labels={e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        mp={}
        for e,labs in env_labels.items():
            p=list(rng.permutation(np.asarray(labs,dtype=object)))
            for old,new in zip(labs,p):mp[(e,old)]=str(new)
        s,_=G.stat(rows,mp)
        if s is not None and math.isfinite(s):null.append(float(s))
    a=np.asarray(null,float)
    if len(a)<MIN_VALID:
        return {"status":"STOP_RANDOMIZATION_SUPPORT","valid_permutations":int(len(a))}
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    pos=sum(v>0 for v in ind.values())
    return {
      "status":"DONE","K":float(obs),"bat_means":ind,
      "positive_bats":int(pos),"n_bats":int(len(ind)),
      "positive_fraction":float(pos/len(ind)),
      "valid_permutations":int(len(a)),"requested_permutations":NPERM,"seed":seed,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),"p_one_sided":p
    }

def main():
    traj=G.P.load_rhino()
    rows,support=G.build_rows(traj)
    if rows is None:
        print(json.dumps({"contract":"GEOMETRY_POLICY_FAMILY_ABLATION_CONTRACT_V1.md",**support},indent=2))
        return
    if support.get("retained_features")!=G.FEATURES:
        raise RuntimeError("frozen all-eight geometry support no longer exact")
    results={}
    for name,(idx,seed) in VARIANTS.items():
        results[name]=calibrate(subrows(rows,idx),support["usable_envs"],seed)
    robust=True
    for name in ("drop_G","drop_H","drop_V"):
        q=results[name]
        robust = robust and q.get("status")=="DONE" and q["K"]>0 and q["p_one_sided"]<=.05 and q["positive_bats"]>=4
    print(json.dumps({
      "contract":"GEOMETRY_POLICY_FAMILY_ABLATION_CONTRACT_V1.md",
      "status":"POST_PRIMARY_EXPLORATORY_MECHANISM_DIAGNOSTIC",
      "feature_families":{
        "G":["path_efficiency_3d","horizontal_displacement_ratio","abs_vertical_displacement_ratio","vertical_range_ratio"],
        "H":["median_abs_horizontal_turn_angle","p90_abs_horizontal_turn_angle"],
        "V":["median_abs_vertical_slope","p90_abs_vertical_slope"]
      },
      "results":results,
      "diagnostic_verdict":"ROBUST_TO_ALL_FAMILY_ABLATIONS" if robust else "DEPENDENT_ON_AT_LEAST_ONE_GEOMETRY_FAMILY"
    },indent=2))

if __name__=="__main__":main()
