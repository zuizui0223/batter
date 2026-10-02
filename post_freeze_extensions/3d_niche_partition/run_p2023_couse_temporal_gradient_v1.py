#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
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

vert=load_module("couse_vert_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py")
shift=load_module("couse_shift_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_shiftability_v1.py")

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_temporal_gradient_contract_v1.json"
PREF=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_temporal_gradient_preflight_receipt_v1.json"
COUSE_CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
COUSE_RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/couse_shiftability_receipt_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_temporal_gradient_result_v1.json"

PANEL="phyllostomus_2023"


def parse_dyad(s):
    c,a,b=s.split("|||",2)
    return (c,a,b)


def dyad_slope(dt_s,sep_m):
    x=np.asarray(dt_s,dtype=float)/60.0
    y=np.asarray(sep_m,dtype=float)
    xc=x-x.mean()
    denom=float(np.sum(xc*xc))
    if denom<=0:
        return None
    return float(np.sum(xc*(y-y.mean()))/denom)


def band_panel_stat(dt,sep,dyads,lo,hi,cumulative=False):
    vals=[]
    represented=0
    details=[]
    for d in sorted(set(dyads)):
        ix=np.array([i for i,x in enumerate(dyads) if x==d],dtype=int)
        if cumulative:
            keep=ix[dt[ix]<=hi]
        else:
            if lo==0:
                keep=ix[(dt[ix]>=0)&(dt[ix]<=hi)]
            else:
                keep=ix[(dt[ix]>lo)&(dt[ix]<=hi)]
        if len(keep)>=3:
            represented+=1
            med=float(np.median(sep[keep]))
            vals.append(med)
            details.append((d,len(keep),med))
    return (float(np.mean(vals)) if represented>=3 else None, represented, details)


