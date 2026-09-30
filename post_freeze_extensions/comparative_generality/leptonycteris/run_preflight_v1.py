#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math, os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/leptonycteris/source_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/leptonycteris/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/leptonycteris/PREFLIGHT_RESULT_V1.md"
RECEIPT=ROOT/"post_freeze_extensions/comparative_generality/leptonycteris/altitude_opening_receipt_v1.json"

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def fetch(file_id,token):
    r=requests.get(
        f"https://datadryad.org/api/v2/files/{file_id}/download",
        headers={
            "Authorization":f"Bearer {token}",
            "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
            "User-Agent":"batter-leptonycteris-comparative-preflight-v1/1.0"
        },
        timeout=180,allow_redirects=True
    )
    r.raise_for_status()
    raw=r.content
    if not raw.startswith(b"PK\x03\x04"):
        raise RuntimeError("download is not an XLSX ZIP stream")
    return raw

def utm_epsg(lon,lat):
    zone=int(math.floor((lon+180.0)/6.0)+1)
    zone=max(1,min(60,zone))
    return 32600+zone if lat>=0 else 32700+zone

def smooth(counts,alpha=0.5):
    x=np.asarray(counts,dtype=float)+alpha
    return x/x.sum()

def horizontal_arrays(session_records,cell_universe):
    cells=sorted(cell_universe)
    cidx={c:i for i,c in enumerate(cells)}
    keys=sorted(session_records)
    individuals=sorted({session_records[k]["id"] for k in keys})
    iidx={x:i for i,x in enumerate(individuals)}
    S=len(keys);C=len(cells)
    counts=np.zeros((S,C),dtype=np.int32)
    labels=np.empty(S,dtype=np.int16)
    for si,key in enumerate(keys):
        rec=session_records[key]
        labels[si]=iidx[rec["id"]]
        for c in rec["cells"]:
            counts[si,cidx[c]]+=1
    return {"keys":keys,"cells":cells,"individuals":individuals,"counts":counts,"labels":labels}

def eval_horizontal(A,labels):
    counts=A["counts"];S,C=counts.shape
    ids=A["individuals"];L=len(ids)
    alpha=0.5
    sess_probs=(counts+alpha)/(counts.sum(axis=1,keepdims=True)+alpha*C)
    group_counts=np.zeros((L,C),dtype=np.int64)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
    group_probs=(group_counts+alpha)/(group_counts.sum(axis=1,keepdims=True)+alpha*C)

    rows=[]
    idx=np.arange(S)
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        other_labs=np.array([x for x in range(L) if x!=lab],dtype=int)
        if len(self_sel)==0 or len(other_labs)==0:
            continue
        ps=sess_probs[self_sel].mean(axis=0)
        po=group_probs[other_labs].mean(axis=0)
        n=int(counts[t].sum())
        if n<50:
            continue
        score=float(np.sum(counts[t]*(np.log(ps)-np.log(po)))/n)
        rows.append({"session_index":t,"label":lab,"score":score,"events":n})

    per={}
    for lab in sorted({r["label"] for r in rows}):
        vals=[r["score"] for r in rows if r["label"]==lab]
        per[lab]=float(np.mean(vals))
    source=float(np.mean(list(per.values()))) if per else None
    return source,per,rows

def tail_summary(values,obs):
    x=np.asarray(values,dtype=float)
    sd=float(x.std(ddof=1))
    return {
        "n":int(x.size),
        "mean":float(x.mean()),
        "sd":sd,
        "q025":float(np.quantile(x,0.025)),
        "q50":float(np.quantile(x,0.5)),
        "q975":float(np.quantile(x,0.975)),
        "observed":float(obs),
        "observed_minus_null_mean":float(obs-x.mean()),
        "null_standardized_deviation":float((obs-x.mean())/sd) if sd>0 else None,
        "p_null_ge_observed":float((1+np.sum(x>=obs))/(x.size+1)),
        "p_null_le_observed":float((1+np.sum(x<=obs))/(x.size+1))
    }

