#!/usr/bin/env python3
from __future__ import annotations

import copy,csv,io,json,math,sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core
import scripts.run_eidolon_independent_replication as eid
from post_freeze_extensions.behavior_proxy_inventory.run_v1 import SOURCES,get,canon

CONTRACT=ROOT/"post_freeze_extensions/body_mass_transfer/preflight_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/body_mass_transfer/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/body_mass_transfer/PREFLIGHT_RESULT_V1.md"


def ref_mass(panel):
    data=get(SOURCES[panel]["reference"],panel,"reference")
    rd=csv.DictReader(io.StringIO(data.decode("utf-8-sig"),newline=""))
    m={}
    for raw in rd:
        r={canon(k):("" if v is None else str(v).strip()) for k,v in raw.items() if k is not None}
        try:
            mass=float(r.get("animal_mass",""))
            if not math.isfinite(mass): continue
        except Exception:
            continue
        ids={r.get("animal_id",""),r.get("individual_local_identifier",""),r.get("individual_id","")}
        for iid in ids:
            if iid: m[iid]=mass
    return m


def xy_records(panel):
    if panel=="eidolon":
        gps=eid.get(eid.GPS_URL,eid.GPS_MD5,eid.GPS_SIZE)
        ref=eid.get(eid.REF_URL,eid.REF_MD5)
        rows=eid.read_csv(gps); refs=eid.read_csv(ref)
        pre=eid.build_pre_numeric(rows,refs)
        transformers={c:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True) for c,meta in pre["projections"].items()}
        rec=[]
        for idx,row in enumerate(rows):
            sid=pre["session_for_row"].get(idx)
            if sid is None: continue
            sm=pre["session_meta"][sid]; cohort=sm["cohort"]
            if cohort not in pre["admitted_cohorts"]: continue
            lon=eid.finite_float(row.get("location_long")); lat=eid.finite_float(row.get("location_lat"))
            if lon is None or lat is None: continue
            try: t=eid.parse_time(row.get("timestamp",""))
            except Exception: continue
            x,y=transformers[cohort].transform(lon,lat)
            rec.append({"cohort":cohort,"iid":sm["individual"],"session":sid,"t":t,"x":x,"y":y})
        return rec

    cpath={
      "hypsignathus":"contract/hypsignathus_replication_v1.json",
      "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
      "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
      "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
    }[panel]
    base=json.loads((ROOT/cpath).read_text())
    if panel=="phyllostomus_2016":
        contract=copy.deepcopy(base)
        contract["vertical"]={"field":base["vertical"]["primary_field"],"primary_edges_m":base["vertical"]["edges_m"]}
    else:
        contract=base
    ua="batter-body-mass-transfer-preflight-v1/1.0"
    gps=core.get(contract["source"]["gps"],ua); ref=core.get(contract["source"]["reference"],ua)
    rows,headers=core.read_csv(gps); refs,_=core.read_csv(ref)
    pre=core.build_pre_numeric(rows,headers,refs,contract)
    transformers={c:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True) for c,meta in pre["projections"].items()}
    rec=[]
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None: continue
        sm=pre["session_meta"][sid]; cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]: continue
        lon=core.finite_float(row.get("location_long")); lat=core.finite_float(row.get("location_lat"))
        if lon is None or lat is None: continue
        try: t=core.parse_time(row.get("timestamp",""))
        except Exception: continue
        x,y=transformers[cohort].transform(lon,lat)
        rec.append({"cohort":cohort,"iid":sm["individual"],"session":sid,"t":t,"x":x,"y":y})
    return rec


def angle(a,b,c):
    v1=(b["x"]-a["x"],b["y"]-a["y"]); v2=(c["x"]-b["x"],c["y"]-b["y"])
    n1=math.hypot(*v1); n2=math.hypot(*v2)
    if n1<=0 or n2<=0: return None
    z=max(-1,min(1,(v1[0]*v2[0]+v1[1]*v2[1])/(n1*n2)))
    return math.acos(z)


