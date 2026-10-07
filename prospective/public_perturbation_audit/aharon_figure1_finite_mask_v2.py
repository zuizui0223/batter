#!/usr/bin/env python3
"""Finite-mask-only support audit for Aharon Figure 1."""

from __future__ import annotations
import io,json,re,tempfile,urllib.parse,urllib.request,zipfile
from pathlib import Path
import numpy as np, scipy.io

HERE=Path(__file__).resolve().parent
GATE=HERE/"AHARON_FIGURE1_STRUCTURE_V2.json"
OUT=HERE/"AHARON_FIGURE1_FINITE_MASK_V2.json"
OUTMD=HERE/"AHARON_FIGURE1_FINITE_MASK_V2.md"
DATASET="f6mvhj5gj9";VERSION=3;TARGET="Figure 1.zip"
BATS=("500","503","505","510");CONDS=("con","75","300")
HEADERS={"User-Agent":"Mozilla/5.0 batter-aharon-finite-mask/2.0","Accept":"application/json,*/*"}

def get_bytes(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEADERS,"Accept":accept})
    with urllib.request.urlopen(req,timeout=120) as r:return r.read()

def rows():
    u=f"https://data.mendeley.com/api/datasets/{DATASET}/files?"+urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
    x=json.loads(get_bytes(u,"application/json").decode())
    return x if isinstance(x,list) else x.get("items") or x.get("files") or x.get("results") or x.get("data") or []

def zipbytes():
    for row in rows():
        if (row.get("filename") or row.get("name"))==TARGET:
            cd=row.get("content_details") or {};u=cd.get("download_url") or row.get("download_url")
            return get_bytes(u)
    raise RuntimeError("Figure 1.zip absent")

def matrix(data):
    with tempfile.NamedTemporaryFile(suffix=".mat") as tf:
        tf.write(data);tf.flush();m=scipy.io.loadmat(tf.name)
    vars=[(k,v) for k,v in m.items() if not k.startswith("__") and isinstance(v,np.ndarray) and np.issubdtype(v.dtype,np.number)]
    if len(vars)!=1: raise RuntimeError(f"expected one numeric variable, got {[k for k,_ in vars]}")
    return np.asarray(vars[0][1],dtype=float)

def main():
    if json.loads(GATE.read_text()).get("gate")!="PASS_AHARON_FIGURE1_STRUCTURE":
        raise SystemExit("STOP: structure gate not PASS")
    pat=re.compile(r"(500|503|505|510)_YRLturns_together_(con|75|300)\.mat$",re.I)
    out={}
    with zipfile.ZipFile(io.BytesIO(zipbytes())) as z:
        for name in z.namelist():
            m=pat.search(name)
            if not m:continue
            b=m.group(1);c=m.group(2).lower();a=matrix(z.read(name))
            valid=0
            for j in range(a.shape[1]):
                right=np.isfinite(a[0::2,j])
                left=np.isfinite(a[1::2,j])
                if np.any(right) and np.any(left):valid+=1
            out[(b,c)]={"rows":int(a.shape[0]),"columns":int(a.shape[1]),"valid_trials":int(valid),"invalid_trials":int(a.shape[1]-valid)}
    gate=(len(out)==12 and all(x["valid_trials"]>=5 for x in out.values()))
    result={"version":2,"cells":{"|".join(k):v for k,v in out.items()},
            "gate":"PASS_AHARON_FIGURE1_FINITE_SUPPORT" if gate else "STOP_AHARON_FIGURE1_FINITE_SUPPORT"}
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    lines=["# Aharon Figure-1 finite-mask result v2","","**FINITE MASK COUNTS ONLY — NO TURNING MAGNITUDES.**",""]
    for b in BATS:
        for c in CONDS:
            x=out.get((b,c));lines.append(f"- {b} | {c}: valid={x['valid_trials'] if x else 'MISSING'} / columns={x['columns'] if x else 'NA'}")
    lines+=["","## Verdict","",f"**{result['gate']}**",""];OUTMD.write_text("\n".join(lines)+"\n");print(OUTMD.read_text())
if __name__=="__main__":main()
