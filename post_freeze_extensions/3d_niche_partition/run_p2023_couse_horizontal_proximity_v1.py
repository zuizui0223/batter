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

vert=load_module("couse_vert_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_vertical_separation_v1.py")
shift=load_module("couse_shift_v1",ROOT/"post_freeze_extensions/3d_niche_partition/run_couse_shiftability_v1.py")

CFG=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_horizontal_proximity_contract_v1.json"
PREF=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_horizontal_proximity_preflight_receipt_v1.json"
COUSE_CFG=ROOT/"post_freeze_extensions/3d_niche_partition/couse_vertical_separation_contract_v1.json"
COUSE_RECEIPT=ROOT/"post_freeze_extensions/3d_niche_partition/couse_shiftability_receipt_v1.json"
OUT=ROOT/"post_freeze_extensions/3d_niche_partition/p2023_couse_horizontal_proximity_result_v1.json"
PANEL="phyllostomus_2023"


def parse_dyad(s):
    c,a,b=s.split("|||",2)
    return (c,a,b)


def slope(x_scaled,y):
    x=np.asarray(x_scaled,dtype=float)
    y=np.asarray(y,dtype=float)
    xc=x-x.mean()
    den=float(np.sum(xc*xc))
    if den<=0: return None
    return float(np.sum(xc*(y-y.mean()))/den)


def endpoint_key(m,side):
    if side=="a":
        return (m["cohort"],m["a"],m["a_session"],m["a_t"].isoformat(),tuple(m["cell"]))
    return (m["cohort"],m["b"],m["b_session"],m["b_t"].isoformat(),tuple(m["cell"]))


def xy_lookup(records):
    out={}
    for r in records:
        cell=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0))
        key=(r["cohort"],r["iid"],r["session"],r["t"].isoformat(),cell)
        if key in out: raise RuntimeError(f"duplicate endpoint key {key}")
        out[key]=r
    return out


def band_panel_stat(dist,sep,dyad_seq,lo,hi,cumulative=False):
    vals=[]
    nrep=0
    for d in sorted(set(dyad_seq)):
        ix=np.array([i for i,x in enumerate(dyad_seq) if x==d],dtype=int)
        if cumulative:
            keep=ix[dist[ix]<=hi]
        else:
            keep=ix[(dist[ix]>=0)&(dist[ix]<=hi)] if lo==0 else ix[(dist[ix]>lo)&(dist[ix]<=hi)]
        if len(keep)>=3:
            vals.append(float(np.median(sep[keep])))
            nrep+=1
    return (float(np.mean(vals)) if nrep>=3 else None,nrep)


