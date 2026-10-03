#!/usr/bin/env python3
from __future__ import annotations

import argparse, copy, gzip, hashlib, json, math, sys, urllib.request
from collections import defaultdict
from pathlib import Path

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core
import scripts.run_cross_panel_estimator_calibration as cal
from post_freeze_extensions.strategy_maintenance import wind_support_preflight_v1 as ws

CONTRACT=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_contract_v1.json"
GATE=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_structural_preflight_v2.json"
DEM_RECEIPT=ROOT/"post_freeze_extensions/strategy_maintenance/terrain_dem_preflight_receipt_v1.json"
OUTDIR=ROOT/"post_freeze_extensions/strategy_maintenance/reaction_norm_results"

def source_contract(panel):
    base=json.loads((ROOT/ws.CPATH[panel]).read_text())
    if panel=="phyllostomus_2016":
        c=copy.deepcopy(base)
        c["vertical"]={"field":base["vertical"]["primary_field"],"primary_edges_m":base["vertical"]["edges_m"]}
        return c
    return base

def load_numeric_records(panel):
    c=source_contract(panel)
    ua="batter-individual-wind-reaction-norm-v1/1.0"
    gps=core.get(c["source"]["gps"],ua); ref=core.get(c["source"]["reference"],ua)
    rows,headers=core.read_csv(gps); refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,c)
    tr={co:Transformer.from_crs("EPSG:4326",f"EPSG:{m['epsg']}",always_xy=True) for co,m in pre["projections"].items()}
    hfield=c["vertical"]["field"]
    rec=[]
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None: continue
        sm=pre["session_meta"][sid]; cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]: continue
        lon=core.finite_float(row.get("location_long")); lat=core.finite_float(row.get("location_lat")); h=core.finite_float(row.get(hfield))
        if lon is None or lat is None or h is None: continue
        try: t=core.parse_time(row.get("timestamp",""))
        except Exception: continue
        x,y=tr[cohort].transform(lon,lat)
        rec.append({"cohort":str(cohort),"session":str(sid),"iid":str(sm["individual"]),"t":t,"x":float(x),"y":float(y),"lon":float(lon),"lat":float(lat),"native_h":float(h),"night":core.shifted_night(t)})
    return rec,c

def parse_tile_sw(tile):
    lat=int(tile[1:3])*(1 if tile[0]=="N" else -1)
    lon=int(tile[4:7])*(1 if tile[3]=="E" else -1)
    return lat,lon

def tile_id(lat,lon):
    la=math.floor(float(lat)); lo=math.floor(float(lon))
    return ("N" if la>=0 else "S")+f"{abs(la):02d}"+("E" if lo>=0 else "W")+f"{abs(lo):03d}"

def load_dem_grids(panel):
    receipt=json.loads(DEM_RECEIPT.read_text())
    if receipt.get("status")!="DEM_MAY_OPEN": raise RuntimeError("DEM receipt not openable")
    prec=receipt["panels"][panel]
    grids={}
    for info in prec["tiles"]:
        req=urllib.request.Request(info["url"],headers={"User-Agent":"batter-strategy-maintenance/1.0"})
        with urllib.request.urlopen(req,timeout=300) as r: blob=r.read()
        if hashlib.sha256(blob).hexdigest()!=info["gzip_sha256"]: raise RuntimeError("DEM gzip SHA mismatch")
        raw=gzip.decompress(blob); n=int(info["grid_n"])
        arr=np.frombuffer(raw,dtype=">i2").reshape((n,n))
        grids[info["tile"]]=arr
    return grids,prec

def bilinear_hgt(grids,lat,lon):
    tile=tile_id(lat,lon)
    if tile not in grids: raise RuntimeError(f"missing DEM tile {tile}")
    arr=grids[tile]; n=arr.shape[0]; lat0,lon0=parse_tile_sw(tile)
    row=(lat0+1.0-float(lat))*(n-1); col=(float(lon)-lon0)*(n-1)
    r0=int(math.floor(row)); c0=int(math.floor(col)); r1=min(r0+1,n-1); c1=min(c0+1,n-1)
    vals=np.array([arr[r0,c0],arr[r0,c1],arr[r1,c0],arr[r1,c1]],dtype=float)
    if np.any(vals==-32768): raise RuntimeError("DEM void touched")
    dr=row-r0; dc=col-c0; v00,v01,v10,v11=vals
    return float(v00*(1-dr)*(1-dc)+v01*(1-dr)*dc+v10*dr*(1-dc)+v11*dr*dc)

def add_zrel(panel,records):
    grids,prec=load_dem_grids(panel)
    if len(records)!=int(prec["coordinate_row_count"]):
        raise RuntimeError(f"{panel}: numeric coordinate rows {len(records)} != pinned {prec['coordinate_row_count']}")
    rel=np.empty(len(records),dtype=float)
    for i,r in enumerate(records):
        rel[i]=r["native_h"]-bilinear_hgt(grids,r["lat"],r["lon"])
    by=defaultdict(list)
    for i,r in enumerate(records): by[(r["cohort"],r["session"])].append(i)
    for key,ix in by.items():
        med=float(np.median(rel[ix]))
        for i in ix: records[i]["z_rel"]=float(rel[i]-med)
    return records

