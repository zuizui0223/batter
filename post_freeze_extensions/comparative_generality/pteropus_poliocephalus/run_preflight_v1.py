#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/source_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/PREFLIGHT_RESULT_V1.md"
RECEIPT=ROOT/"post_freeze_extensions/comparative_generality/pteropus_poliocephalus/height_opening_receipt_v1.json"
UA={"User-Agent":"batter-pteropus-poliocephalus-source-v1/1.0"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def parse_boolish(v):
    s=str(v).strip().lower()
    if s in {"true","t","1","yes","y"}: return True
    if s in {"false","f","0","no","n"}: return False
    return None

def utm_epsg(lon,lat):
    z=int(math.floor((lon+180)/6)+1); z=max(1,min(60,z))
    return 32600+z if lat>=0 else 32700+z

def eval_horizontal(counts,labels):
    counts=np.asarray(counts,dtype=np.int64)
    labels=np.asarray(labels,dtype=int)
    S,C=counts.shape
    L=int(labels.max())+1 if len(labels) else 0
    alpha=.5
    sess=(counts+alpha)/(counts.sum(1,keepdims=True)+alpha*C)
    gcounts=np.zeros((L,C),dtype=np.int64)
    for lab in range(L):
        ix=np.flatnonzero(labels==lab)
        if len(ix): gcounts[lab]=counts[ix].sum(0)
    gprob=(gcounts+alpha)/(gcounts.sum(1,keepdims=True)+alpha*C)
    vals=defaultdict(list); rows=[]; idx=np.arange(S)
    for t in range(S):
        lab=int(labels[t]); self_ix=np.flatnonzero((labels==lab)&(idx!=t))
        others=np.array([x for x in range(L) if x!=lab],dtype=int)
        n=int(counts[t].sum())
        if not len(self_ix) or not len(others) or n<50: continue
        ps=sess[self_ix].mean(0); po=gprob[others].mean(0)
        score=float(np.sum(counts[t]*(np.log(ps)-np.log(po)))/n)
        vals[lab].append(score); rows.append((t,lab,n,score))
    if not vals: return None,{},rows
    per={k:float(np.mean(v)) for k,v in vals.items()}
    return float(np.mean(list(per.values()))),per,rows

def tail(null,obs):
    x=np.asarray(null,dtype=float); sd=float(x.std(ddof=1))
    return {
      "n":int(len(x)),"mean":float(x.mean()),"sd":sd,
      "q025":float(np.quantile(x,.025)),"q50":float(np.quantile(x,.5)),"q975":float(np.quantile(x,.975)),
      "observed":float(obs),"observed_minus_null_mean":float(obs-x.mean()),
      "null_standardized_deviation":float((obs-x.mean())/sd) if sd>0 else None,
      "p_null_ge_observed":float((1+np.sum(x>=obs))/(len(x)+1)),
      "p_null_le_observed":float((1+np.sum(x<=obs))/(len(x)+1))
    }

def main():
    c=json.loads(CONTRACT.read_text())
    r=requests.get(c["source"]["event_url"],headers=UA,timeout=300)
    r.raise_for_status(); raw=r.content; sha=hashlib.sha256(raw).hexdigest()

    hdr=pd.read_csv(io.BytesIO(raw),nrows=0)
    req=c["outcome_blind_rows"]["required_presence"]
    extra=["visible","algorithm-marked-outlier"]
    cols=[x for x in req+extra if x in hdr.columns]
    missing=[x for x in req if x not in hdr.columns]
    if missing: raise RuntimeError(f"missing frozen fields: {missing}")
    df=pd.read_csv(io.BytesIO(raw),dtype=str,usecols=cols,low_memory=False)

    mask=pd.Series(True,index=df.index)
    for col in req: mask &= present(df[col])
    d=df.loc[mask].copy()

    if "visible" in d.columns:
        keep=[]
        for x in d["visible"]:
            b=parse_boolish(x); keep.append(True if b is None else b)
        d=d.loc[keep].copy()
    if "algorithm-marked-outlier" in d.columns:
        keep=[]
        for x in d["algorithm-marked-outlier"]:
            b=parse_boolish(x); keep.append(True if b is None else (not b))
        d=d.loc[keep].copy()

    d["iid"]=d["individual-local-identifier"].astype(str).str.strip()
    d["t"]=pd.to_datetime(d["timestamp"],errors="coerce",utc=True,format="mixed")
    d["lon"]=pd.to_numeric(d["location-long"],errors="coerce")
    d["lat"]=pd.to_numeric(d["location-lat"],errors="coerce")
    bad=d["t"].isna()|d["lon"].isna()|d["lat"].isna()
    d=d.loc[~bad].copy()
    if d.empty: raise RuntimeError("no nonvertical-valid rows")

    epsg=utm_epsg(float(d["lon"].median()),float(d["lat"].median()))
    tr=Transformer.from_crs("EPSG:4326",f"EPSG:{epsg}",always_xy=True)
    e,n=tr.transform(d["lon"].to_numpy(dtype=float),d["lat"].to_numpy(dtype=float))
    d["cx"]=np.floor(np.asarray(e)/5000).astype(int); d["cy"]=np.floor(np.asarray(n)/5000).astype(int)
    d["cell"]=list(zip(d["cx"],d["cy"]))

    # Pre-existing frozen Movebank session rule: split at gap >4h.
    d=d.sort_values(["iid","t"]).copy()
    session_id=[]
    for iid,g in d.groupby("iid",sort=False):
        prev=None; k=0
        for t in g["t"]:
            if prev is not None and (t-prev)>pd.Timedelta(hours=4): k+=1
            session_id.append((g.index[len(session_id)-sum(len(x) for _,x in [])] if False else None))
            prev=t
    # Assign safely by group indices.
    d["session_num"]=-1
    for iid,g in d.groupby("iid",sort=True):
        prev=None;k=0
        vals=[]
        for t in g["t"]:
            if prev is not None and (t-prev)>pd.Timedelta(hours=4): k+=1
            vals.append(k);prev=t
        d.loc[g.index,"session_num"]=vals
    d["session_key"]=d["iid"]+"::"+d["session_num"].astype(int).astype(str)

    scount=d.groupby(["iid","session_key"],sort=True).size().rename("n").reset_index()
    qual=scount[scount["n"]>=50].copy()
    repeat=[]; train={}
    for iid in sorted(d["iid"].unique()):
        q=qual[qual["iid"]==iid]
        if len(q)>=2:
            repeat.append(iid)
            train[iid]=[{"session":str(x.session_key),"events":int(x.n)} for x in q.itertuples(index=False)]

    keyset={x["session"] for rows in train.values() for x in rows}
    qd=d[d["session_key"].isin(keyset)].copy()

    sessions={}; by_iid=defaultdict(list)
    for (iid,sid),g in qd.groupby(["iid","session_key"],sort=True):
        cells=list(g["cell"]); key=str(sid)
        sessions[key]={"iid":iid,"session":key,"cells":cells,"cell_set":set(cells),"n":len(cells)}
        by_iid[iid].append(key)

    horizontal={"status":"NOT_EVALUABLE_UNDER_FROZEN_SESSION_GATE"}
    cell_universe=set()
    if sessions:
        cell_universe=set().union(*(x["cell_set"] for x in sessions.values()))
    if len(repeat)>=2 and sessions:
        cells=sorted(cell_universe); cidx={x:i for i,x in enumerate(cells)}
        skeys=sorted(sessions); iids=sorted(repeat); iidx={x:i for i,x in enumerate(iids)}
        counts=np.zeros((len(skeys),len(cells)),dtype=np.int32); labels=np.zeros(len(skeys),dtype=np.int16)
        for si,sid in enumerate(skeys):
            labels[si]=iidx[sessions[sid]["iid"]]
            for cel in sessions[sid]["cells"]: counts[si,cidx[cel]]+=1
        obs,per,_=eval_horizontal(counts,labels)
        if obs is not None:
            B=int(c["horizontal_individuality"]["B"]); rng=np.random.default_rng(int(c["horizontal_individuality"]["seed"]))
            null=[]; invalid=0
            for _ in range(B):
                v,_,_=eval_horizontal(counts,rng.permutation(labels))
                if v is None: invalid+=1
                else: null.append(float(v))
            horizontal={
              "status":"EVALUATED","observed":float(obs),"eligible_individuals":len(per),
              "individual_scores":{iids[int(k)]:float(v) for k,v in per.items()},
              "B":B,"seed":int(c["horizontal_individuality"]["seed"]),
              "valid_null_replicates":len(null),"invalid_null_replicates":invalid,
              "calibration":tail(null,obs)
            }

    targets=[]; eval_by_id=defaultdict(list); allkeys=list(sessions)
    for sid,sr in sorted(sessions.items()):
        iid=sr["iid"]; selfkeys=[x for x in by_iid[iid] if x!=sid]; otherkeys=[x for x in allkeys if sessions[x]["iid"]!=iid]
        supported=0
        if selfkeys and otherkeys:
            ss=set().union(*(sessions[x]["cell_set"] for x in selfkeys))
            oo=set().union(*(sessions[x]["cell_set"] for x in otherkeys))
            supported=sum(cel in ss and cel in oo for cel in sr["cells"])
        ok=supported>=50
        row={"iid":iid,"session":sid,"target_events":int(sr["n"]),"supported_events":int(supported),"evaluable":bool(ok)}
        targets.append(row)
        if ok: eval_by_id[iid].append({k:row[k] for k in ["session","target_events","supported_events"]})
    eval_ids=sorted(eval_by_id)
    gate=len(eval_ids)>=5
    decision="STRUCTURAL_PASS_HEIGHT_STILL_UNOPENED" if gate else "STRUCTURAL_STOP"

    payload={
      "schema_version":1,"study_id":c["study_id"],"numeric_height_values_parsed":False,
      "raw_sha256":sha,"rows_file":int(len(df)),"rows_nonvertical_valid":int(len(d)),
      "unique_individuals":int(d["iid"].nunique()),"projection_epsg":epsg,"horizontal_grid_m":5000,
      "qualified_sessions_ge50":int(len(qual)),"repeat_eligible_ids":repeat,"repeat_eligible_n":len(repeat),
      "training_sessions":train,"cell_universe_size":len(cell_universe),
      "horizontal_individuality":horizontal,"vertical_target_support":targets,
      "vertical_evaluable_ids":eval_ids,"vertical_evaluable_n":len(eval_ids),
      "vertical_gate_pass":bool(gate),"decision":decision
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    receipt={
      "schema_version":1,"study_id":"batter-pteropus-poliocephalus-height-opening-receipt-v1",
      "status":"HEIGHT_MAY_OPEN" if gate else "STOP","raw_sha256":sha,"projection_epsg":epsg,
      "horizontal_grid_m":5000,"cell_universe":[list(x) for x in sorted(cell_universe)],
      "repeat_eligible_ids":repeat,"training_sessions":train,"horizontal_individuality":horizontal,
      "vertical_evaluable_ids":eval_ids,
      "frozen_vertical_target_sessions":{iid:eval_by_id[iid] for iid in eval_ids},
      "source_contract_sha256":hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
      "numeric_height_values_parsed":False,
      "next_step":"Commit receipt unchanged before opening height-above-msl." if gate else "STOP; do not lower gates."
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")

    cal=horizontal.get("calibration",{})
    lines=[
      "# Pteropus poliocephalus nonvertical source preflight v1","",
      "**Numeric height-above-msl values were not parsed or summarized.**","",
      f"- raw SHA256: `{sha}`",f"- nonvertical-valid rows: **{len(d)}**",
      f"- individuals: **{d['iid'].nunique()}**",f"- projection: **EPSG:{epsg}**",
      f"- >=50-event sessions: **{len(qual)}**",f"- repeat-eligible IDs: **{len(repeat)}**","",
      "## Horizontal individuality","",
      f"- status: **{horizontal['status']}**",
    ]
    if cal:
        lines += [f"- calibrated excess: **{cal['observed_minus_null_mean']:+.5f}**",f"- p_upper: **{cal['p_null_ge_observed']:.4f}**"]
    lines += ["","## Vertical structural gate","",f"- evaluable IDs: **{len(eval_ids)}**",f"- decision: **{decision}**",""]
    OUT_MD.write_text("\n".join(lines))

    print(json.dumps({
      "decision":decision,"individuals":int(d["iid"].nunique()),"qualified_sessions":int(len(qual)),
      "repeat_n":len(repeat),"horizontal_status":horizontal["status"],
      "horizontal_excess":cal.get("observed_minus_null_mean"),"horizontal_p":cal.get("p_null_ge_observed"),
      "vertical_evaluable_n":len(eval_ids),"height_parsed":False
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
