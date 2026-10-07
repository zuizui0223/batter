#!/usr/bin/env python3
"""Descriptive leave-one-out state-rewriting decomposition.

No p-values. Cannot rescue the frozen primary.
"""

from __future__ import annotations
import io, json, urllib.parse, urllib.request
from collections import defaultdict
from pathlib import Path
import numpy as np, openpyxl

HERE=Path(__file__).resolve().parent
OUT=HERE/"STATE_REWRITING_SECONDARY_RESULT_V1.json"
OUTMD=HERE/"STATE_REWRITING_SECONDARY_RESULT_V1.md"

DATASET="wh7c636y3t"; VERSION=1
TARGET="All seasons personality data.xlsx"
FILE_URL=f"https://data.mendeley.com/api/datasets/{DATASET}/files?"+urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
HEADERS={"User-Agent":"Mozilla/5.0 batter-state-rewriting/1.0","Accept":"application/json,*/*"}
TRAITS=("Boldness","ExpuNIQUE","AllActivityNormed")

def get_bytes(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=180) as r: return r.read()

def get_json(url): return json.loads(get_bytes(url,"application/json").decode("utf-8"))

def envelope(x):
    if isinstance(x,list): return x
    for k in ("items","files","results","data"):
        if isinstance(x,dict) and isinstance(x.get(k),list): return x[k]
    raise RuntimeError("unknown envelope")

def download():
    for row in envelope(get_json(FILE_URL)):
        if (row.get("filename") or row.get("name"))==TARGET:
            url=(row.get("content_details") or {}).get("download_url") or row.get("download_url")
            return get_bytes(url)
    raise RuntimeError("target absent")

def lab(x):
    if x is None: return None
    if isinstance(x,float) and np.isnan(x): return None
    if isinstance(x,float) and x.is_integer(): return str(int(x))
    return str(x).strip()

def one_num(vals):
    q=[]
    for x in vals:
        try:
            v=float(x)
            if np.isfinite(v): q.append(v)
        except Exception: pass
    u=sorted(set(q))
    if len(u)!=1: raise RuntimeError("trait grain drift")
    return u[0]

def load_rows():
    wb=openpyxl.load_workbook(io.BytesIO(download()),read_only=True,data_only=True)
    ws=wb["Full_Data"]; it=ws.iter_rows(values_only=True)
    h=list(next(it)); needed=["Bat_no","Season","Colony type","Trial",*TRAITS]
    ix={x:h.index(x) for x in needed}
    raw=[{x:r[ix[x]] for x in needed} for r in it]; wb.close()

    groups=defaultdict(list); treat=defaultdict(set); season=defaultdict(set)
    for r in raw:
        b,t=lab(r["Bat_no"]),lab(r["Trial"])
        if b is None or t is None: continue
        groups[(b,t)].append(r)
        if lab(r["Colony type"]) is not None: treat[b].add(lab(r["Colony type"]))
        if lab(r["Season"]) is not None: season[b].add(lab(r["Season"]))

    units={}
    for (b,t),rr in groups.items():
        sl={lab(x["Season"]) for x in rr if lab(x["Season"]) is not None}
        if not any(x in {"2","2.0","2020-2021","2020–2021"} for x in sl): continue
        try: units[(b,t)]=np.array([one_num([x[z] for x in rr]) for z in TRAITS],float)
        except RuntimeError: pass

    bats=sorted({b for b,t in units if all((b,k) in units for k in ("1","2","3"))})
    out=[]
    for b in bats:
        if len(treat[b])!=1: raise RuntimeError(f"treatment conflict {b}")
        q=next(iter(treat[b])).lower()
        g="enriched" if ("enrich" in q and "impover" not in q) else "impoverished"
        out.append({"bat":b,"group":g,"y1":units[(b,"1")],"y2":units[(b,"2")],"y3":units[(b,"3")]})
    return out

def summary(x):
    x=np.asarray(x,float)
    return {"mean":float(np.mean(x)),"median":float(np.median(x))}

def main():
    rows=load_rows()
    if len(rows)!=29: raise RuntimeError(f"expected 29, got {len(rows)}")

    pre=np.vstack([r["y1"] for r in rows]+[r["y2"] for r in rows])
    mu=pre.mean(axis=0); sd=pre.std(axis=0,ddof=1)
    if np.any(~np.isfinite(sd)) or np.any(sd<=0): raise RuntimeError("bad baseline scale")

    for r in rows:
        r["b"]=(((r["y1"]-mu)/sd)+((r["y2"]-mu)/sd))/2
        r["t"]=(r["y3"]-mu)/sd
        r["d"]=r["t"]-r["b"]

    err={"B":[],"G":[],"BplusS":[]}
    bygroup={g:{m:[] for m in err} for g in ("enriched","impoverished")}
    individual=[]

    for i,r in enumerate(rows):
        peers=[x for j,x in enumerate(rows) if j!=i and x["group"]==r["group"]]
        group_t=np.mean(np.vstack([x["t"] for x in peers]),axis=0)
        shift=np.mean(np.vstack([x["d"] for x in peers]),axis=0)
        pred={
            "B":r["b"],
            "G":group_t,
            "BplusS":r["b"]+shift,
        }
        e={m:float(np.sum((r["t"]-p)**2)) for m,p in pred.items()}
        for m in err:
            err[m].append(e[m]); bygroup[r["group"]][m].append(e[m])
        individual.append({"bat":r["bat"],"group":r["group"],"errors":e})

    result={
        "version":1,"n":len(rows),
        "overall":{m:summary(v) for m,v in err.items()},
        "by_group":{g:{m:summary(v) for m,v in d.items()} for g,d in bygroup.items()},
        "fractions":{
            "BplusS_better_than_B":float(np.mean(np.array(err["BplusS"])<np.array(err["B"]))),
            "BplusS_better_than_G":float(np.mean(np.array(err["BplusS"])<np.array(err["G"]))),
            "B_better_than_G":float(np.mean(np.array(err["B"])<np.array(err["G"]))),
        },
        "individual":individual,
        "inferential_status":"DESCRIPTIVE_ONLY_POST_PRIMARY",
    }
    OUT.write_text(json.dumps(result,indent=2)+"\n")

    means={m:result["overall"][m]["mean"] for m in err}
    winner=min(means,key=means.get)
    lines=[
        "# Early-experience state-rewriting secondary result v1","",
        "**DESCRIPTIVE ONLY — NO P-VALUES; CANNOT RESCUE PRIMARY.**","",
        f"- n = **{len(rows)}**",
        f"- lowest overall mean-error model = **{winner}**","",
        "## Overall squared error","",
    ]
    for m in ("B","G","BplusS"):
        lines.append(f"- {m}: mean={result['overall'][m]['mean']:.6f}; median={result['overall'][m]['median']:.6f}")
    lines += ["","## Pairwise fractions","",
        f"- B+S better than B: {result['fractions']['BplusS_better_than_B']:.3f}",
        f"- B+S better than G: {result['fractions']['BplusS_better_than_G']:.3f}",
        f"- B better than G: {result['fractions']['B_better_than_G']:.3f}","",
        "## Treatment groups",""]
    for g in ("enriched","impoverished"):
        lines.append(f"### {g}")
        for m in ("B","G","BplusS"):
            q=result["by_group"][g][m]
            lines.append(f"- {m}: mean={q['mean']:.6f}; median={q['median']:.6f}")
        lines.append("")
    OUTMD.write_text("\n".join(lines)+"\n")
    print(OUTMD.read_text())

if __name__=="__main__": main()
