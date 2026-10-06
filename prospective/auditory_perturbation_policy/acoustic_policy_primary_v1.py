#!/usr/bin/env python3
"""Frozen numeric implementation for ACOUSTIC_POLICY_PRIMARY_V1.md.

DO NOT RUN unless STRUCTURAL_RESULT_V1 verdict is PASS_OPEN_NUMERIC_PRIMARY.
"""

from __future__ import annotations

import itertools
import json
import math
import pathlib
import tempfile
import urllib.request

import numpy as np
import scipy.io

HERE=pathlib.Path(__file__).resolve().parent
OUT=HERE/"ACOUSTIC_POLICY_RESULT_V1.json"
OUTMD=HERE/"ACOUSTIC_POLICY_RESULT_V1.md"

BASE="https://zenodo.org/records/13857870/files"
BATS=["jane","bea","jason","stella"]
CONDITIONS={1:"Saline",2:"Ligand"}
FEATURES=["Duration","Bandwidth","IPI","CallRate"]

def fetch(name):
    url=f"{BASE}/{name}?download=1"
    req=urllib.request.Request(url,headers={"User-Agent":"batter-acoustic-primary/1.0"})
    with urllib.request.urlopen(req,timeout=120) as r:
        return r.read()

def load_struct(bat):
    data=fetch(f"{bat}_audiopooldata.mat")
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data); tf.flush()
        mat=scipy.io.loadmat(tf.name,squeeze_me=True,struct_as_record=False)
    st=mat.get("audiopoolstruct")
    if st is None:
        raise RuntimeError(f"{bat}: missing audiopoolstruct")
    return st

def flatten(x):
    return np.asarray(x).reshape(-1)

def trial_objects(x):
    arr=np.asarray(x,dtype=object)
    if arr.ndim==0:
        return [arr.item()]
    return list(arr.reshape(-1))

def finite_mean(x):
    try:
        arr=np.asarray(x,dtype=float).reshape(-1)
    except Exception:
        return math.nan
    arr=arr[np.isfinite(arr)]
    if arr.size==0:
        return math.nan
    return float(np.mean(arr))

def trial_rows(bat):
    st=load_struct(bat)

    treatment=flatten(st.treatment)
    trialtype=flatten(st.trialtype)
    lengthadjust=flatten(st.lengthtrialadjust)
    onsets=trial_objects(st.onsetcalltrial)
    durations=trial_objects(st.callduration)
    bandwidths=trial_objects(st.callbandwidth)

    n=min(
        len(treatment),len(trialtype),len(lengthadjust),
        len(onsets),len(durations),len(bandwidths)
    )

    rows=[]
    for i in range(n):
        tr=int(treatment[i]) if np.isfinite(treatment[i]) else -999
        tp=float(trialtype[i]) if np.isfinite(trialtype[i]) else math.nan
        if tr not in (1,2) or not np.isfinite(tp) or not (tp < 4):
            continue

        duration=finite_mean(durations[i])
        bandwidth=finite_mean(bandwidths[i])

        try:
            onset=np.asarray(onsets[i],dtype=float).reshape(-1)
            onset=onset[np.isfinite(onset)]
        except Exception:
            onset=np.asarray([],dtype=float)

        ipi=float(np.mean(np.diff(onset))) if onset.size>=2 else math.nan

        try:
            ladj=float(np.asarray(lengthadjust[i]).reshape(-1)[0])
        except Exception:
            ladj=math.nan
        callrate=float(onset.size/ladj) if np.isfinite(ladj) and ladj>0 else math.nan

        feat=np.asarray([duration,bandwidth,ipi,callrate],dtype=float)
        if np.all(np.isfinite(feat)):
            rows.append({
                "bat":bat,
                "condition":tr,
                "condition_name":CONDITIONS[tr],
                "features":feat,
            })
    return rows

def standardize(rows):
    out=[]
    scalers={}
    for cond in (1,2):
        rr=[r for r in rows if r["condition"]==cond]
        mat=np.vstack([r["features"] for r in rr])
        mu=mat.mean(axis=0)
        sd=mat.std(axis=0,ddof=1)
        if np.any(~np.isfinite(sd)) or np.any(sd<=0):
            raise RuntimeError(f"{CONDITIONS[cond]}: zero/nonfinite SD")
        scalers[cond]={"mean":mu,"sd":sd}
        for r in rr:
            q=dict(r)
            q["z"]=(r["features"]-mu)/sd
            out.append(q)
    return out,scalers

