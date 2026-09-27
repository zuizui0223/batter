#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import sys

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_biological_effect_translation as bet
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_new_species_replications as core
import scripts.run_eidolon_independent_replication as eid

CONTRACT=Path("contract/tag_altitude_bias_audit_v1.json")
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
CELL=5000.0


def cfg():
    x=json.loads(CONTRACT.read_text(encoding="utf-8"))
    settings={p["panel"]:p for p in x["primary_shift_invariant_shape_test"]["permutation"]["settings"]}
    required=x["primary_shift_invariant_shape_test"]["required_evaluable_individuals"]
    return x,settings,required


def panel_raw(panel):
    if panel=="tadarida":
        rows=bet.get_tad_rows()
        tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
        counts=Counter()
        rec=[]
        for row in rows:
            iid=str(row.get("animal-id","")).strip()
            day=str(row.get("BatDay","")).strip()
            lon=bet.finite_float(row.get("location-long"))
            lat=bet.finite_float(row.get("location-lat"))
            h=bet.finite_float(row.get("height-above-msl"))
            if not iid or not day or lon is None or lat is None or h is None:
                continue
            try:
                t=core.parse_time(row.get("timestamp",""))
            except Exception:
                continue
            x,y=tr.transform(lon,lat)
            sid=f"{iid}::{day}"
            counts[sid]+=1
            rec.append({"cohort":"focal","iid":iid,"session":sid,"t":t,"x":x,"y":y,"h":h})
        retained={s for s,n in counts.items() if n>=50}
        rec=[r for r in rec if r["session"] in retained]
        return rec,{"gps_rows":len(rows),"source":"tadarida annotated archive"}

    cpath={
        "eidolon":"contract/eidolon_independent_replication_v1.json",
        "hypsignathus":"contract/hypsignathus_replication_v1.json",
        "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
        "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
        "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
    }[panel]

    if panel=="eidolon":
        contract=json.loads(Path(cpath).read_text(encoding="utf-8"))
        gps=eid.get(eid.GPS_URL,eid.GPS_MD5,eid.GPS_SIZE)
        ref=eid.get(eid.REF_URL,eid.REF_MD5)
        rows=eid.read_csv(gps)
        refs=eid.read_csv(ref)
        pre=eid.build_pre_numeric(rows,refs)
        height=eid.HEIGHT_FIELD
        finite=eid.finite_float
        parse=eid.parse_time
        source={"gps_md5":eid.GPS_MD5,"reference_md5":eid.REF_MD5,"gps_rows":len(rows)}
    else:
        base=json.loads(Path(cpath).read_text(encoding="utf-8"))
        if panel=="phyllostomus_2016":
            contract=copy.deepcopy(base)
            contract["vertical"]={"field":base["vertical"]["primary_field"],"primary_edges_m":base["vertical"]["edges_m"]}
        else:
            contract=base
        ua="batter-tag-altitude-bias-audit-v1/1.0"
        gps=core.get(contract["source"]["gps"],ua)
        ref=core.get(contract["source"]["reference"],ua)
        rows,headers=core.read_csv(gps)
        refs,_=core.read_csv(ref)
        pre=core.build_pre_numeric(rows,headers,refs,contract)
        height=contract["vertical"]["field"]
        finite=core.finite_float
        parse=core.parse_time
        source={"gps_md5":contract["source"]["gps"]["md5"],"reference_md5":contract["source"]["reference"]["md5"],"gps_rows":len(rows)}

    transformers={
        cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True)
        for cohort,meta in pre["projections"].items()
    }
    rec=[]
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None:
            continue
        sm=pre["session_meta"][sid]
        cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]:
            continue
        lon=finite(row.get("location_long")); lat=finite(row.get("location_lat")); h=finite(row.get(height))
        if lon is None or lat is None or h is None:
            continue
        try:
            t=parse(row.get("timestamp",""))
        except Exception:
            continue
        x,y=transformers[cohort].transform(lon,lat)
        rec.append({"cohort":cohort,"iid":sm["individual"],"session":sid,"t":t,"x":x,"y":y,"h":h})
    return rec,source


