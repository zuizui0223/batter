#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import sys

import numpy as np
from pyproj import Transformer

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_biological_effect_translation as bet
import scripts.run_cross_panel_endpoint_exclusion as endpoint
import scripts.run_new_species_replications as core
import scripts.run_eidolon_independent_replication as eid

CONTRACT=Path("contract/tag_altitude_bias_preflight_v1.json")


def load_contract():
    cfg=json.loads(CONTRACT.read_text(encoding="utf-8"))
    return cfg,{p["id"]:p for p in cfg["panels"]}


def _canon_refs(refs):
    return refs


def _metadata_by_individual(refs):
    out=defaultdict(lambda: defaultdict(set))
    for r in refs:
        iid=str(
            r.get("animal_id")
            or r.get("individual_local_identifier")
            or r.get("individual_id")
            or ""
        ).strip()
        if not iid:
            continue
        for f in ("deployment_id","tag_local_identifier","tag_id","deploy_on_date","deploy_off_date"):
            v=str(r.get(f,"")).strip()
            if v:
                out[iid][f].add(v)
    return {
        iid:{f:sorted(vals) for f,vals in sorted(fields.items())}
        for iid,fields in sorted(out.items())
    }


def load_structural_panel(panel_id):
    cfg,panels=load_contract()
    spec=panels[panel_id]
    refs=[]

    if panel_id=="tadarida":
        rows=bet.get_tad_rows()
        tr=Transformer.from_crs("EPSG:4326","EPSG:3035",always_xy=True)
        by_session=defaultdict(list)
        for idx,row in enumerate(rows):
            iid=str(row.get("animal-id","")).strip()
            day=str(row.get("BatDay","")).strip()
            lon=bet.finite_float(row.get("location-long"))
            lat=bet.finite_float(row.get("location-lat"))
            raw_height=str(row.get("height-above-msl","")).strip()
            if not iid or not day or lon is None or lat is None or not raw_height:
                continue
            try:
                t=core.parse_time(row.get("timestamp",""))
            except Exception:
                continue
            x,y=tr.transform(lon,lat)
            sid=f"{iid}::{day}"
            by_session[sid].append({
                "cohort":"focal",
                "iid":iid,
                "session":sid,
                "t":t,
                "x":float(x),
                "y":float(y),
            })
        retained={sid for sid,vals in by_session.items() if len(vals)>=50}
        records=[r for sid in sorted(retained) for r in sorted(by_session[sid],key=lambda z:z["t"])]
        session_meta={
            sid:{
                "individual":by_session[sid][0]["iid"],
                "cohort":"focal",
                "status":"eligible",
            }
            for sid in sorted(retained)
        }
        admitted=["focal"]
        source={"rows":len(rows),"structural_session_count":len(retained)}
        metadata={}
        return spec,records,session_meta,admitted,metadata,source

    if panel_id=="eidolon":
        gps=eid.get(eid.GPS_URL,eid.GPS_MD5,eid.GPS_SIZE)
        ref=eid.get(eid.REF_URL,eid.REF_MD5)
        rows=eid.read_csv(gps)
        refs=eid.read_csv(ref)
        pre=eid.build_pre_numeric(rows,refs)
        finite_float=eid.finite_float
        parse_time=eid.parse_time
    else:
        source_contract=json.loads(Path(spec["contract"]).read_text(encoding="utf-8"))
        if panel_id=="phyllostomus_2016":
            c=copy.deepcopy(source_contract)
            c["vertical"]={
                "field":source_contract["vertical"]["primary_field"],
                "primary_edges_m":source_contract["vertical"]["edges_m"],
            }
            source_contract=c
        ua="batter-tag-altitude-bias-preflight-v1/1.0"
        gps=core.get(source_contract["source"]["gps"],ua)
        ref=core.get(source_contract["source"]["reference"],ua)
        rows,headers=core.read_csv(gps)
        refs,_=core.read_csv(ref)
        pre=core.build_pre_numeric(rows,headers,refs,source_contract)
        finite_float=core.finite_float
        parse_time=core.parse_time

    transformers={
        cohort:Transformer.from_crs("EPSG:4326",f"EPSG:{meta['epsg']}",always_xy=True)
        for cohort,meta in pre["projections"].items()
    }
    records=[]
    for idx,row in enumerate(rows):
        sid=pre["session_for_row"].get(idx)
        if sid is None:
            continue
        sm=pre["session_meta"][sid]
        cohort=sm["cohort"]
        if cohort not in pre["admitted_cohorts"]:
            continue
        lon=finite_float(row.get("location_long"))
        lat=finite_float(row.get("location_lat"))
        if lon is None or lat is None:
            continue
        try:
            t=parse_time(row.get("timestamp",""))
        except Exception:
            continue
        x,y=transformers[cohort].transform(lon,lat)
        records.append({
            "cohort":cohort,
            "iid":sm["individual"],
            "session":sid,
            "t":t,
            "x":float(x),
            "y":float(y),
        })
    source={
        "rows":len(rows),
        "structural_session_count":len({r["session"] for r in records}),
        "admitted_cohorts":list(pre["admitted_cohorts"]),
    }
    return spec,records,pre["session_meta"],list(pre["admitted_cohorts"]),_metadata_by_individual(refs),source