def encode_strata(events):
    keys=sorted({tuple(r["stratum"]) for r in events})
    mp={k:i for i,k in enumerate(keys)}
    for r in events: r["sid_int"]=mp[tuple(r["stratum"])]
    return mp

def arr_for(rows):
    return {
        "w":np.asarray([r["wind_speed"] for r in rows],dtype=float),
        "z":np.asarray([r["z_rel"] for r in rows],dtype=float),
        "s":np.asarray([r["sid_int"] for r in rows],dtype=np.int32),
    }

def interval(w):
    if len(w)<2: return None
    return float(np.quantile(w,.05)),float(np.quantile(w,.95))

def model_stats(rows):
    if not rows: return None
    a=arr_for(rows); w,z,s=a["w"],a["z"],a["s"]
    mu_w={}; mu_z={}; sxx=0.0; sxy=0.0
    for st in np.unique(s):
        m=(s==st); ww=w[m]; zz=z[m]
        mw=float(np.mean(ww)); mz=float(np.mean(zz))
        mu_w[int(st)]=mw; mu_z[int(st)]=mz
        wc=ww-mw; zc=zz-mz
        sxx+=float(np.sum(wc*wc)); sxy+=float(np.sum(wc*zc))
    beta=(sxy/sxx) if sxx>1e-12 else None
    iv=interval(w)
    return {"mu_w":mu_w,"mu_z":mu_z,"beta":beta,"q05":iv[0] if iv else None,"q95":iv[1] if iv else None,"sxx":sxx}

def population_stats(group_stats,exclude_label):
    donors=[g for lab,g in group_stats.items() if lab!=exclude_label and g is not None and g["beta"] is not None]
    if not donors: return None
    beta=float(np.mean([g["beta"] for g in donors]))
    strata=sorted({s for g in donors for s in g["mu_z"]})
    mu_z={}; mu_w={}
    for s in strata:
        zz=[g["mu_z"][s] for g in donors if s in g["mu_z"]]
        ww=[g["mu_w"][s] for g in donors if s in g["mu_w"]]
        if zz and ww:
            mu_z[s]=float(np.mean(zz)); mu_w[s]=float(np.mean(ww))
    return {"beta":beta,"mu_z":mu_z,"mu_w":mu_w}

def evaluate(events,labels,min_events=50,details=False):
    by_session=defaultdict(list)
    for r in events: by_session[(r["cohort"],r["session"])].append(r)
    cohorts=defaultdict(list)
    for key in by_session: cohorts[key[0]].append(key)

    session_out=[]; per_label=defaultdict(list); beta_rows=[]
    for cohort,keys in cohorts.items():
        group_keys=defaultdict(list)
        for k in keys: group_keys[labels[k]].append(k)
        group_rows={lab:[r for k in ks for r in by_session[k]] for lab,ks in group_keys.items()}
        group_stats={lab:model_stats(rows) for lab,rows in group_rows.items()}
        pop_cache={lab:population_stats(group_stats,lab) for lab in group_keys}

        for key in keys:
            lab=labels[key]
            self_keys=[k for k in group_keys[lab] if k!=key]
            if not self_keys: continue
            self_rows=[r for k in self_keys for r in by_session[k]]
            ss=model_stats(self_rows)
            pop=pop_cache.get(lab)
            if ss is None or ss["beta"] is None or pop is None: continue

            donor_ivs=[]
            for olab,g in group_stats.items():
                if olab==lab or g is None or g["q05"] is None: continue
                donor_ivs.append((g["q05"],g["q95"]))

            targ=by_session[key]; keep=[]
            for r in targ:
                w=float(r["wind_speed"]); st=int(r["sid_int"])
                env=(ss["q05"]<=w<=ss["q95"] and sum(lo<=w<=hi for lo,hi in donor_ivs)>=2)
                support=(st in ss["mu_z"] and st in pop["mu_z"])
                if env and support: keep.append(r)
            if len(keep)<min_events: continue

            w=np.asarray([r["wind_speed"] for r in keep]); z=np.asarray([r["z_rel"] for r in keep]); s=np.asarray([r["sid_int"] for r in keep],dtype=int)
            b=np.asarray([ss["mu_z"][int(st)] for st in s])
            c=b+float(ss["beta"])*(w-np.asarray([ss["mu_w"][int(st)] for st in s]))
            a=np.asarray([pop["mu_z"][int(st)] for st in s])+float(pop["beta"])*(w-np.asarray([pop["mu_w"][int(st)] for st in s]))
            mae_a=float(np.mean(np.abs(z-a))); mae_b=float(np.mean(np.abs(z-b))); mae_c=float(np.mean(np.abs(z-c)))
            dcb=mae_b-mae_c; dba=mae_a-mae_b
            row={"cohort":cohort,"session":key[1],"label":str(lab),"events":len(keep),"mae_A":mae_a,"mae_B":mae_b,"mae_C":mae_c,"D_CB":dcb,"D_BA":dba,"beta_self":float(ss["beta"])}
            session_out.append(row); per_label[lab].append(row); beta_rows.append(float(ss["beta"]))

    ind=[]
    for lab,rows in per_label.items():
        ind.append({"label":str(lab),"sessions":len(rows),"D_CB":float(np.mean([r["D_CB"] for r in rows])),"D_BA":float(np.mean([r["D_BA"] for r in rows])),"beta_mean":float(np.mean([r["beta_self"] for r in rows]))})
    if not ind: return None
    out={"D_CB":float(np.mean([r["D_CB"] for r in ind])),"D_BA":float(np.mean([r["D_BA"] for r in ind])),"eligible_individuals":len(ind),"eligible_sessions":len(session_out),"scored_events":int(sum(r["events"] for r in session_out))}
    if details: out.update({"individuals":ind,"sessions":session_out,"beta_session_mean":float(np.mean(beta_rows)) if beta_rows else None})
    return out

