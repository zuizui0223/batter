#!/usr/bin/env python3
from __future__ import annotations

import hashlib, io, json, math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/nyctalus_resource_context/structural_contract_v1.json"
OUT=ROOT/"post_freeze_extensions/nyctalus_resource_context/structural_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/nyctalus_resource_context/STRUCTURAL_RESULT_V1.md"
UA={"User-Agent":"batter-nyctalus-resource-context-preflight-v1/1.0"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def fetch_file(record_id,name):
    meta=requests.get(f"https://zenodo.org/api/records/{record_id}",headers=UA,timeout=90)
    meta.raise_for_status()
    rec=meta.json()
    target=None
    for f in rec.get("files",[]):
        if (f.get("key") or f.get("filename"))==name:
            target=f; break
    if target is None:
        raise RuntimeError(f"missing source file {name}")
    url=(target.get("links") or {}).get("content") or (target.get("links") or {}).get("self")
    r=requests.get(url,headers=UA,timeout=240)
    r.raise_for_status()
    raw=r.content
    return raw,hashlib.sha256(raw).hexdigest()

def parse_bins(vals):
    return [math.inf if x=="inf" else float(x) for x in vals]

def bin_index(x,edges):
    for i in range(len(edges)-1):
        if edges[i] <= x < edges[i+1]:
            return i
    return len(edges)-2

def link_context(obs,rsf,c):
    used=rsf[rsf["response_rvso"].astype(str)=="1"].copy()
    if len(obs)!=int(c["linkage"]["expected_observed_rows"]) or len(used)!=len(obs):
        raise RuntimeError(f"unexpected observed/used row counts {len(obs)} / {len(used)}")

    rows=[]
    max_allowed=float(c["linkage"]["maximum_allowed_distance_m"])
    all_tracks=sorted(obs["trackid"].astype(str).unique())
    if len(all_tracks)!=int(c["linkage"]["expected_tracks"]):
        raise RuntimeError(f"unexpected track count {len(all_tracks)}")

    for tid in all_tracks:
        og=obs[obs["trackid"].astype(str)==tid].copy()
        ug=used[used["trackid"].astype(str)==tid].copy()
        if len(og)!=len(ug):
            raise RuntimeError(f"track {tid}: observed {len(og)} != RSF used {len(ug)}")
        ox=pd.to_numeric(og["x"],errors="coerce").to_numpy(dtype=float)
        oy=pd.to_numeric(og["y"],errors="coerce").to_numpy(dtype=float)
        ux=pd.to_numeric(ug["x_"],errors="coerce").to_numpy(dtype=float)
        uy=pd.to_numeric(ug["y_"],errors="coerce").to_numpy(dtype=float)
        if not (np.isfinite(ox).all() and np.isfinite(oy).all() and np.isfinite(ux).all() and np.isfinite(uy).all()):
            raise RuntimeError(f"track {tid}: coordinate parse failure")
        D=np.hypot(ox[:,None]-ux[None,:],oy[:,None]-uy[None,:])
        ix=np.argmin(D,axis=1)
        mins=D[np.arange(len(og)),ix]
        if len(set(int(x) for x in ix))!=len(og):
            raise RuntimeError(f"track {tid}: non-bijective nearest assignment")
        if float(mins.max())>max_allowed:
            raise RuntimeError(f"track {tid}: max linkage distance {float(mins.max())} > {max_allowed}")
        ug_reset=ug.reset_index(drop=True)
        og_reset=og.reset_index(drop=True)
        for i,j in enumerate(ix):
            o=og_reset.iloc[i]
            u=ug_reset.iloc[int(j)]
            rows.append({
                "bat_id":str(o["bat_id"]),
                "trackid":str(o["trackid"]),
                "Year":str(o["Year"]).strip(),
                "field_period":str(o["field_period"]).strip(),
                "move_state":str(o["move_state"]).strip(),
                "x":float(ox[i]),
                "y":float(oy[i]),
                "Height_presence":str(o["Height"]),
                "roost_km":str(u[c["fixed_context"]["roost_distance_field"]]),
                "landcover":str(u[c["fixed_context"]["detailed_landcover_field"]]).strip(),
                "forestornot":str(u[c["fixed_context"]["coarse_landcover_field"]]).strip(),
                "link_distance_m":float(mins[i])
            })
    d=pd.DataFrame(rows)
    if len(d)!=len(obs):
        raise RuntimeError("linked row count mismatch")
    return d

def evaluate(d,context_name,c):
    q=d[d["move_state"].isin(c["fixed_context"]["valid_move_states"])].copy()
    q["xcell"]=np.floor(q["x"].astype(float)/float(c["fixed_context"]["horizontal_grid_m"])).astype(int)
    q["ycell"]=np.floor(q["y"].astype(float)/float(c["fixed_context"]["horizontal_grid_m"])).astype(int)
    edges=parse_bins(c["fixed_context"]["roost_distance_bins_km"])
    q["roost_bin"]=[bin_index(float(x),edges) for x in q["roost_km"]]

    base=list(zip(q["xcell"],q["ycell"],q["move_state"].astype(str)))
    if context_name=="roost_only":
        q["stratum"]=[b+(int(rb),) for b,rb in zip(base,q["roost_bin"])]
    elif context_name=="roost_forest":
        q["stratum"]=[b+(int(rb),str(lc)) for b,rb,lc in zip(base,q["roost_bin"],q["forestornot"])]
    elif context_name=="roost_landcover":
        q["stratum"]=[b+(int(rb),str(lc)) for b,rb,lc in zip(base,q["roost_bin"],q["landcover"])]
    else:
        raise ValueError(context_name)

    by_track={}
    tracks_by_ind=defaultdict(list)
    tracks_by_cohort=defaultdict(list)
    for (cohort,tid),g in q.groupby([q["Year"].astype(str)+"::"+q["field_period"].astype(str),"trackid"],sort=True):
        bats=sorted(g["bat_id"].unique())
        if len(bats)!=1:
            raise RuntimeError(f"track {tid} maps to {bats}")
        iid=bats[0]
        rec={
            "cohort":cohort,"trackid":tid,"bat_id":iid,
            "strata":set(g["stratum"].tolist()),
            "target_strata":g["stratum"].tolist(),
            "event_count":int(len(g))
        }
        key=(cohort,tid)
        by_track[key]=rec
        tracks_by_ind[(cohort,iid)].append(key)
        tracks_by_cohort[cohort].append(key)

    min_events=int(c["fixed_context"]["minimum_supported_target_events"])
    rows=[]
    eligible=set()
    for key,rec in sorted(by_track.items()):
        cohort=rec["cohort"]; iid=rec["bat_id"]
        self_keys=[k for k in tracks_by_ind[(cohort,iid)] if k!=key]
        other_keys=[k for k in tracks_by_cohort[cohort] if by_track[k]["bat_id"]!=iid]
        if not self_keys or not other_keys:
            rows.append({"cohort":cohort,"trackid":rec["trackid"],"bat_id":iid,"supported_events":0,"evaluable":False})
            continue
        self_support=set().union(*(by_track[k]["strata"] for k in self_keys))
        other_support=set().union(*(by_track[k]["strata"] for k in other_keys))
        supported=sum(s in self_support and s in other_support for s in rec["target_strata"])
        ok=supported>=min_events
        if ok:
            eligible.add(iid)
        rows.append({
            "cohort":cohort,"trackid":rec["trackid"],"bat_id":iid,
            "target_events":rec["event_count"],"supported_events":int(supported),"evaluable":bool(ok)
        })
    return {
        "eligible_individual_count":len(eligible),
        "eligible_ids":sorted(eligible),
        "eligible_track_count":sum(1 for r in rows if r["evaluable"]),
        "track_support":rows
    }

def main():
    c=json.loads(CONTRACT.read_text())
    rid=int(c["source"]["record_id"])
    obs_raw,obs_sha=fetch_file(rid,c["source"]["observed_file"])
    rsf_raw,rsf_sha=fetch_file(rid,c["source"]["rsf_file"])
    if obs_sha!=c["source"]["observed_sha256"]:
        raise RuntimeError(f"observed source SHA mismatch {obs_sha}")

    obs=pd.read_csv(io.BytesIO(obs_raw),dtype=str,low_memory=False)
    rsf=pd.read_csv(io.BytesIO(rsf_raw),dtype=str,low_memory=False)

    need_obs=["bat_id","trackid","x","y","Height","Year","field_period","move_state"]
    need_rsf=["response_rvso","trackid","x_","y_",
              c["fixed_context"]["roost_distance_field"],
              c["fixed_context"]["detailed_landcover_field"],
              c["fixed_context"]["coarse_landcover_field"]]
    missing=[x for x in need_obs if x not in obs.columns]+[x for x in need_rsf if x not in rsf.columns]
    if missing:
        raise RuntimeError(f"missing fields {missing}")

    mask=pd.Series(True,index=obs.index)
    for col in need_obs:
        mask &= present(obs[col])
    obs=obs.loc[mask,need_obs].copy()
    if len(obs)!=int(c["linkage"]["expected_observed_rows"]):
        raise RuntimeError(f"presence-qualified observed rows {len(obs)} != expected")

    linked=link_context(obs,rsf,c)
    linked["roost_km"]=pd.to_numeric(linked["roost_km"],errors="coerce")
    if linked["roost_km"].isna().any():
        raise RuntimeError(f"roost distance parse failures {int(linked['roost_km'].isna().sum())}")
    if (linked["roost_km"]<0).any():
        raise RuntimeError("negative roost distance")
    if (linked["landcover"].str.strip()=="").any() or (linked["forestornot"].str.strip()=="").any():
        raise RuntimeError("missing land-cover context")

    results={name:evaluate(linked,name,c) for name in c["candidate_contexts"]}
    required=int(c["selection_rule"]["required_n"])
    selected=None
    for name in c["selection_rule"]["priority"]:
        if results[name]["eligible_individual_count"]>=required:
            selected=name
            break

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "numeric_height_values_read":False,
        "observed_sha256":obs_sha,
        "rsf_sha256":rsf_sha,
        "linked_rows":int(len(linked)),
        "linkage_distance_m":{
            "median":float(linked["link_distance_m"].median()),
            "q95":float(linked["link_distance_m"].quantile(0.95)),
            "max":float(linked["link_distance_m"].max())
        },
        "candidate_results":results,
        "required_n":required,
        "selected_context":selected,
        "vertical_test_may_open":selected is not None,
        "decision":(
            f"PASS: freeze {selected} as the only source-RSF resource-context vertical attribution"
            if selected else
            "STRUCTURAL STOP: no resource context retains required support"
        ),
        "claim_boundary":c["claim_boundary"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Nyctalus source-RSF resource-context preflight v1","",
        "**Numeric Height values were never parsed.**","",
        f"- deterministic linked rows: **{len(linked)}**",
        f"- maximum link distance: **{linked['link_distance_m'].max():.3f} m**",
        f"- required evaluable individuals: **{required}**","",
        "| candidate | evaluable n | eligible tracks | gate |",
        "|---|---:|---:|---|"
    ]
    for name in c["selection_rule"]["priority"]:
        x=results[name]
        lines.append(f"| {name} | {x['eligible_individual_count']} | {x['eligible_track_count']} | {'PASS' if x['eligible_individual_count']>=required else 'FAIL'} |")
    lines += ["",f"Selected context: **{selected if selected else 'NONE / STOP'}**","",payload["decision"],""]
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps({
        "candidate_n":{k:v["eligible_individual_count"] for k,v in results.items()},
        "required_n":required,
        "selected_context":selected,
        "vertical_test_may_open":selected is not None,
        "linkage_max_m":float(linked["link_distance_m"].max())
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
