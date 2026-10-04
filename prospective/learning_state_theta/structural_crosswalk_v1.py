#!/usr/bin/env python3
"""Outcome-blind structural crosswalk for Yamada raw-analysis workbook.

Reads only C,D,E,N,O from 1st_table.
"""
from __future__ import annotations
import collections, hashlib, io, json, re, urllib.request, zipfile
import xml.etree.ElementTree as ET

FID=33969680
SIZE=18023
MD5="cb7e2f738d85ee80becb5949317ff625"
URL=f"https://ndownloader.figshare.com/files/{FID}"
UA="batter-yamada-structural-crosswalk/1.0"
ALLOWED_COLS={"C":"condition","D":"bats_id","E":"trial","N":"origin_name","O":"for_article_datasets_name"}
SHEET="1st_table"
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def get_bytes():
    req=urllib.request.Request(URL,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with urllib.request.urlopen(req,timeout=60) as r:
        b=r.read(SIZE+1)
    if len(b)!=SIZE: raise RuntimeError(f"size mismatch {len(b)} != {SIZE}")
    if hashlib.md5(b).hexdigest()!=MD5: raise RuntimeError("MD5 mismatch")
    return b

def shared(z,needed):
    if not needed:return {}
    out={};i=-1
    with z.open("xl/sharedStrings.xml") as fh:
        for _,e in ET.iterparse(fh,events=("end",)):
            if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
                i+=1
                if i in needed: out[i]="".join(t.text or "" for t in e.findall(".//m:t",NS))
                e.clear()
    return out

def col_letters(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def read_allowed(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    target=None
    for sh in wb.findall("m:sheets/m:sheet",NS):
        if sh.attrib.get("name")==SHEET:
            rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target=relmap[rid].lstrip("/")
            break
    if target is None: raise RuntimeError("sheet missing")
    if not target.startswith("xl/"): target="xl/"+target
    root=ET.fromstring(z.read(target))
    rows=root.findall("m:sheetData/m:row",NS)

    tmp=[];need=set()
    for row in rows[1:]:
        d={"excel_row":int(row.attrib.get("r","0"))}
        for c in row.findall("m:c",NS):
            cc=col_letters(c.attrib.get("r"))
            if cc not in ALLOWED_COLS: continue
            key=ALLOWED_COLS[cc]; typ=c.attrib.get("t")
            if typ=="inlineStr":
                t=c.find(".//m:t",NS); d[key]=t.text if t is not None else None
            else:
                v=c.find("m:v",NS)
                if v is None: continue
                if typ=="s":
                    ix=int(v.text); need.add(ix); d[key]=("S",ix)
                elif typ=="b":
                    d[key]="1" if v.text=="1" else "0"
                else:
                    d[key]=v.text
        if len(d)>1: tmp.append(d)
    ss=shared(z,need)
    return [{k:(ss[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()} for d in tmp]

def norm(v):
    if v is None:return None
    s=str(v).strip()
    return None if s=="" or s.lower() in {"na","nan","none","null","n/a"} else s

def main():
    rows=read_allowed(get_bytes())
    # Normalize only for structural equality; preserve source values in rows.
    for r in rows:
        for k in ALLOWED_COLS.values():
            r[k]=norm(r.get(k))
    by_bat=collections.defaultdict(list)
    for r in rows:
        if r.get("bats_id") is not None:
            by_bat[r["bats_id"]].append(r)

    cond_vocab=collections.Counter(r.get("condition") for r in rows)
    trial_vocab=collections.Counter(r.get("trial") for r in rows)
    bats=[]
    cond_bats=collections.defaultdict(set)
    for bat,rr in sorted(by_bat.items(),key=lambda kv:str(kv[0])):
        conds=sorted(set(x["condition"] for x in rr if x.get("condition") is not None))
        trials=sorted(set(x["trial"] for x in rr if x.get("trial") is not None),key=str)
        for c in conds:cond_bats[c].add(bat)
        bats.append({
          "bat_id":bat,"n_rows":len(rr),"conditions":conds,"trials":trials,
          "rows":[{
            "excel_row":x["excel_row"],"condition":x.get("condition"),"trial":x.get("trial"),
            "origin_name":x.get("origin_name"),"for_article_datasets_name":x.get("for_article_datasets_name")
          } for x in rr]
        })

    out={
      "contract":"STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md",
      "kinematic_outcomes_opened":False,
      "n_structural_rows":len(rows),
      "condition_vocabulary":{str(k):v for k,v in sorted(cond_vocab.items(),key=lambda kv:str(kv[0]))},
      "trial_vocabulary":{str(k):v for k,v in sorted(trial_vocab.items(),key=lambda kv:str(kv[0]))},
      "n_unique_bats":len(by_bat),
      "bats_per_condition":{str(k):len(v) for k,v in sorted(cond_bats.items(),key=lambda kv:str(kv[0]))},
      "bat_summaries":bats,
    }
    # Pure support checks except raw-sheet one-to-one, which a separate deterministic
    # mapping script will adjudicate against the already-opened workbook sheet names.
    same_trial_sets={tuple(x["trials"]) for x in bats}
    out["support_checks"]={
      "exactly_14_bats":len(by_bat)==14,
      "exactly_28_rows":len(rows)==28,
      "all_bats_two_rows":all(x["n_rows"]==2 for x in bats),
      "all_bats_one_condition":all(len(x["conditions"])==1 for x in bats),
      "seven_bats_each_condition":sorted(len(v) for v in cond_bats.values())==[7,7] if len(cond_bats)==2 else False,
      "common_two_trial_labels":len(same_trial_sets)==1 and all(len(x["trials"])==2 for x in bats),
      "common_trial_set":list(next(iter(same_trial_sets))) if len(same_trial_sets)==1 else None,
    }
    out["pre_crosswalk_verdict"]="PASS_TO_DETERMINISTIC_SHEET_CROSSWALK" if all(out["support_checks"][k] for k in [
      "exactly_14_bats","exactly_28_rows","all_bats_two_rows","all_bats_one_condition","seven_bats_each_condition","common_two_trial_labels"
    ]) else "STOP_STRUCTURAL_SUPPORT"
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
