#!/usr/bin/env python3
from __future__ import annotations

import argparse, copy, gzip, hashlib, json, math, sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import requests
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core
import scripts.run_cross_panel_estimator_calibration as cal
import scripts.run_tag_altitude_bias_shape as shape
from batter.analysis import z_bin
from post_freeze_extensions.strategy_maintenance import wind_support_preflight_v1 as ws

CFG=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_contract_v1.json"
DEM_RECEIPT=ROOT/"post_freeze_extensions/strategy_maintenance/inherited_terrain_dem_receipt_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_results"

CPATH={
    "hypsignathus":"contract/hypsignathus_replication_v1.json",
    "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
    "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
}
EDGES=(-math.inf,-400.0,-200.0,-100.0,-50.0,0.0,50.0,100.0,200.0,400.0,math.inf)
K=len(EDGES)-1
ALPHA=0.5


def source_contract(panel):
    return json.loads((ROOT/CPATH[panel]).read_text(encoding="utf-8"))


def load_records(panel):
    c=source_contract(panel)
    gps=core.get(c["source"]["gps"],"batter-strategy-maintenance-reaction-norm/1.0")
    ref=core.get(c["source"]["reference"],"batter-strategy-maintenance-reaction-norm/1.0")
    rows,headers=core.read_csv(gps); refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,c)
    transformers={
        cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True)
        for cohort,meta in pre["projections"].items()
    }
    hfield=c["vertical"]["field"]
    rec=[]
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
        rec.append({"cohort":str(cohort),"session":str(sid),"iid":str(sm["individual"]),"t":t,
                    "x":float(x),"y":float(y),"lat":float(lat),"lon":float(lon),"native_h":float(h)})
    # Inherit the exact centered-shape session universe used by the completed
    # 500-m terrain diagnostic before decoding DEM values.
    shape_records=[
        {"cohort":r["cohort"],"session":r["session"],"iid":r["iid"],"t":r["t"],
         "x":r["x"],"y":r["y"],"h":r["native_h"]}
        for r in rec
    ]
    events_by_cohort,_=shape.centered_events(shape_records)
    arrays={co:cal.make_cohort_arrays(ev,len(shape.EDGES)-1) for co,ev in sorted(events_by_cohort.items())}
    _,_,audit_rows=cal.observed_eval(arrays)
    allowed={(r["cohort"],r["session"],r["individual"]) for r in audit_rows}
    rec=[r for r in rec if (r["cohort"],r["session"],r["iid"]) in allowed]

    receipt=json.loads(DEM_RECEIPT.read_text())
    expected=int(receipt["panels"][panel]["coordinate_row_count"])
    if len(rec)!=expected:
        raise RuntimeError(f"{panel}: centered-audit record count {len(rec)} != inherited DEM receipt {expected}")
    return rec,c


def parse_tile_sw(tile):
    lat=int(tile[1:3])*(1 if tile[0]=="N" else -1)
    lon=int(tile[4:7])*(1 if tile[3]=="E" else -1)
    return lat,lon


def tile_id(lat,lon):
    la=math.floor(float(lat)); lo=math.floor(float(lon))
    return ("N" if la>=0 else "S")+f"{abs(la):02d}"+("E" if lo>=0 else "W")+f"{abs(lo):03d}"


def load_dem(panel):
    receipt=json.loads(DEM_RECEIPT.read_text())
    grids={}
    for info in receipt["panels"][panel]["tiles"]:
        rr=requests.get(info["url"],headers={"User-Agent":"batter-strategy-maintenance-reaction-norm/1.0"},timeout=300)
        rr.raise_for_status()
        if hashlib.sha256(rr.content).hexdigest()!=info["gzip_sha256"]:
            raise RuntimeError(f"{info['tile']}: DEM gzip SHA mismatch")
        raw=gzip.decompress(rr.content); n=int(info["grid_n"])
        if len(raw)!=n*n*2: raise RuntimeError(f"{info['tile']}: DEM byte length mismatch")
        grids[info["tile"]]=np.frombuffer(raw,dtype=">i2").reshape((n,n))
    return grids


