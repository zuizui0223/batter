#!/usr/bin/env python3
"""Outcome-blind deterministic crosswalk from Yamada source IDs to 28 raw sheets."""
from __future__ import annotations
import hashlib, importlib.util, io, json, re, urllib.request, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("S",HERE/"structural_crosswalk_v1.py")
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

RAW_ID=33969677
RAW_SIZE=932367
RAW_MD5="2226ea5b19fb077ddcce66cb6e97088c"
RAW_URL=f"https://ndownloader.figshare.com/files/{RAW_ID}"
UA="batter-yamada-raw-sheet-crosswalk/1.0"
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

def download_raw():
    req=urllib.request.Request(RAW_URL,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=90) as r:b=r.read(RAW_SIZE+1)
    if len(b)!=RAW_SIZE:raise RuntimeError(f"raw size mismatch {len(b)}")
    if hashlib.md5(b).hexdigest()!=RAW_MD5:raise RuntimeError("raw MD5 mismatch")
    return b

def raw_sheet_records(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    out=[]
    for sh in wb.findall("m:sheets/m:sheet",NS):
        name=sh.attrib.get("name") or ""
        low=name.lower()
        x=low
        if x.startswith("y_"):x=x[2:]
        m=re.match(r"^bat_?([a-z])(?:_|$)",x)
        if not m:
            raise RuntimeError(f"cannot parse raw bat label: {name}")
        lab=m.group(1).upper()
        if "1st" in low and "12th" not in low:trial="1"
        elif "12th" in low and "1st" not in low:trial="12"
        else:raise RuntimeError(f"cannot resolve trial: {name}")
        if "chain" in low:cond="1"
        elif "_ac_" in low or "acril" in low:cond="2"
        else:raise RuntimeError(f"cannot resolve condition: {name}")
        out.append({"sheet":name,"condition":cond,"trial":trial,"raw_label":lab})
    return out

def candidates(v):
    v=S.norm(v)
    if v is None:return set()
    x=v.strip().lower()
    if x.startswith("bat"):x=x[3:]
    x=x.lstrip("_")
    out=set()
    if len(x)==1 and x.isalpha():
        out.add(x.upper())
    for tok in re.split(r"[_\W]+",x):
        if len(tok)==1 and tok.isalpha():
            out.add(tok.upper())
    return out

def main():
    small=S.read_allowed(S.get_bytes())
    for r in small:
        for k in S.ALLOWED_COLS.values():r[k]=S.norm(r.get(k))
    raw=raw_sheet_records(download_raw())
    if len(raw)!=28:raise RuntimeError(f"expected 28 raw sheets, got {len(raw)}")

    bats=sorted(set(r["bats_id"] for r in small if r.get("bats_id") is not None),key=lambda x:int(float(x)))
    mappings=[];errors=[];used=[]
    for bat in bats:
        rr=[r for r in small if r.get("bats_id")==bat]
        conds=sorted(set(r["condition"] for r in rr))
        if len(conds)!=1:
            errors.append({"bat_id":bat,"error":"condition_ambiguous"});continue
        cond=conds[0]
        r1=[r for r in rr if r.get("trial")=="1"]
        if len(r1)!=1:
            errors.append({"bat_id":bat,"error":"trial1_not_unique"});continue
        r1=r1[0]
        article_cand=sorted(candidates(r1.get("for_article_datasets_name")))
        origin_cand=sorted(candidates(r1.get("origin_name")))
        available_labels=sorted(set(x["raw_label"] for x in raw if x["condition"]==cond))
        article_matches=sorted(set(article_cand)&set(available_labels))
        origin_matches=sorted(set(origin_cand)&set(available_labels))
        if len(article_matches)==1:
            matches=article_matches
            mapping_key="for_article_datasets_name"
        elif len(article_matches)==0 and len(origin_matches)==1:
            matches=origin_matches
            mapping_key="origin_name_fallback"
        else:
            errors.append({"bat_id":bat,"condition":cond,
                           "article_candidates":article_cand,"origin_candidates":origin_cand,
                           "available_labels":available_labels,
                           "article_matches":article_matches,"origin_matches":origin_matches,
                           "error":"priority_label_match_not_unique"})
            continue
        lab=matches[0]
        entry={"bat_id":bat,"condition":cond,"source_origin_name":r1.get("origin_name"),
               "source_article_name":r1.get("for_article_datasets_name"),
               "article_candidates":article_cand,"origin_candidates":origin_cand,
               "mapping_key":mapping_key,"matched_raw_label":lab,"trials":{}}
        for trial in ["1","12"]:
            sheets=[x["sheet"] for x in raw if x["condition"]==cond and x["trial"]==trial and x["raw_label"]==lab]
            if len(sheets)!=1:
                errors.append({"bat_id":bat,"condition":cond,"trial":trial,"raw_label":lab,
                               "sheets":sheets,"error":"sheet_not_unique"})
            else:
                entry["trials"][trial]=sheets[0]
                used.append(sheets[0])
        mappings.append(entry)

    duplicate_used=sorted([x for x in set(used) if used.count(x)>1])
    unused=sorted(set(x["sheet"] for x in raw)-set(used))
    complete=(len(errors)==0 and len(mappings)==14 and len(used)==28 and not duplicate_used and not unused)
    out={
      "contract":"RAW_SHEET_CROSSWALK_CONTRACT_V1.md + RAW_SHEET_CROSSWALK_PRIORITY_AMENDMENT_V1.md",
      "kinematic_outcomes_opened":False,
      "n_raw_sheets":len(raw),
      "raw_sheet_structure":raw,
      "n_source_bats":len(bats),
      "mappings":mappings,
      "errors":errors,
      "duplicate_used_sheets":duplicate_used,
      "unused_raw_sheets":unused,
      "verdict":"PASS_TO_POLICY_SUPPORT_GATE" if complete else "STOP_CROSSWALK"
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
