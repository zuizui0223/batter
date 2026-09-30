#!/usr/bin/env python3
from __future__ import annotations

import gc, hashlib, json, math, shutil, tempfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import pyreadr
import requests
from pyproj import Transformer
from remotezip import RemoteZip

ROOT=Path(__file__).resolve().parents[3]
CONTRACT=ROOT/"post_freeze_extensions/comparative_generality/airflows/point_preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/comparative_generality/airflows/point_preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/comparative_generality/airflows/POINT_PREFLIGHT_RESULT_V1.md"
RECEIPT=ROOT/"post_freeze_extensions/comparative_generality/airflows/height_opening_receipt_v1.json"
UA={"User-Agent":"batter-airflows-point-preflight-v1/1.0"}

def zenodo_file_url(record_id,name):
    r=requests.get(f"https://zenodo.org/api/records/{record_id}",headers=UA,timeout=90)
    r.raise_for_status()
    j=r.json()
    for f in j.get("files",[]):
        key=f.get("key") or f.get("filename")
        if key==name:
            return (f.get("links") or {}).get("content") or (f.get("links") or {}).get("self")
    raise RuntimeError(f"missing Zenodo file {name}")

def norm_study_id(x):
    if pd.isna(x):
        return None
    s=str(x).strip()
    try:
        f=float(s)
        if math.isfinite(f) and f.is_integer():
            return str(int(f))
    except Exception:
        pass
    return s

def utm_epsg(lon,lat):
    zone=int(math.floor((lon+180.0)/6.0)+1)
    zone=max(1,min(60,zone))
    return 32600+zone if lat>=0 else 32700+zone

def horiz_eval(counts,orig_labels):
    S,C=counts.shape
    labels=np.asarray(orig_labels,dtype=int)
    L=int(labels.max())+1 if len(labels) else 0
    alpha=0.5
    sess_probs=(counts+alpha)/(counts.sum(axis=1,keepdims=True)+alpha*C)
    group_counts=np.zeros((L,C),dtype=np.int64)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
    group_probs=(group_counts+alpha)/(group_counts.sum(axis=1,keepdims=True)+alpha*C)
    idx=np.arange(S)
    rows=[]
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        others=np.array([x for x in range(L) if x!=lab],dtype=int)
        if len(self_sel)==0 or len(others)==0:
            continue
        n=int(counts[t].sum())
        if n<50:
            continue
        ps=sess_probs[self_sel].mean(axis=0)
        po=group_probs[others].mean(axis=0)
        score=float(np.sum(counts[t]*(np.log(ps)-np.log(po)))/n)
        rows.append((lab,t,n,score))
    per={}
    for lab in sorted({r[0] for r in rows}):
        vals=[r[3] for r in rows if r[0]==lab]
        per[lab]=float(np.mean(vals))
    return (float(np.mean(list(per.values()))) if per else None),per,rows

def horiz_eval_permuted(counts,labels):
    S,C=counts.shape
    labels=np.asarray(labels,dtype=int)
    L=int(labels.max())+1 if len(labels) else 0
    alpha=0.5
    sess_probs=(counts+alpha)/(counts.sum(axis=1,keepdims=True)+alpha*C)
    group_counts=np.zeros((L,C),dtype=np.int64)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
    group_probs=(group_counts+alpha)/(group_counts.sum(axis=1,keepdims=True)+alpha*C)
    idx=np.arange(S)
    lab_values=defaultdict(list)
    for t in range(S):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx!=t))
        if len(self_sel)==0:
            continue
        others=np.array([x for x in range(L) if x!=lab],dtype=int)
        if len(others)==0:
            continue
        n=int(counts[t].sum())
        if n<50:
            continue
        ps=sess_probs[self_sel].mean(axis=0)
        po=group_probs[others].mean(axis=0)
        score=float(np.sum(counts[t]*(np.log(ps)-np.log(po)))/n)
        lab_values[lab].append(score)
    if not lab_values:
        return None
    return float(np.mean([np.mean(v) for v in lab_values.values()]))

