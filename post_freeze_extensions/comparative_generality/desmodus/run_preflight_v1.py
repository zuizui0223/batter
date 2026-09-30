#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math, os
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
from remotezip import RemoteZip

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/desmodus/source_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/desmodus/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/desmodus/PREFLIGHT_RESULT_V1.md"
RECEIPT=ROOT/"post_freeze_extensions/comparative_generality/desmodus/altitude_opening_receipt_v1.json"

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def utm_epsg(lon,lat):
    zone=int(math.floor((lon+180.0)/6.0)+1)
    zone=max(1,min(60,zone))
    return 32600+zone if lat>=0 else 32700+zone

def tail_summary(values,obs):
    x=np.asarray(values,dtype=float)
    sd=float(x.std(ddof=1))
    return {
        "n":int(x.size),"mean":float(x.mean()),"sd":sd,
        "q025":float(np.quantile(x,.025)),"q50":float(np.quantile(x,.5)),
        "q975":float(np.quantile(x,.975)),"observed":float(obs),
        "observed_minus_null_mean":float(obs-x.mean()),
        "null_standardized_deviation":float((obs-x.mean())/sd) if sd>0 else None,
        "p_null_ge_observed":float((1+np.sum(x>=obs))/(x.size+1)),
        "p_null_le_observed":float((1+np.sum(x<=obs))/(x.size+1))
    }

def extract_inner(c,token):
    url=f"https://datadryad.org/api/v2/files/{c['source']['dryad_archive_file_id']}/download"
    rz=RemoteZip(url,headers={
        "Authorization":f"Bearer {token}",
        "User-Agent":"batter-desmodus-comparative-preflight-v1/1.0"
    })
    with rz.open(c["source"]["inner_path"]) as f:
        raw=f.read()
    rz.close()
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=c["source"]["inner_sha256"]:
        raise RuntimeError(f"inner XLSX SHA mismatch {sha}")
    return raw,sha

def make_harray(records):
    keys=sorted(records)
    cells=sorted(set().union(*(records[k]["cell_set"] for k in keys)))
    ids=sorted({records[k]["id"] for k in keys})
    cidx={c:i for i,c in enumerate(cells)}
    iidx={x:i for i,x in enumerate(ids)}
    counts=np.zeros((len(keys),len(cells)),dtype=np.int32)
    labels=np.empty(len(keys),dtype=np.int16)
    for si,k in enumerate(keys):
        r=records[k];labels[si]=iidx[r["id"]]
        for cell in r["cells"]:
            counts[si,cidx[cell]]+=1
    return {"keys":keys,"cells":cells,"ids":ids,"counts":counts,"labels":labels}

def eval_hcohort(A,labels):
    counts=A["counts"];S,C=counts.shape;L=len(A["ids"]);alpha=.5
    sess=(counts+alpha)/(counts.sum(axis=1,keepdims=True)+alpha*C)
    group=np.zeros((L,C),dtype=np.int64)
    for lab in range(L):
        ix=np.flatnonzero(labels==lab)
        if len(ix):group[lab]=counts[ix].sum(axis=0)
    gp=(group+alpha)/(group.sum(axis=1,keepdims=True)+alpha*C)
    rows=[];idx=np.arange(S)
    for t in range(S):
        lab=int(labels[t]);self_ix=np.flatnonzero((labels==lab)&(idx!=t))
        other=np.array([x for x in range(L) if x!=lab],dtype=int)
        if len(self_ix)==0 or len(other)==0:continue
        ps=sess[self_ix].mean(axis=0);po=gp[other].mean(axis=0)
        n=int(counts[t].sum())
        if n<50:continue
        score=float(np.sum(counts[t]*(np.log(ps)-np.log(po)))/n)
        rows.append({"target":t,"label":lab,"score":score})
    per={}
    for lab in sorted({x["label"] for x in rows}):
        per[lab]=float(np.mean([x["score"] for x in rows if x["label"]==lab]))
    return per,rows

