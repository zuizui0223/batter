#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import io
import json
import math
import os
import sys
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

DESIGN=ROOT/"post_freeze_extensions/hipposideros_external_validation/primary_design_v1.json"
RECEIPT=ROOT/"post_freeze_extensions/hipposideros_external_validation/height_opening_receipt_v1.json"
OUT=ROOT/"post_freeze_extensions/hipposideros_external_validation/primary_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/hipposideros_external_validation/PRIMARY_RESULT_V1.md"

FILE_ID=4102381
DOWNLOAD=f"https://datadryad.org/api/v2/files/{FILE_ID}/download"
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def load_raw(token):
    headers={
        "Accept":"application/json",
        "Authorization":f"Bearer {token}",
        "User-Agent":"batter-hipposideros-primary-validation-v1/1.0",
    }
    r=requests.get(DOWNLOAD,headers=headers,timeout=180,allow_redirects=True)
    r.raise_for_status()
    return r.content

def build_session_date(d, rule):
    t=pd.to_datetime(d["timestamp"],errors="coerce")
    if t.isna().any():
        raise RuntimeError(f"timestamp parse failures: {int(t.isna().sum())}")
    if rule=="timestamp_minus_12h_then_date":
        return (t-pd.Timedelta(hours=12)).dt.date.astype(str)
    if rule=="raw_calendar_date":
        return t.dt.date.astype(str)
    raise RuntimeError(f"unknown frozen session rule {rule}")

def receipt_session_sets(receipt):
    train={}
    targets={}
    for sp,by_id in receipt["training_universe_ge50_sessions_by_species"].items():
        s=set()
        for iid,rows in by_id.items():
            for x in rows:
                s.add((iid,str(x["session_date"])))
        train[sp]=s
    for sp,by_id in receipt["frozen_evaluable_target_sessions_by_species"].items():
        m={}
        for iid,rows in by_id.items():
            for x in rows:
                m[(iid,str(x["session_date"]))]=int(x["supported_events"])
        targets[sp]=m
    return train,targets