def bilinear(grids,lat,lon):
    tile=tile_id(lat,lon)
    if tile not in grids: raise RuntimeError(f"missing DEM tile {tile}")
    arr=grids[tile]; n=arr.shape[0]; lat0,lon0=parse_tile_sw(tile)
    row=(lat0+1.0-float(lat))*(n-1); col=(float(lon)-lon0)*(n-1)
    r0=int(math.floor(row)); c0=int(math.floor(col)); r1=min(r0+1,n-1); c1=min(c0+1,n-1)
    vals=np.array([arr[r0,c0],arr[r0,c1],arr[r1,c0],arr[r1,c1]],dtype=float)
    if np.any(vals==-32768): raise RuntimeError("DEM void touched")
    dr=row-r0; dc=col-c0
    v00,v01,v10,v11=vals
    return float(v00*(1-dr)*(1-dc)+v01*(1-dr)*dc+v10*dr*(1-dc)+v11*dr*dc)


def add_centered_terrain_height(panel,records):
    grids=load_dem(panel)
    raw=[]
    for r in records:
        tr=float(r["native_h"]-bilinear(grids,r["lat"],r["lon"]))
        r["terrain_rel_raw"]=tr; raw.append(tr)
    by=defaultdict(list)
    for i,r in enumerate(records): by[(r["cohort"],r["session"])].append(i)
    for key,idx in by.items():
        med=float(np.median([records[i]["terrain_rel_raw"] for i in idx]))
        for i in idx: records[i]["z_rel"]=float(records[i]["terrain_rel_raw"]-med)
    return records


def prepare_endpoints(panel):
    records,_=load_records(panel)
    add_centered_terrain_height(panel,records)
    eps,kin_thresholds=ws.kinematic_endpoints(records)
    ds=ws.open_era5(); ws.annotate_wind(eps,ds)
    wind_med={}
    for cohort in sorted({r["cohort"] for r in eps}):
        wind_med[cohort]=float(np.median([r["wind_speed"] for r in eps if r["cohort"]==cohort]))
    for r in eps:
        r["wind_state"]=int(r["wind_speed"]>wind_med[r["cohort"]])
        r["base"]=(math.floor(r["x"]/500.0),math.floor(r["y"]/500.0),int(r["state"]))
        r["wind"]=r["base"]+(int(r["wind_state"]),)
        r["zbin"]=int(z_bin(float(r["z_rel"]),edges=EDGES))
    return eps,kin_thresholds,wind_med


def smooth(counts):
    x=np.asarray(counts,dtype=float)+ALPHA
    return x/float(np.sum(x))


def make_blocks(eps):
    by=defaultdict(list)
    for r in eps: by[(r["cohort"],r["session"])].append(r)
    blocks={}
    for sk,vals in sorted(by.items()):
        base_counts=defaultdict(lambda:np.zeros(K,dtype=np.int32))
        wind_counts=defaultdict(lambda:np.zeros(K,dtype=np.int32))
        target_counts=defaultdict(lambda:np.zeros(K,dtype=np.int32))
        for r in vals:
            base_counts[r["base"]][r["zbin"]]+=1
            wind_counts[r["wind"]][r["zbin"]]+=1
            target_counts[(r["base"],r["wind"])][r["zbin"]]+=1
        blocks[sk]={
            "cohort":sk[0],"session":sk[1],"iid":vals[0]["iid"],
            "base_counts":dict(base_counts),"wind_counts":dict(wind_counts),"target_counts":dict(target_counts),
            "base_prof":{k:smooth(v) for k,v in base_counts.items()},
            "wind_prof":{k:smooth(v) for k,v in wind_counts.items()},
            "events":len(vals),
        }
    return blocks


