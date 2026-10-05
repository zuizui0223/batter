#!/usr/bin/env python3
"""Prospective learning-state maintenance primary on Yamada summary endpoints."""
from __future__ import annotations

import collections
import hashlib
import io
import json
import math
import re
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
import numpy as np

API="https://api.figshare.com/v2/articles/19102712"
FID=33969680
NAME="raw_analysis_data_by_yamada.xlsx"
SIZE=18023
MD5="cb7e2f738d85ee80becb5949317ff625"
UA="batter-learning-state-maintenance-primary/1.0"

ALLOW_COLS={
    "C":"condition",
    "D":"bats_id",
    "E":"trial",
    "K":"max_flight_speed",
    "L":"meandering_width",
}
NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
NPERM=9999
SEED_P1=202610050941
SEED_SPEED=202610050942
SEED_WIDTH=202610050943

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("download budget exceeded")
    return b

def col_letter(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def shared(z,need):
    if not need:return {}
    out={};idx=-1
    with z.open("xl/sharedStrings.xml") as fh:
        for _,e in ET.iterparse(fh,events=("end",)):
            if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
                idx+=1
                if idx in need:
                    out[idx]="".join(t.text or "" for t in e.findall(".//m:t",NS))
                e.clear()
    return out

def read_rows(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    target=None
    for sh in wb.findall("m:sheets/m:sheet",NS):
        if sh.attrib.get("name")=="1st_table":
            rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target=relmap[rid].lstrip("/")
            break
    if target is None:raise RuntimeError("1st_table missing")
    if not target.startswith("xl/"):target="xl/"+target
    root=ET.fromstring(z.read(target))
    rows=root.findall("m:sheetData/m:row",NS)
    tmp=[];need=set()
    for row in rows:
        rn=int(row.attrib.get("r","0"))
        if rn<2 or rn>29:continue
        d={"source_row":rn}
        for c in row.findall("m:c",NS):
            col=col_letter(c.attrib.get("r"))
            if col not in ALLOW_COLS:continue
            typ=c.attrib.get("t")
            if typ=="inlineStr":
                t=c.find(".//m:t",NS)
                d[ALLOW_COLS[col]]=t.text if t is not None else None
            else:
                v=c.find("m:v",NS)
                if v is None:continue
                if typ=="s":
                    ix=int(v.text);need.add(ix);d[ALLOW_COLS[col]]=("S",ix)
                else:
                    d[ALLOW_COLS[col]]=v.text
        tmp.append(d)
    ss=shared(z,need)
    return [{k:(ss[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()} for d in tmp]

def as_int(v):
    try:
        x=float(str(v).strip())
        return int(x) if x.is_integer() else None
    except Exception:return None

def as_float(v):
    try:
        x=float(str(v).strip())
        return x if math.isfinite(x) else None
    except Exception:return None

def fetch():
    art=get_json(API)
    f=next((x for x in art.get("files") or [] if int(x["id"])==FID),None)
    if f is None:raise RuntimeError("file missing")
    if f.get("name")!=NAME or int(f.get("size") or 0)!=SIZE:raise RuntimeError("metadata drift")
    b=get_bytes(f["download_url"],SIZE+4096)
    if len(b)!=SIZE or hashlib.md5(b).hexdigest()!=MD5:raise RuntimeError("integrity")
    raw=read_rows(b)
    rows=[]
    for r in raw:
        cond=as_int(r.get("condition"));bat=str(r.get("bats_id","")).strip();trial=as_int(r.get("trial"))
        speed=as_float(r.get("max_flight_speed"));width=as_float(r.get("meandering_width"))
        if cond not in (1,2) or not bat or trial not in (1,12):continue
        rows.append({"condition":cond,"bat":bat,"trial":trial,"speed":speed,"width":width})
    return rows

def complete_subjects(rows):
    by=collections.defaultdict(dict)
    cond={}
    for r in rows:
        key=r["bat"]
        if r["trial"] in by[key]:
            raise RuntimeError(f"duplicate bat/trial {key}/{r['trial']}")
        by[key][r["trial"]]=r
        cond.setdefault(key,r["condition"])
        if cond[key]!=r["condition"]:raise RuntimeError(f"condition drift {key}")
    bats=[]
    for b,d in sorted(by.items(),key=lambda kv:int(kv[0])):
        if set(d)=={1,12} and all(d[t]["speed"] is not None and d[t]["width"] is not None for t in (1,12)):
            bats.append(b)
    cc=collections.Counter(cond[b] for b in bats)
    if len(bats)<12 or cc[1]<5 or cc[2]<5:
        raise RuntimeError(f"STOP complete support bats={len(bats)} cond={dict(cc)}")
    return bats,cond,by

def standardized_state(bats,cond,by):
    # endpoint standardization within condition x trial.
    z={}
    descriptive={}
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        for t in (1,12):
            sp=np.array([by[b][t]["speed"] for b in cb],float)
            wi=np.array([by[b][t]["width"] for b in cb],float)
            spsd=float(np.std(sp,ddof=1));wisd=float(np.std(wi,ddof=1))
            if not (spsd>0 and wisd>0):raise RuntimeError(f"zero SD c={c} t={t}")
            descriptive[(c,t)]={
                "n":len(cb),
                "mean_max_flight_speed":float(np.mean(sp)),
                "sd_max_flight_speed":spsd,
                "mean_meandering_width":float(np.mean(wi)),
                "sd_meandering_width":wisd,
            }
            for b in cb:
                z[(b,t)]=np.array([
                    (by[b][t]["speed"]-float(np.mean(sp)))/spsd,
                    (by[b][t]["width"]-float(np.mean(wi)))/wisd,
                ],float)
    return z,descriptive

def policy_stat(bats,cond,z,label12=None):
    per={}
    condition_means=[]
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        vals=[]
        for b in cb:
            assigned=label12[b] if label12 is not None else b
            own=z[(assigned,12)]
            dself=float(np.linalg.norm(z[(b,1)]-own))
            others=[j for j in cb if j!=assigned]
            dother=float(np.mean([np.linalg.norm(z[(b,1)]-z[(j,12)]) for j in others]))
            k=dother-dself
            per[b]=k
            vals.append(k)
        condition_means.append(float(np.mean(vals)))
    return float(np.mean(condition_means)),per

def perm12(bats,cond,rng):
    mp={}
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        p=list(rng.permutation(np.array(cb,dtype=object)))
        for b,j in zip(cb,p):mp[b]=str(j)
    return mp

def pearson_endpoint(bats,cond,z,index,label12=None):
    x=[];y=[]
    for b in bats:
        assigned=label12[b] if label12 is not None else b
        x.append(float(z[(b,1)][index]))
        y.append(float(z[(assigned,12)][index]))
    if np.std(x,ddof=1)<=0 or np.std(y,ddof=1)<=0:return math.nan
    return float(np.corrcoef(np.array(x),np.array(y))[0,1])

def condition_corrs(bats,cond,z,index):
    out={}
    for c in (1,2):
        cb=[b for b in bats if cond[b]==c]
        x=[z[(b,1)][index] for b in cb];y=[z[(b,12)][index] for b in cb]
        out[str(c)]=float(np.corrcoef(x,y)[0,1])
    return out

def main():
    rows=fetch()
    bats,cond,by=complete_subjects(rows)
    z,desc=standardized_state(bats,cond,by)

    K,ki=policy_stat(bats,cond,z,None)
    pos=sum(v>0 for v in ki.values())
    rng=np.random.default_rng(SEED_P1)
    null=np.empty(NPERM,float)
    for q in range(NPERM):
        mp=perm12(bats,cond,rng)
        null[q]=policy_stat(bats,cond,z,mp)[0]
    p1=float((1+np.sum(null>=K))/(NPERM+1))
    need=math.ceil(.70*len(bats))
    p1_support=bool(K>0 and p1<=.05 and pos>=need)

    secondaries={}
    for name,idx,seed in [("speed",0,SEED_SPEED),("meandering_width",1,SEED_WIDTH)]:
        obs=pearson_endpoint(bats,cond,z,idx,None)
        rng=np.random.default_rng(seed)
        n=np.empty(NPERM,float)
        for q in range(NPERM):
            mp=perm12(bats,cond,rng)
            n[q]=pearson_endpoint(bats,cond,z,idx,mp)
        secondaries[name]={
            "pearson_r":obs,
            "condition_specific_r":condition_corrs(bats,cond,z,idx),
            "null_mean":float(np.mean(n)),
            "null_q025":float(np.quantile(n,.025)),
            "null_q975":float(np.quantile(n,.975)),
            "p_one_sided":float((1+np.sum(n>=obs))/(NPERM+1)),
            "seed":seed,
        }

    out={
      "contract":"LEARNING_STATE_MAINTENANCE_PRIMARY_CONTRACT_V1.md",
      "status":"PROSPECTIVE_OUTCOME_OPENED",
      "species":"Rhinolophus ferrumequinum nippon",
      "n_evaluable_subjects":len(bats),
      "subjects_by_condition":{str(c):sum(cond[b]==c for b in bats) for c in (1,2)},
      "P1_policy_identity":{
        "K_policy":K,
        "K_i":ki,
        "positive_subjects":pos,
        "required_positive_subjects":need,
        "positive_fraction":pos/len(bats),
        "permutations":NPERM,
        "seed":SEED_P1,
        "null_mean":float(np.mean(null)),
        "null_q025":float(np.quantile(null,.025)),
        "null_q975":float(np.quantile(null,.975)),
        "p_one_sided":p1,
        "verdict":"PASS_PERSONAL_STATE_MAINTENANCE" if p1_support else "FAIL_PERSONAL_STATE_MAINTENANCE",
      },
      "P2_endpoint_persistence":secondaries,
      "published_learning_descriptives":{
        f"condition_{c}_trial_{t}":v for (c,t),v in sorted(desc.items())
      },
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
