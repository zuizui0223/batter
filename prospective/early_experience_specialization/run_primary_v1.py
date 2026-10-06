#!/usr/bin/env python3
"""Frozen randomized early-experience individualization primary v1.

Runs only after COHORT_STRUCTURE_RESULT_V1.json authorizes numerical opening.
"""

from __future__ import annotations

import io
import json
from collections import defaultdict, Counter
from pathlib import Path
import urllib.parse
import urllib.request

import numpy as np
import openpyxl

HERE=Path(__file__).resolve().parent
GATE=HERE/"COHORT_STRUCTURE_RESULT_V1.json"
OUT=HERE/"PRIMARY_RESULT_V1.json"
OUTMD=HERE/"PRIMARY_RESULT_V1.md"

DATASET="wh7c636y3t"
VERSION=1
TARGET="All seasons personality data.xlsx"
FILE_URL=(
    f"https://data.mendeley.com/api/datasets/{DATASET}/files?"
    + urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
)
HEADERS={"User-Agent":"Mozilla/5.0 batter-early-experience-primary/1.0","Accept":"application/json,*/*"}

TRAITS=("Boldness","ExpuNIQUE","AllActivityNormed")
NPERM=199_999
SEED=202610070817


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


def download_target():
    for row in rows_from_envelope(get_json(FILE_URL)):
        name=row.get("filename") or row.get("name")
        if name==TARGET:
            cd=row.get("content_details") or {}
            url=cd.get("download_url") or row.get("download_url")
            if not url:
                raise RuntimeError("target download URL absent")
            return get_bytes(url)
    raise RuntimeError("target file absent")


def label(x):
    if x is None:
        return None
    if isinstance(x,float) and np.isnan(x):
        return None
    if isinstance(x,float) and x.is_integer():
        return str(int(x))
    return str(x).strip()


def one_numeric(values,bat,trial,trait):
    out=[]
    for x in values:
        try:
            v=float(x)
            if np.isfinite(v):
                out.append(v)
        except Exception:
            pass
    uniq=sorted(set(out))
    if len(uniq)!=1:
        raise RuntimeError(
            f"trait grain drift bat={bat} trial={trial} trait={trait} distinct={len(uniq)}"
        )
    return uniq[0]


def load_units():
    data=download_target()
    wb=openpyxl.load_workbook(io.BytesIO(data),read_only=True,data_only=True)
    ws=wb["Full_Data"]
    it=ws.iter_rows(values_only=True)
    header=list(next(it))
    needed=["Bat_no","Season","Origin","Colony type","Trial",*TRAITS]
    idx={x:header.index(x) for x in needed}

    raw=[]
    for row in it:
        raw.append({x:row[idx[x]] for x in needed})
    wb.close()

    groups=defaultdict(list)
    meta=defaultdict(lambda:{"origin":set(),"treatment":set(),"season":set()})
    for r in raw:
        bat=label(r["Bat_no"])
        trial=label(r["Trial"])
        season=label(r["Season"])
        if bat is None or trial is None:
            continue
        groups[(bat,trial)].append(r)
        if season is not None:
            meta[bat]["season"].add(season)
        if label(r["Origin"]) is not None:
            meta[bat]["origin"].add(label(r["Origin"]))
        if label(r["Colony type"]) is not None:
            meta[bat]["treatment"].add(label(r["Colony type"]))

    units={}
    for (bat,trial),rr in groups.items():
        season_levels={label(r["Season"]) for r in rr if label(r["Season"]) is not None}
        if not any(x in {"2","2.0","2020-2021","2020–2021"} for x in season_levels):
            continue
        try:
            y=np.array([one_numeric([r[t] for r in rr],bat,trial,t) for t in TRAITS],dtype=float)
        except RuntimeError:
            continue
        units[(bat,trial)]=y

    bats=sorted({
        bat for (bat,tr) in units
        if all((bat,t) in units for t in ("1","2","3"))
    })

    rows=[]
    for bat in bats:
        origins=meta[bat]["origin"]
        treatments=meta[bat]["treatment"]
        if len(origins)!=1 or len(treatments)!=1:
            raise RuntimeError(f"metadata conflict {bat}: origin={origins}, treatment={treatments}")
        rows.append({
            "bat":bat,
            "origin":next(iter(origins)),
            "treatment":next(iter(treatments)),
            "y1":units[(bat,"1")],
            "y2":units[(bat,"2")],
            "y3":units[(bat,"3")],
        })
    return rows


def classify_treatment(x):
    q=x.lower()
    if "enrich" in q and "impover" not in q:
        return "enriched"
    if "impover" in q:
        return "impoverished"
    raise RuntimeError(f"unknown treatment label {x!r}")