def evaluate(blocks,label_map):
    cohort_sessions=defaultdict(list)
    for sk,b in blocks.items(): cohort_sessions[b["cohort"]].append(sk)
    session_scores=[]
    for cohort,sessions in cohort_sessions.items():
        sb_sum=defaultdict(lambda:defaultdict(lambda:np.zeros(K,dtype=float)))
        sb_n=defaultdict(lambda:defaultdict(int))
        sw_sum=defaultdict(lambda:defaultdict(lambda:np.zeros(K,dtype=float)))
        sw_n=defaultdict(lambda:defaultdict(int))
        ow_counts=defaultdict(lambda:defaultdict(lambda:np.zeros(K,dtype=np.int64)))
        for sk in sessions:
            b=blocks[sk]; lab=label_map[sk]
            for key,p in b["base_prof"].items(): sb_sum[lab][key]+=p; sb_n[lab][key]+=1
            for key,p in b["wind_prof"].items(): sw_sum[lab][key]+=p; sw_n[lab][key]+=1
            for key,v in b["wind_counts"].items(): ow_counts[lab][key]+=v

        ow_prof=defaultdict(dict)
        global_sum=defaultdict(lambda:np.zeros(K,dtype=float)); global_n=defaultdict(int)
        for lab,dd in ow_counts.items():
            for key,cnt in dd.items():
                p=smooth(cnt); ow_prof[lab][key]=p; global_sum[key]+=p; global_n[key]+=1

        for sk in sessions:
            b=blocks[sk]; lab=label_map[sk]
            rn_num=0.0; self_num=0.0; nscore=0
            for (base,wind),tc in b["target_counts"].items():
                # B: same individual, same base, excluding target session.
                nb=sb_n[lab].get(base,0); sum_b=sb_sum[lab].get(base)
                if sum_b is None: continue
                if base in b["base_prof"]: nb2=nb-1; bsum=sum_b-b["base_prof"][base]
                else: nb2=nb; bsum=sum_b
                if nb2<=0: continue
                pb=bsum/float(nb2)

                # C: same individual, same base + wind state, excluding target session.
                nw=sw_n[lab].get(wind,0); sum_c=sw_sum[lab].get(wind)
                if sum_c is None: continue
                if wind in b["wind_prof"]: nw2=nw-1; csum=sum_c-b["wind_prof"][wind]
                else: nw2=nw; csum=sum_c
                if nw2<=0: continue
                pc=csum/float(nw2)

                # A: other individuals, same base + wind state.
                na=global_n.get(wind,0); asum=global_sum.get(wind)
                if asum is None: continue
                if wind in ow_prof.get(lab,{}): na2=na-1; aa=asum-ow_prof[lab][wind]
                else: na2=na; aa=asum
                if na2<=0: continue
                pa=aa/float(na2)

                n=int(np.sum(tc))
                if n<=0: continue
                rn_num += float(np.sum(tc*(np.log(pc)-np.log(pb))))
                self_num += float(np.sum(tc*(np.log(pb)-np.log(pa))))
                nscore += n
            if nscore>=50:
                session_scores.append({"cohort":cohort,"session":b["session"],"label":lab,"scored":nscore,
                                       "G_RN":rn_num/nscore,"G_SELF":self_num/nscore})

    by_label=defaultdict(list)
    for r in session_scores: by_label[(r["cohort"],r["label"])].append(r)
    ind=[]
    for key,rows in by_label.items():
        ind.append({"cohort":key[0],"label":key[1],"sessions":len(rows),
                    "G_RN":float(np.mean([r["G_RN"] for r in rows])),
                    "G_SELF":float(np.mean([r["G_SELF"] for r in rows]))})
    if not ind: return {"eligible_individuals":0,"G_RN":None,"G_SELF":None,"individuals":[],"sessions":session_scores}
    return {"eligible_individuals":len(ind),"G_RN":float(np.mean([x["G_RN"] for x in ind])),
            "G_SELF":float(np.mean([x["G_SELF"] for x in ind])),"individuals":ind,"sessions":session_scores}


def original_labels(blocks):
    return {sk:b["iid"] for sk,b in blocks.items()}


