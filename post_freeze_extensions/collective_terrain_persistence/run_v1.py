#!/usr/bin/env python3
from __future__ import annotations
import copy, importlib.util, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core
import scripts.run_tag_altitude_bias_shape as shape

def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); assert spec.loader is not None
    spec.loader.exec_module(mod); return mod

collective=load_module("collective3d",ROOT/"post_freeze_extensions/collective_personal_3d_decomposition/run_v1.py")
# DEM helper implementation is the frozen copy bundled on this branch.\nterrain=load_module("terrain3d",ROOT/"post_freeze_extensions/3d_niche_partition/run_original_terrain_geometry_v1.py")

CFG=ROOT/"post_freeze_extensions/collective_terrain_persistence/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/collective_terrain_persistence/result_v1.json"

CPATH={
 "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
 "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json"
}

def source_contract(panel):
    base=json.loads((ROOT/CPATH[panel]).read_text())
    if panel=="phyllostomus_2016":
        c=copy.deepcopy(base)
        c["vertical"]={"field":base["vertical"]["primary_field"],"primary_edges_m":base["vertical"]["edges_m"]}
        return c
    return base

def raw_records_with_latlon(panel):
    c=source_contract(panel)
    gps=core.get(c["source"]["gps"],"batter-collective-terrain-persistence-v1/1.0")
    ref=core.get(c["source"]["reference"],"batter-collective-terrain-persistence-v1/1.0")
    rows,headers=core.read_csv(gps); refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,c)
    hfield=c["vertical"]["field"]
    transformers={cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True)
                  for cohort,meta in pre["projections"].items()}
    out=[]
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None: continue
        sm=pre["session_meta"][sid]; cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]: continue
        lon=core.finite_float(row.get("location_long")); lat=core.finite_float(row.get("location_lat"))
        h=core.finite_float(row.get(hfield))
        if lon is None or lat is None or h is None: continue
        try: t=core.parse_time(row.get("timestamp",""))
        except Exception: continue
        x,y=transformers[cohort].transform(lon,lat)
        out.append({"cohort":str(cohort),"session":str(sid),"iid":str(sm["individual"]),
                    "t":t,"x":float(x),"y":float(y),"lon":float(lon),"lat":float(lat),"native_h":float(h)})
    return out

def terrain_sessions(panel,c):
    receipt=json.loads((ROOT/c["dem"]["receipt"]).read_text())
    prec=receipt["panels"][panel]
    grids=terrain.load_tiles(prec,-32768)
    rec=raw_records_with_latlon(panel)
    for r in rec:
        z=terrain.bilinear_hgt(grids,r["lat"],r["lon"],-32768)
        r["h"]=r["native_h"]-z
    grid=float(c["common_geometry"]["horizontal_grid_m"])
    alpha=float(c["common_geometry"]["jeffreys_alpha"])
    minfix=int(c["common_geometry"]["minimum_session_fixes"])
    by=defaultdict(list)
    for r in rec: by[(r["cohort"],r["session"],r["iid"])].append(r)
    out=[]
    for (cohort,sid,iid),vals in sorted(by.items()):
        if len(vals)<minfix: continue
        med=float(np.median([r["h"] for r in vals]))
        counts=defaultdict(lambda:np.zeros(collective.K,dtype=np.int64))
        for r in vals:
            cell=(math.floor(r["x"]/grid),math.floor(r["y"]/grid))
            zb=shape.z_bin(float(r["h"]-med),edges=collective.EDGES)
            counts[cell][zb]+=1
        total=int(sum(int(v.sum()) for v in counts.values()))
        if total<minfix: continue
        pxy={cell:float(v.sum())/total for cell,v in counts.items()}
        pz={cell:(v.astype(float)+alpha)/(float(v.sum())+alpha*collective.K) for cell,v in counts.items()}
        marg_counts=np.sum(np.stack(list(counts.values())),axis=0)
        marg=(marg_counts.astype(float)+alpha)/(float(marg_counts.sum())+alpha*collective.K)
        mt=collective.median_time([r["t"] for r in vals])
        out.append({"cohort":cohort,"session":sid,"individual":iid,"mid_time":mt,
                    "night":(mt-collective.timedelta(hours=12)).date().isoformat(),
                    "counts":dict(counts),"pxy":pxy,"pz":pz,"marginal":marg,"n":total})
    return out

def main():
    c=json.loads(CFG.read_text())
    results={}
    for p in c["panels"]:
        sessions=terrain_sessions(p,c)
        results[p]=collective.run_laneA(p,sessions,c)
    payload={"schema_version":1,"study_id":c["study_id"],"panels":results,"claim_boundary":c["claim_boundary"]}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({p:{"observed":v["observed_mean_ozxy"],"null":v["null_mean"],
                              "excess":v["observed_minus_null_mean"],"p":v["p_null_ge_observed"],
                              "supported":v["supported"]} for p,v in results.items()},sort_keys=True))
    return 0
if __name__=="__main__": raise SystemExit(main())
