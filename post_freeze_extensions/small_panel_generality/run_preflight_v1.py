#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/small_panel_generality/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/small_panel_generality/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/small_panel_generality/PREFLIGHT_RESULT_V1.md"
RECEIPT=ROOT/"post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
UA={"User-Agent":"batter-small-panel-generality-v1/1.0"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def norm(x):
    return "_".join(str(x).strip().lower().replace("-","_").replace(" ","_").replace(".","_").split("_"))

def boolish(x):
    s=str(x).strip().lower()
    if s in {"true","t","1","yes","y"}: return True
    if s in {"false","f","0","no","n"}: return False
    return None

def utm_epsg(lon,lat):
    z=int(math.floor((lon+180.0)/6.0)+1); z=max(1,min(60,z))
    return 32600+z if lat>=0 else 32700+z

def horizontal_eval(counts,labels):
    counts=np.asarray(counts,dtype=np.int64); labels=np.asarray(labels,dtype=int)
    S,C=counts.shape; L=int(labels.max())+1
    alpha=.5
    sess=(counts+alpha)/(counts.sum(1,keepdims=True)+alpha*C)
    gc=np.zeros((L,C),dtype=np.int64)
    for lab in range(L):
        ix=np.flatnonzero(labels==lab)
        if len(ix): gc[lab]=counts[ix].sum(0)
    gp=(gc+alpha)/(gc.sum(1,keepdims=True)+alpha*C)
    idx=np.arange(S); vals=defaultdict(list)
    for t in range(S):
        lab=int(labels[t]); self_ix=np.flatnonzero((labels==lab)&(idx!=t))
        others=np.array([x for x in range(L) if x!=lab],dtype=int)
        if not len(self_ix) or not len(others): continue
        n=int(counts[t].sum())
        if n<50: continue
        ps=sess[self_ix].mean(0); po=gp[others].mean(0)
        score=float(np.sum(counts[t]*(np.log(ps)-np.log(po)))/n)
        vals[lab].append(score)
    if len(vals)!=L: return None,{}
    per={lab:float(np.mean(v)) for lab,v in vals.items()}
    return float(np.mean(list(per.values()))),per

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

def parse_source(src,c):
    r=requests.get(src["event_url"],headers=UA,timeout=300)
    r.raise_for_status(); raw=r.content; sha=hashlib.sha256(raw).hexdigest()
    if src.get("event_sha256") and sha!=src["event_sha256"]:
        raise RuntimeError(f"{src['source_id']}: source SHA changed")

    header=pd.read_csv(io.BytesIO(raw),nrows=0)
    cmap={norm(x):x for x in header.columns}
    required=["timestamp","location_long","location_lat","individual_local_identifier",norm(src["vertical_field"])]
    missing=[x for x in required if x not in cmap]
    if missing: raise RuntimeError(f"{src['source_id']}: missing fields {missing}")
    use=[cmap[x] for x in required]
    for q in ["visible","algorithm_marked_outlier","manually_marked_outlier","import_marked_outlier"]:
        if q in cmap: use.append(cmap[q])
    use=list(dict.fromkeys(use))
    df=pd.read_csv(io.BytesIO(raw),dtype=str,usecols=use,low_memory=False)

    tcol=cmap["timestamp"]; loncol=cmap["location_long"]; latcol=cmap["location_lat"]
    iidcol=cmap["individual_local_identifier"]; hcol=cmap[norm(src["vertical_field"])]
    mask=present(df[tcol])&present(df[loncol])&present(df[latcol])&present(df[iidcol])&present(df[hcol])
    d=df.loc[mask].copy()

    if "visible" in cmap and cmap["visible"] in d:
        vals=[]
        for x in d[cmap["visible"]]:
            b=boolish(x); vals.append(True if b is None else b)
        d=d.loc[vals].copy()
    for q in ["algorithm_marked_outlier","manually_marked_outlier","import_marked_outlier"]:
        if q in cmap and cmap[q] in d:
            vals=[]
            for x in d[cmap[q]]:
                b=boolish(x); vals.append(True if b is None else (not b))
            d=d.loc[vals].copy()

    d["iid"]=d[iidcol].astype(str).str.strip()
    d["t"]=pd.to_datetime(d[tcol],errors="coerce",utc=True,format="mixed")
    d["lon"]=pd.to_numeric(d[loncol],errors="coerce")
    d["lat"]=pd.to_numeric(d[latcol],errors="coerce")
    bad=d["t"].isna()|d["lon"].isna()|d["lat"].isna()
    d=d.loc[~bad].sort_values(["iid","t"]).copy()

    epsg=utm_epsg(float(d["lon"].median()),float(d["lat"].median()))
    tr=Transformer.from_crs("EPSG:4326",f"EPSG:{epsg}",always_xy=True)
    e,n=tr.transform(d["lon"].to_numpy(dtype=float),d["lat"].to_numpy(dtype=float))
    d["cx"]=np.floor(np.asarray(e)/5000.0).astype(int)
    d["cy"]=np.floor(np.asarray(n)/5000.0).astype(int)
    d["cell"]=list(zip(d["cx"],d["cy"]))

    # Frozen >4h-gap session rule.
    d["sess_num"]=-1
    for iid,g in d.groupby("iid",sort=True):
        vals=[]; k=0; prev=None
        for t in g["t"]:
            if prev is not None and (t-prev)>pd.Timedelta(hours=4): k+=1
            vals.append(k); prev=t
        d.loc[g.index,"sess_num"]=vals
    d["session"]=d["iid"]+"::"+d["sess_num"].astype(int).astype(str)

    sc=d.groupby(["iid","session"],sort=True).size().rename("n").reset_index()
    qual=sc[sc["n"]>=50].copy()
    repeat=[]; train={}
    for iid in sorted(d["iid"].unique()):
        q=qual[qual["iid"]==iid]
        if len(q)>=2:
            repeat.append(iid)
            train[iid]=[{"session":str(x.session),"events":int(x.n)} for x in q.itertuples(index=False)]

    rec={
      "source_id":src["source_id"],"taxon":src["taxon"],"doi":src["doi"],"vertical_field":src["vertical_field"],
      "numeric_vertical_values_parsed":False,"raw_sha256":sha,"rows_file":int(len(df)),
      "rows_presence_qualified_after_filters":int(len(d)),"individuals_with_presence":int(d["iid"].nunique()),
      "projection_epsg":epsg,"qualified_sessions_ge50":int(len(qual)),
      "repeat_eligible_ids":repeat,"repeat_eligible_n":len(repeat)
    }
    if len(repeat)!=4:
        rec.update({"decision":"STRUCTURAL_STOP_REPEAT_COUNT","horizontal_individuality":{"status":"NOT_OPENED"},"vertical_gate_pass":False})
        return rec,None

    keyset={z["session"] for rows in train.values() for z in rows}
    qd=d[d["session"].isin(keyset)].copy()
    sessions={}; by_iid=defaultdict(list)
    for (iid,sid),g in qd.groupby(["iid","session"],sort=True):
        cells=list(g["cell"]); sessions[sid]={"iid":iid,"cells":cells,"cell_set":set(cells),"n":len(cells)}
        by_iid[iid].append(sid)
    cells=sorted(set().union(*(x["cell_set"] for x in sessions.values())))
    cidx={x:i for i,x in enumerate(cells)}
    skeys=sorted(sessions); iids=sorted(repeat); iidx={x:i for i,x in enumerate(iids)}
    counts=np.zeros((len(skeys),len(cells)),dtype=np.int32); labels=np.zeros(len(skeys),dtype=np.int16)
    for si,sid in enumerate(skeys):
        labels[si]=iidx[sessions[sid]["iid"]]
        for cel in sessions[sid]["cells"]: counts[si,cidx[cel]]+=1

    obs,per=horizontal_eval(counts,labels)
    if obs is None: raise RuntimeError(f"{src['source_id']}: horizontal metric unevaluable despite four repeat IDs")
    B=int(c["horizontal_axis"]["B"]); seed=int(c["horizontal_axis"]["seed_by_source"][src["source_id"]])
    rng=np.random.default_rng(seed); null=[]; invalid=0
    for _ in range(B):
        val,_=horizontal_eval(counts,rng.permutation(labels))
        if val is None: invalid+=1
        else: null.append(float(val))
    hcal=tail(null,obs)
    horizontal={
      "status":"EVALUATED","observed":float(obs),"eligible_individuals":len(per),
      "individual_scores":{iids[int(k)]:float(v) for k,v in per.items()},
      "B":B,"seed":seed,"valid_null_replicates":len(null),"invalid_null_replicates":invalid,
      "calibration":hcal
    }

    targets=[]; eval_by=defaultdict(list); allkeys=list(sessions)
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
        if ok: eval_by[iid].append({k:row[k] for k in ["session","target_events","supported_events"]})
    eval_ids=sorted(eval_by); gate=(len(eval_ids)==4)
    rec.update({
      "cell_universe_size":len(cells),"training_sessions":train,"horizontal_individuality":horizontal,
      "vertical_target_support":targets,"vertical_evaluable_ids":eval_ids,"vertical_evaluable_n":len(eval_ids),
      "vertical_gate_pass":gate,"decision":"PASS_TO_VERTICAL" if gate else "STRUCTURAL_STOP_COMMON_SUPPORT"
    })
    receipt=None
    if gate:
        receipt={
          "source_id":src["source_id"],"taxon":src["taxon"],"doi":src["doi"],"vertical_field":src["vertical_field"],
          "vertical_semantics":src["vertical_semantics"],"raw_sha256":sha,"projection_epsg":epsg,
          "horizontal_grid_m":5000,"cell_universe":[list(x) for x in cells],
          "repeat_eligible_ids":repeat,"training_sessions":train,"horizontal_individuality":horizontal,
          "vertical_evaluable_ids":eval_ids,"frozen_vertical_target_sessions":{iid:eval_by[iid] for iid in eval_ids}
        }
    return rec,receipt

def main():
    c=json.loads(CONTRACT.read_text())
    results=[]; receipts={}
    for src in c["closed_source_set"]:
        rec,receipt=parse_source(src,c); results.append(rec)
        if receipt is not None: receipts[src["source_id"]]=receipt
    passing=[x for x in results if x.get("vertical_gate_pass")]
    payload={
      "schema_version":1,"study_id":c["study_id"],"numeric_vertical_values_parsed":False,
      "source_results":results,"passing_source_count":len(passing),
      "passing_sources":[x["source_id"] for x in passing],
      "decision":"SOURCES_PASS_TO_VERTICAL" if passing else "ALL_SOURCES_STRUCTURAL_STOP"
    }
    OUT.parent.mkdir(parents=True,exist_ok=True); OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    receipt={
      "schema_version":1,"study_id":"batter-small-panel-height-opening-receipt-v1",
      "status":"HEIGHT_MAY_OPEN" if receipts else "STOP","sources":receipts,
      "contract_sha256":hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),"numeric_vertical_values_parsed":False,
      "next_step":"Commit unchanged before opening vertical values in passing sources." if receipts else "STOP."
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    lines=["# Small-panel generality preflight v1","","**No numeric vertical value was parsed or summarized.**","",
           "| source | taxon | repeat n | horizontal excess | horiz p | vertical-evaluable n | decision |",
           "|---|---|---:|---:|---:|---:|---|"]
    for x in results:
        cal=x.get("horizontal_individuality",{}).get("calibration",{})
        lines.append(f"| {x['source_id']} | {x['taxon']} | {x['repeat_eligible_n']} | {cal.get('observed_minus_null_mean','—')} | {cal.get('p_null_ge_observed','—')} | {x.get('vertical_evaluable_n',0)} | {x['decision']} |")
    lines += ["",f"**Programme decision: {payload['decision']}**",""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
      "passing_sources":payload["passing_sources"],
      "results":[{
        "source_id":x["source_id"],"taxon":x["taxon"],"repeat_n":x["repeat_eligible_n"],
        "horizontal_excess":x.get("horizontal_individuality",{}).get("calibration",{}).get("observed_minus_null_mean"),
        "horizontal_p":x.get("horizontal_individuality",{}).get("calibration",{}).get("p_null_ge_observed"),
        "vertical_n":x.get("vertical_evaluable_n",0),"decision":x["decision"]
      } for x in results]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
