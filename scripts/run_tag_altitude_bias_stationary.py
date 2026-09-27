#!/usr/bin/env python3
"""Secondary stationary-height correction for tag-altitude-bias audit v1."""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

from batter.analysis import Event, z_bin
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_preflight as pre
import scripts.run_tag_altitude_bias_shape as shape

AUDIT=Path("contract/tag_altitude_bias_audit_v1.json")
GRID=100.0
CELL=5000.0


def parse_edges(values):
    out=[]
    for x in values:
        if x=="-inf": out.append(-math.inf)
        elif x=="inf": out.append(math.inf)
        else: out.append(float(x))
    return tuple(out)


def original_edges(panel):
    if panel=="tadarida":
        return (-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
    cmap={
        "eidolon":"contract/eidolon_independent_replication_v1.json",
        "hypsignathus":"contract/hypsignathus_replication_v1.json",
        "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
        "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
        "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
    }
    c=json.loads(Path(cmap[panel]).read_text(encoding="utf-8"))
    vals=c["vertical"]["edges_m"] if panel=="phyllostomus_2016" else c["vertical"]["primary_edges_m"]
    return parse_edges(vals)


def settings(panel):
    c=json.loads(AUDIT.read_text(encoding="utf-8"))
    s={x["panel"]:x for x in c["primary_shift_invariant_shape_test"]["permutation"]["settings"]}[panel]
    return c,s


def parse_shared_key(key):
    # cohort names may contain ::, so parse the final two tokens as integer cell coordinates.
    parts=key.split("::")
    cx=int(parts[-2]); cy=int(parts[-1])
    cohort="::".join(parts[:-2])
    return cohort,(cx,cy)


def stationary_candidates_height(records):
    # Same x-y/time-only definition as frozen preflight; h is carried but never used in eligibility.
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)
    out=[]
    for _key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda r:r["t"])
        for i in range(1,len(vals)-1):
            a,b,c=vals[i-1],vals[i],vals[i+1]
            dt1=(b["t"]-a["t"]).total_seconds()
            dt2=(c["t"]-b["t"]).total_seconds()
            if not (0<dt1<=1200 and 0<dt2<=1200):
                continue
            s1=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/dt1
            s2=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/dt2
            if s1<=0.5 and s2<=0.5:
                out.append(b)
    return out


def estimate_offsets(records,preflight):
    stationary=preflight["stationary"]
    shared_def={
        parse_shared_key(k):set(v["individual_fix_counts"])
        for k,v in stationary["shared_cells"].items()
    }
    supported=set(stationary["supported_individuals"])

    candidates=stationary_candidates_height(records)
    by_cell=defaultdict(lambda: defaultdict(list))
    for r in candidates:
        key=(r["cohort"],(math.floor(r["x"]/GRID),math.floor(r["y"]/GRID)))
        if key not in shared_def or r["iid"] not in supported:
            continue
        by_cell[key][r["iid"]].append(float(r["h"]))

    cell_offsets=defaultdict(list)
    cell_qc={}
    for key,expected_ids in sorted(shared_def.items(),key=lambda x:str(x[0])):
        by_iid=by_cell.get(key,{})
        missing=sorted(i for i in expected_ids if i not in by_iid or not by_iid[i])
        if missing:
            raise RuntimeError(f"finite-height stationary support mismatch {key}: missing {missing}")
        med={iid:float(np.median(by_iid[iid])) for iid in sorted(expected_ids)}
        ref=float(np.median(list(med.values())))
        for iid,value in med.items():
            cell_offsets[iid].append(value-ref)
        cell_qc[f"{key[0]}::{key[1][0]}::{key[1][1]}"]={
            "individual_count":len(med),
            "reference_height_not_written":True,
            "individual_medians_not_written":True,
        }

    offsets={iid:float(np.median(vals)) for iid,vals in sorted(cell_offsets.items()) if vals}
    missing_supported=sorted(supported-set(offsets))
    if missing_supported:
        raise RuntimeError(f"no stationary offset estimate for supported individuals: {missing_supported}")
    return offsets,cell_qc


