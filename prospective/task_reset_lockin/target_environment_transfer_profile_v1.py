#!/usr/bin/env python3
"""Post-primary target-environment transfer profiles across movement, geometry and pulse."""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent

def loadmod(name,path):
    spec=importlib.util.spec_from_file_location(name,HERE/path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    return mod

P=loadmod("P","rhino_configuration_identity_primary_v1.py")
G=loadmod("G","geometry_only_policy_v1.py")
Q=loadmod("Q","rhino_pulse_identity_v1.py")

def generic_profile(rows):
    cent=collections.defaultdict(list)
    for r in rows:
        cent[(r["env"],r["bat"])].append(r["z"])
    cent={k:np.mean(np.vstack(v),axis=0) for k,v in cent.items()}
    bats=sorted(set(b for _,b in cent))
    presence=collections.defaultdict(set)
    for e,b in cent:presence[b].add(e)

    by_env_bat=collections.defaultdict(list)
    n_target=collections.Counter()
    for r in rows:
        e,b=r["env"],r["bat"]
        own_envs=[ee for ee in sorted(presence[b]) if ee!=e and (ee,b) in cent]
        if len(own_envs)<2:continue
        own=np.mean(np.vstack([cent[(ee,b)] for ee in own_envs]),axis=0)
        donors=[]
        for j in bats:
            if j==b:continue
            jes=[ee for ee in sorted(presence[j]) if ee!=e and (ee,j) in cent]
            if len(jes)>=2:
                donors.append(np.mean(np.vstack([cent[(ee,j)] for ee in jes]),axis=0))
        if len(donors)<2:continue
        dself=float(np.linalg.norm(r["z"]-own))
        dother=float(np.mean([np.linalg.norm(r["z"]-x) for x in donors]))
        by_env_bat[(e,b)].append(dother-dself)
        n_target[e]+=1

    out={}
    for e in sorted(set(r["env"] for r in rows)):
        bm={}
        for b in bats:
            v=by_env_bat.get((e,b),[])
            if v:bm[b]=float(np.mean(v))
        if not bm:
            out[str(e)]={"status":"STOP_NO_TARGET_SUPPORT","n_targets":int(n_target[e])}
            continue
        vals=list(bm.values())
        pos=sum(v>0 for v in vals)
        frac=pos/len(vals)
        stat=float(np.mean(vals))
        out[str(e)]={
          "status":"BROADLY_TRANSFERRED" if stat>0 and frac>=.70 else "CONTEXT_DEPENDENT",
          "I_env":stat,
          "bat_means":bm,
          "positive_bats":pos,
          "n_evaluable_bats":len(vals),
          "positive_fraction":frac,
          "n_targets":int(n_target[e]),
        }
    return out

def movement_rows(traj):
    support,obj=P.build_b_structure(traj)
    if obj is None:return None,support
    rows,bats,env_presence,candidates,targets=obj
    return rows,support

def geometry_rows(traj):
    rows,support=G.build_rows(traj)
    return rows,support

def pulse_rows(raw):
    obj,support=Q.build(raw)
    if obj is None:return None,support
    rows,bats,targets,usable,candidates=obj
    return rows,support

def modality(data,builder):
    rows,support=builder(data)
    if rows is None:return {"status":"STOP_SUPPORT","support":support}
    prof=generic_profile(rows)
    broad=sum(v.get("status")=="BROADLY_TRANSFERRED" for v in prof.values())
    return {
      "status":"ALL_ENVIRONMENTS_TRANSFERRED" if broad==len(prof) else "PARTIAL_CONTEXT_DEPENDENCE",
      "n_broadly_transferred":broad,
      "n_environments":len(prof),
      "support":support,
      "target_environment_profiles":prof,
    }

def main():
    traj=P.load_rhino()
    pulse=Q.load_rows()
    out={
      "contract":"TARGET_ENVIRONMENT_TRANSFER_PROFILE_CONTRACT_V1.md",
      "status":"POST_PRIMARY_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "movement_policy":modality(traj,movement_rows),
      "geometry_only_policy":modality(traj,geometry_rows),
      "pulse_policy":modality(pulse,pulse_rows),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
