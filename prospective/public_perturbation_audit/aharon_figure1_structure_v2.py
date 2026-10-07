#!/usr/bin/env python3
"""Structure-only audit of Aharon Figure 1 turning matrices."""

from __future__ import annotations
import io,json,re,tempfile,urllib.parse,urllib.request,zipfile
from pathlib import Path
import scipy.io

HERE=Path(__file__).resolve().parent
OUT=HERE/"AHARON_FIGURE1_STRUCTURE_V2.json"
OUTMD=HERE/"AHARON_FIGURE1_STRUCTURE_V2.md"

DATASET="f6mvhj5gj9"; VERSION=3; TARGET="Figure 1.zip"
BATS=("500","503","505","510")
CONDS=("con","75","300")
HEADERS={"User-Agent":"Mozilla/5.0 batter-aharon-figure1-structure/2.0","Accept":"application/json,*/*"}

def get_bytes(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def file_rows():
    url=f"https://data.mendeley.com/api/datasets/{DATASET}/files?"+urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
    x=json.loads(get_bytes(url,"application/json").decode())
    return x if isinstance(x,list) else x.get("items") or x.get("files") or x.get("results") or x.get("data") or []

def download_target():
    for row in file_rows():
        if (row.get("filename") or row.get("name"))==TARGET:
            cd=row.get("content_details") or {}
            url=cd.get("download_url") or row.get("download_url")
            if not url: raise RuntimeError("no Figure 1 download URL")
            return get_bytes(url)
    raise RuntimeError("Figure 1.zip absent")

def whos(data):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data);tf.flush()
        return scipy.io.whosmat(tf.name)

def main():
    zdata=download_target()
    cells={}
    members=[]
    pat=re.compile(r"(500|503|505|510)_YRLturns_together_(con|75|300)\.mat$",re.I)
    with zipfile.ZipFile(io.BytesIO(zdata)) as z:
        for name in z.namelist():
            m=pat.search(name)
            if not m: continue
            bat=m.group(1);cond=m.group(2).lower()
            rows=whos(z.read(name))
            members.append({"path":name,"bat":bat,"condition":cond,"variables":[{"name":v,"shape":list(sh),"class":cl} for v,sh,cl in rows]})
            numeric=[x for x in rows if x[2] in {"double","single","int8","uint8","int16","uint16","int32","uint32","int64","uint64"}]
            if len(numeric)==1:
                v,sh,cl=numeric[0]
                cells[(bat,cond)]={"shape":list(sh),"class":cl,"variable":v}

    missing=[f"{b}|{c}" for b in BATS for c in CONDS if (b,c) not in cells]
    bad=[]
    for key,x in cells.items():
        sh=x["shape"]
        if len(sh)!=2 or sh[0]<2 or sh[1]<5: bad.append({"cell":"|".join(key),"shape":sh})
    gate=(len(cells)==12 and not missing and not bad)
    result={"version":2,"bats":list(BATS),"conditions":list(CONDS),"members":members,
            "cells":{"|".join(k):v for k,v in cells.items()},"missing":missing,"bad_shape":bad,
            "gate":"PASS_AHARON_FIGURE1_STRUCTURE" if gate else "STOP_AHARON_FIGURE1_STRUCTURE"}
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Aharon Figure-1 structural result v2","","**STRUCTURE ONLY — NO TURNING VALUES.**","",
           f"- cells recovered: **{len(cells)}/12**",f"- missing: {missing or 'none'}",f"- bad shape: {bad or 'none'}",""]
    for b in BATS:
        for c in CONDS:
            x=cells.get((b,c))
            lines.append(f"- {b} | {c}: {x['shape'] if x else 'MISSING'}")
    lines+=["","## Verdict","",f"**{result['gate']}**",""]
    OUTMD.write_text("\n".join(lines)+"\n");print(OUTMD.read_text())

if __name__=="__main__":main()
