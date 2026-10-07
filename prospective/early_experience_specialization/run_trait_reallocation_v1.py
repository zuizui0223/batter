#!/usr/bin/env python3
"""Descriptive exact additive decomposition of the frozen Rachum primary across 3 traits.

No p-values. Primary verdict cannot change.
"""

from __future__ import annotations
import io,json,urllib.parse,urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np, openpyxl

HERE=Path(__file__).resolve().parent
PRIMARY=HERE/"PRIMARY_RESULT_V1.json"
OUT=HERE/"TRAIT_REALLOCATION_RESULT_V1.json"
OUTMD=HERE/"TRAIT_REALLOCATION_RESULT_V1.md"

DATASET="wh7c636y3t"; VERSION=1; TARGET="All seasons personality data.xlsx"
FILE_URL=f"https://data.mendeley.com/api/datasets/{DATASET}/files?"+urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
HEADERS={"User-Agent":"Mozilla/5.0 batter-early-trait-decomposition/1.0","Accept":"application/json,*/*"}
TRAITS=("Boldness","ExpuNIQUE","AllActivityNormed")
DISPLAY=("Boldness","Exploration","Activity")

def get_bytes(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=180) as r:return r.read()

def get_json(url):return json.loads(get_bytes(url,"application/json").decode())

def envelope(x):
    if isinstance(x,list):return x
    for k in ("items","files","results","data"):
        if isinstance(x,dict) and isinstance(x.get(k),list):return x[k]
    raise RuntimeError("unknown file envelope")

def download():
    for row in envelope(get_json(FILE_URL)):
        if (row.get("filename") or row.get("name"))==TARGET:
            u=(row.get("content_details") or {}).get("download_url") or row.get("download_url")
            if not u:raise RuntimeError("download url absent")
            return get_bytes(u)
    raise RuntimeError("target absent")

def lab(x):
    if x is None:return None
    if isinstance(x,float) and np.isnan(x):return None
    if isinstance(x,float) and x.is_integer():return str(int(x))
    return str(x).strip()

def one_num(vals):
    q=[]
    for x in vals:
        try:
            v=float(x)
            if np.isfinite(v):q.append(v)
        except Exception:pass
    u=sorted(set(q))
    if len(u)!=1:raise RuntimeError("trait grain drift")
    return u[0]

def load_rows():
    wb=openpyxl.load_workbook(io.BytesIO(download()),read_only=True,data_only=True)
    ws=wb["Full_Data"]; it=ws.iter_rows(values_only=True)
    h=list(next(it)); needed=["Bat_no","Season","Colony type","Trial",*TRAITS]
    ix={x:h.index(x) for x in needed}
    raw=[{x:r[ix[x]] for x in needed} for r in it];wb.close()

    groups=defaultdict(list);treat=defaultdict(set)
    for r in raw:
        b,t=lab(r["Bat_no"]),lab(r["Trial"])
        if b is None or t is None:continue
        groups[(b,t)].append(r)
        q=lab(r["Colony type"])
        if q is not None:treat[b].add(q)

    units={}
    for (b,t),rr in groups.items():
        seasons={lab(x["Season"]) for x in rr if lab(x["Season"]) is not None}
        if not any(x in {"2","2.0","2020-2021","2020–2021"} for x in seasons):continue
        try:units[(b,t)]=np.array([one_num([x[z] for x in rr]) for z in TRAITS],float)
        except RuntimeError:pass

    bats=sorted({b for b,t in units if all((b,k) in units for k in ("1","2","3"))})
    out=[]
    for b in bats:
        if len(treat[b])!=1:raise RuntimeError(f"treatment conflict {b}")
        q=next(iter(treat[b])).lower()
        g="enriched" if ("enrich" in q and "impover" not in q) else "impoverished"
        out.append({"bat":b,"group":g,"y1":units[(b,"1")],"y2":units[(b,"2")],"y3":units[(b,"3")]})
    return out

def main():
    p=json.loads(PRIMARY.read_text())
    assert p["verdict"]=="UNSUPPORTED_INDIVIDUALIZATION"
    rows=load_rows()
    assert len(rows)==29

    pre=np.vstack([r["y1"] for r in rows]+[r["y2"] for r in rows])
    mu=pre.mean(axis=0);sd=pre.std(axis=0,ddof=1)
    assert np.all(np.isfinite(sd)&(sd>0))

    groups=np.array([r["group"] for r in rows],dtype=object)
    z1=np.vstack([(r["y1"]-mu)/sd for r in rows])
    z2=np.vstack([(r["y2"]-mu)/sd for r in rows])
    z3=np.vstack([(r["y3"]-mu)/sd for r in rows])
    delta=z3-(z1+z2)/2

    resid=np.empty_like(delta)
    for g in ("enriched","impoverished"):
        idx=(groups==g)
        resid[idx]=delta[idx]-delta[idx].mean(axis=0,keepdims=True)

    ie=(groups=="enriched");ii=(groups=="impoverished")
    ve=np.mean(resid[ie]**2,axis=0)
    vi=np.mean(resid[ii]**2,axis=0)
    dk=ve-vi
    dsum=float(np.sum(dk))
    assert abs(dsum-float(p["D"]))<1e-10,(dsum,p["D"])

    pos=float(np.sum(dk[dk>0]));neg=float(np.sum(dk[dk<0]))
    abst=float(np.sum(np.abs(dk)))
    canc=float(1-abs(dsum)/abst) if abst>0 else float("nan")

    rowsout=[]
    for name,a,b,d in zip(DISPLAY,ve,vi,dk):
        rowsout.append({
            "trait":name,
            "V_enriched":float(a),
            "V_impoverished":float(b),
            "D":float(d),
            "sign":"E>I" if d>0 else ("E<I" if d<0 else "equal")
        })

    result={
        "version":1,
        "primary_D":float(p["D"]),
        "sum_trait_D":dsum,
        "positive_sum":pos,
        "negative_sum":neg,
        "absolute_sum":abst,
        "cancellation_ratio":canc,
        "traits":rowsout,
        "inferential_status":"DESCRIPTIVE_ONLY_POST_PRIMARY"
    }
    OUT.write_text(json.dumps(result,indent=2)+"\n")

    lines=[
        "# Early-experience trait reallocation result v1","",
        "**DESCRIPTIVE ONLY — NO P-VALUES; PRIMARY VERDICT UNCHANGED.**","",
        f"- primary D = **{p['D']:+.6f}**",
        f"- sum of trait contributions = **{dsum:+.6f}**",
        f"- positive contribution sum = **{pos:+.6f}**",
        f"- negative contribution sum = **{neg:+.6f}**",
        f"- absolute contribution sum = **{abst:.6f}**",
        f"- cancellation ratio = **{canc:.6f}**","",
        "| trait | V enriched | V impoverished | D = E-I | sign |",
        "|---|---:|---:|---:|---|"
    ]
    for q in rowsout:
        lines.append(f"| {q['trait']} | {q['V_enriched']:.6f} | {q['V_impoverished']:.6f} | {q['D']:+.6f} | {q['sign']} |")
    lines += ["","The three trait contributions sum exactly to the frozen multivariate D.","No trait-wise p-value is authorized.",""]
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__":main()
