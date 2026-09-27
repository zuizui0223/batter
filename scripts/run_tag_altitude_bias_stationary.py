#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
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

CONTRACT=Path("contract/tag_altitude_bias_audit_v1.json")
APPLICABILITY=Path("config/tag_altitude_bias_stationary_applicability_v1.json")
EDGES=(-math.inf,0.0,50.0,100.0,200.0,400.0,800.0,1600.0,3200.0,math.inf)
CELL=5000.0


def load_cfg(panel):
    if not APPLICABILITY.exists():
        raise RuntimeError("stationary applicability config has not been frozen")
    app=json.loads(APPLICABILITY.read_text(encoding="utf-8"))
    spec=app["panels"][panel]
    if not spec["feasible"]:
        raise RuntimeError(f"panel {panel} is structurally ineligible for stationary correction")
    c=json.loads(CONTRACT.read_text(encoding="utf-8"))
    pset={x["panel"]:x for x in c["primary_shift_invariant_shape_test"]["permutation"]["settings"]}[panel]
    return c,app,spec,pset


def stationary_structure(records):
    # Selection uses x-y/time only; h is carried but ignored until after support is frozen.
    candidates,_=pre.stationary_candidates(records,0.5,1200)
    by_cell=defaultdict(lambda: defaultdict(list))
    for r in candidates:
        cell=(math.floor(r["x"]/100.0),math.floor(r["y"]/100.0))
        by_cell[(r["cohort"],cell)][r["iid"]].append(r)

    shared={}
    for key,by_iid in sorted(by_cell.items()):
        per_cell={iid:vals for iid,vals in by_iid.items() if len(vals)>=5}
        if len(per_cell)>=3:
            shared[key]=per_cell

    indiv=defaultdict(lambda: {"fixes":0,"cells":set(),"cohorts":set()})
    for (cohort,cell),by_iid in shared.items():
        for iid,vals in by_iid.items():
            indiv[iid]["fixes"]+=len(vals)
            indiv[iid]["cells"].add((cohort,cell))
            indiv[iid]["cohorts"].add(cohort)
    supported={
        iid for iid,v in indiv.items()
        if v["fixes"]>=10 and len(v["cells"])>=1
    }
    return candidates,shared,supported


def estimate_offsets(shared,supported):
    # Cell reference uses all per-cell-supported individuals (>=5 fixes in a shared cell).
    cell_refs={}
    cell_individual_medians={}
    for key,by_iid in sorted(shared.items()):
        med={iid:float(np.median([r["h"] for r in vals])) for iid,vals in by_iid.items()}
        ref=float(np.median(list(med.values())))
        cell_refs[key]=ref
        cell_individual_medians[key]=med

    offsets=defaultdict(list)
    for (cohort,cell),med in cell_individual_medians.items():
        ref=cell_refs[(cohort,cell)]
        for iid,value in med.items():
            if iid in supported:
                offsets[(cohort,iid)].append(float(value-ref))

    final={
        (cohort,iid):float(np.median(vals))
        for (cohort,iid),vals in offsets.items()
        if vals
    }
    details={
        f"{cohort}::{iid}":{
            "offset_m":value,
            "shared_cell_count":len(offsets[(cohort,iid)]),
        }
        for (cohort,iid),value in sorted(final.items())
    }
    return final,details


def build_events(records,supported,eligible_cohorts,offsets,corrected):
    counts=Counter()
    raw=[]
    for r in records:
        key=(r["cohort"],r["iid"])
        if r["cohort"] not in eligible_cohorts or r["iid"] not in supported or key not in offsets:
            continue
        h=float(r["h"]-offsets[key]) if corrected else float(r["h"])
        sid=r["session"]
        counts[(r["cohort"],sid)]+=1
        raw.append((r,h))

    retained={(c,s) for (c,s),n in counts.items() if n>=50}
    events=defaultdict(list)
    for r,h in raw:
        if (r["cohort"],r["session"]) not in retained:
            continue
        events[r["cohort"]].append(Event(
            individual=r["iid"],
            timestamp=r["t"],
            cell=(math.floor(r["x"]/CELL),math.floor(r["y"]/CELL)),
            zbin=z_bin(h,edges=EDGES),
            session=r["session"],
        ))
    return dict(events),{
        "retained_sessions":len(retained),
        "retained_events":sum(len(v) for v in events.values()),
        "retained_individuals":len({e.individual for v in events.values() for e in v}),
    }


def arrays(events):
    return {c:cal.make_cohort_arrays(e,len(EDGES)-1) for c,e in sorted(events.items()) if e}


def observed(A):
    return cal.observed_eval(A)