def statistic(delta,treatment):
    enriched=np.where(treatment=="enriched")[0]
    impoverished=np.where(treatment=="impoverished")[0]
    if len(enriched)==0 or len(impoverished)==0:
        raise RuntimeError("empty treatment group")

    def v(idxs):
        x=delta[idxs]
        resid=x-x.mean(axis=0,keepdims=True)
        return float(np.mean(np.sum(resid*resid,axis=1)))

    ve=v(enriched)
    vi=v(impoverished)
    return ve-vi,ve,vi


def main():
    gate=json.loads(GATE.read_text())
    if gate.get("gate")!="PASS_OPEN_FROZEN_PRIMARY":
        raise SystemExit("STOP: cohort structure gate did not authorize numerical primary")

    rows=load_units()
    if len(rows)!=gate.get("season2_complete_trials_1_3_n"):
        raise RuntimeError("complete cohort count drift from structural receipt")

    treatment=np.array([classify_treatment(r["treatment"]) for r in rows],dtype=object)
    origin=np.array([r["origin"] for r in rows],dtype=object)

    tc=Counter(treatment)
    if sorted(tc.values())!=[14,15]:
        raise RuntimeError(f"unexpected treatment counts {tc}")

    # Pooled pre-treatment scaling from Trials 1–2 only.
    pre=np.vstack([r["y1"] for r in rows]+[r["y2"] for r in rows])
    mu=pre.mean(axis=0)
    sd=pre.std(axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0):
        raise RuntimeError("nonfinite/zero baseline SD")

    z1=np.vstack([(r["y1"]-mu)/sd for r in rows])
    z2=np.vstack([(r["y2"]-mu)/sd for r in rows])
    z3=np.vstack([(r["y3"]-mu)/sd for r in rows])
    baseline=(z1+z2)/2
    delta=z3-baseline

    obs,ve,vi=statistic(delta,treatment)

    baseline_means={}
    for g in ("enriched","impoverished"):
        idx=np.where(treatment==g)[0]
        baseline_means[g]=baseline[idx].mean(axis=0)
    baseline_mean_distance=float(np.linalg.norm(
        baseline_means["enriched"]-baseline_means["impoverished"]
    ))

    strata=[]
    for org in sorted(set(origin)):
        idx=np.where(origin==org)[0]
        n_enriched=int(np.sum(treatment[idx]=="enriched"))
        strata.append((org,idx,n_enriched))

    rng=np.random.default_rng(SEED)
    extreme=0
    null_sum=0.0
    null_sq=0.0

    for _ in range(NPERM):
        perm=np.empty(len(rows),dtype=object)
        for org,idx,k in strata:
            chosen=rng.choice(idx,size=k,replace=False)
            perm[idx]="impoverished"
            perm[chosen]="enriched"
        d,_,_=statistic(delta,perm)
        null_sum+=d
        null_sq+=d*d
        if d>=obs-1e-15:
            extreme+=1

    p=(1+extreme)/(NPERM+1)
    null_mean=null_sum/NPERM
    null_sd=float(max(0.0,null_sq/NPERM-null_mean**2)**0.5)

    result={
        "version":1,
        "source":"10.17632/wh7c636y3t.1",
        "traits":list(TRAITS),
        "n":len(rows),
        "treatment_counts":dict(tc),
        "origin_treatment_counts":{
            f"{org} | {g}":int(np.sum((origin==org)&(treatment==g)))
            for org in sorted(set(origin)) for g in ("enriched","impoverished")
        },
        "baseline_scaling_sd":sd.tolist(),
        "baseline_mean_distance":baseline_mean_distance,
        "V_enriched":ve,
        "V_impoverished":vi,
        "D":obs,
        "n_permutations":NPERM,
        "seed":SEED,
        "null_mean":null_mean,
        "null_sd":null_sd,
        "extreme_count":extreme,
        "p_one_sided":p,
        "verdict":"SUPPORTED_INDIVIDUALIZATION" if (obs>0 and p<=0.05) else "UNSUPPORTED_INDIVIDUALIZATION",
    }
    OUT.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")

    lines=[
        "# Early-experience individualization primary result v1","",
        f"- n = **{result['n']}**",
        f"- enriched / impoverished = **{tc.get('enriched',0)} / {tc.get('impoverished',0)}**",
        f"- V_enriched = **{ve:.6f}**",
        f"- V_impoverished = **{vi:.6f}**",
        f"- D = **{obs:+.6f}**",
        f"- randomizations = **{NPERM:,}**",
        f"- p_one_sided = **{p:.6f}**",
        f"- verdict = **{result['verdict']}**","",
        "## Design audit","",
        f"- baseline mean-vector distance = {baseline_mean_distance:.6f}",
    ]
    for key,val in result["origin_treatment_counts"].items():
        lines.append(f"- {key}: {val}")
    lines += ["","The primary tests dispersion of individual change vectors after removing the common treatment-group mean change.",""]
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())


if __name__=="__main__":
    main()
