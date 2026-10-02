#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod

cv=load_module(
    "couse_vertical_v1",
    ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py"
)

CONTRACT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_localization_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_localization_result_v1.json"


def prepare(scope):
    panel="phyllostomus_2023"
    cfg=json.loads(cv.CFG.read_text())
    receipt=json.loads(cv.RECEIPT.read_text())

    # Freeze x-y-time encounter set first.
    xy=cv.shift.pre.load_xy_time(panel)
    tol=600
    centers,_=cv.ep.endpoint_centers(xy)
    radius=float(cfg["endpoint_exclusion"]["radius_m"])
    rr_xy,_,_=cv.shift.shiftable_records(xy,tol)
    encounters,dyads,inds=cv.shift.build_primary_encounters(
        rr_xy,tol,cfg,scope,centers,radius
    )

    # Load z only after encounter structure is fixed.
    records,src_contract=cv.load_panel_records(panel)
    terrain_summary=cv.add_terrain_relative_z(panel,records,src_contract)
    rr_z,_,_=cv.shift.shiftable_records(records,tol)
    if scope=="endpoint_excluded":
        rr_z=[r for r in rr_z if cv.ep.is_away(r,centers,radius)]

    lookup=cv.make_record_lookup(rr_z)
    groups,ga,pa,gb,pb,di,dyad_list=cv.build_phase_groups(
        rr_z,lookup,encounters
    )
    return cfg,terrain_summary,encounters,dyads,inds,groups,ga,pa,gb,pb,di,dyad_list


def observed_and_null(groups,ga,pa,gb,pb,di,dyad_list,B,seed,return_dyad_null=False):
    za=cv.observed_endpoint_values(groups,ga,pa)
    zb=cv.observed_endpoint_values(groups,gb,pb)
    sep=np.abs(za-zb)
    obs,obs_dyad=cv.panel_stat(sep,di,len(dyad_list))

    rng=np.random.default_rng(int(seed))
    null=np.empty(B,dtype=float)
    null_dyad=np.empty((B,len(dyad_list)),dtype=float) if return_dyad_null else None
    for b in range(B):
        shifts=cv.draw_group_shifts(groups,rng)
        za_p=cv.permuted_endpoint_values(groups,ga,pa,shifts)
        zb_p=cv.permuted_endpoint_values(groups,gb,pb,shifts)
        val,meds=cv.panel_stat(np.abs(za_p-zb_p),di,len(dyad_list))
        null[b]=val
        if return_dyad_null:
            null_dyad[b,:]=meds
    return sep,obs,obs_dyad,null,null_dyad


def shiftable_fraction(groups,ga,gb):
    n=0; ok=0
    for arr in (ga,gb):
        for gid in arr:
            n+=1
            if int(groups[int(gid)]["n"])>=2:
                ok+=1
    return ok/n if n else None


def main():
    dc=json.loads(CONTRACT.read_text())
    B=int(dc["leave_one_dyad_out"]["B"])
    seed=int(dc["leave_one_dyad_out"]["seed"])

    # A. Frozen all-space primary universe, leave one dyad out.
    cfg,terr,enc,dyads,inds,groups,ga,pa,gb,pb,di,dlist=prepare("all_space")
    if len(enc)!=679 or len(dlist)!=8 or len(inds)!=6:
        raise RuntimeError("2023 primary universe mismatch")

    sep,obs,obs_dyad,null,null_dyad=observed_and_null(
        groups,ga,pa,gb,pb,di,dlist,B,seed,return_dyad_null=True
    )

    full_cal=cv.cal.tail_summary(null.tolist(),float(obs))
    loo=[]
    for k,d in enumerate(dlist):
        keep=[i for i in range(len(dlist)) if i!=k]
        obs_k=float(np.mean(obs_dyad[keep]))
        null_k=np.mean(null_dyad[:,keep],axis=1)
        cal=cv.cal.tail_summary(null_k.tolist(),obs_k)
        loo.append({
            "removed_dyad":{"cohort":d[0],"individual_a":d[1],"individual_b":d[2]},
            "remaining_dyads":len(keep),
            "observed_m":obs_k,
            "null_mean_m":cal["mean"],
            "excess_m":cal["observed_minus_null_mean"],
            "p_upper":cal["p_null_ge_observed"],
        })

    # B. Endpoint-excluded sub-universe, descriptive only.
    eB=int(dc["endpoint_excluded"]["B"])
    eseed=int(dc["endpoint_excluded"]["seed"])
    _,_,eenc,edyads,einds,egroups,ega,epa,egb,epb,edi,edlist=prepare("endpoint_excluded")
    if len(eenc)!=629 or len(edlist)!=6 or len(einds)!=4:
        raise RuntimeError("2023 endpoint-excluded universe mismatch")
    esep,eobs,eobs_dyad,enull,_=observed_and_null(
        egroups,ega,epa,egb,epb,edi,edlist,eB,eseed,return_dyad_null=False
    )
    ecal=cv.cal.tail_summary(enull.tolist(),float(eobs))

    payload={
        "schema_version":1,
        "study_id":dc["study_id"],
        "classification":dc["classification"],
        "primary_reference":{
            "observed_m":float(obs),
            "null_mean_m":full_cal["mean"],
            "excess_m":full_cal["observed_minus_null_mean"],
            "p_upper":full_cal["p_null_ge_observed"],
        },
        "leave_one_dyad_out":loo,
        "endpoint_excluded_descriptive":{
            "individuals":len(einds),
            "dyads":len(edlist),
            "encounters":len(eenc),
            "shiftable_endpoint_fraction":shiftable_fraction(egroups,ega,egb),
            "observed_m":float(eobs),
            "null_mean_m":ecal["mean"],
            "excess_m":ecal["observed_minus_null_mean"],
            "tail_location_p_upper_descriptive":ecal["p_null_ge_observed"],
            "inferential":False,
        },
        "claim_boundary":[
            "all diagnostics are post-outcome",
            "leave-one-dyad-out p-values are sensitivity summaries, not independent tests",
            "endpoint-excluded universe failed the frozen >=5-individual gate",
            "no diagnostic may replace the corrected primary result"
        ]
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    print(json.dumps({
        "full_p":full_cal["p_null_ge_observed"],
        "loo_p_min":min(x["p_upper"] for x in loo),
        "loo_p_max":max(x["p_upper"] for x in loo),
        "loo_excess_min":min(x["excess_m"] for x in loo),
        "loo_excess_max":max(x["excess_m"] for x in loo),
        "endpoint_excluded_individuals":len(einds),
        "endpoint_excluded_observed_m":float(eobs),
        "endpoint_excluded_null_mean_m":ecal["mean"],
        "endpoint_excluded_excess_m":ecal["observed_minus_null_mean"],
        "endpoint_excluded_tail_location":ecal["p_null_ge_observed"],
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
