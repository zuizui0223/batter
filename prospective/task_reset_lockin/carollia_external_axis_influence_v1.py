#!/usr/bin/env python3
"""Post-external Carollia axis decomposition and single-trial influence audit."""
from __future__ import annotations
import collections, copy, importlib.util, json, math, re
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("C",HERE/"carollia_fixed_two_axis_validation_v1.py")
C=importlib.util.module_from_spec(spec);spec.loader.exec_module(C)

NPERM=9999
SEEDS={"I":202610051201,"M":202610051202,"DELTA":202610051203}
EXTREME="C3_2_20231216_traj_bat_pos_RESULTS.mat"

def load_rows():
    listing=C.get_json(C.API)
    rows=[]
    for f in listing:
        name=f.get("name") or ""
        m=C.PAT.match(name)
        if not m: continue
        bat=m.group("bat");date=m.group("date")
        if date not in C.FIXED_BLOCKS or bat not in C.FIXED_BLOCKS[date]:
            continue
        rawurl=f"https://raw.githubusercontent.com/{C.OWNER}/{C.REPO}/{C.PIN}/Trial_Data_Carolia/{name}"
        b=C.get_bytes(rawurl)
        feat,sup=C.read_trial(b)
        rows.append({
            "filename":name,"bat":bat,"trial":m.group("trial"),"date":date,
            "valid":True,"feature":np.asarray(feat,float),**sup
        })
    counts=collections.defaultdict(collections.Counter)
    for r in rows: counts[r["date"]][r["bat"]]+=1
    if not all(counts[d][b]>=3 for d,bs in C.FIXED_BLOCKS.items() for b in bs):
        raise RuntimeError(f"structural support drift: {dict(counts)}")
    return rows,counts

def fresh(rows):
    return [{**r,"feature":np.asarray(r["feature"],float).copy()} for r in rows]

def prepare(rows):
    rr=fresh(rows)
    C.standardize_by_block(rr)
    return rr

def calibrate_component(rows,component,seed):
    obs=C.stat(rows,None,component)
    if obs is None: raise RuntimeError(f"obs failed {component}")
    rng=np.random.default_rng(seed)
    null=[]
    for _ in range(NPERM):
        lab=C.perm_labels(rows,rng)
        q=C.stat(rows,lab,component)
        if q is not None:null.append(q["K"])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs["K"]))/(1+len(a)))
    pos=sum(v>0 for v in obs["bat_means"].values());n=len(obs["bat_means"])
    blockpos=all(v>0 for v in obs["block_means"].values())
    supported=obs["K"]>0 and p<=.05 and pos/n>=.70 and blockpos and len(a)>=9500
    return {
      **obs,"positive_bats":pos,"n_bats":n,"positive_fraction":pos/n,
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":seed,"null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED" if supported else "UNSUPPORTED"
    }

def delta_calibration(rows):
    o2=C.stat(rows,None,"2D");oi=C.stat(rows,None,"I")
    if o2 is None or oi is None:raise RuntimeError("delta obs failed")
    obs=float(o2["K"]-oi["K"])
    rng=np.random.default_rng(SEEDS["DELTA"]);null=[]
    for _ in range(NPERM):
        lab=C.perm_labels(rows,rng)
        q2=C.stat(rows,lab,"2D");qi=C.stat(rows,lab,"I")
        if q2 is not None and qi is not None:
            null.append(q2["K"]-qi["K"])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs))/(1+len(a)))
    return {
      "DeltaK_2D_minus_I":obs,
      "requested_permutations":NPERM,"valid_permutations":int(len(a)),
      "seed":SEEDS["DELTA"],"null_mean":float(a.mean()),
      "null_q025":float(np.quantile(a,.025)),"null_q975":float(np.quantile(a,.975)),
      "p_one_sided":p,
      "diagnostic_verdict":"SUPPORTED_INCREMENTAL_M" if (obs>0 and p<=.05 and len(a)>=9500) else "UNSUPPORTED_INCREMENTAL_M"
    }

def influence(raw_rows,counts):
    removable=[]
    for i,r in enumerate(raw_rows):
        if counts[r["date"]][r["bat"]]>3:
            removable.append((i,r["filename"]))
    reps=[]
    for i,name in removable:
        sub=[r for k,r in enumerate(raw_rows) if k!=i]
        rr=prepare(sub)
        q2=C.stat(rr,None,"2D");qi=C.stat(rr,None,"I");qm=C.stat(rr,None,"M")
        if q2 is None or qi is None or qm is None:
            raise RuntimeError(f"jackknife failed {name}")
        reps.append({
          "removed":name,
          "K_2D":float(q2["K"]),"K_I":float(qi["K"]),"K_M":float(qm["K"]),
          "block_means_2D":q2["block_means"],
          "block_means_I":qi["block_means"],
          "block_means_M":qm["block_means"],
        })
    def summary(key):
        x=np.asarray([r[key] for r in reps],float)
        return {"min":float(x.min()),"median":float(np.median(x)),"max":float(x.max())}
    min2=min(reps,key=lambda r:r["K_2D"]) if reps else None
    mini=min(reps,key=lambda r:r["K_I"]) if reps else None
    extreme=next((r for r in reps if r["removed"]==EXTREME),None)
    return {
      "n_removable_trials":len(reps),
      "K_2D_summary":summary("K_2D") if reps else None,
      "K_I_summary":summary("K_I") if reps else None,
      "K_M_summary":summary("K_M") if reps else None,
      "minimum_K_2D_deletion":min2,
      "minimum_K_I_deletion":mini,
      "extreme_track_deletion":extreme,
      "all_K_2D_positive":all(r["K_2D"]>0 for r in reps),
      "all_2D_block_means_positive":all(all(v>0 for v in r["block_means_2D"].values()) for r in reps),
      "replicates":reps
    }

def main():
    raw,counts=load_rows()
    rows=prepare(raw)
    out={
      "contract":"CAROLLIA_EXTERNAL_AXIS_INFLUENCE_CONTRACT_V1.md",
      "status":"POST_EXTERNAL_PRIMARY_ROBUSTNESS_BOUNDARY_DIAGNOSTIC",
      "species":"Carollia perspicillata",
      "source_pin":C.PIN,
      "n_valid_trials":len(rows),
      "D1_FlightIntensity":calibrate_component(rows,"I",SEEDS["I"]),
      "D2_ManeuveringExtent":calibrate_component(rows,"M",SEEDS["M"]),
      "D3_incremental_M":delta_calibration(rows),
      "D4_single_trial_influence":influence(raw,counts),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