def centered_events(records):
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    events=defaultdict(list)
    medians={}
    for (cohort,sid),vals in sorted(by_session.items()):
        med=float(np.median([r["h"] for r in vals]))
        medians[f"{cohort}::{sid}"]=med
        for r in vals:
            resid=float(r["h"]-med)
            events[cohort].append(Event(
                individual=r["iid"],
                timestamp=r["t"],
                cell=(math.floor(r["x"]/CELL),math.floor(r["y"]/CELL)),
                zbin=z_bin(resid,edges=EDGES),
                session=sid,
            ))
    return dict(events),medians


def run(panel):
    contract,settings,required=cfg()
    records,source=panel_raw(panel)
    events_by_cohort,medians=centered_events(records)
    k=len(EDGES)-1
    arrays={c:cal.make_cohort_arrays(e,k) for c,e in sorted(events_by_cohort.items())}
    observed,per_ind,session_rows=cal.observed_eval(arrays)

    req=int(required[panel])
    if observed["eligible_individuals"]!=req:
        raise RuntimeError(f"centered evaluable n mismatch {panel}: {observed['eligible_individuals']} != {req}")

    spec=settings[panel]
    rng=np.random.default_rng(int(spec["seed"]))
    null=[]
    null_adv=[]
    eligible=[]
    invalid=0
    for _ in range(int(spec["B"])):
        s=cal.perm_eval(arrays,rng)
        if s["eligible_individuals"]<1 or s["common_cell_marginal"] is None:
            invalid+=1
            continue
        null.append(float(s["common_cell_marginal"]))
        null_adv.append(float(s["common_cell_advantage"]))
        eligible.append(int(s["eligible_individuals"]))
    if not null:
        raise RuntimeError("no valid centered-height null replicates")

    margin=cal.tail_summary(null,float(observed["common_cell_marginal"]))
    adv=cal.tail_summary(null_adv,float(observed["common_cell_advantage"]))
    passes=margin["observed_minus_null_mean"]>0 and margin["p_null_ge_observed"]<=0.05

    payload={
        "study_id":contract["study_id"],
        "contract":str(CONTRACT),
        "panel_id":panel,
        "source":source,
        "transformation":{
            "center":"session median",
            "centered_edges_m":list(EDGES),
            "horizontal_cell_m":CELL,
            "session_medians_not_reported":True,
        },
        "observed":{
            **observed,
            "individual_results":per_ind,
            "session_results":session_rows,
        },
        "permutation":{
            "B":int(spec["B"]),
            "seed":int(spec["seed"]),
            "common_cell_shape_identity":margin,
            "common_cell_shape_advantage":adv,
            "invalid_replicates":invalid,
            "eligible_individual_count":{
                "observed":observed["eligible_individuals"],
                "null_mean":float(np.mean(eligible)),
                "null_min":int(np.min(eligible)),
                "null_max":int(np.max(eligible)),
            }
        },
        "primary_verdict":{
            "required_evaluable_individuals":req,
            "exact_n_met":True,
            "calibrated_shape_identity_positive":margin["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":margin["p_null_ge_observed"]<=0.05,
            "pass":bool(passes),
        },
        "claim_boundary":{
            "additive_session_offset_removed_exactly":True,
            "constant_tag_offset_removed_exactly":True,
            "does_not_identify_device_bias_magnitude":True,
            "does_not_test_nonadditive_device_error":True,
        }
    }
    out=Path(f"results/tag_altitude_bias_shape_{panel}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":panel,
        "n":observed["eligible_individuals"],
        "observed":observed["common_cell_marginal"],
        "null_mean":margin["mean"],
        "calibrated_excess":margin["observed_minus_null_mean"],
        "p_upper":margin["p_null_ge_observed"],
        "pass":passes,
    },sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["tadarida","eidolon","hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    run(args.panel)
    return 0

if __name__=="__main__":
    raise SystemExit(main())
