#!/usr/bin/env python3
from __future__ import annotations

import copy, json, math, sys
from collections import defaultdict
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core

CONTRACT=ROOT/"post_freeze_extensions/strategy_maintenance/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/strategy_maintenance/wind_support_preflight_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/strategy_maintenance/WIND_SUPPORT_PREFLIGHT_V1.md"

CPATH={
    "hypsignathus":"contract/hypsignathus_replication_v1.json",
    "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
    "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
    "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
}
EXPECTED_N={"hypsignathus":19,"phyllostomus_2022":23,"phyllostomus_2023":11,"phyllostomus_2016":9}
KIN={"speed_quantiles":[0.5],"turn_quantiles":[0.5],"turn_bins":2}
MAX_DT=1800
GRID_M=500.0
MIN_SUPPORTED=50


def source_contract(panel):
    base=json.loads((ROOT/CPATH[panel]).read_text(encoding="utf-8"))
    if panel!="phyllostomus_2016":
        return base
    c=copy.deepcopy(base)
    c["vertical"]={
        "field":base["vertical"]["primary_field"],
        "primary_edges_m":base["vertical"]["edges_m"],
    }
    return c


def angle(v1x,v1y,v2x,v2y):
    a=math.hypot(v1x,v1y); b=math.hypot(v2x,v2y)
    if a<=0 or b<=0:
        return None
    cc=max(-1.0,min(1.0,(v1x*v2x+v1y*v2y)/(a*b)))
    return math.acos(cc)


def load_xy_time(panel):
    c=source_contract(panel)
    gps=core.get(c["source"]["gps"],"batter-strategy-maintenance-wind-preflight/1.0")
    ref=core.get(c["source"]["reference"],"batter-strategy-maintenance-wind-preflight/1.0")
    rows,headers=core.read_csv(gps)
    refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,c)
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
        lon=core.finite_float(row.get("location_long"))
        lat=core.finite_float(row.get("location_lat"))
        if lon is None or lat is None:
            continue
        try:
            t=core.parse_time(row.get("timestamp",""))
        except Exception:
            continue
        x,y=transformers[cohort].transform(lon,lat)
        rec.append({
            "cohort":str(cohort),"session":str(sid),"iid":str(sm["individual"]),
            "t":t,"x":float(x),"y":float(y),"lat":float(lat),"lon":float(lon),
            "night":core.shifted_night(t),
        })
    return rec,{"admitted_cohorts":pre["admitted_cohorts"],"records":len(rec)}


