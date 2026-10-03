#!/usr/bin/env python3
from __future__ import annotations

import json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))

import scripts.run_new_species_replications as core

OUT=ROOT/"prospective/route_emergence/source_preflight_v1.json"
OUT_MD=ROOT/"prospective/route_emergence/SOURCE_PREFLIGHT_RESULT_V1.md"

PANELS={
    "hypsignathus":"contract/hypsignathus_replication_v1.json",
    "phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
    "phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
    "phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json",
}

META_TOKENS=(
    "age","life","stage","sex","reproduct","lact","preg","juven","adult",
    "manip","site","deploy","capture","release","transloc","relocat","comment",
    "remark","description","status","death","birth","group","colony","roost"
)
NOVELTY_TOKENS=(
    "juvenile","juven","subadult","newly","volant","transloc","relocat",
    "novel","release","released","reintroduction","reintroduced","moved",
    "new site","new roost","experimental"
)

def selected_metadata(refs,headers):
    cols=[h for h in headers if any(t in h.lower() for t in META_TOKENS)]
    values={}
    novelty_hits=[]
    for h in cols:
        vv=sorted({str(r.get(h,"")).strip() for r in refs if str(r.get(h,"")).strip()})
        values[h]=vv[:50]
        for v in vv:
            lv=v.lower()
            if any(t in lv for t in NOVELTY_TOKENS):
                novelty_hits.append({"field":h,"value":v})
    return cols,values,novelty_hits

def build_xy_sessions(rows,headers,refs,contract):
    refmap=core.reference_map(refs)
    explicit_present=any(f in headers for f in core.OUTLIER_FIELDS)
    min_session=int(contract["exclusions"]["session_minimum_events"])
    candidates=defaultdict(list)

    for idx,row in enumerate(rows):
        animal=core.iid(row)
        if not animal: continue
        ref=refmap.get(animal,{})
        if ref.get("manipulated"): continue
        if core.source_outlier(row,explicit_present): continue
        lon=core.finite_float(row.get("location_long"))
        lat=core.finite_float(row.get("location_lat"))
        if lon is None or lat is None: continue
        try: t=core.parse_time(row.get("timestamp",""))
        except Exception: continue
        site=ref.get("site")
        if not site: continue
        candidates[animal].append((idx,t,lon,lat,site))

    sessions=defaultdict(list)
    for animal,vals in sorted(candidates.items()):
        blocks=core.split_blocks(vals,4*3600)
        for sidx,block in enumerate(blocks,1):
            if len(block)<min_session: continue
            tmed=sorted(x[1] for x in block)[len(block)//2]
            sessions[animal].append({
                "session":f"{animal}::S{sidx}",
                "rows":len(block),
                "median_time":tmed,
                "first_time":min(x[1] for x in block),
                "last_time":max(x[1] for x in block),
                "site_values":sorted({x[4] for x in block}),
            })
    return sessions

def main():
    result={"schema_version":1,"study_id":"batter-personal-3d-route-emergence-source-preflight-v1",
            "classification":"reference metadata + x-y-time only; no route-shape or vertical outcome opened",
            "panels":{}}
    for panel,path in PANELS.items():
        c=json.loads((ROOT/path).read_text())
        ua="batter-route-emergence-source-preflight-v1/1.0"
        gps=core.get(c["source"]["gps"],ua)
        ref=core.get(c["source"]["reference"],ua)
        rows,headers=core.read_csv(gps)
        refs,ref_headers=core.read_csv(ref)
        cols,meta,novelty=selected_metadata(refs,ref_headers)
        sessions=build_xy_sessions(rows,headers,refs,c)

        individuals=[]
        qualifying=[]
        for iid,ss in sorted(sessions.items()):
            times=sorted(x["median_time"] for x in ss)
            span=(times[-1]-times[0]).total_seconds()/86400 if len(times)>=2 else 0.0
            row={"individual":iid,"eligible_sessions":len(ss),"span_days":float(span),
                 "first_session":times[0].isoformat() if times else None,
                 "last_session":times[-1].isoformat() if times else None}
            individuals.append(row)
            if len(ss)>=6 and span>=7:
                qualifying.append(iid)

        result["panels"][panel]={
            "taxon":c.get("taxon","Phyllostomus hastatus" if "phyllostomus" in panel else None),
            "gps_rows":len(rows),
            "reference_rows":len(refs),
            "reference_metadata_columns":cols,
            "reference_metadata_values":meta,
            "novelty_or_reset_token_hits":novelty,
            "individuals_with_eligible_xy_sessions":len(individuals),
            "individuals_qualifying_for_three_phase_structure":len(qualifying),
            "qualifying_individual_ids":qualifying,
            "structural_pass":len(qualifying)>=5,
            "individual_session_structure":individuals,
        }

    result["any_explicit_novelty_or_reset_token"]=any(
        x["novelty_or_reset_token_hits"] for x in result["panels"].values())
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

    lines=["# Personal 3-D route emergence source preflight v1","",
           "**REFERENCE METADATA + X-Y-TIME ONLY. No route-shape or vertical outcome opened.**","",
           "| panel | individuals with sessions | >=6 sessions & >=7 d | structural pass | novelty/reset metadata token |",
           "|---|---:|---:|---|---|"]
    for p,x in result["panels"].items():
        lines.append(f"| {p} | {x['individuals_with_eligible_xy_sessions']} | {x['individuals_qualifying_for_three_phase_structure']} | {'PASS' if x['structural_pass'] else 'FAIL'} | {'yes' if x['novelty_or_reset_token_hits'] else 'no'} |")
    lines += ["",
      "Structural PASS only means a chronological three-phase analysis would have replication.",
      "It does not establish Tier A/B route formation; first tracking is not assumed to be first environmental experience.",
      "",
      f"Any explicit novelty/reset token in reference metadata: **{result['any_explicit_novelty_or_reset_token']}**",
      ""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
      "panels":{p:{"qualifying_n":x["individuals_qualifying_for_three_phase_structure"],
                    "structural_pass":x["structural_pass"],
                    "novelty_hits":x["novelty_or_reset_token_hits"]}
                for p,x in result["panels"].items()},
      "any_explicit_novelty_or_reset_token":result["any_explicit_novelty_or_reset_token"]
    },sort_keys=True))

if __name__=="__main__":
    main()