def stationary_candidates(records,max_speed,max_gap):
    by_session=defaultdict(list)
    for r in records:
        by_session[(r["cohort"],r["session"])].append(r)

    out=[]
    session_counts={}
    for key,vals in sorted(by_session.items()):
        vals=sorted(vals,key=lambda r:r["t"])
        n=0
        for i in range(1,len(vals)-1):
            a,b,c=vals[i-1],vals[i],vals[i+1]
            dt1=(b["t"]-a["t"]).total_seconds()
            dt2=(c["t"]-b["t"]).total_seconds()
            if not (0<dt1<=max_gap and 0<dt2<=max_gap):
                continue
            s1=math.hypot(b["x"]-a["x"],b["y"]-a["y"])/dt1
            s2=math.hypot(c["x"]-b["x"],c["y"]-b["y"])/dt2
            if s1<=max_speed and s2<=max_speed:
                out.append(b)
                n+=1
        session_counts[f"{key[0]}::{key[1]}"]=n
    return out,session_counts


def shared_stationary_support(candidates,cell_m,min_ind,min_per_ind,min_total_individual_fixes,min_shared_cells):
    by_cell=defaultdict(lambda: defaultdict(list))
    for r in candidates:
        cell=(math.floor(r["x"]/cell_m),math.floor(r["y"]/cell_m))
        by_cell[(r["cohort"],cell)][r["iid"]].append(r)

    shared={}
    for (cohort,cell),by_iid in sorted(by_cell.items()):
        supported={iid:vals for iid,vals in by_iid.items() if len(vals)>=min_per_ind}
        if len(supported)>=min_ind:
            shared[(cohort,cell)]=supported

    individual=defaultdict(lambda: {"fixes":0,"cells":set(),"cohorts":set()})
    for (cohort,cell),by_iid in shared.items():
        for iid,vals in by_iid.items():
            individual[iid]["fixes"]+=len(vals)
            individual[iid]["cells"].add((cohort,cell))
            individual[iid]["cohorts"].add(cohort)

    supported_individuals={}
    for iid,v in sorted(individual.items()):
        if v["fixes"]>=min_total_individual_fixes and len(v["cells"])>=min_shared_cells:
            supported_individuals[iid]={
                "stationary_candidate_fixes_in_shared_cells":int(v["fixes"]),
                "shared_cell_count":int(len(v["cells"])),
                "cohorts":sorted(v["cohorts"]),
            }

    shared_summary={
        f"{cohort}::{cell[0]}::{cell[1]}":{
            "distinct_individuals":len(by_iid),
            "individual_fix_counts":{iid:len(vals) for iid,vals in sorted(by_iid.items())},
        }
        for (cohort,cell),by_iid in shared.items()
    }
    return shared_summary,supported_individuals


def temporal_overlap(records):
    by=defaultdict(list)
    for r in records:
        by[(r["cohort"],r["iid"])].append(r["t"])

    pair_rows=[]
    cohorts=sorted({c for c,_ in by})
    for cohort in cohorts:
        ids=sorted(i for c,i in by if c==cohort)
        windows={iid:(min(by[(cohort,iid)]),max(by[(cohort,iid)])) for iid in ids}
        for i in range(len(ids)):
            for j in range(i+1,len(ids)):
                a,b=ids[i],ids[j]
                a0,a1=windows[a]; b0,b1=windows[b]
                start=max(a0,b0); end=min(a1,b1)
                overlap=max(0.0,(end-start).total_seconds()/3600.0)
                start_diff=abs((a0-b0).total_seconds())/86400.0
                pair_rows.append({
                    "cohort":cohort,
                    "i":a,
                    "j":b,
                    "overlap_hours":overlap,
                    "start_difference_days":start_diff,
                })

    if not pair_rows:
        return {
            "individual_pairs":0,
            "positive_overlap_fraction":None,
            "median_positive_overlap_hours":None,
            "median_start_difference_days":None,
            "q25_start_difference_days":None,
            "q75_start_difference_days":None,
        }
    overlaps=np.asarray([r["overlap_hours"] for r in pair_rows],dtype=float)
    starts=np.asarray([r["start_difference_days"] for r in pair_rows],dtype=float)
    pos=overlaps[overlaps>0]
    return {
        "individual_pairs":int(len(pair_rows)),
        "positive_overlap_fraction":float(np.mean(overlaps>0)),
        "median_positive_overlap_hours":float(np.median(pos)) if len(pos) else None,
        "median_start_difference_days":float(np.median(starts)),
        "q25_start_difference_days":float(np.quantile(starts,0.25)),
        "q75_start_difference_days":float(np.quantile(starts,0.75)),
    }