def eval_hsource(arrays,labels_by_local):
    vals=[];details={}
    for local,A in arrays.items():
        per,rows=eval_hcohort(A,labels_by_local[local])
        details[local]={"individual_scores":per,"session_results":rows}
        vals.extend(per.values())
    return (float(np.mean(vals)) if vals else None),details,len(vals)

def main():
    c=json.loads(CONTRACT.read_text())
    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:raise RuntimeError("DRYAD_API_TOKEN missing")
    raw,sha=extract_inner(c,token)

    f=c["fields"]
    cols=[f["cohort"],f["individual"],f["session_date"],f["timestamp"],f["longitude"],f["latitude"],f["altitude"]]
    df=pd.read_excel(io.BytesIO(raw),sheet_name=c["source"]["sheet"],usecols=cols,dtype=str,engine="openpyxl")

    # ALTITUDE is used only for source-coded missingness. No numeric altitude conversion occurs here.
    req=[f["cohort"],f["individual"],f["session_date"],f["timestamp"],f["longitude"],f["latitude"]]
    mask=pd.Series(True,index=df.index)
    for col in req:mask &= present(df[col])
    alt=df[f["altitude"]].fillna("").astype(str).str.strip()
    mask &= ~alt.isin(set(c["row_qualification"]["altitude_missing_codes"]))
    d=df.loc[mask,cols].copy()
    d["local"]=d[f["cohort"]].astype(str).str.strip()
    d["id"]=d[f["individual"]].astype(str).str.strip()
    d["date_parsed"]=pd.to_datetime(d[f["session_date"]],errors="coerce",format="mixed")
    d["lon"]=pd.to_numeric(d[f["longitude"]],errors="coerce")
    d["lat"]=pd.to_numeric(d[f["latitude"]],errors="coerce")
    bad=d["date_parsed"].isna()|d["lon"].isna()|d["lat"].isna()|(d["lon"]==0)|(d["lat"]==0)
    d=d.loc[~bad].copy()
    d["session_date"]=d["date_parsed"].dt.date.astype(str)
    # Drop raw altitude immediately after missingness use.
    d=d.drop(columns=[f["altitude"]])

    # >=50 session structure.
    sc=(d.groupby(["local","id","session_date"],sort=True).size().rename("n").reset_index())
    qual=sc[sc["n"]>=50].copy()
    repeat_by_local={}
    qual_sessions={}
    for local in sorted(d["local"].unique()):
        repeat=[];byid={}
        for iid in sorted(d.loc[d["local"]==local,"id"].unique()):
            q=qual[(qual["local"]==local)&(qual["id"]==iid)]
            if len(q)>=2:
                repeat.append(iid)
                byid[iid]=[{"session_date":str(x.session_date),"fixes":int(x.n)} for x in q.itertuples(index=False)]
        repeat_by_local[local]=repeat
        qual_sessions[local]=byid
    admitted=[x for x,v in repeat_by_local.items() if len(v)>=int(c["cohort_admission"]["minimum_repeat_individuals"])]

    # If no admitted local, fail closed before any horizontal/vertical effect.
    if not admitted:
        payload={
            "schema_version":1,"study_id":c["study_id"],"numeric_altitude_values_parsed":False,
            "inner_sha256":sha,"rows_presence_qualified":int(len(d)),
            "locals":sorted(d["local"].unique()),"qualified_sessions_ge50":int(len(qual)),
            "repeat_ids_by_local":repeat_by_local,"admitted_locals":[],
            "horizontal_individuality":{"status":"NOT_EVALUABLE_NO_ADMITTED_LOCAL"},
            "vertical_evaluable_ids":[],"vertical_gate_pass":False,"decision":"STRUCTURAL_FAIL"
        }
        OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
        receipt={"schema_version":1,"status":"STOP","inner_sha256":sha,"numeric_altitude_values_parsed":False,
                 "reason":"no Local has >=3 repeat individuals under frozen >=50-fix-session rule",
                 "next_step":"STOP; do not lower gates or open numeric ALTITUDE."}
        RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
        OUT_MD.write_text("# Desmodus comparative-source preflight v1\n\n**STRUCTURAL FAIL BEFORE ALTITUDE.**\n\nNo Local has >=3 repeat individuals under the frozen >=50-fix-session rule. Numeric ALTITUDE was not parsed.\n")
        print(json.dumps({"decision":"STRUCTURAL_FAIL","admitted_locals":[],"numeric_altitude_values_parsed":False},sort_keys=True))
        return 0

    # Deterministic projection per admitted Local.
    epsg_by_local={}
    for local in admitted:
        g=d[d["local"]==local]
        epsg=utm_epsg(float(g["lon"].median()),float(g["lat"].median()))
        epsg_by_local[local]=epsg
        tr=Transformer.from_crs("EPSG:4326",f"EPSG:{epsg}",always_xy=True)
        ix=d["local"]==local
        e,n=tr.transform(d.loc[ix,"lon"].to_numpy(dtype=float),d.loc[ix,"lat"].to_numpy(dtype=float))
        d.loc[ix,"easting"]=e;d.loc[ix,"northing"]=n
    d=d[d["local"].isin(admitted)].copy()
    d["cell_x"]=np.floor(d["easting"].astype(float)/5000).astype(int)
    d["cell_y"]=np.floor(d["northing"].astype(float)/5000).astype(int)
    d["cell"]=list(zip(d["cell_x"],d["cell_y"]))

    keyset={(loc,iid,x["session_date"]) for loc,b in qual_sessions.items() if loc in admitted for iid,ss in b.items() for x in ss}
    keep=[(loc,iid,sd) in keyset for loc,iid,sd in zip(d["local"],d["id"],d["session_date"])]
    qd=d.loc[keep].copy()

    records_by_local=defaultdict(dict);sessions_by_ind=defaultdict(list);keys_by_local=defaultdict(list)
    for (loc,iid,sd),g in qd.groupby(["local","id","session_date"],sort=True):
        key=(loc,iid,sd);cells=list(g["cell"])
        records_by_local[loc][key]={"id":iid,"session_date":sd,"cells":cells,"cell_set":set(cells),"n":len(cells)}
        sessions_by_ind[(loc,iid)].append(key);keys_by_local[loc].append(key)

    # Horizontal individuality.
    arrays={loc:make_harray(records_by_local[loc]) for loc in admitted}
    obs_labels={loc:arrays[loc]["labels"].copy() for loc in admitted}
    hobs,hdetails,hn=eval_hsource(arrays,obs_labels)
    if hobs is None:raise RuntimeError("horizontal metric unexpectedly unevaluable after admitted-local gate")
    B=int(c["horizontal_individuality"]["B"]);seed=int(c["horizontal_individuality"]["seed"])
    rng=np.random.default_rng(seed);null=[]
    for _ in range(B):
        labs={loc:rng.permutation(arrays[loc]["labels"]) for loc in admitted}
        val,_,_=eval_hsource(arrays,labs)
        if val is not None:null.append(float(val))
    hcal=tail_summary(null,hobs)

    # Vertical common-support preflight.
    target_rows=[];eval_ids=defaultdict(list)
    for loc in admitted:
        for key,rec in sorted(records_by_local[loc].items()):
            _,iid,sd=key
            self_keys=[x for x in sessions_by_ind[(loc,iid)] if x!=key]
            other_keys=[x for x in keys_by_local[loc] if x[1]!=iid]
            self_support=set().union(*(records_by_local[loc][x]["cell_set"] for x in self_keys)) if self_keys else set()
            other_support=set().union(*(records_by_local[loc][x]["cell_set"] for x in other_keys)) if other_keys else set()
            supported=sum(cell in self_support and cell in other_support for cell in rec["cells"])
            ok=supported>=50
            target_rows.append({"local":loc,"id":iid,"session_date":sd,"target_events":rec["n"],
                                "supported_events":int(supported),"evaluable":bool(ok)})
            if ok:eval_ids[(loc,iid)].append({"session_date":sd,"target_events":rec["n"],"supported_events":int(supported)})

    eval_keys=sorted(eval_ids)
    gate=len(eval_keys)>=int(c["vertical_preflight"]["minimum_estimator_evaluable_individuals_source"])
    decision="STRUCTURAL_PASS_ALTITUDE_STILL_UNOPENED" if gate else "STRUCTURAL_FAIL"

    # JSON-safe horizontal details.
    hdetail_out={}
    for loc,dd in hdetails.items():
        hdetail_out[loc]={
            "individual_scores":{arrays[loc]["ids"][int(k)]:float(v) for k,v in dd["individual_scores"].items()},
            "evaluable_individuals":len(dd["individual_scores"])
        }

    payload={
        "schema_version":1,"study_id":c["study_id"],"numeric_altitude_values_parsed":False,
        "inner_sha256":sha,"rows_presence_qualified":int(len(d)),
        "qualified_sessions_ge50":int(len(qual)),"repeat_ids_by_local":repeat_by_local,
        "admitted_locals":admitted,"projection_epsg_by_local":epsg_by_local,
        "training_universe_ge50_sessions":{loc:qual_sessions[loc] for loc in admitted},
        "horizontal_individuality":{"observed":hobs,"evaluable_individuals":hn,"by_local":hdetail_out,
                                   "B":B,"seed":seed,"calibration":hcal},
        "vertical_target_support":target_rows,
        "vertical_evaluable_individual_keys":[{"local":x[0],"id":x[1]} for x in eval_keys],
        "vertical_evaluable_individual_count":len(eval_keys),
        "vertical_gate_pass":bool(gate),"decision":decision
    }
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    receipt={
        "schema_version":1,"study_id":"batter-desmodus-altitude-opening-receipt-v1",
        "status":"ALTITUDE_MAY_OPEN" if gate else "STOP",
        "inner_sha256":sha,"admitted_locals":admitted,"projection_epsg_by_local":epsg_by_local,
        "horizontal_grid_m":5000,
        "training_universe_ge50_sessions":{loc:qual_sessions[loc] for loc in admitted},
        "horizontal_individuality":payload["horizontal_individuality"],
        "vertical_evaluable_individual_keys":payload["vertical_evaluable_individual_keys"],
        "frozen_vertical_target_sessions":{f"{loc}::{iid}":rows for (loc,iid),rows in sorted(eval_ids.items())},
        "minimum_session_fixes":50,"minimum_supported_target_events":50,
        "source_contract_sha256":hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "numeric_altitude_values_parsed":False,
        "next_step":"Commit receipt unchanged then open numeric ALTITUDE once." if gate else "STOP; no threshold rescue."
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Desmodus comparative-source preflight v1","",
        "**Numeric ALTITUDE magnitudes were not parsed. ALTITUDE was used only for frozen source-coded missingness.**","",
        f"- inner SHA256: `{sha}`",
        f"- admitted Local cohorts: **{admitted}**",
        f"- >=50-fix sessions: **{len(qual)}**","",
        "## Horizontal individuality","",
        f"- observed: **{hobs:+.5f}**",
        f"- null mean: **{hcal['mean']:+.5f}**",
        f"- calibrated excess: **{hcal['observed_minus_null_mean']:+.5f}**",
        f"- p_upper: **{hcal['p_null_ge_observed']:.4f}**",
        f"- evaluable individuals: **{hn}**","",
        "## Vertical gate","",
        f"- estimator-evaluable individuals: **{len(eval_keys)}**",
        f"- gate: **{'PASS' if gate else 'FAIL'}**",
        f"- ALTITUDE may open: **{gate}**",""
    ]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")
    print(json.dumps({"admitted_locals":admitted,"horizontal_observed":hobs,
                      "horizontal_calibrated_excess":hcal["observed_minus_null_mean"],
                      "horizontal_p_upper":hcal["p_null_ge_observed"],
                      "horizontal_n":hn,"vertical_evaluable_n":len(eval_keys),
                      "vertical_gate_pass":gate,"decision":decision},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
