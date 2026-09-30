#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=ROOT/"post_freeze_extensions/noctule_independent_validation/contract_v1.json"
OUT=ROOT/"post_freeze_extensions/noctule_independent_validation/preflight_result_v1.json"
OUT_MD=ROOT/"post_freeze_extensions/noctule_independent_validation/PREFLIGHT_RESULT_V1.md"
UA={"User-Agent":"batter-noctule-independent-validation-v1/1.0"}

def present(s):
    txt=s.astype(str).str.strip()
    return s.notna() & txt.ne("") & ~txt.str.lower().isin({"na","nan","null","none"})

def main():
    c=json.loads(CONTRACT.read_text())
    src=c["source"]
    r=requests.get(src["download_url"],headers=UA,timeout=180)
    r.raise_for_status()
    data=r.content
    sha=hashlib.sha256(data).hexdigest()
    if sha!=src["sha256"]:
        raise RuntimeError(f"source sha256 {sha} != frozen {src['sha256']}")

    import io
    df=pd.read_csv(io.BytesIO(data),dtype=str,low_memory=False)
    if len(df)!=int(src["row_count_expected"]):
        raise RuntimeError(f"row count {len(df)} != frozen {src['row_count_expected']}")

    f=src["fields"]
    need=[f["individual"],f["session"],f["x"],f["y"],f["native_vertical"],f["year"],f["field_period"]]
    for col in need:
        if col not in df.columns:
            raise RuntimeError(f"missing frozen field {col}")

    # Vertical magnitude remains unopened: use only presence/non-presence.
    mask=pd.Series(True,index=df.index)
    for col in need:
        mask &= present(df[col])
    d=df.loc[mask,need].copy()
    if d.empty:
        raise RuntimeError("no presence-qualified rows")

    d["x_num"]=pd.to_numeric(d[f["x"]],errors="coerce")
    d["y_num"]=pd.to_numeric(d[f["y"]],errors="coerce")
    d=d.loc[d["x_num"].notna() & d["y_num"].notna()].copy()
    d["iid"]=d[f["individual"]].astype(str)
    d["session"]=d[f["session"]].astype(str)
    d["cohort"]=d[f["year"]].astype(str)+"::"+d[f["field_period"]].astype(str)
    grid=float(c["preflight"]["common_cell_grid_m"])
    d["cx"]=(d["x_num"]/grid).apply(math.floor)
    d["cy"]=(d["y_num"]/grid).apply(math.floor)

    min_session=int(c["preflight"]["minimum_presence_qualified_fixes_per_session"])
    counts=d.groupby(["cohort","iid","session"]).size().rename("n").reset_index()
    elig=counts.loc[counts["n"]>=min_session].copy()
    eligible_keys=set(zip(elig["cohort"],elig["iid"],elig["session"]))
    de=d.loc[d.apply(lambda z:(z["cohort"],z["iid"],z["session"]) in eligible_keys,axis=1)].copy()

    sessions_by=defaultdict(list)
    indivs_by_cohort=defaultdict(set)
    support={}
    session_n={}
    for (cohort,iid,sid),g in de.groupby(["cohort","iid","session"],sort=True):
        key=(cohort,iid,sid)
        sessions_by[(cohort,iid)].append(key)
        indivs_by_cohort[cohort].add(iid)
        support[key]=set(zip(g["cx"].astype(int),g["cy"].astype(int)))
        session_n[key]=len(g)

    repeat_by_cohort={}
    for cohort,ids in sorted(indivs_by_cohort.items()):
        repeat_by_cohort[cohort]=sorted(iid for iid in ids if len(sessions_by[(cohort,iid)])>=2)

    min_target=int(c["preflight"]["minimum_supported_target_fixes"])
    target_rows=[]
    eval_inds_by_cohort=defaultdict(set)
    eval_sessions_by_cohort=defaultdict(list)

    # For exact support counts, count each target row/fix whose cell is in both self and other support.
    for (cohort,iid),self_keys in sorted(sessions_by.items()):
        if len(self_keys)<2:
            continue
        other_keys=[
            k for other in sorted(indivs_by_cohort[cohort])
            if other!=iid
            for k in sessions_by[(cohort,other)]
        ]
        if not other_keys:
            continue
        other_support=set().union(*(support[k] for k in other_keys))
        for key in sorted(self_keys):
            self_train=[k for k in self_keys if k!=key]
            self_support=set().union(*(support[k] for k in self_train))
            g=de.loc[
                (de["cohort"]==cohort)&
                (de["iid"]==iid)&
                (de["session"]==key[2])
            ]
            supported=int(sum((int(cx),int(cy)) in self_support and (int(cx),int(cy)) in other_support
                              for cx,cy in zip(g["cx"],g["cy"])))
            ok=supported>=min_target
            target_rows.append({
                "cohort":cohort,
                "individual":iid,
                "session":key[2],
                "target_fixes":int(len(g)),
                "supported_fixes":supported,
                "evaluable":bool(ok),
                "self_training_sessions":len(self_train),
                "other_individual_count":len(indivs_by_cohort[cohort]-{iid})
            })
            if ok:
                eval_inds_by_cohort[cohort].add(iid)
                eval_sessions_by_cohort[cohort].append(key[2])

    cohort_summary={}
    for cohort in sorted(indivs_by_cohort):
        e=elig.loc[elig["cohort"]==cohort]
        cohort_summary[cohort]={
            "individuals_with_any_track_ge50":int(e["iid"].nunique()),
            "tracks_ge50":int(len(e)),
            "repeat_individuals_ge2_tracks_ge50":len(repeat_by_cohort.get(cohort,[])),
            "repeat_individual_ids":repeat_by_cohort.get(cohort,[]),
            "evaluable_individuals_common_cell":len(eval_inds_by_cohort.get(cohort,set())),
            "evaluable_individual_ids":sorted(eval_inds_by_cohort.get(cohort,set())),
            "evaluable_target_sessions":len(eval_sessions_by_cohort.get(cohort,[]))
        }

    total_eval=len(set((cohort,iid) for cohort,ids in eval_inds_by_cohort.items() for iid in ids))
    gate=total_eval>=int(c["preflight"]["minimum_repeat_individuals_total"])

    payload={
        "schema_version":1,
        "study_id":c["study_id"],
        "source_sha256_verified":sha,
        "numeric_vertical_values_read":False,
        "vertical_operation":"presence only",
        "presence_qualified_rows":int(len(d)),
        "tracks_ge50_total":int(len(elig)),
        "repeat_individual_cohort_units_total":int(sum(len(x) for x in repeat_by_cohort.values())),
        "evaluable_individual_cohort_units_total":int(total_eval),
        "cohorts":cohort_summary,
        "target_sessions":target_rows,
        "preflight_pass":bool(gate),
        "gate":c["preflight"]["gate"],
        "stop_rule":c["stop_rule"]
    }
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

    lines=[
        "# Independent common-noctule validation preflight v1","",
        "**OUTCOME-BLIND: native Height magnitudes were not parsed or summarized.**","",
        f"- source SHA256 verified: `{sha}`",
        f"- presence-qualified rows: **{len(d):,}**",
        f"- >=50-fix tracks: **{len(elig)}**",
        f"- evaluable individual×cohort units under 5-km common-cell support: **{total_eval}**",
        f"- preflight gate: **{'PASS' if gate else 'FAIL'}**","",
        "| cohort | >=50 tracks | repeat individuals | common-cell evaluable individuals | evaluable target sessions |",
        "|---|---:|---:|---:|---:|"
    ]
    for cohort,x in cohort_summary.items():
        lines.append(
            f"| {cohort} | {x['tracks_ge50']} | {x['repeat_individuals_ge2_tracks_ge50']} | "
            f"{x['evaluable_individuals_common_cell']} | {x['evaluable_target_sessions']} |"
        )
    lines.append("")
    OUT_MD.write_text("\n".join(lines))

    print(json.dumps({
        "preflight_pass":gate,
        "evaluable_individual_cohort_units_total":total_eval,
        "tracks_ge50_total":int(len(elig)),
        "cohorts":{k:{
            "tracks_ge50":v["tracks_ge50"],
            "repeat":v["repeat_individuals_ge2_tracks_ge50"],
            "evaluable":v["evaluable_individuals_common_cell"],
            "target_sessions":v["evaluable_target_sessions"]
        } for k,v in cohort_summary.items()}
    },sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