def paired_calibration(Au,Ac,B,seed):
    if set(Au)!=set(Ac):
        raise RuntimeError("uncorrected/corrected cohort mismatch")
    for cohort in Au:
        if Au[cohort]["sessions"]!=Ac[cohort]["sessions"]:
            raise RuntimeError(f"session mismatch {cohort}")
        if not np.array_equal(Au[cohort]["orig_labels"],Ac[cohort]["orig_labels"]):
            raise RuntimeError(f"label mismatch {cohort}")

    ou,piu,sru=observed(Au)
    oc,pic,src=observed(Ac)
    rng=np.random.default_rng(int(seed))
    nu=[]; nc=[]; eu=[]; ec=[]
    for _ in range(int(B)):
        rows_u=[]; rows_c=[]
        for cohort in sorted(Au):
            labels=rng.permutation(Au[cohort]["orig_labels"])
            rows_u.extend(cal.eval_cohort(Au[cohort],labels,cohort))
            rows_c.extend(cal.eval_cohort(Ac[cohort],labels,cohort))
        su=cal.aggregate_panel(rows_u)[0]
        sc=cal.aggregate_panel(rows_c)[0]
        if su["eligible_individuals"]<1 or sc["eligible_individuals"]<1:
            continue
        nu.append(float(su["common_cell_marginal"]))
        nc.append(float(sc["common_cell_marginal"]))
        eu.append(int(su["eligible_individuals"]))
        ec.append(int(sc["eligible_individuals"]))
    if not nu or not nc:
        raise RuntimeError("no valid paired stationary permutations")
    return (
        ou,piu,sru,cal.tail_summary(nu,float(ou["common_cell_marginal"])),
        oc,pic,src,cal.tail_summary(nc,float(oc["common_cell_marginal"])),
        {"uncorrected_null_n_mean":float(np.mean(eu)),"corrected_null_n_mean":float(np.mean(ec))}
    )


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True)
    args=ap.parse_args()
    c,app,spec,pset=load_cfg(args.panel)

    records,source=shape.panel_raw(args.panel)
    candidates,shared,supported=stationary_structure(records)
    expected_supported=set(spec["supported_individuals"])
    if supported!=expected_supported:
        raise RuntimeError(
            f"stationary supported-individual reconstruction mismatch: "
            f"{sorted(supported)} != {sorted(expected_supported)}"
        )
    eligible_cohorts=set(spec["eligible_cohorts"])
    offsets,offset_details=estimate_offsets(shared,supported)

    # Every scored supported individual/cohort must have an empirical offset.
    scored_supported={
        (r["cohort"],r["iid"]) for r in records
        if r["iid"] in supported and r["cohort"] in eligible_cohorts
    }
    missing=sorted(scored_supported-set(offsets))
    if missing:
        raise RuntimeError(f"missing stationary offsets for supported individual/cohort: {missing}")

    eu,qcu=build_events(records,supported,eligible_cohorts,offsets,False)
    ec,qcc=build_events(records,supported,eligible_cohorts,offsets,True)
    Au=arrays(eu); Ac=arrays(ec)

    ou,piu,sru,cu,oc,pic,src,cc,elig=paired_calibration(
        Au,Ac,int(pset["B"]),int(pset["seed"])
    )

    offset_vals=np.asarray(list(offsets.values()),dtype=float)
    payload={
        "study_id":c["study_id"],
        "component":"secondary_stationary_height_correction",
        "contract":str(CONTRACT),
        "applicability":str(APPLICABILITY),
        "panel_id":args.panel,
        "source":source,
        "stationary_support":{
            "candidate_fix_count":len(candidates),
            "shared_cell_count":len(shared),
            "supported_individuals":sorted(supported),
            "eligible_cohorts":sorted(eligible_cohorts),
        },
        "offsets":{
            "individual_cohort_count":len(offsets),
            "median_offset_m":float(np.median(offset_vals)),
            "median_absolute_offset_m":float(np.median(np.abs(offset_vals))),
            "min_offset_m":float(offset_vals.min()),
            "max_offset_m":float(offset_vals.max()),
            "details":offset_details,
        },
        "uncorrected_same_subset":{
            "qc":qcu,
            "observed":ou,
            "calibration":cu,
        },
        "stationary_corrected":{
            "qc":qcc,
            "observed":oc,
            "calibration":cc,
            "calibrated_identity_positive":cc["observed_minus_null_mean"]>0,
            "upper_tail_le_0_05":cc["p_null_ge_observed"]<=0.05,
        },
        "paired_permutation":{
            "B":int(pset["B"]),
            "seed":int(pset["seed"]),
            **elig,
        },
        "claim_boundary":{
            "secondary_corroboration_only":True,
            "stationary_reference_not_verified_true_roost_height":True,
            "cannot_rescue_primary_shape_failure":True,
        }
    }
    out=Path(f"results/tag_altitude_bias_stationary_{args.panel}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":args.panel,
        "supported_individuals":len(supported),
        "median_absolute_offset_m":payload["offsets"]["median_absolute_offset_m"],
        "uncorrected":{
            "obs":ou["common_cell_marginal"],
            "null":cu["mean"],
            "excess":cu["observed_minus_null_mean"],
            "p":cu["p_null_ge_observed"],
        },
        "corrected":{
            "obs":oc["common_cell_marginal"],
            "null":cc["mean"],
            "excess":cc["observed_minus_null_mean"],
            "p":cc["p_null_ge_observed"],
        },
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
