#!/usr/bin/env python3
"""Post-primary leave-one-environment robustness across movement, geometry and pulse carriers."""
from __future__ import annotations
import importlib.util, json, math
from pathlib import Path

HERE=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

P=loadmod("P","rhino_configuration_identity_primary_v1.py")
G=loadmod("G","geometry_only_policy_v1.py")
Q=loadmod("Q","rhino_pulse_identity_v1.py")

ENVS=list(range(1,8))

def summarize(stat,indiv):
    vals={str(k):float(v) for k,v in indiv.items()}
    n=len(vals);npos=sum(v>0 for v in vals.values())
    return {
      "statistic":float(stat),
      "bat_means":vals,
      "positive_bats":npos,
      "n_bats":n,
      "positive_fraction":npos/n if n else None,
    }

def movement_observed(traj):
    support,obj=P.build_b_structure(traj)
    if obj is None:
        return {"status":"STOP","support":support}
    rows,bats,env_presence,candidates,targets=obj
    obs=P.b_stat(rows,bats,targets,None)
    if obs is None:return {"status":"STOP_OBSERVED","support":support}
    stat,indiv,_=obs
    return {"status":"PASS_SUPPORT",**summarize(stat,indiv),
            "usable_envs":support.get("usable_envs"),"retained_features":support.get("retained_features")}

def geometry_observed(traj):
    rows,support=G.build_rows(traj)
    if rows is None:return {"status":"STOP","support":support}
    obs=G.stat(rows)
    if obs[0] is None:return {"status":"STOP_OBSERVED","support":support}
    stat,indiv=obs
    return {"status":"PASS_SUPPORT",**summarize(stat,indiv),
            "usable_envs":support.get("usable_envs"),"retained_features":support.get("retained_features")}

def pulse_observed(raw):
    obj,support=Q.build(raw)
    if obj is None:return {"status":"STOP","support":support}
    rows,bats,targets,usable,candidates=obj
    obs=P.b_stat(rows,bats,targets,None)
    if obs is None:return {"status":"STOP_OBSERVED","support":support}
    stat,indiv,_=obs
    return {"status":"PASS_SUPPORT",**summarize(stat,indiv),
            "usable_envs":usable,"retained_features":support.get("retained_features")}

def modality(full_data,fun):
    full=fun(full_data)
    if full.get("status")!="PASS_SUPPORT":
        return {"full":full,"status":"STOP_FULL_SUPPORT"}
    loo={}
    for e in ENVS:
        subset=[r for r in full_data if r["env"]!=e]
        loo[str(e)]=fun(subset)
    valid=[v for v in loo.values() if v.get("status")=="PASS_SUPPORT"]
    if len(valid)!=7:
        return {"full":full,"loo":loo,"status":"STOP_LOO_SUPPORT"}
    stats=[v["statistic"] for v in valid]
    fracs=[v["positive_fraction"] for v in valid]
    robust=all(x>0 for x in stats) and all(x>=.70 for x in fracs)
    return {
      "full":full,"loo":loo,
      "loo_min_statistic":float(min(stats)),
      "loo_max_statistic":float(max(stats)),
      "loo_min_over_full":float(min(stats)/full["statistic"]) if full["statistic"]!=0 else None,
      "loo_positive_statistics":sum(x>0 for x in stats),
      "loo_n":7,
      "minimum_positive_fraction":float(min(fracs)),
      "status":"ENVIRONMENT_ROBUST" if robust else "ENVIRONMENT_SENSITIVE",
    }

def main():
    movement=P.load_rhino()
    pulse=Q.load_rows()
    out={
      "contract":"LEAVE_ONE_ENVIRONMENT_CARRIER_ROBUSTNESS_CONTRACT_V1.md",
      "status":"POST_PRIMARY_ROBUSTNESS_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "movement_policy":modality(movement,movement_observed),
      "geometry_only_policy":modality(movement,geometry_observed),
      "pulse_policy":modality(pulse,pulse_observed),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
