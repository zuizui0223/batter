#!/usr/bin/env python3
"""Outcome-blind cohort/row-grain audit for the randomized early-experience dataset."""

from __future__ import annotations

import io
import json
from collections import Counter, defaultdict
from pathlib import Path
import urllib.parse
import urllib.request

import numpy as np
import openpyxl

HERE=Path(__file__).resolve().parent
OUT=HERE/"COHORT_STRUCTURE_RESULT_V1.json"
OUTMD=HERE/"COHORT_STRUCTURE_RESULT_V1.md"

DATASET="wh7c636y3t"
VERSION=1
TARGET="All seasons personality data.xlsx"
FILE_URL=(
    f"https://data.mendeley.com/api/datasets/{DATASET}/files?"
    + urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
)
HEADERS={"User-Agent":"Mozilla/5.0 batter-early-experience-cohort/1.0","Accept":"application/json,*/*"}

DESIGN_COLS=[
    "Bat_no","Individual","Season","Origin","Colony","Colony type","Trial name","Trial"
]
TRAITS=["Boldness","ExpuNIQUE","AllActivityNormed"]


def get_bytes(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=180) as r:
        return r.read()


def get_json(url):
    return json.loads(get_bytes(url,"application/json").decode("utf-8"))


def rows_from_envelope(x):
    if isinstance(x,list):
        return x
    for k in ("items","files","results","data"):
        if isinstance(x,dict) and isinstance(x.get(k),list):
            return x[k]
    raise RuntimeError("unknown file envelope")


def get_target_file():
    for row in rows_from_envelope(get_json(FILE_URL)):
        name=row.get("filename") or row.get("name")
        if name==TARGET:
            cd=row.get("content_details") or {}
            url=cd.get("download_url") or row.get("download_url")
            if not url:
                raise RuntimeError("target download URL absent")
            return row,url
    raise RuntimeError("target file absent")


def norm_label(x):
    if x is None:
        return None
    if isinstance(x,float) and np.isnan(x):
        return None
    if isinstance(x,float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


def finite_numeric(x):
    try:
        v=float(x)
        return np.isfinite(v)
    except Exception:
        return False


def main():
    meta,url=get_target_file()
    data=get_bytes(url)
    wb=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True)
    ws=wb["Full_Data"]

    it=ws.iter_rows(values_only=True)
    header=list(next(it))
    idx={name:header.index(name) for name in DESIGN_COLS+TRAITS}

    rows=[]
    for raw in it:
        r={name:raw[idx[name]] for name in DESIGN_COLS+TRAITS}
        rows.append(r)
    wb.close()

    design_levels={}
    for col in ("Season","Origin","Colony","Colony type","Trial name","Trial"):
        design_levels[col]=dict(sorted(Counter(
            norm_label(r[col]) for r in rows if norm_label(r[col]) is not None
        ).items()))

    # Structural bat × trial groups.
    groups=defaultdict(list)
    for r in rows:
        bat=norm_label(r["Bat_no"])
        trial=norm_label(r["Trial"])
        if bat is not None and trial is not None:
            groups[(bat,trial)].append(r)

    trait_grain={}
    usable_units={}
    for trait in TRAITS:
        inconsistent=[]
        usable=[]
        for key,rr in groups.items():
            vals=[]
            for r in rr:
                if finite_numeric(r[trait]):
                    vals.append(float(r[trait]))
            # structural distinct count only; values themselves are never reported.
            distinct=len(set(vals))
            if distinct>1:
                inconsistent.append({"bat":key[0],"trial":key[1],"n_distinct":distinct})
            if distinct==1:
                usable.append(key)
        trait_grain[trait]={
            "n_bat_trial_units":len(groups),
            "n_constant_finite_units":len(usable),
            "n_inconsistent_units":len(inconsistent),
            "inconsistent_units":inconsistent[:50],
        }
        usable_units[trait]=set(usable)

    # Design metadata for Season 2 only.
    s2=[r for r in rows if norm_label(r["Season"]) in {"2","2.0","2020-2021","2020–2021"}]
    s2_bats=sorted(set(norm_label(r["Bat_no"]) for r in s2 if norm_label(r["Bat_no"]) is not None))

    bat_meta={}
    metadata_conflicts=[]
    for bat in s2_bats:
        rr=[r for r in s2 if norm_label(r["Bat_no"])==bat]
        meta={}
        for col in ("Origin","Colony","Colony type"):
            vals=sorted(set(norm_label(r[col]) for r in rr if norm_label(r[col]) is not None))
            meta[col]=vals
            if len(vals)>1:
                metadata_conflicts.append({"bat":bat,"column":col,"levels":vals})
        bat_meta[bat]=meta

    complete=[]
    for bat in s2_bats:
        ok=True
        for trial in ("1","2","3"):
            for trait in TRAITS:
                if (bat,trial) not in usable_units[trait]:
                    ok=False
        if ok:
            complete.append(bat)

    def single(meta,col):
        vals=meta.get(col,[])
        return vals[0] if len(vals)==1 else None

    treatment_counts=Counter()
    origin_treatment=Counter()
    for bat in complete:
        tr=single(bat_meta[bat],"Colony type")
        org=single(bat_meta[bat],"Origin")
        treatment_counts[tr]+=1
        origin_treatment[(org,tr)]+=1

    gate=(
        len(metadata_conflicts)==0
        and all(trait_grain[t]["n_inconsistent_units"]==0 for t in TRAITS)
        and len(complete)>=20
        and len([k for k in treatment_counts if k is not None])==2
    )

    result={
        "source_file":TARGET,
        "sha256":(meta.get("content_details") or {}).get("sha256_hash") or meta.get("sha256_hash"),
        "n_raw_rows":len(rows),
        "design_levels":design_levels,
        "n_bat_trial_groups":len(groups),
        "trait_grain":trait_grain,
        "season2_n_bats":len(s2_bats),
        "season2_complete_trials_1_3_n":len(complete),
        "season2_complete_treatment_counts":{str(k):int(v) for k,v in treatment_counts.items()},
        "season2_complete_origin_treatment_counts":{
            f"{org} | {tr}":int(v) for (org,tr),v in sorted(origin_treatment.items(),key=lambda x:str(x[0]))
        },
        "metadata_conflicts":metadata_conflicts,
        "gate":"PASS_OPEN_FROZEN_PRIMARY" if gate else "STOP_STRUCTURE_MISMATCH",
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Early-experience cohort structure result v1","",
        "**DESIGN / GRAIN ONLY — NO TRAIT VALUES REPORTED.**","",
        f"- raw rows: **{len(rows)}**",
        f"- bat × trial groups: **{len(groups)}**",
        f"- Season 2 source bats: **{len(s2_bats)}**",
        f"- Season 2 complete Trials 1–3 cohort: **{len(complete)}**",
        f"- treatment counts in complete cohort: **{dict(treatment_counts)}**",
        "",
        "## Origin × treatment counts","",
    ]
    for (org,tr),n in sorted(origin_treatment.items(),key=lambda x:str(x[0])):
        lines.append(f"- {org} | {tr}: {n}")
    lines += ["","## Trait row-grain checks",""]
    for trait in TRAITS:
        g=trait_grain[trait]
        lines.append(
            f"- {trait}: constant finite units={g['n_constant_finite_units']}; "
            f"inconsistent units={g['n_inconsistent_units']}"
        )
    lines += ["","## Verdict","",f"**{result['gate']}**",""]
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())


if __name__=="__main__":
    main()