def main():
    cfg=json.loads(CFG.read_text())
    pf=json.loads(PREF.read_text())
    couse=json.loads(COUSE_CFG.read_text())
    receipt=json.loads(COUSE_RECEIPT.read_text())
    if not pf.get("horizontal_proximity_may_open"):
        raise RuntimeError("horizontal-proximity preflight did not permit opening")
    if pf["encounter_sha256"]!=cfg["frozen_primary"]["encounter_sha256"]:
        raise RuntimeError("preflight encounter SHA mismatch")
    slope_dyads={parse_dyad(x) for x in pf["slope_evaluable_dyads"]}

    # Reconstruct exact x-y-time encounter set before z.
    xy=shift.pre.load_xy_time(PANEL)
    rr_xy,encounters,dyads,inds,esha,_=vert.reconstruct_primary(PANEL,xy,couse,receipt)
    if esha!=cfg["frozen_primary"]["encounter_sha256"]:
        raise RuntimeError("primary encounter SHA mismatch before z")
    lookup_xy=xy_lookup(rr_xy)

    dist=[]
    dyad_seq=[]
    for m in encounters:
        a=lookup_xy[endpoint_key(m,"a")]
        b=lookup_xy[endpoint_key(m,"b")]
        dist.append(float(math.hypot(a["x"]-b["x"],a["y"]-b["y"])))
        dyad_seq.append((m["cohort"],m["a"],m["b"]))
    dist=np.asarray(dist,dtype=float)

    # Open terrain-relative z only after x-y receipt matches.
    records,contract=vert.load_panel_records(PANEL)
    vert.add_terrain_relative_z(PANEL,records,contract)
    rr,enc_z,dyads_z,inds_z,esha_z,_=vert.reconstruct_primary(PANEL,records,couse,receipt)
    if esha_z!=esha or len(enc_z)!=len(encounters):
        raise RuntimeError("encounter universe changed after z opening")

    lookup=vert.make_record_lookup(rr)
    group_data,ga,pa,gb,pb,di,dyad_list=vert.build_phase_groups(rr,lookup,encounters)

    za=vert.observed_endpoint_values(group_data,ga,pa)
    zb=vert.observed_endpoint_values(group_data,gb,pb)
    sep=np.abs(za-zb)

    obs_slopes={}
    for d in sorted(slope_dyads):
        ix=np.array([i for i,x in enumerate(dyad_seq) if x==d],dtype=int)
        b=slope(dist[ix]/100.0,sep[ix])
        if b is None: raise RuntimeError(f"frozen spatial slope undefined {d}")
        obs_slopes[d]=b
    obs=float(np.mean(list(obs_slopes.values())))

    B=int(cfg["null"]["B"]); seed=int(cfg["null"]["seed"])
    rng=np.random.default_rng(seed)
    null=np.empty(B,dtype=float)

    bands=[tuple(map(float,x)) for x in cfg["descriptive_bands_m"]]
    cumulative=[float(x) for x in cfg["descriptive_cumulative_upper_m"]]
    band_null={f"{int(lo)}-{int(hi)}":np.full(B,np.nan) for lo,hi in bands}
    cum_null={f"<={int(hi)}":np.full(B,np.nan) for hi in cumulative}

    for b in range(B):
        shifts=vert.draw_group_shifts(group_data,rng)
        za_p=vert.permuted_endpoint_values(group_data,ga,pa,shifts)
        zb_p=vert.permuted_endpoint_values(group_data,gb,pb,shifts)
        sp=np.abs(za_p-zb_p)

        bs=[]
        for d in sorted(slope_dyads):
            ix=np.array([i for i,x in enumerate(dyad_seq) if x==d],dtype=int)
            g=slope(dist[ix]/100.0,sp[ix])
            if g is None: raise RuntimeError("null spatial slope undefined")
            bs.append(g)
        null[b]=float(np.mean(bs))

        for lo,hi in bands:
            stat,_=band_panel_stat(dist,sp,dyad_seq,lo,hi,False)
            if stat is not None: band_null[f"{int(lo)}-{int(hi)}"][b]=stat
        for hi in cumulative:
            stat,_=band_panel_stat(dist,sp,dyad_seq,0,hi,True)
            if stat is not None: cum_null[f"<={int(hi)}"][b]=stat

    null_mean=float(np.mean(null))
    p_lower=float((1+np.sum(null<=obs))/(B+1))
    p_upper=float((1+np.sum(null>=obs))/(B+1))
    supported=bool((obs-null_mean)<0 and p_lower<=0.05)

    band_results=[]
    for lo,hi in bands:
        stat,nrep=band_panel_stat(dist,sep,dyad_seq,lo,hi,False)
        arr=band_null[f"{int(lo)}-{int(hi)}"]; valid=arr[np.isfinite(arr)]
        if lo==0: mask=(dist>=0)&(dist<=hi)
        else: mask=(dist>lo)&(dist<=hi)
        band_results.append({
            "band_m":[int(lo),int(hi)],
            "encounters":int(np.sum(mask)),
            "dyads_with_at_least_3_encounters":int(nrep),
            "observed_equal_dyad_median_m":stat,
            "null_mean_m":float(np.mean(valid)) if len(valid) else None,
            "descriptive_p_upper":float((1+np.sum(valid>=stat))/(len(valid)+1)) if len(valid) and stat is not None else None,
            "descriptive_p_lower":float((1+np.sum(valid<=stat))/(len(valid)+1)) if len(valid) and stat is not None else None,
        })

    cum_results=[]
    for hi in cumulative:
        stat,nrep=band_panel_stat(dist,sep,dyad_seq,0,hi,True)
        arr=cum_null[f"<={int(hi)}"]; valid=arr[np.isfinite(arr)]
        cum_results.append({
            "upper_m":int(hi),
            "encounters":int(np.sum(dist<=hi)),
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
        "frozen_dyads":len(dyads),
        "slope_evaluable_dyads":[
            {"cohort":d[0],"individual_a":d[1],"individual_b":d[2],"observed_slope_m_per_100m":float(obs_slopes[d])}
            for d in sorted(obs_slopes)
        ],
        "primary_horizontal_proximity_gradient":{
            "observed_mean_slope_m_per_100m":obs,
            "null_mean_m_per_100m":null_mean,
            "observed_minus_null_mean":float(obs-null_mean),
            "q025":float(np.quantile(null,0.025)),
            "q50":float(np.quantile(null,0.5)),
            "q975":float(np.quantile(null,0.975)),
            "p_null_le_observed":p_lower,
            "p_null_ge_observed":p_upper,
            "supported":supported,
        },
        "distance_descriptive":pf["distance_overall_m"],
        "bands":band_results,
        "cumulative":cum_results,
        "interpretation":(
            "vertical separation increases as paired fixes become horizontally closer"
            if supported else
            "the 2023 co-use excess does not show the predeclared negative horizontal-proximity gradient"
        ),
        "claim_boundary":[
            "post-outcome localization diagnostic",
            "cannot rescue or replace the frozen co-use primary result",
            "does not establish competition or intentional avoidance",
            "bandwise tail locations are descriptive"
        ]
    }
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "slope_evaluable_dyads":len(obs_slopes),
        "observed_mean_slope_m_per_100m":obs,
        "null_mean_m_per_100m":null_mean,
        "excess_slope":obs-null_mean,
        "p_lower":p_lower,"p_upper":p_upper,"supported":supported,
        "bands":band_results,"cumulative":cum_results
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