def cohort_supported_repeat_counts(records,supported_ids):
    sessions=defaultdict(set)
    for r in records:
        if r["iid"] in supported_ids:
            sessions[(r["cohort"],r["iid"])].add(r["session"])
    out=defaultdict(list)
    for (cohort,iid),sids in sessions.items():
        if len(sids)>=2:
            out[cohort].append(iid)
    return {c:len(set(ids)) for c,ids in sorted(out.items())}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--panel",required=True)
    args=ap.parse_args()

    cfg,panels=load_contract()
    if args.panel not in panels:
        raise SystemExit(f"unknown panel {args.panel}")
    spec,records,session_meta,admitted,metadata,source=load_structural_panel(args.panel)

    sd=cfg["stationary_definition"]
    candidates,session_candidate_counts=stationary_candidates(
        records,float(sd["speed_max_m_per_s"]),int(sd["neighbor_gap_max_s"])
    )
    shared,supported=shared_stationary_support(
        candidates,
        float(sd["stationary_grid_cell_m"]),
        int(sd["shared_cell_rule"]["min_distinct_individuals"]),
        int(sd["shared_cell_rule"]["min_stationary_candidate_fixes_per_individual_in_cell"]),
        int(sd["individual_offset_support_rule"]["min_stationary_candidate_fixes_across_shared_cells"]),
        int(sd["individual_offset_support_rule"]["min_shared_cells"]),
    )

    threshold=max(5,math.ceil(0.5*int(spec["original_evaluable_n"])))
    cohort_repeat=cohort_supported_repeat_counts(records,set(supported))
    cohort_ok=any(v>=3 for v in cohort_repeat.values())
    feasible=len(supported)>=threshold and cohort_ok

    deployment_multi={
        iid:{
            "deployment_id_count":len(fields.get("deployment_id",[])),
            "tag_local_identifier_count":len(fields.get("tag_local_identifier",[])),
            "tag_id_count":len(fields.get("tag_id",[])),
            "metadata":fields,
        }
        for iid,fields in sorted(metadata.items())
    }

    payload={
        "study_id":cfg["study_id"],
        "contract":str(CONTRACT),
        "panel_id":args.panel,
        "taxon":spec["taxon"],
        "numeric_vertical_values_parsed":False,
        "source":source,
        "stationary":{
            "candidate_fix_count":len(candidates),
            "sessions_with_candidates":int(sum(v>0 for v in session_candidate_counts.values())),
            "session_candidate_counts":session_candidate_counts,
            "shared_cell_count":len(shared),
            "shared_cells":shared,
            "supported_individual_count":len(supported),
            "supported_individuals":supported,
            "feasibility_threshold":threshold,
            "supported_repeat_individuals_by_cohort":cohort_repeat,
            "cohort_requirement_met":cohort_ok,
            "stationary_correction_feasible":feasible,
        },
        "deployment_metadata":{
            "individuals_with_metadata":len(deployment_multi),
            "individuals_with_multiple_deployment_ids":sum(v["deployment_id_count"]>1 for v in deployment_multi.values()),
            "individuals_with_multiple_tag_local_identifiers":sum(v["tag_local_identifier_count"]>1 for v in deployment_multi.values()),
            "individuals_with_multiple_tag_ids":sum(v["tag_id_count"]>1 for v in deployment_multi.values()),
            "individual_details":deployment_multi,
        },
        "temporal_overlap":temporal_overlap(records),
        "claim_boundary":{
            "feasibility_not_evidence_for_or_against_tag_bias":True,
            "timing_summary_descriptive_only":True,
            "no_vertical_values_opened":True,
        }
    }
    out=Path(f"results/tag_altitude_bias_preflight_{args.panel}_v1.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "panel":args.panel,
        "stationary_correction_feasible":feasible,
        "candidate_fixes":len(candidates),
        "shared_cells":len(shared),
        "supported_individuals":len(supported),
        "threshold":threshold,
        "cohort_repeat":cohort_repeat,
        "temporal_overlap":payload["temporal_overlap"],
        "multi_deployment_ids":payload["deployment_metadata"]["individuals_with_multiple_deployment_ids"],
        "multi_tag_ids":payload["deployment_metadata"]["individuals_with_multiple_tag_ids"],
    },sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
