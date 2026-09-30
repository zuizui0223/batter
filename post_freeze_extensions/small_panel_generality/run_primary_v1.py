#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math, re, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal

CONTRACT=ROOT/"post_freeze_extensions/small_panel_generality/contract_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/small_panel_generality/height_opening_receipt_v1.json"
OUT=ROOT/"post_freeze_extensions/small_panel_generality/primary_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/small_panel_generality/PRIMARY_RESULT_V1.md"
UA={"User-Agent":"batter-small-panel-generality-primary-v1/1.0"}
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1

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

def load_source(src,rec):
    r=requests.get(src["event_url"],headers=UA,timeout=300)
    r.raise_for_status(); raw=r.content; sha=hashlib.sha256(raw).hexdigest()
    if sha!=rec["raw_sha256"]:
        raise RuntimeError(f"{src['source_id']}: raw SHA mismatch")

    hdr=pd.read_csv(io.BytesIO(raw),nrows=0)
    cmap={norm(x):x for x in hdr.columns}
    req=["timestamp","location_long","location_lat","individual_local_identifier",norm(src["vertical_field"])]
    missing=[x for x in req if x not in cmap]
    if missing: raise RuntimeError(f"{src['source_id']}: missing fields {missing}")
    use=[cmap[x] for x in req]
    for q in ["visible","algorithm_marked_outlier","manually_marked_outlier","import_marked_outlier"]:
        if q in cmap: use.append(cmap[q])
    use=list(dict.fromkeys(use))
    df=pd.read_csv(io.BytesIO(raw),dtype=str,usecols=use,low_memory=False)

    tcol=cmap["timestamp"]; loncol=cmap["location_long"]; latcol=cmap["location_lat"]
    iidcol=cmap["individual_local_identifier"]; hcol=cmap[norm(src["vertical_field"])]
    mask=present(df[tcol])&present(df[loncol])&present(df[latcol])&present(df[iidcol])&present(df[hcol])
    d=df.loc[mask].copy()

    if "visible" in cmap and cmap["visible"] in d:
        keep=[]
        for x in d[cmap["visible"]]:
            b=boolish(x); keep.append(True if b is None else b)
        d=d.loc[keep].copy()
    for q in ["algorithm_marked_outlier","manually_marked_outlier","import_marked_outlier"]:
        if q in cmap and cmap[q] in d:
            keep=[]
            for x in d[cmap[q]]:
                b=boolish(x); keep.append(True if b is None else (not b))
            d=d.loc[keep].copy()

    d["iid"]=d[iidcol].astype(str).str.strip()
    d["t"]=pd.to_datetime(d[tcol],errors="coerce",utc=True,format="mixed")
    d["lon"]=pd.to_numeric(d[loncol],errors="coerce")
    d["lat"]=pd.to_numeric(d[latcol],errors="coerce")
    bad=d["t"].isna()|d["lon"].isna()|d["lat"].isna()
    d=d.loc[~bad].sort_values(["iid","t"]).copy()

    # First numeric vertical opening for this programme.
    h=pd.to_numeric(d[hcol],errors="coerce")
    if h.isna().any() or not np.isfinite(h.to_numpy(dtype=float)).all():
        raise RuntimeError(f"{src['source_id']}: vertical parse/nonfinite failure")
    d["height_num"]=h.astype(float)

    # Reconstruct the frozen >4 h sessions.
    d["sess_num"]=-1
    for iid,g in d.groupby("iid",sort=True):
        vals=[]; k=0; prev=None
        for t in g["t"]:
            if prev is not None and (t-prev)>pd.Timedelta(hours=4): k+=1
            vals.append(k); prev=t
        d.loc[g.index,"sess_num"]=vals
    d["session"]=d["iid"]+"::"+d["sess_num"].astype(int).astype(str)

    frozen_sessions={z["session"] for rows in rec["training_sessions"].values() for z in rows}
    d=d[d["session"].isin(frozen_sessions)].copy()
    if set(d["session"].unique())!=frozen_sessions:
        missing=sorted(frozen_sessions-set(d["session"].unique()))
        raise RuntimeError(f"{src['source_id']}: frozen sessions missing {missing}")

    tr=Transformer.from_crs("EPSG:4326",f"EPSG:{int(rec['projection_epsg'])}",always_xy=True)
    e,n=tr.transform(d["lon"].to_numpy(dtype=float),d["lat"].to_numpy(dtype=float))
    d["cx"]=np.floor(np.asarray(e)/5000.0).astype(int)
    d["cy"]=np.floor(np.asarray(n)/5000.0).astype(int)

    d["session_median"]=d.groupby("session")["height_num"].transform("median")
    d["resid"]=d["height_num"]-d["session_median"]

    events=[]
    for row in d.itertuples(index=False):
        events.append(Event(
            individual=str(row.iid),
            timestamp=row.t.to_pydatetime(),
            cell=(int(row.cx),int(row.cy)),
            zbin=z_bin(float(row.resid),edges=EDGES),
            session=str(row.session)
        ))
    return events,sha

def frozen_targets(rec):
    out={}
    for iid,rows in rec["frozen_vertical_target_sessions"].items():
        for x in rows:
            out[str(x["session"])]={
                "iid":str(iid),
                "supported_events":int(x["supported_events"]),
                "target_events":int(x["target_events"])
            }
    return out