def centroids(rows):
    c={}
    counts={}
    for bat in BATS:
        for cond in (1,2):
            rr=[r for r in rows if r["bat"]==bat and r["condition"]==cond]
            if len(rr)<5:
                raise RuntimeError(f"{bat} {CONDITIONS[cond]}: <5 valid trials")
            c[(bat,cond)]=np.mean(np.vstack([r["z"] for r in rr]),axis=0)
            counts[(bat,cond)]=len(rr)
    return c,counts

def stat(c,saline_mapping):
    """Map each Ligand bat to one Saline bat; return K and per-Ligand advantages."""
    vals={}
    assigned=set(saline_mapping.values())
    if assigned != set(BATS):
        raise ValueError("mapping must be bijective")

    for ligand_bat in BATS:
        saline_self=saline_mapping[ligand_bat]
        target=c[(ligand_bat,2)]
        dself=float(np.linalg.norm(target-c[(saline_self,1)]))
        other_bats=[b for b in BATS if b != saline_self]
        dother=float(np.mean([
            np.linalg.norm(target-c[(b,1)]) for b in other_bats
        ]))
        vals[ligand_bat]={
            "assigned_saline_bat":saline_self,
            "self_distance":dself,
            "other_distance":dother,
            "K_i":dother-dself,
        }
    return float(np.mean([v["K_i"] for v in vals.values()])),vals

def leave_one_feature_out(c):
    out={}
    for drop in range(4):
        cc={}
        keep=[k for k in range(4) if k!=drop]
        for key,val in c.items():
            cc[key]=np.asarray(val)[keep]
        observed={b:b for b in BATS}
        kval,_=stat(cc,observed)
        out[FEATURES[drop]]=kval
    return out

def render(result):
    lines=[
        "# Auditory perturbation acoustic-policy result v1","",
        "## Primary","",
        f"- K = **{result['K']:.8f}**",
        f"- exact p = **{result['p_exact']:.8f}**",
        f"- exact permutations = **{result['n_permutations']}**",
        f"- verdict = **{result['verdict']}**","",
        "## Individual advantages","",
        "| bat | K_i | self distance | mean other distance |",
        "|---|---:|---:|---:|",
    ]
    for bat in BATS:
        v=result["individual"][bat]
        lines.append(
            f"| {bat} | {v['K_i']:.8f} | {v['self_distance']:.8f} | {v['other_distance']:.8f} |"
        )
    lines += ["","## Trial support",""]
    for bat in BATS:
        lines.append(
            f"- {bat}: Saline={result['trial_counts'][bat]['Saline']}, "
            f"Ligand={result['trial_counts'][bat]['Ligand']}"
        )
    lines += ["","## Boundary","",
              "The exact p-value has only 24 possible identity mappings.",
              "No robustness diagnostic changes the frozen primary verdict.",""]
    return "\n".join(lines)

def main():
    structural_path=HERE/"STRUCTURAL_RESULT_V1.json"
    if not structural_path.exists():
        raise SystemExit("STOP: structural result missing")
    structural=json.loads(structural_path.read_text())
    if structural.get("verdict")!="PASS_OPEN_NUMERIC_PRIMARY":
        raise SystemExit("STOP: structural gate did not pass")

    raw=[]
    for bat in BATS:
        raw.extend(trial_rows(bat))

    zrows,scalers=standardize(raw)
    c,counts=centroids(zrows)

    observed_map={b:b for b in BATS}
    K,individual=stat(c,observed_map)

    null=[]
    for perm in itertools.permutations(BATS):
        mapping={lig:sal for lig,sal in zip(BATS,perm)}
        kp,_=stat(c,mapping)
        null.append({
            "mapping":[mapping[b] for b in BATS],
            "K":kp,
        })

    extreme=sum(x["K"] >= K-1e-15 for x in null)
    p=extreme/len(null)
    verdict="SUPPORTED" if K>0 and p<=0.05 else "UNSUPPORTED"

    result={
        "version":1,
        "features":FEATURES,
        "K":K,
        "p_exact":p,
        "n_permutations":len(null),
        "extreme_count":extreme,
        "verdict":verdict,
        "individual":individual,
        "trial_counts":{
            bat:{
                "Saline":counts[(bat,1)],
                "Ligand":counts[(bat,2)],
            } for bat in BATS
        },
        "centroids":{
            bat:{
                "Saline":c[(bat,1)].tolist(),
                "Ligand":c[(bat,2)].tolist(),
            } for bat in BATS
        },
        "condition_scalers":{
            CONDITIONS[cond]:{
                "mean":scalers[cond]["mean"].tolist(),
                "sd":scalers[cond]["sd"].tolist(),
            } for cond in (1,2)
        },
        "leave_one_feature_out_K":leave_one_feature_out(c),
        "null":null,
    }

    OUT.write_text(json.dumps(result,indent=2)+"\n")
    OUTMD.write_text(render(result)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":
    main()
