#!/usr/bin/env python3
"""Transparent non-fitted flight-intensity scalar diagnostic.

Implements FLIGHT_INTENSITY_SCALAR_CONTRACT_V1.md exactly.
"""
from __future__ import annotations
import collections, importlib.util, json
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"rhino_configuration_identity_primary_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
SEED=202610042301

def load_scalar_rows():
    traj=P.load_rhino()
    ft=[r for r in traj if r["feature_valid"]]
    envs=sorted(set(r["env"] for r in ft))
    rows=[]
    for e in envs:
        rr=[r for r in ft if r["env"]==e]
        M=np.vstack([r["features"] for r in rr]).astype(float)
        mu=M.mean(axis=0);sd=M.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"bad feature SD env={e}")
        for r in rr:
            z=(r["features"]-mu)/sd
            q=dict(r)
            q["flight_intensity"]=float(np.mean(z[:4]))
            rows.append(q)
    if len(rows)!=45:
        raise RuntimeError(f"expected 45 rows, got {len(rows)}")
    return rows,envs

def labelsets(rows,envs):
    return {e:sorted(set(r["bat"] for r in rows if r["env"]==e)) for e in envs}

def observed_mapping(rows,envs):
    return {(e,b):b for e in envs for b in sorted(set(r["bat"] for r in rows if r["env"]==e))}

def perm_mapping(ls,rng):
    mp={}
    for e,labs in ls.items():
        perm=list(rng.permutation(np.asarray(labs,dtype=object)))
        for old,new in zip(labs,perm):
            mp[(e,old)]=str(new)
    return mp

def stat(rows,envs,mapping):
    perbat=collections.defaultdict(list)
    for e0 in envs:
        # training cluster mean per assigned bat per environment
        assigned=collections.defaultdict(dict)
        for e in envs:
            if e==e0: continue
            for old in sorted(set(r["bat"] for r in rows if r["env"]==e)):
                vals=[r["flight_intensity"] for r in rows if r["env"]==e and r["bat"]==old]
                if vals:
                    assigned[mapping[(e,old)]][e]=float(np.mean(vals))
        cent={}
        for b,d in assigned.items():
            if len(d)>=2:
                cent[b]=float(np.mean(list(d.values())))
        if len(cent)<3:
            return None,{}
        for old in sorted(set(r["bat"] for r in rows if r["env"]==e0)):
            new=mapping[(e0,old)]
            if new not in cent: continue
            donors=[b for b in cent if b!=new]
            if len(donors)<2: continue
            vals=[r["flight_intensity"] for r in rows if r["env"]==e0 and r["bat"]==old]
            for z in vals:
                ds=abs(z-cent[new])
                do=float(np.mean([abs(z-cent[b]) for b in donors]))
                perbat[new].append(do-ds)
    bm={b:float(np.mean(v)) for b,v in perbat.items() if v}
    if len(bm)<3:
        return None,bm
    return float(np.mean(list(bm.values()))),bm

def main():
    rows,envs=load_scalar_rows()
    obsmap=observed_mapping(rows,envs)
    obs,bm=stat(rows,envs,obsmap)
    if obs is None:
        raise RuntimeError("observed support failed")
    ls=labelsets(rows,envs)
    rng=np.random.default_rng(SEED)
    null=np.empty(NPERM,float)
    for i in range(NPERM):
        mp=perm_mapping(ls,rng)
        s,_=stat(rows,envs,mp)
        if s is None:
            raise RuntimeError("unexpected invalid permutation")
        null[i]=s
    p=float((1+np.sum(null>=obs))/(NPERM+1))
    pos=sum(v>0 for v in bm.values()); frac=pos/len(bm)
    out={
      "contract":"FLIGHT_INTENSITY_SCALAR_CONTRACT_V1.md",
      "status":"POST_PRIMARY_INTERPRETABILITY_DIAGNOSTIC",
      "species":"Rhinolophus nippon",
      "n_trajectories":len(rows),
      "definition":"mean(z_median_speed,z_p90_speed,z_median_abs_vertical_speed,z_p90_abs_vertical_speed)",
      "K_scalar":float(obs),
      "bat_means":bm,
      "positive_bats":pos,
      "n_bats":len(bm),
      "positive_fraction":frac,
      "requested_permutations":NPERM,
      "valid_permutations":NPERM,
      "seed":SEED,
      "null_mean":float(null.mean()),
      "null_q025":float(np.quantile(null,.025)),
      "null_q975":float(np.quantile(null,.975)),
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_TRANSPARENT_SCALAR" if (obs>0 and p<=.05 and frac>=.70) else "UNSUPPORTED_TRANSPARENT_SCALAR",
      "reference_PCA1_K":0.9578480313876993,
      "reference_full8_K":0.9435600964999665,
      "fraction_of_PCA1_K":float(obs/0.9578480313876993),
      "fraction_of_full8_K":float(obs/0.9435600964999665),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