def kinematic_endpoints(records):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["session"])].append(r)
    out=[]
    for (cohort,session),vals in sorted(by.items()):
        vals=sorted(vals,key=lambda x:x["t"])
        for i in range(2,len(vals)):
            a,b,c=vals[i-2],vals[i-1],vals[i]
            dt1=(b["t"]-a["t"]).total_seconds()
            dt2=(c["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(x) and 0<x<=MAX_DT for x in (dt1,dt2)):
                continue
            v1x,v1y=b["x"]-a["x"],b["y"]-a["y"]
            v2x,v2y=c["x"]-b["x"],c["y"]-b["y"]
            turn=angle(v1x,v1y,v2x,v2y)
            if turn is None:
                continue
            speed=math.hypot(v2x,v2y)/dt2
            out.append({**c,"speed":float(speed),"turn":float(turn)})
    sp=defaultdict(list); tu=defaultdict(list)
    for r in out:
        sp[r["cohort"]].append(r["speed"]); tu[r["cohort"]].append(r["turn"])
    thresholds={}
    for cohort in sorted(sp):
        thresholds[cohort]={
            "speed":float(np.quantile(np.asarray(sp[cohort]),0.5)),
            "turn":float(np.quantile(np.asarray(tu[cohort]),0.5)),
        }
    for r in out:
        th=thresholds[r["cohort"]]
        sb=int(r["speed"]>th["speed"]); tb=int(r["turn"]>th["turn"])
        r["state"]=sb*2+tb
        r["stratum"]=(math.floor(r["x"]/GRID_M),math.floor(r["y"]/GRID_M),r["state"])
    return out,thresholds


def xy_supported_universe(endpoints):
    by_session=defaultdict(list); sessions_by_ind=defaultdict(list); inds_by_cohort=defaultdict(set)
    for r in endpoints:
        key=(r["cohort"],r["session"])
        by_session[key].append(r)
    for key,vals in by_session.items():
        iid=vals[0]["iid"]; cohort=key[0]
        sessions_by_ind[(cohort,iid)].append(key)
        inds_by_cohort[cohort].add(iid)
    supports={k:{r["stratum"] for r in vals} for k,vals in by_session.items()}
    kept=[]; rows=[]; eval_inds=set()
    for key,vals in sorted(by_session.items()):
        cohort,session=key; iid=vals[0]["iid"]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        if not self_keys:
            rows.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":False,"supported_events":0,"reason":"no_other_self_session"})
            continue
        self_support=set().union(*(supports[k] for k in self_keys))
        other_keys=[]
        for other in inds_by_cohort[cohort]:
            if other!=iid:
                other_keys.extend(sessions_by_ind[(cohort,other)])
        if not other_keys:
            rows.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":False,"supported_events":0,"reason":"no_other_individual"})
            continue
        other_support=set().union(*(supports[k] for k in other_keys))
        sv=[r for r in vals if r["stratum"] in self_support and r["stratum"] in other_support]
        ok=len(sv)>=MIN_SUPPORTED
        if ok:
            eval_inds.add(iid); kept.extend(sv)
        rows.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":bool(ok),"supported_events":len(sv),"kinematic_endpoints":len(vals)})
    return kept,rows,sorted(eval_inds)


def open_era5():
    import icechunk
    import xarray as xr
    storage=icechunk.s3_storage(bucket="earthmover-icechunk-era5",prefix="icechunkV2",region="us-east-1",anonymous=True)
    repo=icechunk.Repository.open(storage)
    session=repo.readonly_session("main")
    ds=xr.open_zarr(session.store,group="single/temporal",consolidated=False,chunks=None)
    required={"u10","v10"}
    missing=sorted(required-set(ds.data_vars))
    if missing:
        raise RuntimeError(f"ERA5 temporal group missing {missing}; vars={list(ds.data_vars)[:50]}")
    return ds


def nearest_hour(dt):
    ts=pd.Timestamp(dt)
    if ts.tzinfo is not None:
        ts=ts.tz_convert("UTC").tz_localize(None)
    return (ts+pd.Timedelta(minutes=30)).floor("h")


def annotate_wind(events,ds):
    latv=np.asarray(ds["latitude"].values,dtype=float)
    lonv=np.asarray(ds["longitude"].values,dtype=float)
    # accommodate either [-180,180) or [0,360)
    lon_0360=bool(np.nanmin(lonv)>=0 and np.nanmax(lonv)>180)
    groups=defaultdict(list)
    for i,r in enumerate(events):
        lon=r["lon"]%360.0 if lon_0360 else ((r["lon"]+180.0)%360.0-180.0)
        yi=int(np.argmin(np.abs(latv-r["lat"])))
        # circular distance for longitude
        d=np.abs(lonv-lon); d=np.minimum(d,360.0-d)
        xi=int(np.argmin(d))
        hr=nearest_hour(r["t"])
        r["era5_lat"]=float(latv[yi]); r["era5_lon"]=float(lonv[xi]); r["era5_hour"]=hr.isoformat()
        groups[(yi,xi,hr.year)].append((i,hr))
    for (yi,xi,year),pairs in groups.items():
        hrs=[h for _,h in pairs]
        start=min(hrs); stop=max(hrs)
        point=ds[["u10","v10"]].isel(latitude=yi,longitude=xi).sel(valid_time=slice(np.datetime64(start),np.datetime64(stop))).load()
        times=pd.DatetimeIndex(point["valid_time"].values)
        u=np.asarray(point["u10"].values,dtype=float); v=np.asarray(point["v10"].values,dtype=float)
        lookup={pd.Timestamp(t): (float(uu),float(vv)) for t,uu,vv in zip(times,u,v)}
        for idx,hr in pairs:
            key=pd.Timestamp(hr).tz_localize(None)
            if key not in lookup:
                raise RuntimeError(f"ERA5 hour missing {key} at {yi},{xi}")
            uu,vv=lookup[key]
            events[idx]["u10"]=uu; events[idx]["v10"]=vv; events[idx]["wind_speed"]=float(math.hypot(uu,vv))
    return events


def interval(vals):
    a=np.asarray(vals,dtype=float)
    if len(a)<2:
        return None
    return float(np.quantile(a,0.05)),float(np.quantile(a,0.95))


def panel_support(panel,events,session_rows,eval_inds):
    if len(eval_inds)!=EXPECTED_N[panel]:
        raise RuntimeError(f"{panel}: x-y-time evaluable n {len(eval_inds)} != expected {EXPECTED_N[panel]}")
    by_session=defaultdict(list); sessions_by_ind=defaultdict(list)
    for r in events:
        key=(r["cohort"],r["session"])
        by_session[key].append(r)
    for key,vals in by_session.items():
        sessions_by_ind[(key[0],vals[0]["iid"])].append(key)

    panel_iv=interval([r["wind_speed"] for r in events])
    if panel_iv is None or panel_iv[1]<=panel_iv[0]:
        raise RuntimeError(panel+": degenerate panel wind range")
    panel_span=panel_iv[1]-panel_iv[0]

    ind_rows={}
    span_good=0
    repeat_count=0
    for iid in eval_inds:
        vals=[r for r in events if r["iid"]==iid]
        sess=sorted({r["session"] for r in vals})
        iv=interval([r["wind_speed"] for r in vals])
        frac=((iv[1]-iv[0])/panel_span) if iv else None
        if len(sess)>=2:
            repeat_count+=1
        if frac is not None and frac>=0.4:
            span_good+=1
        ind_rows[iid]={"eligible_sessions":len(sess),"q05":iv[0] if iv else None,"q95":iv[1] if iv else None,"span_fraction":frac}

    session_fraction_rows=[]
    matched_events=[]
    for key,vals in sorted(by_session.items()):
        cohort,session=key; iid=vals[0]["iid"]
        self_keys=[k for k in sessions_by_ind[(cohort,iid)] if k!=key]
        self_vals=[r["wind_speed"] for k in self_keys for r in by_session[k]]
        siv=interval(self_vals)
        donors={}
        for (co,other),keys in sessions_by_ind.items():
            if co!=cohort or other==iid:
                continue
            ov=[r["wind_speed"] for k in keys for r in by_session[k]]
            oiv=interval(ov)
            if oiv: donors[other]=oiv
        nmatch=0
        for r in vals:
            w=r["wind_speed"]
            self_ok=bool(siv and siv[0]<=w<=siv[1])
            nd=sum(lo<=w<=hi for lo,hi in donors.values())
            ok=self_ok and nd>=2
            if ok:
                nmatch+=1; matched_events.append(r)
        session_fraction_rows.append({"cohort":cohort,"session":session,"individual":iid,"events":len(vals),"matched":nmatch,"fraction":nmatch/len(vals) if vals else None})

    by_i=defaultdict(list)
    for r in session_fraction_rows:
        by_i[r["individual"]].append(r["fraction"])
    ind_fracs={iid:float(np.mean(v)) for iid,v in by_i.items() if v}
    panel_matched=float(np.mean(list(ind_fracs.values()))) if ind_fracs else 0.0

    night_counts=defaultdict(int)
    for r in matched_events: night_counts[r["night"]]+=1
    total=sum(night_counts.values())
    max_night=(max(night_counts.values())/total) if total else 1.0

    gates={
        "exact_expected_xy_evaluable_n":len(eval_inds)==EXPECTED_N[panel],
        "repeat_individuals_ge_5":repeat_count>=5,
        "individuals_span_ge_40pct_ge_5":span_good>=5,
        "equal_individual_matched_target_fraction_ge_0_5":panel_matched>=0.5,
        "max_single_night_fraction_le_0_5":max_night<=0.5,
    }
    return {
        "panel":panel,
        "xy_evaluable_individuals":len(eval_inds),
        "repeat_individuals":repeat_count,
        "individuals_span_ge_40pct":span_good,
        "panel_wind_q05":panel_iv[0],"panel_wind_q95":panel_iv[1],
        "equal_individual_matched_target_fraction":panel_matched,
        "matched_event_count":total,
        "max_single_night_fraction":max_night,
        "gates":gates,"pass":all(gates.values()),
        "individuals":ind_rows,"session_environment_support":session_fraction_rows,
        "xy_session_support":session_rows,
    }


def markdown(payload):
    lines=["# ERA5 wind identifiability preflight v1","",
           "**ENVIRONMENT + X-Y-TIME ONLY. No numeric vertical response was parsed or used.**","",
           "| panel | x-y-time n | repeat n | span>=40% n | matched fraction | max night | pass |",
           "|---|---:|---:|---:|---:|---:|---|"]
    for p,x in payload["panels"].items():
        lines.append(f"| {p} | {x['xy_evaluable_individuals']} | {x['repeat_individuals']} | {x['individuals_span_ge_40pct']} | {x['equal_individual_matched_target_fraction']:.3f} | {x['max_single_night_fraction']:.3f} | {'PASS' if x['pass'] else 'FAIL'} |")
    lines += ["",f"Panels passing: **{payload['pass_count']}/4**",f"Reaction-norm outcome may be opened: **{payload['feasible_to_open_vertical_outcome']}**",""]
    return "\n".join(lines)


def main():
    cfg=json.loads(CONTRACT.read_text())
    prepared={}
    for panel in cfg["panels"]:
        records,src=load_xy_time(panel)
        eps,thresholds=kinematic_endpoints(records)
        universe,srows,eval_inds=xy_supported_universe(eps)
        if len(eval_inds)!=EXPECTED_N[panel]:
            raise RuntimeError(f"{panel}: pre-ERA5 x-y-time n {len(eval_inds)} != expected {EXPECTED_N[panel]}")
        prepared[panel]={"events":universe,"session_rows":srows,"eval_inds":eval_inds,"source":src,"thresholds":thresholds}

    ds=open_era5()
    panels={}
    for panel,x in prepared.items():
        annotate_wind(x["events"],ds)
        res=panel_support(panel,x["events"],x["session_rows"],x["eval_inds"])
        res["source_structure"]=x["source"]
        res["kinematic_thresholds"]=x["thresholds"]
        panels[panel]=res

    pc=sum(int(x["pass"]) for x in panels.values())
    payload={
        "schema_version":1,
        "study_id":"batter-strategy-maintenance-wind-support-preflight-v1",
        "classification":"x-y-time + ERA5 wind support only; numeric vertical outcome unopened",
        "era5":{"provider":"Earthmover Icechunk ERA5 public AWS","bucket":"earthmover-icechunk-era5","prefix":"icechunkV2","group":"single/temporal","variables":["u10","v10"],"grid":"0.25 degree","frequency":"hourly"},
        "panels":panels,"pass_count":pc,
        "feasible_to_open_vertical_outcome":pc>=3,
        "decision_rule":"open reaction-norm vertical outcome only if at least 3 of 4 panels pass all frozen support gates",
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text(markdown(payload)+"\n")
    print(json.dumps({"pass_count":pc,"feasible":pc>=3,"panels":{p:{"pass":x["pass"],"matched":x["equal_individual_matched_target_fraction"],"span_good":x["individuals_span_ge_40pct"],"repeat":x["repeat_individuals"],"max_night":x["max_single_night_fraction"]} for p,x in panels.items()}},sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