def main():
    c=json.loads(CONTRACT.read_text())
    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN missing; do not use unauthenticated fallback")

    raw=fetch(int(c["source"]["file_id"]),token)
    sha=hashlib.sha256(raw).hexdigest()

    # Header-only vertical verification.
    sheet=c["source"]["sheet_name"]\n    header=pd.read_excel(io.BytesIO(raw),sheet_name=sheet,nrows=0,engine="openpyxl")
    required=c["outcome_blind_allowed_fields"]
    vertical=c["vertical_header_only"]
    missing=[x for x in required+[vertical] if x not in header.columns]
    if missing:
        raise RuntimeError(f"missing frozen fields: {missing}")

    # Numeric altitude is never loaded.
    df=pd.read_excel(io.BytesIO(raw),sheet_name=sheet,usecols=required,dtype=str,engine="openpyxl")
    if vertical in df.columns:
        raise RuntimeError("vertical field unexpectedly loaded")

    mask=pd.Series(True,index=df.index)
    for col in required:
        mask &= present(df[col])
    d=df.loc[mask,required].copy()
    d["id"]=d["Tag ID"].astype(str).str.strip()
    d["t"]=pd.to_datetime(d["Fix Date-Time (UTC-5)"],errors="coerce",format="mixed")
    d["lon"]=pd.to_numeric(d["Longitude"],errors="coerce")
    d["lat"]=pd.to_numeric(d["Latitude"],errors="coerce")
    bad=d["t"].isna()|d["lon"].isna()|d["lat"].isna()
    if bad.any():
        raise RuntimeError(f"nonvertical parse failures: {int(bad.sum())}")
    d["session_date"]=d["t"].dt.date.astype(str)

    medlon=float(d["lon"].median());medlat=float(d["lat"].median())
    epsg=utm_epsg(medlon,medlat)
    transformer=Transformer.from_crs("EPSG:4326",f"EPSG:{epsg}",always_xy=True)
    east,north=transformer.transform(d["lon"].to_numpy(dtype=float),d["lat"].to_numpy(dtype=float))
    d["easting"]=east;d["northing"]=north
    d["cell_x"]=np.floor(d["easting"]/5000.0).astype(int)
    d["cell_y"]=np.floor(d["northing"]/5000.0).astype(int)
    d["cell"]=list(zip(d["cell_x"],d["cell_y"]))

    # Frozen >=50 session gate.
    counts=(
        d.groupby(["id","session_date"],sort=True)
        .size().rename("n").reset_index()
    )
    qual=counts[counts["n"]>=50].copy()
    repeat_ids=[]
    qualifying_sessions={}
    for iid in sorted(d["id"].unique()):
        q=qual[qual["id"]==iid]
        if len(q)>=2:
            repeat_ids.append(iid)
            qualifying_sessions[iid]=[
                {"session_date":str(x.session_date),"nonvertical_valid_fixes":int(x.n)}
                for x in q.itertuples(index=False)
            ]

    if not repeat_ids:
        payload={
            "schema_version":1,
            "study_id":c["study_id"],
            "numeric_altitude_values_read":False,
            "raw_sha256":sha,
            "raw_size_bytes":len(raw),
            "sheet_name":sheet,
            "rows_nonvertical_valid":int(len(d)),
            "unique_ids":sorted(d["id"].unique()),
            "unique_id_count":int(d["id"].nunique()),
            "projection_epsg":epsg,
            "horizontal_grid_m":5000,
            "qualified_sessions_ge50":int(len(qual)),
            "repeat_eligible_ids":[],
            "repeat_eligible_id_count":0,
            "horizontal_individuality":{"status":"NOT_EVALUABLE_UNDER_FROZEN_SESSION_GATE"},
            "vertical_evaluable_ids":[],
            "vertical_evaluable_id_count":0,
            "vertical_gate_pass":False,
            "decision":"STRUCTURAL_FAIL"
        }
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
        receipt={
            "schema_version":1,
            "study_id":"batter-leptonycteris-altitude-opening-receipt-v1",
            "status":"STOP",
            "raw_sha256":sha,
            "sheet_name":sheet,
            "projection_epsg":epsg,
            "horizontal_grid_m":5000,
            "minimum_session_fixes":50,
            "minimum_supported_target_events":50,
            "numeric_altitude_values_read":False,
            "reason":"zero individuals have at least two >=50-fix sessions under the frozen source rule",
            "next_step":"STOP; do not lower the session threshold or open Altitude."
        }
        RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
        OUT_MD.write_text(
            "# Leptonycteris comparative-source preflight v1\\n\\n"
            "**STRUCTURAL FAIL BEFORE ALTITUDE. Numeric Altitude values were not read.**\\n\\n"
            f"- raw SHA256: \`{sha}\`\\n"
            f"- GPS sheet: **{sheet}**\\n"
            f"- nonvertical-valid rows: **{len(d)}**\\n"
            f"- unique Tag IDs: **{d['id'].nunique()}**\\n"
            f"- >=50-fix sessions: **{len(qual)}**\\n"
            "- repeat-eligible IDs (>=2 such sessions): **0**\\n"
            "- horizontal individuality: **NOT EVALUABLE under frozen session gate**\\n"
            "- vertical gate: **FAIL / Altitude remains unopened**\\n\\n"
            "Do not lower the >=50-fix session rule as rescue.\\n",
            encoding="utf-8"
        )
        print(json.dumps({
            "raw_sha256":sha,
            "unique_ids":int(d["id"].nunique()),
            "projection_epsg":epsg,
            "repeat_eligible_n":0,
            "horizontal_status":"NOT_EVALUABLE_UNDER_FROZEN_SESSION_GATE",
            "vertical_gate_pass":False,
            "decision":"STRUCTURAL_FAIL"
        },sort_keys=True))
        return 0

    keyset={(iid,x["session_date"]) for iid,ss in qualifying_sessions.items() for x in ss}
    keep=[(iid,sd) in keyset for iid,sd in zip(d["id"],d["session_date"])]
    qd=d.loc[keep].copy()

    session_records={}
    sessions_by_ind=defaultdict(list)
    all_keys=[]
    for (iid,sd),g in qd.groupby(["id","session_date"],sort=True):
        key=(iid,sd)
        rec={
            "id":iid,
            "session_date":sd,
            "event_count":int(len(g)),
            "cells":list(g["cell"]),
            "cell_set":set(g["cell"])
        }
        session_records[key]=rec
        sessions_by_ind[iid].append(key)
        all_keys.append(key)
    cell_universe=set().union(*(r["cell_set"] for r in session_records.values()))

    # Prospective horizontal individuality opened before altitude.
    A=horizontal_arrays(session_records,cell_universe)
    obs,per,rows=eval_horizontal(A,A["labels"])
    if obs is None:
        raise RuntimeError("horizontal identity statistic unevaluable")
    B=int(c["horizontal_individuality"]["B"]);seed=int(c["horizontal_individuality"]["seed"])
    rng=np.random.default_rng(seed)
    null=[]
    invalid=0
    for _ in range(B):
        labels=rng.permutation(A["labels"])
        val,_,_=eval_horizontal(A,labels)
        if val is None:
            invalid+=1
        else:
            null.append(float(val))
    if not null:
        raise RuntimeError("no valid horizontal null replicates")
    hcal=tail_summary(null,obs)

    # Exact vertical common-support preflight, still without altitude.
    target_support=[]
    evaluable_ids=defaultdict(list)
    for key,rec in sorted(session_records.items()):
        iid,sd=key
        self_keys=[x for x in sessions_by_ind[iid] if x!=key]
        other_keys=[x for x in all_keys if x[0]!=iid]
        if not self_keys or not other_keys:
            supported=0
        else:
            self_support=set().union(*(session_records[x]["cell_set"] for x in self_keys))
            other_support=set().union(*(session_records[x]["cell_set"] for x in other_keys))
            supported=sum(cel in self_support and cel in other_support for cel in rec["cells"])
        ok=supported>=50
        target_support.append({
            "id":iid,"session_date":sd,
            "target_events":rec["event_count"],
            "self_training_sessions":len(self_keys),
            "other_training_sessions":len(other_keys),
            "supported_events":int(supported),
            "support_fraction":float(supported/rec["event_count"]),
            "evaluable":bool(ok)
        })
        if ok:
            evaluable_ids[iid].append({
                "session_date":sd,
                "target_events":rec["event_count"],
                "supported_events":int(supported)
            })

    eval_ids=sorted(evaluable_ids)
    gate=len(eval_ids)>=int(c["vertical_preflight"]["minimum_estimator_evaluable_individuals"])
    decision="STRUCTURAL_PASS_ALTITUDE_STILL_UNOPENED" if gate else "STRUCTURAL_FAIL"

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_altitude_values_read":False,
        "raw_sha256":sha,
        "raw_size_bytes":len(raw),
        "rows_nonvertical_valid":int(len(d)),
        "unique_ids":sorted(d["id"].unique()),
        "unique_id_count":int(d["id"].nunique()),
        "median_lon":medlon,"median_lat":medlat,
        "projection_epsg":epsg,
        "horizontal_grid_m":5000,
        "cell_universe_size":len(cell_universe),
        "qualified_sessions_ge50":int(len(qual)),
        "repeat_eligible_ids":repeat_ids,
        "repeat_eligible_id_count":len(repeat_ids),
        "training_universe_ge50_sessions":qualifying_sessions,
        "horizontal_individuality":{
            "observed":float(obs),
            "eligible_individuals":len(per),
            "individual_scores":{A["individuals"][lab]:float(v) for lab,v in per.items()},
            "B":B,"seed":seed,
            "valid_null_replicates":len(null),
            "invalid_null_replicates":invalid,
            "calibration":hcal
        },
        "vertical_target_support":target_support,
        "vertical_evaluable_ids":eval_ids,
        "vertical_evaluable_id_count":len(eval_ids),
        "vertical_gate_pass":bool(gate),
        "decision":decision
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    receipt={
        "schema_version":1,
        "study_id":"batter-leptonycteris-altitude-opening-receipt-v1",
        "status":"ALTITUDE_MAY_OPEN" if gate else "STOP",
        "raw_sha256":sha,
        "projection_epsg":epsg,
        "horizontal_grid_m":5000,
        "cell_universe":[list(x) for x in sorted(cell_universe)],
        "repeat_eligible_ids":repeat_ids,
        "training_universe_ge50_sessions":qualifying_sessions,
        "horizontal_individuality":payload["horizontal_individuality"],
        "vertical_evaluable_ids":eval_ids,
        "frozen_vertical_target_sessions":{
            iid:evaluable_ids[iid] for iid in eval_ids
        },
        "minimum_session_fixes":50,
        "minimum_supported_target_events":50,
        "source_contract_sha256":hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "numeric_altitude_values_read":False,
        "next_step":(
            "Commit this receipt unchanged, then and only then open numeric Altitude under the frozen vertical primary."
            if gate else
            "STOP; do not lower source structural thresholds."
        )
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Leptonycteris comparative-source preflight v1","",
        "**Numeric Altitude values were not read.**","",
        f"- raw SHA256: `{sha}`",
        f"- nonvertical-valid rows: **{len(d)}**",
        f"- unique Tag IDs: **{d['id'].nunique()}**",
        f"- projection: **EPSG:{epsg}**",
        f"- 5-km cells: **{len(cell_universe)}**",
        f"- >=50-fix sessions: **{len(qual)}**",
        f"- repeat-eligible IDs: **{len(repeat_ids)}**",
        "",
        "## Horizontal individuality (opened before altitude)","",
        f"- observed gain: **{obs:+.5f}**",
        f"- null mean: **{hcal['mean']:+.5f}**",
        f"- calibrated excess: **{hcal['observed_minus_null_mean']:+.5f}**",
        f"- p(null >= observed): **{hcal['p_null_ge_observed']:.4f}**",
        f"- null-standardized deviation: **{hcal['null_standardized_deviation']:+.3f}**","",
        "## Vertical structural gate","",
        f"- estimator-evaluable IDs: **{len(eval_ids)}** — {', '.join(eval_ids)}",
        f"- gate: **{'PASS' if gate else 'FAIL'}**",
        f"- Altitude may open: **{gate}**","",
        "The public source's ~1-km roost-neighbourhood exclusion remains a fixed source limitation.",""
    ]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "raw_sha256":sha,
        "unique_ids":int(d["id"].nunique()),
        "projection_epsg":epsg,
        "repeat_eligible_n":len(repeat_ids),
        "horizontal_observed":obs,
        "horizontal_calibrated_excess":hcal["observed_minus_null_mean"],
        "horizontal_p_upper":hcal["p_null_ge_observed"],
        "vertical_evaluable_n":len(eval_ids),
        "vertical_gate_pass":gate,
        "decision":decision
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