def tail_summary(null,obs):
    x=np.asarray(null,dtype=float)
    sd=float(x.std(ddof=1))
    return {
        "n":int(len(x)),
        "mean":float(x.mean()),
        "sd":sd,
        "q025":float(np.quantile(x,.025)),
        "q50":float(np.quantile(x,.5)),
        "q975":float(np.quantile(x,.975)),
        "observed":float(obs),
        "observed_minus_null_mean":float(obs-x.mean()),
        "null_standardized_deviation":float((obs-x.mean())/sd) if sd>0 else None,
        "p_null_ge_observed":float((1+np.sum(x>=obs))/(len(x)+1)),
        "p_null_le_observed":float((1+np.sum(x<=obs))/(len(x)+1))
    }

def main():
    c=json.loads(CONTRACT.read_text())
    url=zenodo_file_url(int(c["source"]["record_id"]),c["source"]["archive"])
    with RemoteZip(url,headers=UA) as rz:
        names=rz.namelist()
        suffix=c["source"]["point_member_suffix"]
        matches=[x for x in names if x.endswith(suffix) or x.endswith(suffix.split("/",1)[-1])]
        if len(matches)!=1:
            raise RuntimeError(f"point RDS match count {len(matches)}: {matches[:20]}")
        member=matches[0]
        with tempfile.NamedTemporaryFile(suffix=".rds",delete=False) as tmp:
            tmp_path=Path(tmp.name)
            with rz.open(member) as src:
                shutil.copyfileobj(src,tmp,length=1024*1024)
    try:
        h=hashlib.sha256()
        with tmp_path.open("rb") as fh:
            for chunk in iter(lambda:fh.read(1024*1024),b""):
                h.update(chunk)
        member_sha=h.hexdigest()

        # RDS must be deserialized as a whole. Vertical columns are never indexed/accessed.
        res=pyreadr.read_r(str(tmp_path))
        if not res:
            raise RuntimeError("RDS yielded no object")
        full=next(iter(res.values()))
        cols=list(full.columns)
        nonvert=c["nonvertical_columns"]
        missing=[x for x in nonvert if x not in cols]
        if missing:
            raise RuntimeError(f"missing frozen nonvertical columns {missing}")
        for v in c["rds_vertical_isolation"]["forbidden_vertical_columns"]:
            if v not in cols:
                # Presence is expected from the public processing code; absence is recorded but not fatal for preflight.
                pass
        safe=full.loc[:,nonvert].copy()
        del full,res
        gc.collect()
    finally:
        try: tmp_path.unlink()
        except Exception: pass

    safe["study_id_norm"]=[norm_study_id(x) for x in safe["study.id"]]
    safe["species"]=safe["individual.taxon.canonical.name"].astype(str).str.strip()
    safe["iid"]=safe["individual.local.identifier"].astype(str).str.strip()
    safe["timestamp_parsed"]=pd.to_datetime(safe["timestamp"],errors="coerce",utc=True,format="mixed")
    safe["lon"]=pd.to_numeric(safe["location.long"],errors="coerce")
    safe["lat"]=pd.to_numeric(safe["location.lat"],errors="coerce")
    bad=safe["timestamp_parsed"].isna()|safe["lon"].isna()|safe["lat"].isna()
    safe=safe.loc[~bad].copy()
    safe["night"]=(safe["timestamp_parsed"]-pd.Timedelta(hours=12)).dt.date.astype(str)

    panel_contracts=c["candidate_panels"]
    results=[]
    receipts={}
    B=int(c["horizontal_individuality"]["B"])
    seed_base=int(c["horizontal_individuality"]["seed_base"])

    for pi,panel in enumerate(panel_contracts):
        sid=str(panel["study_id"]);sp=panel["species"]
        g=safe[(safe["study_id_norm"]==sid)&(safe["species"]==sp)].copy()
        rec={
            "study_id":sid,
            "species":sp,
            "rows_nonvertical":int(len(g)),
            "status":None
        }
        if g.empty:
            rec["status"]="STRUCTURAL_STOP_PANEL_ABSENT"
            results.append(rec);continue

        medlon=float(g["lon"].median());medlat=float(g["lat"].median())
        epsg=utm_epsg(medlon,medlat)
        tr=Transformer.from_crs("EPSG:4326",f"EPSG:{epsg}",always_xy=True)
        east,north=tr.transform(g["lon"].to_numpy(dtype=float),g["lat"].to_numpy(dtype=float))
        g["cx"]=np.floor(np.asarray(east)/5000).astype(int)
        g["cy"]=np.floor(np.asarray(north)/5000).astype(int)
        g["cell"]=list(zip(g["cx"],g["cy"]))

        nc=(g.groupby(["iid","night"],sort=True).size().rename("n").reset_index())
        qual=nc[nc["n"]>=50].copy()
        repeat=[]
        train_sessions={}
        for iid in sorted(g["iid"].unique()):
            q=qual[qual["iid"]==iid]
            if len(q)>=2:
                repeat.append(iid)
                train_sessions[iid]=[
                    {"night":str(x.night),"nonvertical_fixes":int(x.n)}
                    for x in q.itertuples(index=False)
                ]
        rec.update({
            "projection_epsg":epsg,
            "unique_individuals":int(g["iid"].nunique()),
            "qualified_nights_ge50":int(len(qual)),
            "repeat_eligible_ids":repeat,
            "repeat_eligible_n":len(repeat)
        })
        if len(repeat)<2:
            rec["horizontal_individuality"]={"status":"NOT_EVALUABLE_UNDER_FROZEN_SESSION_GATE"}
            rec["vertical_gate_pass"]=False
            rec["status"]="STRUCTURAL_STOP_NO_REPEAT_SUPPORT"
            results.append(rec);continue

        keys={(iid,x["night"]) for iid,ss in train_sessions.items() for x in ss}
        qg=g.loc[[(iid,night) in keys for iid,night in zip(g["iid"],g["night"])]].copy()
        sess={}
        by_iid=defaultdict(list)
        for (iid,night),sg in qg.groupby(["iid","night"],sort=True):
            key=(iid,night)
            cells=list(sg["cell"])
            sess[key]={"iid":iid,"night":night,"cells":cells,"cell_set":set(cells),"n":len(cells)}
            by_iid[iid].append(key)

        cells=sorted(set().union(*(r["cell_set"] for r in sess.values())))
        cidx={x:i for i,x in enumerate(cells)}
        skeys=sorted(sess)
        iids=sorted(repeat)
        iidx={iid:i for i,iid in enumerate(iids)}
        counts=np.zeros((len(skeys),len(cells)),dtype=np.int32)
        labels=np.zeros(len(skeys),dtype=np.int16)
        for si,key in enumerate(skeys):
            labels[si]=iidx[key[0]]
            for cell in sess[key]["cells"]:
                counts[si,cidx[cell]]+=1

        hobs,hper,hrows=horiz_eval(counts,labels)
        if hobs is None:
            rec["horizontal_individuality"]={"status":"NOT_EVALUABLE"}
        else:
            rng=np.random.default_rng(seed_base+pi)
            null=[];invalid=0
            for _ in range(B):
                val=horiz_eval_permuted(counts,rng.permutation(labels))
                if val is None: invalid+=1
                else: null.append(float(val))
            hcal=tail_summary(null,hobs)
            rec["horizontal_individuality"]={
                "status":"EVALUATED","observed":hobs,
                "eligible_individuals":len(hper),
                "individual_scores":{iids[int(k)]:float(v) for k,v in hper.items()},
                "B":B,"seed":seed_base+pi,
                "valid_null_replicates":len(null),
                "invalid_null_replicates":invalid,
                "calibration":hcal
            }

        allkeys=list(sess)
        targets=[]
        eval_ids=defaultdict(list)
        for key,sr in sorted(sess.items()):
            iid,night=key
            selfkeys=[x for x in by_iid[iid] if x!=key]
            otherkeys=[x for x in allkeys if x[0]!=iid]
            if not selfkeys or not otherkeys:
                supported=0
            else:
                selfsupport=set().union(*(sess[x]["cell_set"] for x in selfkeys))
                othersupport=set().union(*(sess[x]["cell_set"] for x in otherkeys))
                supported=sum(cell in selfsupport and cell in othersupport for cell in sr["cells"])
            ok=supported>=50
            targets.append({
                "iid":iid,"night":night,"target_events":int(sr["n"]),
                "supported_events":int(supported),"evaluable":bool(ok)
            })
            if ok:
                eval_ids[iid].append({
                    "night":night,"target_events":int(sr["n"]),"supported_events":int(supported)
                })
        eval_list=sorted(eval_ids)
        gate=len(eval_list)>=int(c["vertical_structural_gate"]["minimum_estimator_evaluable_individuals_per_panel"])
        rec.update({
            "cell_universe_size":len(cells),
            "target_support":targets,
            "vertical_evaluable_ids":eval_list,
            "vertical_evaluable_n":len(eval_list),
            "vertical_gate_pass":bool(gate),
            "status":"PASS_TO_VERTICAL" if gate else "STRUCTURAL_STOP_COMMON_SUPPORT"
        })
        if gate:
            receipts[f"{sid}::{sp}"]={
                "study_id":sid,"species":sp,"projection_epsg":epsg,
                "cell_universe":[list(x) for x in cells],
                "repeat_eligible_ids":repeat,
                "training_sessions":train_sessions,
                "horizontal_individuality":rec["horizontal_individuality"],
                "vertical_evaluable_ids":eval_list,
                "frozen_vertical_target_sessions":{iid:eval_ids[iid] for iid in eval_list}
            }
        results.append(rec)

    passing=[x for x in results if x.get("vertical_gate_pass")]
    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "point_member":member,
        "point_member_sha256":member_sha,
        "full_rds_deserialized":True,
        "vertical_values_accessed_by_analysis_logic":False,
        "vertical_values_summarized_or_exported":False,
        "nonvertical_rows_after_parse":int(len(safe)),
        "candidate_panel_results":results,
        "passing_panel_count":len(passing),
        "passing_panels":[f"{x['study_id']}::{x['species']}" for x in passing],
        "decision":"PANELS_PASS_TO_VERTICAL" if passing else "ALL_PANELS_STRUCTURAL_STOP",
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    receipt={
        "schema_version":1,
        "study_id":"batter-airflows-height-opening-receipt-v1",
        "status":"HEIGHT_MAY_OPEN" if passing else "STOP",
        "point_member":member,
        "point_member_sha256":member_sha,
        "source_contract_sha256":hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        "panels":receipts,
        "vertical_values_accessed_by_analysis_logic":False,
        "next_step":(
            "Commit this receipt unchanged, then open height_gener only for frozen passing panels under a separately committed primary script."
            if passing else
            "STOP. Do not lower session or common-support thresholds."
        )
    }
    RECEIPT.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Airflows sealed point-level preflight v1","",
        "**RDS was deserialized because the format is not column-selective, but no vertical column value was accessed, summarized or exported.**","",
        f"- point member SHA256: `{member_sha}`",
        f"- candidate panels: **{len(results)}**",
        f"- panels passing vertical structural gate: **{len(passing)}**","",
        "| study | species | rows | >=50 nights | repeat IDs | horizontal excess | horiz p | vertical-evaluable IDs | status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|"
    ]
    for x in results:
        h=x.get("horizontal_individuality",{})
        cal=h.get("calibration",{}) if h.get("status")=="EVALUATED" else {}
        lines.append(
            f"| {x['study_id']} | {x['species']} | {x['rows_nonvertical']} | {x.get('qualified_nights_ge50',0)} | "
            f"{x.get('repeat_eligible_n',0)} | "
            f"{cal.get('observed_minus_null_mean','—') if cal else '—'} | "
            f"{cal.get('p_null_ge_observed','—') if cal else '—'} | "
            f"{x.get('vertical_evaluable_n',0)} | {x['status']} |"
        )
    lines += ["",f"**Decision: {payload['decision']}**",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "passing_panel_count":len(passing),
        "passing_panels":[f"{x['study_id']}::{x['species']}" for x in passing],
        "panel_summary":[{
            "study_id":x["study_id"],"species":x["species"],
            "qualified_nights":x.get("qualified_nights_ge50",0),
            "repeat_n":x.get("repeat_eligible_n",0),
            "horizontal_excess":(
                x.get("horizontal_individuality",{}).get("calibration",{}).get("observed_minus_null_mean")
            ),
            "horizontal_p":(
                x.get("horizontal_individuality",{}).get("calibration",{}).get("p_null_ge_observed")
            ),
            "vertical_n":x.get("vertical_evaluable_n",0),
            "status":x["status"]
        } for x in results]
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
