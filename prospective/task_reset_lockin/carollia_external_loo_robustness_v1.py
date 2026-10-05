#!/usr/bin/env python3
"""Exhaustive leave-one-trial robustness for the frozen Carollia external validation."""
from __future__ import annotations
import copy, importlib.util, json, math, tempfile
from pathlib import Path
import h5py, numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"carollia_fixed_two_axis_validation_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999

def raw_track_and_qc(raw):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(raw);tmp.flush()
        with h5py.File(tmp.name,"r") as h:
            t=P.deref_numeric(h,"RESULTS/track/tSec")
            p=P.deref_numeric(h,"RESULTS/track/pos_sm")
    feat,sup=P.normalize_track(t,p)

    t=np.asarray(t,dtype=float).reshape(-1)
    p=np.asarray(p,dtype=float)
    if p.ndim!=2:raise ValueError("POS_NOT_2D")
    if p.shape[1]==3:pass
    elif p.shape[0]==3:p=p.T
    else:raise ValueError("POS_NOT_3COL")
    n=min(len(t),len(p));t=t[:n];p=p[:n]
    ok=np.isfinite(t)&np.all(np.isfinite(p),axis=1);t=t[ok];p=p[ok]
    order=np.argsort(t,kind="mergesort");t=t[order];p=p[order]
    _,idx=np.unique(t,return_index=True);idx=np.sort(idx);t=t[idx];p=p[idx]
    dt=np.diff(t);dp=np.diff(p,axis=0);good=dt>0
    v=np.linalg.norm(dp[good],axis=1)/dt[good]
    steps=np.linalg.norm(np.diff(p,axis=0),axis=1)
    nz=steps[np.isfinite(steps)&(steps>0)]
    net=float(np.linalg.norm(p[-1]-p[0]))
    ranges=np.ptp(p,axis=0)
    qc={
      **sup,
      "straight_displacement":net,
      "median_speed":float(np.median(v)),
      "p90_speed":float(np.percentile(v,90)),
      "p99_speed":float(np.percentile(v,99)),
      "max_speed":float(np.max(v)),
      "max_step":float(np.max(nz)),
      "median_nonzero_step":float(np.median(nz)),
      "max_over_median_step":float(np.max(nz)/np.median(nz)),
      "x_range":float(ranges[0]),"y_range":float(ranges[1]),"z_range":float(ranges[2]),
    }
    return feat,qc

def load_primary_rows():
    listing=P.get_json(P.API)
    rows=[];qc=[]
    for f in listing:
        name=f.get("name") or "";m=P.PAT.match(name)
        if not m:continue
        bat=m.group("bat");date=m.group("date")
        if date not in P.FIXED_BLOCKS or bat not in P.FIXED_BLOCKS[date]:continue
        rawurl=f"https://raw.githubusercontent.com/{P.OWNER}/{P.REPO}/{P.PIN}/Trial_Data_Carolia/{name}"
        raw=P.get_bytes(rawurl)
        feat,q=raw_track_and_qc(raw)
        rec={"filename":name,"bat":bat,"trial":m.group("trial"),"date":date,"valid":True,"feature":feat}
        rows.append(rec)
        qc.append({"filename":name,"bat":bat,"trial":m.group("trial"),"date":date,**q})
    return rows,qc

def standardize_fresh(rows):
    rr=[dict(r,feature=np.asarray(r["feature"],float).copy()) for r in rows]
    P.standardize_by_block(rr)
    return rr

def evaluate(rows,seed):
    rr=standardize_fresh(rows)
    obs=P.stat(rr,None,"2D")
    if obs is None:raise RuntimeError("observed stat failed")
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        lab=P.perm_labels(rr,rng)
        q=P.stat(rr,lab,"2D")
        if q is not None:null.append(q["K"])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs["K"]))/(1+len(a)))
    pos=sum(v>0 for v in obs["bat_means"].values());n=len(obs["bat_means"])
    blockpos=all(v>0 for v in obs["block_means"].values())
    supported=bool(obs["K"]>0 and p<=.05 and pos/n>=.70 and blockpos and len(a)>=9500)
    return {
      "K":float(obs["K"]),
      "block_means":obs["block_means"],
      "positive_bats":pos,"n_bats":n,"positive_fraction":pos/n,
      "valid_permutations":int(len(a)),"p_one_sided":p,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),
      "support_retained":supported,
    }

def main():
    rows,qc=load_primary_rows()
    counts={}
    for r in rows:counts[(r["date"],r["bat"])]=counts.get((r["date"],r["bat"]),0)+1
    admissible=sorted([r["filename"] for r in rows if counts[(r["date"],r["bat"])]>3])
    if len(admissible)!=22:raise RuntimeError(f"expected 22 admissible deletions, got {len(admissible)}")
    outrows=[]
    for k,name in enumerate(admissible,1):
        sub=[r for r in rows if r["filename"]!=name]
        q=evaluate(sub,202610051200+k)
        outrows.append({"removed":name,"seed":202610051200+k,**q})
    target=next(x for x in outrows if x["removed"]=="C3_2_20231216_traj_bat_pos_RESULTS.mat")
    out={
      "contract":"CAROLLIA_EXTERNAL_LOO_ROBUSTNESS_CONTRACT_V1.md",
      "status":"POST_OUTCOME_ROBUSTNESS_AUDIT",
      "n_primary_trials":len(rows),
      "n_admissible_deletions":len(admissible),
      "track_qc":qc,
      "deletion_results":outrows,
      "summary":{
        "min_K":float(min(x["K"] for x in outrows)),
        "max_p_one_sided":float(max(x["p_one_sided"] for x in outrows)),
        "min_positive_fraction":float(min(x["positive_fraction"] for x in outrows)),
        "n_support_retained":sum(bool(x["support_retained"]) for x in outrows),
        "all_22_support_retained":all(x["support_retained"] for x in outrows),
        "C3_2_deletion":target,
      }
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