def state_endpoints(rec,max_dt):
    by=defaultdict(list)
    for r in rec: by[(r["cohort"],r["session"])].append(r)
    ep=[]
    for key,vals in by.items():
        vals=sorted(vals,key=lambda x:x["t"])
        for i in range(2,len(vals)):
            a,b,c=vals[i-2],vals[i-1],vals[i]
            d1=(b["t"]-a["t"]).total_seconds(); d2=(c["t"]-b["t"]).total_seconds()
            if not all(math.isfinite(d) and d>0 and d<=max_dt for d in (d1,d2)): continue
            tr=angle(a,b,c)
            if tr is None: continue
            sp=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/d2
            ep.append({**c,"speed":sp,"turn":tr})
    sp=defaultdict(list); tu=defaultdict(list)
    for r in ep: sp[r["cohort"]].append(r["speed"]);tu[r["cohort"]].append(r["turn"])
    th={c:(float(np.median(sp[c])),float(np.median(tu[c]))) for c in sp}
    out=[]
    for r in ep:
        sm,tm=th[r["cohort"]]
        st=int(r["speed"]>sm)*2+int(r["turn"]>tm)
        out.append({**r,"state":st,"stratum":(math.floor(r["x"]/5000),math.floor(r["y"]/5000),st)})
    return out


def evaluate(panel,c):
    mass=ref_mass(panel)
    ep=state_endpoints(xy_records(panel),int(c["kinematic_state"]["definition"].split("q3_dt1800")[0] or 1800) if False else 1800)
    by_session=defaultdict(list); sessions_by_ind=defaultdict(list); inds_by_cohort=defaultdict(set)
    for r in ep:
        key=(r["cohort"],r["session"])
        by_session[key].append(r)
    for key,vals in by_session.items():
        iid=vals[0]["iid"];cohort=key[0]
        if iid not in mass: continue
        sessions_by_ind[(cohort,iid)].append(key); inds_by_cohort[cohort].add(iid)
    support={k:{r["stratum"] for r in vals} for k,vals in by_session.items()}
    eval_inds=set(); rows=[]
    min_events=int(c["feasibility"]["minimum_supported_target_events"])
    for key,vals in sorted(by_session.items()):
        cohort,session=key;iid=vals[0]["iid"]
        if iid not in mass or iid not in inds_by_cohort[cohort]: continue
        donors=[d for d in inds_by_cohort[cohort] if d!=iid and d in mass]
        donors=sorted(donors,key=lambda d:(abs(mass[d]-mass[iid]),d))
        if len(donors)<2:
            rows.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":False,"reason":"fewer_than_two_mass_donors"});continue
        nclose=math.ceil(len(donors)/2)
        close=donors[:nclose];far=donors[nclose:]
        if not far:
            rows.append({"cohort":cohort,"session":session,"individual":iid,"evaluable":False,"reason":"empty_far_group"});continue
        close_keys=[k for d in close for k in sessions_by_ind[(cohort,d)]]
        far_keys=[k for d in far for k in sessions_by_ind[(cohort,d)]]
        cs=set().union(*(support[k] for k in close_keys)) if close_keys else set()
        fs=set().union(*(support[k] for k in far_keys)) if far_keys else set()
        sup=sum(r["stratum"] in cs and r["stratum"] in fs for r in vals)
        ok=sup>=min_events
        if ok: eval_inds.add(iid)
        rows.append({"cohort":cohort,"session":session,"individual":iid,"close_donors":close,"far_donors":far,"supported_events":int(sup),"target_events":len(vals),"evaluable":ok,"reason":"eligible" if ok else "insufficient_common_support"})
    return {"evaluable_individuals":len(eval_inds),"evaluable_individual_ids":sorted(eval_inds),"session_support":rows}


def main():
    c=json.loads(CONTRACT.read_text())
    results={}
    allpass=True
    for p in c["panels"]:
        x=evaluate(p,c);base=int(c["feasibility"]["baseline_n"][p])
        x["baseline_n"]=base;x["retention_fraction"]=x["evaluable_individuals"]/base
        x["required_n"]=max(5,math.ceil(0.70*base))
        x["panel_pass"]=x["evaluable_individuals"]>=x["required_n"]
        allpass=allpass and x["panel_pass"];results[p]=x
    payload={"schema_version":1,"study_id":c["study_id"],"vertical_values_used":False,"panel_results":results,"feasible_to_open_vertical_outcome":allpass,"stop_rule":c["stop_rule"]}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    OUT_MD.write_text("# Body-mass transfer feasibility preflight v1\n\n**MASS + X-Y-TIME ONLY. No vertical outcome used.**\n\nFeasible: **"+str(allpass)+"**\n")
    print(json.dumps({"feasible":allpass,"counts":{p:results[p]["evaluable_individuals"] for p in c["panels"]},"required":{p:results[p]["required_n"] for p in c["panels"]}},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