def permuted_labels(events,rng):
    sessions=defaultdict(dict)
    for r in events: sessions[r["cohort"]][r["session"]]=r["iid"]
    out={}
    for cohort,mp in sessions.items():
        keys=sorted(mp); labs=np.asarray([mp[k] for k in keys],dtype=object)
        pl=rng.permutation(labs)
        for k,lab in zip(keys,pl): out[(cohort,k)]=str(lab)
    return out

def observed_labels(events):
    return {(r["cohort"],r["session"]):r["iid"] for r in events}

def run(panel):
    cfg=json.loads(CONTRACT.read_text())
    gate=json.loads(GATE.read_text())
    if not gate.get("vertical_outcome_may_open"):
        raise RuntimeError("continuous reaction-norm structural gate is not open")
    if panel not in cfg["panels"]: raise RuntimeError("panel not eligible")

    records,_=load_numeric_records(panel)
    add_zrel(panel,records)
    eps,_=ws.kinematic_endpoints(records)
    ds=ws.open_era5(); ws.annotate_wind(eps,ds)
    events,_,base_inds=ws.xy_supported_universe(eps)
    encode_strata(events)

    labels=observed_labels(events)
    obs=evaluate(events,labels,int(cfg["conditioning"]["minimum_scored_target_events"]),details=True)
    if obs is None: raise RuntimeError("no observed evaluable individuals")
    required=int(cfg["structural_gate"]["required_evaluable_individuals"][panel])
    if obs["eligible_individuals"]<required:
        raise RuntimeError(f"{panel}: observed evaluable n {obs['eligible_individuals']} < frozen required {required}")

    B=int(cfg["permutation"]["B"]); seed=int(cfg["permutation"]["seeds"][panel]); rng=np.random.default_rng(seed)
    ncb=[]; nba=[]; nel=[]; invalid=0
    for _ in range(B):
        lab=permuted_labels(events,rng)
        x=evaluate(events,lab,int(cfg["conditioning"]["minimum_scored_target_events"]),details=False)
        if x is None:
            invalid+=1; continue
        ncb.append(float(x["D_CB"])); nba.append(float(x["D_BA"])); nel.append(int(x["eligible_individuals"]))
    if not ncb: raise RuntimeError("no valid permutation replicates")

    cb=cal.tail_summary(ncb,float(obs["D_CB"])); ba=cal.tail_summary(nba,float(obs["D_BA"]))
    rn=bool(cb["observed_minus_null_mean"]>0 and cb["p_null_ge_observed"]<=0.05)
    stable=bool(ba["observed_minus_null_mean"]>0 and ba["p_null_ge_observed"]<=0.05)

    payload={
        "schema_version":1,"study_id":cfg["study_id"],"panel":panel,
        "classification":"post-outcome mechanism test under frozen continuous wind reaction-norm contract",
        "observed":obs,
        "permutation":{"B_requested":B,"seed":seed,"valid":len(ncb),"invalid":invalid,"eligible_individuals_null":{"mean":float(np.mean(nel)),"min":int(np.min(nel)),"max":int(np.max(nel))},"D_CB":cb,"D_BA":ba},
        "decision":{"reaction_norm_supported":rn,"stable_self_supported":stable},
        "claim_boundary":["broad ERA5 10-m wind is a context proxy, not measured bat-level airflow","positive reaction norm does not establish learning, adaptation, personality or optimality","negative result does not exclude nonlinear or finer-scale atmospheric responses"]
    }
    OUTDIR.mkdir(parents=True,exist_ok=True)
    (OUTDIR/f"{panel}_reaction_norm_v1.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"panel":panel,"n":obs["eligible_individuals"],"sessions":obs["eligible_sessions"],"events":obs["scored_events"],"D_CB":obs["D_CB"],"D_CB_excess":cb["observed_minus_null_mean"],"p_RN":cb["p_null_ge_observed"],"reaction_norm_supported":rn,"D_BA":obs["D_BA"],"D_BA_excess":ba["observed_minus_null_mean"],"p_SELF":ba["p_null_ge_observed"],"stable_self_supported":stable},sort_keys=True))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--panel",required=True)
    a=ap.parse_args(); run(a.panel)

if __name__=="__main__":
    main()
