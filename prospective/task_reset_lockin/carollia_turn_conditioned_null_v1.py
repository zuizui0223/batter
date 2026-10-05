#!/usr/bin/env python3
"""Post-outcome turn-conditioned null robustness for Carollia fixed two-axis external result."""
from __future__ import annotations
import collections, importlib.util, json, math, tempfile
from pathlib import Path
import h5py, numpy as np

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("P",HERE/"carollia_fixed_two_axis_validation_v1.py")
P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)

NPERM=9999
SEED_COND=202610051221

def read_turn_angles(raw):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tmp:
        tmp.write(raw); tmp.flush()
        with h5py.File(tmp.name,"r") as h:
            try:
                a=P.deref_numeric(h,"RESULTS/turns/angleDeg")
            except Exception:
                return np.asarray([],float)
    a=np.asarray(a,dtype=float).reshape(-1)
    return a[np.isfinite(a)]

def load_rows():
    listing=P.get_json(P.API)
    rows=[]
    for f in listing:
        name=f.get("name") or "";m=P.PAT.match(name)
        if not m:continue
        bat=m.group("bat");date=m.group("date")
        if date not in P.FIXED_BLOCKS or bat not in P.FIXED_BLOCKS[date]:continue
        rawurl=f"https://raw.githubusercontent.com/{P.OWNER}/{P.REPO}/{P.PIN}/Trial_Data_Carolia/{name}"
        raw=P.get_bytes(rawurl)
        feat,sup=P.read_trial(raw)
        ang=read_turn_angles(raw)
        if len(ang)==0:
            cls="no_annotated_turn";amax=None
        else:
            amax=float(np.max(ang)); cls="le90" if amax<=90.0 else "gt90"
        rows.append({
          "filename":name,"bat":bat,"trial":m.group("trial"),"date":date,
          "valid":True,"feature":feat,"turn_class":cls,
          "n_annotated_turns":int(len(ang)),"max_turn_angle_deg":amax,
          **sup
        })
    P.standardize_by_block(rows)
    return rows

def conditional_perm_labels(rows,rng):
    labels=[r["bat"] for r in rows]
    strata=collections.defaultdict(list)
    for i,r in enumerate(rows):
        strata[(r["date"],r["turn_class"])].append(i)
    for _,idx in strata.items():
        vals=np.asarray([labels[i] for i in idx],dtype=object)
        rng.shuffle(vals)
        for k,i in enumerate(idx):labels[i]=str(vals[k])
    return labels

def ordinary_perm_labels(rows,rng):
    return P.perm_labels(rows,rng)

def support_after_filter(rows):
    counts=collections.defaultdict(collections.Counter)
    for r in rows:counts[r["date"]][r["bat"]]+=1
    return all(
      sum(counts[d][b]>=2 for b in P.FIXED_BLOCKS[d])>=3
      for d in P.FIXED_BLOCKS
    ) and all(
      counts[d][b]>=2
      for d in P.FIXED_BLOCKS
      for b in P.FIXED_BLOCKS[d]
    )

def standardize_copy(rows):
    rr=[]
    for r in rows:
        q=dict(r);q["feature"]=np.asarray(r["feature"],float).copy()
        # remove existing standardized fields before recompute
        q.pop("z",None);q.pop("I",None);q.pop("M",None)
        rr.append(q)
    P.standardize_by_block(rr)
    return rr

def evaluate(rows,seed,conditional=False):
    obs=P.stat(rows,None,"2D")
    if obs is None:return None
    rng=np.random.default_rng(seed);null=[]
    for _ in range(NPERM):
        lab=conditional_perm_labels(rows,rng) if conditional else ordinary_perm_labels(rows,rng)
        q=P.stat(rows,lab,"2D")
        if q is not None:null.append(q["K"])
    a=np.asarray(null,float)
    p=float((1+np.sum(a>=obs["K"]))/(1+len(a)))
    pos=sum(v>0 for v in obs["bat_means"].values());n=len(obs["bat_means"])
    return {
      "K":float(obs["K"]),"block_means":obs["block_means"],
      "bat_means":obs["bat_means"],"positive_bats":pos,"n_bats":n,
      "positive_fraction":pos/n,
      "valid_permutations":int(len(a)),"p_one_sided":p,
      "null_mean":float(a.mean()),"null_q025":float(np.quantile(a,.025)),
      "null_q975":float(np.quantile(a,.975)),
    }

def main():
    rows=load_rows()
    exposure=collections.defaultdict(lambda:collections.defaultdict(collections.Counter))
    trial_audit=[]
    for r in rows:
        exposure[r["date"]][r["bat"]][r["turn_class"]]+=1
        trial_audit.append({
          "filename":r["filename"],"date":r["date"],"bat":r["bat"],
          "turn_class":r["turn_class"],"n_annotated_turns":r["n_annotated_turns"],
          "max_turn_angle_deg":r["max_turn_angle_deg"]
        })

    strata=collections.defaultdict(list)
    for i,r in enumerate(rows):strata[(r["date"],r["turn_class"])].append(i)
    stratainfo=[]
    n_effective=0
    for (d,c),idx in sorted(strata.items()):
        labs=[rows[i]["bat"] for i in idx]
        nontrivial=len(idx)>=2 and len(set(labs))>=2
        if nontrivial:n_effective+=len(idx)
        stratainfo.append({
          "date":d,"turn_class":c,"n_trials":len(idx),
          "bat_counts":dict(collections.Counter(labs)),
          "permutable":nontrivial
        })

    cond=evaluate(rows,SEED_COND,conditional=True)
    classes=sorted(set(r["turn_class"] for r in rows))
    loo=[]
    for ci,cls in enumerate(classes,1):
        sub=[r for r in rows if r["turn_class"]!=cls]
        if not support_after_filter(sub):
            loo.append({"removed_turn_class":cls,"status":"STOP_SUPPORT_AFTER_CLASS_REMOVAL"})
            continue
        rr=standardize_copy(sub)
        q=evaluate(rr,202610051230+ci,conditional=False)
        loo.append({"removed_turn_class":cls,"status":"DONE","seed":202610051230+ci,**q})

    out={
      "contract":"CAROLLIA_TURN_CONDITIONED_NULL_CONTRACT_V1.md",
      "status":"POST_OUTCOME_EXTERNAL_ROBUSTNESS_AUDIT",
      "species":"Carollia perspicillata",
      "R1_exposure":{
        "trial_audit":trial_audit,
        "counts_by_date_bat":{
          d:{b:dict(c) for b,c in bd.items()} for d,bd in exposure.items()
        }
      },
      "R2_condition_stratified_null":{
        **cond,
        "seed":SEED_COND,
        "requested_permutations":NPERM,
        "strata":stratainfo,
        "n_permutable_strata":sum(x["permutable"] for x in stratainfo),
        "n_trials_in_permutable_strata":n_effective
      },
      "R3_leave_one_turn_class_out":loo,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