def prepare_events(raw,receipt):
    sha=hashlib.sha256(raw).hexdigest()
    if sha!=receipt["raw_sha256"]:
        raise RuntimeError(f"raw SHA mismatch {sha} != frozen {receipt['raw_sha256']}")

    df=pd.read_csv(io.BytesIO(raw),dtype=str,low_memory=False)
    req=["id","timestamp","longitude","latitude","height"]
    missing=[x for x in req if x not in df.columns]
    if missing:
        raise RuntimeError(f"missing required columns {missing}")

    mask=pd.Series(True,index=df.index)
    for col in req:
        mask &= present(df[col])
    d=df.loc[mask,req].copy()
    d["id"]=d["id"].astype(str).str.strip()
    d["session_date"]=build_session_date(d,receipt["session_rule"])

    prefix_to_species=receipt["species_by_prefix"]
    def map_species(iid):
        p=""
        for ch in iid:
            if ch.isalpha():
                p+=ch
            else:
                break
        return prefix_to_species.get(p)
    d["species"]=d["id"].map(map_species)
    if d["species"].isna().any():
        raise RuntimeError("species mapping failure relative to frozen receipt")

    d["lon_num"]=pd.to_numeric(d["longitude"],errors="coerce")
    d["lat_num"]=pd.to_numeric(d["latitude"],errors="coerce")
    if d[["lon_num","lat_num"]].isna().any().any():
        raise RuntimeError("longitude/latitude parse failure")

    train_sets,target_sets=receipt_session_sets(receipt)
    keep=[
        sp in train_sets and (iid,sd) in train_sets[sp]
        for sp,iid,sd in zip(d["species"],d["id"],d["session_date"])
    ]
    d=d.loc[keep].copy()
    if d.empty:
        raise RuntimeError("no rows remain in frozen training universe")

    # First numeric opening of height in this prospective family.
    h=pd.to_numeric(d["height"],errors="coerce")
    if h.isna().any() or not np.isfinite(h.to_numpy(dtype=float)).all():
        raise RuntimeError("height parse/nonfinite failure in frozen training universe")
    d["height_num"]=h.astype(float)

    transformer=Transformer.from_crs("EPSG:4326","EPSG:32648",always_xy=True)
    east,north=transformer.transform(d["lon_num"].to_numpy(),d["lat_num"].to_numpy())
    d["easting"]=east
    d["northing"]=north
    d["cell_x"]=(d["easting"]//5000).astype(int)
    d["cell_y"]=(d["northing"]//5000).astype(int)

    # Median-center the full frozen night before vertical binning.
    d["session_key"]=d["id"]+"::"+d["session_date"]
    d["session_median"]=d.groupby(["species","session_key"])["height_num"].transform("median")
    d["resid_height"]=d["height_num"]-d["session_median"]

    arrays={}
    target_indices={}
    for sp in receipt["eligible_species_panels"]:
        g=d[d["species"]==sp].copy()
        events=[]
        for r in g.itertuples(index=False):
            events.append(Event(
                individual=str(r.id),
                timestamp=pd.Timestamp(r.timestamp).to_pydatetime(),
                cell=(int(r.cell_x),int(r.cell_y)),
                zbin=z_bin(float(r.resid_height),edges=EDGES),
                session=str(r.session_key),
            ))
        A=cal.make_cohort_arrays(events,K)
        arrays[sp]=A
        idx={s:i for i,s in enumerate(A["sessions"])}
        target_indices[sp]={}
        for (iid,sd),supported in target_sets[sp].items():
            sid=f"{iid}::{sd}"
            if sid not in idx:
                raise RuntimeError(f"frozen target session missing after height opening: {sp} {sid}")
            target_indices[sp][idx[sid]]={
                "session":sid,
                "original_id":iid,
                "preflight_supported_events":supported,
            }
    return arrays,target_indices,sha

def eval_species(A,labels,target_map,species,check_preflight=False):
    counts=A["counts"];cell_tot=A["cell_tot"];sess_cond=A["sess_cond"]
    S,C,K2=counts.shape
    L=len(A["label_names"])

    group_counts=np.zeros((L,C,K2),dtype=np.int32)
    for lab in range(L):
        sel=np.flatnonzero(labels==lab)
        if len(sel):
            group_counts[lab]=counts[sel].sum(axis=0)
    group_cell_tot=group_counts.sum(axis=2)
    group_cond=np.full((L,C,K2),np.nan,dtype=float)
    for lab in range(L):
        pc=np.flatnonzero(group_cell_tot[lab]>0)
        if len(pc):
            group_cond[lab,pc,:]=(group_counts[lab,pc,:]+0.5)/(group_cell_tot[lab,pc,None]+0.5*K2)

    rows=[]
    idx_all=np.arange(S)
    for t,meta in sorted(target_map.items()):
        lab=int(labels[t])
        self_sel=np.flatnonzero((labels==lab)&(idx_all!=t))
        if len(self_sel)==0:
            continue
        other_idx=np.array([x for x in range(L) if x!=lab],dtype=int)
        if len(other_idx)==0:
            continue

        p_self=cal.mean_nan_axis0(sess_cond[self_sel])
        p_other=cal.mean_nan_axis0(group_cond[other_idx])
        target_cell_tot=cell_tot[t]
        supported=(target_cell_tot>0)&(~np.isnan(p_self[:,0]))&(~np.isnan(p_other[:,0]))
        scored=int(target_cell_tot[supported].sum())
        if check_preflight and scored!=int(meta["preflight_supported_events"]):
            raise RuntimeError(
                f"preflight support mismatch {species} {meta['session']}: "
                f"{scored} != {meta['preflight_supported_events']}"
            )
        if scored<50:
            continue

        supported_idx=np.flatnonzero(supported)
        ps=p_self[supported,:]
        po=p_other[supported,:]

        ws=[]
        for s in self_sel:
            w=cell_tot[s,supported_idx].astype(float)
            tot=w.sum()
            if tot>0:
                ws.append(w/tot)
        if not ws:
            continue
        w=np.mean(np.stack(ws),axis=0)
        w=w/w.sum()

        m_self=np.sum(ps*w[:,None],axis=0)
        m_other=np.sum(po*w[:,None],axis=0)
        target_z=counts[t,supported,:].sum(axis=0).astype(float)
        gain=float(np.sum(target_z*(np.log(m_self)-np.log(m_other)))/scored)

        rows.append({
            "species":species,
            "session":A["sessions"][t],
            "pseudo_individual":A["label_names"][lab],
            "original_target_individual":meta["original_id"],
            "scored_events":scored,
            "common_cell_centered_identity":gain,
        })

    per={}
    for lab in sorted({r["pseudo_individual"] for r in rows}):
        rs=[r for r in rows if r["pseudo_individual"]==lab]
        per[lab]={
            "evaluable_target_sessions":len(rs),
            "common_cell_centered_identity":float(np.mean([r["common_cell_centered_identity"] for r in rs])),
        }
    vals=list(per.values())
    return {
        "eligible_individuals":len(vals),
        "common_cell_centered_identity":float(np.mean([v["common_cell_centered_identity"] for v in vals])) if vals else None,
        "individual_results":per,
        "session_results":rows,
    }

def eval_source(arrays,target_indices,labels_by_species,eligible_species,check_preflight=False):
    species_results={}
    values=[]
    for sp in eligible_species:
        r=eval_species(
            arrays[sp],
            labels_by_species[sp],
            target_indices[sp],
            sp,
            check_preflight=check_preflight,
        )
        species_results[sp]=r
        if r["eligible_individuals"]<1 or r["common_cell_centered_identity"] is None:
            return None,species_results
        values.append(float(r["common_cell_centered_identity"]))
    return float(np.mean(values)),species_results

def main():
    if not RECEIPT.exists():
        raise RuntimeError("height_opening_receipt_v1.json is absent; Height opening is prohibited")
    receipt=json.loads(RECEIPT.read_text())
    if receipt.get("status")!="HEIGHT_MAY_OPEN":
        raise RuntimeError(f"receipt status is {receipt.get('status')}; Height opening is prohibited")
    design=json.loads(DESIGN.read_text())

    # Verify the committed design is exactly the design frozen into the receipt.
    dsha=hashlib.sha256(DESIGN.read_bytes()).hexdigest()
    if dsha!=receipt["primary_design_sha256"]:
        raise RuntimeError(f"primary design SHA mismatch {dsha} != {receipt['primary_design_sha256']}")

    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN missing; do not fall back to unauthenticated download")

    raw=load_raw(token)
    arrays,target_indices,raw_sha=prepare_events(raw,receipt)
    eligible_species=list(receipt["eligible_species_panels"])

    obs_labels={sp:arrays[sp]["orig_labels"].copy() for sp in eligible_species}
    observed,species_obs=eval_source(
        arrays,target_indices,obs_labels,eligible_species,check_preflight=True
    )
    if observed is None:
        raise RuntimeError("observed source statistic is unevaluable despite frozen PASS receipt")

    expected_n={
        sp:len(receipt["estimator_evaluable_ids_by_species"][sp])
        for sp in eligible_species
    }
    observed_n={sp:species_obs[sp]["eligible_individuals"] for sp in eligible_species}
    if observed_n!=expected_n:
        raise RuntimeError(f"observed species n {observed_n} != frozen {expected_n}")

    B=int(design["calibration"]["B"])
    seed=int(design["calibration"]["seed"])
    rng=np.random.default_rng(seed)
    null=[]
    species_null={sp:[] for sp in eligible_species}
    species_n={sp:[] for sp in eligible_species}
    invalid=0

    for _ in range(B):
        labels={}
        for sp in eligible_species:
            labels[sp]=rng.permutation(arrays[sp]["orig_labels"])
        val,sr=eval_source(arrays,target_indices,labels,eligible_species,check_preflight=False)
        if val is None:
            invalid+=1
            continue
        null.append(float(val))
        for sp in eligible_species:
            species_null[sp].append(float(sr[sp]["common_cell_centered_identity"]))
            species_n[sp].append(int(sr[sp]["eligible_individuals"]))

    if not null:
        raise RuntimeError("no valid permutation replicates")

    source_cal=cal.tail_summary(null,observed)
    species_cal={
        sp:cal.tail_summary(species_null[sp],float(species_obs[sp]["common_cell_centered_identity"]))
        for sp in eligible_species
    }
    passed=(
        source_cal["observed_minus_null_mean"]>0
        and source_cal["p_null_ge_observed"]<=0.05
    )

    payload={
        "schema_version":1,
        "study_id":"batter-hipposideros-primary-validation-v1",
        "raw_sha256":raw_sha,
        "height_opened_under_frozen_receipt":True,
        "eligible_species_panels":eligible_species,
        "frozen_expected_evaluable_individuals_by_species":expected_n,
        "observed":{
            "source_common_cell_centered_identity":observed,
            "species":species_obs,
        },
        "permutation":{
            "B":B,
            "seed":seed,
            "valid_replicates":len(null),
            "invalid_replicates":invalid,
            "source":source_cal,
            "species_secondary":species_cal,
            "species_evaluable_n_distribution":{
                sp:{
                    "min":int(min(species_n[sp])),
                    "max":int(max(species_n[sp])),
                    "mean":float(np.mean(species_n[sp])),
                }
                for sp in eligible_species
            }
        },
        "primary_verdict":{
            "calibrated_excess_positive":source_cal["observed_minus_null_mean"]>0,
            "p_upper_le_0_05":source_cal["p_null_ge_observed"]<=0.05,
            "pass":bool(passed)
        },
        "interpretation":design["interpretation_matrix"]["PASS" if passed else "FAIL"],
        "claim_boundary":[
            "The source-level verdict is primary; species-specific calibrations are secondary diagnostics.",
            "A FAIL cannot be rescued by alternate grid, bins, species pooling, lower gates or alternate altitude endpoint.",
            "Mechanism extensions cannot overwrite the primary external-validation verdict."
        ]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")

    lines=[
        "# Hipposideros prospective external validation v1","",
        "**Numeric AGL height was opened only after the committed outcome-blind height-opening receipt.**","",
        f"- eligible species panels: **{eligible_species}**",
        f"- evaluable individuals by species: **{observed_n}**",
        f"- source observed centered identity: **{observed:+.5f}**",
        f"- source null mean: **{source_cal['mean']:+.5f}**",
        f"- calibrated excess: **{source_cal['observed_minus_null_mean']:+.5f}**",
        f"- p(null >= observed): **{source_cal['p_null_ge_observed']:.4f}**",
        f"- frozen primary verdict: **{'PASS' if passed else 'FAIL'}**","",
        "## Secondary species diagnostics","",
        "| species | n | observed | null mean | calibrated excess | p upper |",
        "|---|---:|---:|---:|---:|---:|"
    ]
    for sp in eligible_species:
        c=species_cal[sp]
        lines.append(
            f"| {sp} | {observed_n[sp]} | {c['observed']:+.5f} | {c['mean']:+.5f} | "
            f"{c['observed_minus_null_mean']:+.5f} | {c['p_null_ge_observed']:.4f} |"
        )
    lines += ["",design["interpretation_matrix"]["PASS" if passed else "FAIL"],""]
    OUT_MD.write_text("\n".join(lines),encoding="utf-8")

    print(json.dumps({
        "eligible_species_panels":eligible_species,
        "observed_n":observed_n,
        "source_observed":observed,
        "source_null_mean":source_cal["mean"],
        "source_calibrated_excess":source_cal["observed_minus_null_mean"],
        "source_p_upper":source_cal["p_null_ge_observed"],
        "pass":passed
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