def validate_observed_against_receipt(srcid,session_rows,rec):
    frozen=frozen_targets(rec)
    got={str(x["session"]):x for x in session_rows}
    if set(got)!=set(frozen):
        raise RuntimeError(
            f"{srcid}: observed target-session set mismatch; "
            f"missing={sorted(set(frozen)-set(got))[:10]}, extra={sorted(set(got)-set(frozen))[:10]}"
        )
    for sid,fx in frozen.items():
        if int(got[sid]["scored_fixes"])!=fx["supported_events"]:
            raise RuntimeError(
                f"{srcid}: supported-event mismatch {sid}: "
                f"{got[sid]['scored_fixes']} != {fx['supported_events']}"
            )

def main():
    c=json.loads(CONTRACT.read_text())
    rec=json.loads(RECEIPT.read_text())
    if rec.get("status")!="HEIGHT_MAY_OPEN":
        raise RuntimeError(f"receipt status {rec.get('status')} prohibits vertical opening")
    csha=hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    if csha!=rec["contract_sha256"]:
        raise RuntimeError("contract SHA differs from frozen receipt")

    source_specs={x["source_id"]:x for x in c["closed_source_set"]}
    results={}
    for srcid,rinfo in rec["sources"].items():
        src=source_specs[srcid]
        events,sha=load_source(src,rinfo)
        A=cal.make_cohort_arrays(events,K)
        arrays={srcid:A}

        observed,per_ind,session_rows=cal.observed_eval(arrays)
        if observed["eligible_individuals"]!=4:
            raise RuntimeError(f"{srcid}: observed n={observed['eligible_individuals']} != frozen 4")
        validate_observed_against_receipt(srcid,session_rows,rinfo)

        metric="common_cell_marginal"
        obs=float(observed[metric])
        B=int(c["vertical_primary"]["B"])
        seed=int(c["vertical_primary"]["seed_by_source"][srcid])
        rng=np.random.default_rng(seed)
        null=[]; eligible=[]; invalid=0
        for _ in range(B):
            p=cal.perm_eval(arrays,rng)
            if p["eligible_individuals"]<1 or p[metric] is None:
                invalid+=1; continue
            null.append(float(p[metric]))
            eligible.append(int(p["eligible_individuals"]))
        if not null: raise RuntimeError(f"{srcid}: no valid permutations")
        summ=cal.tail_summary(null,obs)
        passed=(summ["observed_minus_null_mean"]>0 and summ["p_null_ge_observed"]<=0.05)

        results[srcid]={
          "taxon":src["taxon"],"doi":src["doi"],"vertical_field":src["vertical_field"],
          "raw_sha256":sha,
          "horizontal_individuality":rinfo["horizontal_individuality"],
          "observed":{
            **observed,
            "individual_results":per_ind,
            "session_results":session_rows
          },
          "primary_metric":metric,
          "permutation":{
            "B":B,"seed":seed,"valid_replicates":len(null),"invalid_replicates":invalid,
            "eligible_individual_count":{
              "observed":4,
              "min":int(min(eligible)),"max":int(max(eligible)),
              "mean":float(np.mean(eligible))
            },
            "calibration":summ
          },
          "primary_pass":bool(passed)
        }

    payload={
      "schema_version":1,"study_id":"batter-small-panel-generality-primary-v1",
      "receipt_commit_boundary":"vertical opened only after frozen receipt existed on branch",
      "sources":results,
      "programme_summary":{
        "source_count":len(results),
        "vertical_pass_count":sum(int(x["primary_pass"]) for x in results.values()),
        "horizontal_vertical_points":{
          srcid:{
            "horizontal_calibrated_excess":x["horizontal_individuality"]["calibration"]["observed_minus_null_mean"],
            "horizontal_p_upper":x["horizontal_individuality"]["calibration"]["p_null_ge_observed"],
            "vertical_calibrated_excess":x["permutation"]["calibration"]["observed_minus_null_mean"],
            "vertical_p_upper":x["permutation"]["calibration"]["p_null_ge_observed"],
            "vertical_pass":x["primary_pass"]
          } for srcid,x in results.items()
        }
      },
      "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
      "# Small-panel generality vertical primary v1","",
      "**Both source vertical outcomes were opened only after the nonvertical receipt was committed.**","",
      "| source | taxon | horizontal excess | horizontal p | vertical excess | vertical p | vertical verdict |",
      "|---|---|---:|---:|---:|---:|---|"
    ]
    for srcid,x in results.items():
        h=x["horizontal_individuality"]["calibration"]; v=x["permutation"]["calibration"]
        lines.append(
          f"| {srcid} | {x['taxon']} | {h['observed_minus_null_mean']:+.5f} | {h['p_null_ge_observed']:.4f} | "
          f"{v['observed_minus_null_mean']:+.5f} | {v['p_null_ge_observed']:.4f} | {'PASS' if x['primary_pass'] else 'FAIL'} |"
        )
    lines += ["","These two sources remain structural STOPs under the earlier >=5-individual comparative-generality v1. This separate programme is reported under its own four-individual frozen design.",""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
      "results":{
        srcid:{
          "taxon":x["taxon"],
          "horizontal_excess":x["horizontal_individuality"]["calibration"]["observed_minus_null_mean"],
          "horizontal_p":x["horizontal_individuality"]["calibration"]["p_null_ge_observed"],
          "vertical_observed":x["permutation"]["calibration"]["observed"],
          "vertical_null_mean":x["permutation"]["calibration"]["mean"],
          "vertical_excess":x["permutation"]["calibration"]["observed_minus_null_mean"],
          "vertical_p":x["permutation"]["calibration"]["p_null_ge_observed"],
          "pass":x["primary_pass"]
        } for srcid,x in results.items()
      }
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