def corrected_events(records,offsets,edges):
    out=defaultdict(list)
    for r in records:
        if r["iid"] not in offsets:
            continue
        h=float(r["h"])-offsets[r["iid"]]
        out[r["cohort"]].append(Event(
            individual=r["iid"],
            timestamp=r["t"],
            cell=(math.floor(r["x"]/CELL),math.floor(r["y"]/CELL)),
            zbin=z_bin(h,edges=edges),
            session=r["session"],
        ))
    return dict(out)


def run(panel):
    ppath=Path(f"results/tag_altitude_bias_preflight_{panel}_v1.json")
    if not ppath.exists():
        raise RuntimeError(f"missing structural preflight result: {ppath}")
    pf=json.loads(ppath.read_text(encoding="utf-8"))

    contract,spec=settings(panel)
    if not pf["stationary"]["stationary_correction_feasible"]:
        payload={
            "study_id":contract["study_id"],
            "panel_id":panel,
            "analysis":"secondary_stationary_height_correction",
            "status":"structurally_not_evaluable",
            "preflight":str(ppath),
            "numeric_vertical_values_opened_for_stationary_correction":False,
            "reason":"frozen x-y/time-only stationary feasibility gate not met",
            "inferential_role":"secondary corroboration only",
        }
        out=Path(f"results/tag_altitude_bias_stationary_{panel}_v1.json")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
        print(json.dumps(payload,sort_keys=True))
        return

    records,source=shape.panel_raw(panel)
    offsets,cell_qc=estimate_offsets(records,pf)
    edges=original_edges(panel)
    events_by_cohort=corrected_events(records,offsets,edges)
    arrays={c:cal.make_cohort_arrays(e,len(edges)-1) for c,e in sorted(events_by_cohort.items()) if e}
    observed,per_ind,session_rows=cal.observed_eval(arrays)

    rng=np.random.default_rng(int(spec["seed"]))
    null=[]
    eligible=[]
    invalid=0
    for _ in range(int(spec["B"])):
        s=cal.perm_eval(arrays,rng)
        if s["eligible_individuals"]<1 or s["common_cell_marginal"] is None:
            invalid+=1
            continue
        null.append(float(s["common_cell_marginal"]))
        eligible.append(int(s["eligible_individuals"]))
    if not null:
        raise RuntimeError("no valid stationary-corrected null replicates")
    margin=cal.tail_summary(null,float(observed["common_cell_marginal"]))

    vals=np.asarray(list(offsets.values()),dtype=float)
    payload={
        "study_id":contract["study_id"],
        "panel_id":panel,
        "analysis":"secondary_stationary_height_correction",
        "status":"evaluable",
        "preflight":str(ppath),
        "source":source,
        "offset_summary_m":{
            "individual_count":len(offsets),
            "median_offset_m":float(np.median(vals)),
            "median_absolute_offset_m":float(np.median(np.abs(vals))),
            "min_offset_m":float(vals.min()),
            "max_offset_m":float(vals.max()),
            "individual_offsets_not_written":True,
        },
        "stationary_cell_qc":cell_qc,
        "observed":{
            **observed,
            "individual_results":per_ind,
            "session_results":session_rows,
        },
        "permutation":{
            "B":int(spec["B"]),
            "seed":int(spec["seed"]),
            "common_cell_marginal":margin,
            "invalid_replicates":invalid,
            "eligible_individual_count":{
                "observed":observed["eligible_individuals"],
                "null_mean":float(np.mean(eligible)),
                "null_min":int(np.min(eligible)),
                "null_max":int(np.max(eligible)),
            },
        },
        "inferential_role":"secondary corroboration only; cannot rescue primary centered-shape failure",
        "warning":"shared stationary cells are empirical calibration locations, not verified roost-height references",
    }
    out=Path(f"results/tag_altitude_bias_stationary_{panel}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":panel,
        "status":"evaluable",
        "offset_individuals":len(offsets),
        "median_absolute_offset_m":payload["offset_summary_m"]["median_absolute_offset_m"],
        "n":observed["eligible_individuals"],
        "observed":observed["common_cell_marginal"],
        "null_mean":margin["mean"],
        "calibrated_excess":margin["observed_minus_null_mean"],
        "p_upper":margin["p_null_ge_observed"],
    },sort_keys=True))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True,choices=["tadarida","eidolon","hypsignathus","phyllostomus_2022","phyllostomus_2023","phyllostomus_2016"])
    args=ap.parse_args()
    run(args.panel)
    return 0


if __name__=="__main__":
    raise SystemExit(main())