def permute_labels(blocks,rng):
    out={}
    by=defaultdict(list)
    for sk,b in blocks.items(): by[b["cohort"]].append(sk)
    for cohort,sessions in by.items():
        sessions=sorted(sessions)
        labels=np.array([blocks[sk]["iid"] for sk in sessions],dtype=object)
        pp=rng.permutation(labels)
        for sk,lab in zip(sessions,pp): out[sk]=str(lab)
    return out


def run(panel):
    cfg=json.loads(CFG.read_text())
    if panel not in cfg["panels"]: raise RuntimeError(panel)
    eps,kin_th,wind_med=prepare_endpoints(panel)
    blocks=make_blocks(eps)
    obs=evaluate(blocks,original_labels(blocks))
    expected=int(cfg["structural_gate"]["required_evaluable_individuals"][panel])
    if obs["eligible_individuals"]<expected:
        raise RuntimeError(f"{panel}: observed vertical pipeline n {obs['eligible_individuals']} < frozen structural minimum {expected}")

    B=int(cfg["permutation"]["B"]); seed=int(cfg["permutation"]["seeds"][panel]); rng=np.random.default_rng(seed)
    nr=[]; ns=[]; nind=[]; invalid=0
    for _ in range(B):
        x=evaluate(blocks,permute_labels(blocks,rng))
        if x["eligible_individuals"]<int(cfg["permutation"]["valid_min_evaluable_labels"]) or x["G_RN"] is None:
            invalid+=1; continue
        nr.append(float(x["G_RN"])); ns.append(float(x["G_SELF"])); nind.append(int(x["eligible_individuals"]))
    if not nr: raise RuntimeError(panel+": no valid permutation replicates")
    cr=cal.tail_summary(nr,float(obs["G_RN"])); cs=cal.tail_summary(ns,float(obs["G_SELF"]))
    rn=bool(cr["observed_minus_null_mean"]>0 and cr["p_null_ge_observed"]<=0.05)
    selfsup=bool(cs["observed_minus_null_mean"]>0 and cs["p_null_ge_observed"]<=0.05)
    if rn and selfsup: category="both"
    elif rn: category="reaction_norm"
    elif selfsup: category="stable_self_history"
    else: category="unresolved"
    payload={
        "schema_version":1,"study_id":cfg["study_id"],"panel":panel,
        "classification":"post-outcome strategy-maintenance mechanism test",
        "vertical_representation":"terrain-relative height, centered by complete retained session median",
        "wind_state_medians_m_s":wind_med,"kinematic_thresholds":kin_th,
        "observed":obs,
        "permutation":{"B_requested":B,"seed":seed,"valid_replicates":len(nr),"invalid_replicates":invalid,
                       "eligible_individuals_null":{"min":int(min(nind)),"max":int(max(nind)),"mean":float(np.mean(nind))},
                       "G_RN":cr,"G_SELF":cs},
        "decision":{"reaction_norm_supported":rn,"stable_self_history_supported":selfsup,"category":category},
        "claim_boundary":[
            "wind state is broad ERA5 10-m wind, not local canopy-scale airflow",
            "positive reaction norm does not establish adaptation, personality, genetic determination or optimality",
            "stable self-history without reaction-norm support is consistent with solution reuse but does not prove memory",
            "P. hastatus 2016 was stopped at the frozen environmental support gate"
        ]
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    path=OUTDIR/f"{panel}_reaction_norm_result_v1.json"
    path.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"panel":panel,"n":obs["eligible_individuals"],
                      "G_RN":obs["G_RN"],"RN_excess":cr["observed_minus_null_mean"],"RN_p":cr["p_null_ge_observed"],"RN_supported":rn,
                      "G_SELF":obs["G_SELF"],"SELF_excess":cs["observed_minus_null_mean"],"SELF_p":cs["p_null_ge_observed"],"SELF_supported":selfsup,
                      "category":category,"valid_null":len(nr)},sort_keys=True))
    return 0


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--panel",required=True,choices=list(CPATH))
    return run(ap.parse_args().panel)

if __name__=="__main__":
    raise SystemExit(main())
