#!/usr/bin/env python3
"""Outcome-blind structural read of Yamada raw_analysis_data_by_yamada.xlsx.

Reads only C,D,E,N,O from rows 2:29 of 1st_table.
"""
from __future__ import annotations
import collections, hashlib, io, json, math, re, urllib.request, zipfile
import xml.etree.ElementTree as ET

API="https://api.figshare.com/v2/articles/19102712"
FID=33969680
NAME="raw_analysis_data_by_yamada.xlsx"
SIZE=18023
MD5="cb7e2f738d85ee80becb5949317ff625"
UA="batter-learning-policy-structural/1.0"

ALLOW_COLS={"C":"condition","D":"bats_id","E":"trial","N":"origin_name","O":"for_article_datasets_name"}
NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("budget exceeded")
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

def norm(v):
    if v is None:return None
    s=str(v).strip()
    return None if s=="" or s.lower() in {"na","nan","none","null","n/a"} else s

def intlike(v):
    s=norm(v)
    if s is None:return None
    try:
        x=float(s)
        if x.is_integer():return int(x)
    except Exception:pass
    return s

def read_allowed(b):
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
                elif typ=="b":
                    d[ALLOW_COLS[col]]="1" if v.text=="1" else "0"
                else:
                    d[ALLOW_COLS[col]]=v.text
        tmp.append(d)
    ss=shared(z,need)
    out=[]
    for d in tmp:
        out.append({k:(ss[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()})
    return out

def main():
    art=get_json(API)
    f=next((x for x in art.get("files") or [] if int(x["id"])==FID),None)
    if f is None:raise RuntimeError("file missing")
    if f.get("name")!=NAME or int(f.get("size") or 0)!=SIZE:raise RuntimeError("metadata drift")
    b=get_bytes(f["download_url"],SIZE+4096)
    if len(b)!=SIZE or hashlib.md5(b).hexdigest()!=MD5:raise RuntimeError("integrity")
    rows=read_allowed(b)

    # Provisional biological key frozen in contract: condition x bats_id if IDs cross conditions.
    clean=[]
    for r in rows:
        cond=intlike(r.get("condition"))
        bat=norm(r.get("bats_id"))
        trial=intlike(r.get("trial"))
        if cond is None and bat is None and trial is None:continue
        clean.append({
          "source_row":r["source_row"],"condition":cond,"bats_id":bat,"trial":trial,
          "origin_name":norm(r.get("origin_name")),
          "for_article_datasets_name":norm(r.get("for_article_datasets_name")),
        })

    id_conditions=collections.defaultdict(set)
    for r in clean:
        if r["bats_id"] is not None and r["condition"] is not None:
            id_conditions[r["bats_id"]].add(r["condition"])
    cross_ids=sorted(k for k,v in id_conditions.items() if len(v)>1)

    for r in clean:
        if r["bats_id"] is None or r["condition"] is None:
            r["subject_key"]=None
        elif cross_ids:
            r["subject_key"]=f'{r["condition"]}::{r["bats_id"]}'
        else:
            r["subject_key"]=r["bats_id"]

    bysub=collections.defaultdict(list)
    for r in clean:
        if r["subject_key"] is not None:bysub[r["subject_key"]].append(r)

    subjects=[]
    duplicate_subject_trial=[]
    for sk,rr in sorted(bysub.items()):
        trials=[x["trial"] for x in rr]
        cnt=collections.Counter(trials)
        for t,n in cnt.items():
            if n>1:duplicate_subject_trial.append({"subject_key":sk,"trial":t,"n":n})
        conds=sorted(set(x["condition"] for x in rr if x["condition"] is not None),key=str)
        origins=sorted(set(x["origin_name"] for x in rr if x["origin_name"] is not None))
        datasets=sorted(set(x["for_article_datasets_name"] for x in rr if x["for_article_datasets_name"] is not None))
        subjects.append({
          "subject_key":sk,
          "bats_id":rr[0]["bats_id"],
          "conditions":conds,
          "trials":sorted(set(trials),key=str),
          "n_rows":len(rr),
          "origin_names":origins,
          "dataset_names":datasets,
          "has_exact_1_and_12":cnt.get(1,0)==1 and cnt.get(12,0)==1 and len(rr)==2,
          "condition_consistent":len(conds)==1,
        })

    eligible=[x for x in subjects if x["has_exact_1_and_12"] and x["condition_consistent"]]
    cond_counts=collections.Counter(x["conditions"][0] for x in eligible if len(x["conditions"])==1)

    passed=(len(eligible)>=12 and len(cond_counts)>=2 and min(cond_counts.values())>=5 and not duplicate_subject_trial)

    out={
      "contract":"STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md",
      "behavioural_outcome_values_opened":False,
      "n_nonempty_structural_rows":len(clean),
      "condition_vocabulary":sorted(set(r["condition"] for r in clean if r["condition"] is not None),key=str),
      "trial_vocabulary":sorted(set(r["trial"] for r in clean if r["trial"] is not None),key=str),
      "raw_bat_ids":sorted(set(r["bats_id"] for r in clean if r["bats_id"] is not None)),
      "bat_ids_crossing_conditions":cross_ids,
      "provisional_key_rule":"condition::bats_id if any bats_id crosses conditions; otherwise bats_id",
      "subjects":subjects,
      "duplicate_subject_trial_rows":duplicate_subject_trial,
      "n_eligible_subjects":len(eligible),
      "eligible_subject_counts_by_condition":{str(k):v for k,v in sorted(cond_counts.items(),key=lambda kv:str(kv[0]))},
      "frozen_minimum_total":12,
      "frozen_minimum_per_condition":5,
      "verdict":"PASS_TO_OUTCOME_CONTRACT" if passed else "STOP_STRUCTURAL_SUPPORT"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