def main():
    cfg=json.loads(CFG.read_text())
    pf=json.loads(PREF.read_text())
    couse=json.loads(COUSE_CFG.read_text())
    receipt=json.loads(COUSE_RECEIPT.read_text())

    if not pf.get("temporal_gradient_may_open"):
        raise RuntimeError("temporal-gradient preflight did not permit opening")
    if pf["encounter_sha256"]!=cfg["frozen_primary"]["encounter_sha256"]:
        raise RuntimeError("gradient preflight encounter SHA mismatch")

    slope_dyads={parse_dyad(x) for x in pf["slope_evaluable_dyads"]}

    # Reconstruct fixed x-y-time universe and verify receipt before z.
    xy=shift.pre.load_xy_time(PANEL)
    _,encounters,dyads,inds,esha,_=vert.reconstruct_primary(
        PANEL,xy,couse,receipt
    )
    if esha!=cfg["frozen_primary"]["encounter_sha256"]:
        raise RuntimeError("primary encounter SHA mismatch before z")

    # Now load terrain-relative z using the exact corrected primary pipeline.
    records,contract=vert.load_panel_records(PANEL)
    vert.add_terrain_relative_z(PANEL,records,contract)
    rr,enc_z,dyads_z,inds_z,esha_z,_=vert.reconstruct_primary(
        PANEL,records,couse,receipt
    )
    if esha_z!=esha or len(enc_z)!=len(encounters):
        raise RuntimeError("encounter universe changed after z opening")

    lookup=vert.make_record_lookup(rr)
    group_data,ga,pa,gb,pb,di,dyad_list=vert.build_phase_groups(
        rr,lookup,encounters
    )

    dyad_of_enc=np.array([dyad_list[int(i)] for i in di],dtype=object)
    dt=np.array([float(m["dt_s"]) for m in encounters],dtype=float)

    za=vert.observed_endpoint_values(group_data,ga,pa)
    zb=vert.observed_endpoint_values(group_data,gb,pb)
    sep=np.abs(za-zb)

    obs_slopes={}
    for d in sorted(slope_dyads):
        ix=np.array([i for i,x in enumerate(dyad_of_enc) if tuple(x)==d],dtype=int)
        b=dyad_slope(dt[ix],sep[ix])
        if b is None:
            raise RuntimeError(f"frozen slope dyad became unslopeable {d}")
        obs_slopes[d]=b
    obs=float(np.mean(list(obs_slopes.values())))

    B=int(cfg["null"]["B"])
    seed=int(cfg["null"]["seed"])
    rng=np.random.default_rng(seed)
    null=np.empty(B,dtype=float)

    # Preallocate band null arrays only for descriptive summaries.
    bands=[tuple(map(float,x)) for x in cfg["descriptive_bands_s"]]
    cumulative=[float(x) for x in cfg["descriptive_cumulative_upper_s"]]
    band_null={f"{int(lo)}-{int(hi)}":np.full(B,np.nan,dtype=float) for lo,hi in bands}
    cum_null={f"<={int(hi)}":np.full(B,np.nan,dtype=float) for hi in cumulative}

    for b in range(B):
        shifts=vert.draw_group_shifts(group_data,rng)
        za_p=vert.permuted_endpoint_values(group_data,ga,pa,shifts)
        zb_p=vert.permuted_endpoint_values(group_data,gb,pb,shifts)
        sp=np.abs(za_p-zb_p)

        slopes=[]
        for d in sorted(slope_dyads):
            ix=np.array([i for i,x in enumerate(dyad_of_enc) if tuple(x)==d],dtype=int)
            beta=dyad_slope(dt[ix],sp[ix])
            if beta is None:
                raise RuntimeError("null slope undefined for frozen dyad")
            slopes.append(beta)
        null[b]=float(np.mean(slopes))

        for lo,hi in bands:
            stat,_,_=band_panel_stat(dt,sp,[tuple(x) for x in dyad_of_enc],lo,hi,False)
            if stat is not None:
                band_null[f"{int(lo)}-{int(hi)}"][b]=stat
        for hi in cumulative:
            stat,_,_=band_panel_stat(dt,sp,[tuple(x) for x in dyad_of_enc],0,hi,True)
            if stat is not None:
                cum_null[f"<={int(hi)}"][b]=stat

    null_mean=float(np.mean(null))
    p_lower=float((1+np.sum(null<=obs))/(B+1))
    p_upper=float((1+np.sum(null>=obs))/(B+1))
    supported=bool((obs-null_mean)<0 and p_lower<=0.05)

    # Observed descriptive bands.
    dyad_seq=[tuple(x) for x in dyad_of_enc]
    band_results=[]
    for lo,hi in bands:
        stat,nrep,details=band_panel_stat(dt,sep,dyad_seq,lo,hi,False)
        arr=band_null[f"{int(lo)}-{int(hi)}"]
        valid=arr[np.isfinite(arr)]
        band_results.append({
            "band_s":[int(lo),int(hi)],
            "encounters":int(np.sum((dt<=hi)&(dt>=0 if lo==0 else dt>lo))),
            "dyads_with_at_least_3_encounters":int(nrep),
            "observed_equal_dyad_median_m":stat,
            "null_mean_m":float(np.mean(valid)) if len(valid) else None,
            "descriptive_p_upper":float((1+np.sum(valid>=stat))/(len(valid)+1)) if len(valid) and stat is not None else None,
            "descriptive_p_lower":float((1+np.sum(valid<=stat))/(len(valid)+1)) if len(valid) and stat is not None else None,
        })

    cumulative_results=[]
    for hi in cumulative:
        stat,nrep,details=band_panel_stat(dt,sep,dyad_seq,0,hi,True)
        arr=cum_null[f"<={int(hi)}"]
        valid=arr[np.isfinite(arr)]
        cumulative_results.append({
            "upper_s":int(hi),
            "encounters":int(np.sum(dt<=hi)),
            "dyads_with_at_least_3_encounters":int(nrep),
            "observed_equal_dyad_median_m":stat,
            "null_mean_m":float(np.mean(valid)) if len(valid) else None,
            "descriptive_p_upper":float((1+np.sum(valid>=stat))/(len(valid)+1)) if len(valid) and stat is not None else None,
        })

    payload={
        "schema_version":1,
        "study_id":cfg["study_id"],
        "classification":cfg["classification"],
        "encounter_sha256":esha,
        "frozen_encounters":len(encounters),
        "frozen_dyads":len(dyad_list),
        "slope_evaluable_dyads":[
            {
                "cohort":d[0],"individual_a":d[1],"individual_b":d[2],
                "observed_slope_m_per_min":float(obs_slopes[d])
            } for d in sorted(obs_slopes)
        ],
        "primary_temporal_gradient":{
            "observed_mean_slope_m_per_min":obs,
            "null_mean_m_per_min":null_mean,
            "observed_minus_null_mean":float(obs-null_mean),
            "q025":float(np.quantile(null,0.025)),
            "q50":float(np.quantile(null,0.5)),
            "q975":float(np.quantile(null,0.975)),
            "p_null_le_observed":p_lower,
            "p_null_ge_observed":p_upper,
            "supported":supported,
        },
        "dt_descriptive":pf["dt_overall_s"],
        "bands":band_results,
        "cumulative":cumulative_results,
        "interpretation":(
            "vertical separation increases as paired fixes become more synchronous"
            if supported else
            "the 2023 co-use excess does not show the predeclared negative temporal-proximity gradient"
        ),
        "claim_boundary":[
            "post-outcome localization diagnostic",
            "does not establish competition or intentional avoidance",
            "bandwise tail locations are descriptive",
            "cannot replace the frozen 600-s primary co-use result"
        ]
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    print(json.dumps({
        "slope_evaluable_dyads":len(obs_slopes),
        "observed_mean_slope_m_per_min":obs,
        "null_mean_m_per_min":null_mean,
        "excess_slope":obs-null_mean,
        "p_lower":p_lower,
        "p_upper":p_upper,
        "supported":supported,
        "bands":band_results,
        "cumulative":cumulative_results,
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
