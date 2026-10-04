#!/usr/bin/env python3
"""Recover source-native Season/Origin block linkage without opening outcomes."""
from __future__ import annotations
import collections, datetime as dt, hashlib, io, json, math, re, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"; DS="wh7c636y3t"; UA="batter-randomization-linkage/1.0"
FILES={
 "baseline":("97b85935-2a81-4af3-be1e-7ff8cfa1eccc","All seasons personality data.xlsx",44838,
             "8155be769fc3e6cf9d3cc0d59fa7c216a176999662cd8272dd99d7741acd723f",
             "Full_Data",{"Bat_no","Individual","Season","Origin","Colony","Colony type"}),
 "outdoor":("48df4e40-8f31-4bbd-a854-4078274e8fb1","Outdoor data.xlsx",52518,
            "03a89b2c7de5db56b9776c34a1827f6063da1074909c081e1dbb942f88c9bd0f",
            "exit_time_temp_new",{"Bat_ID","Environmental condition","Origin","Date","NumberDaysOut"}),
}
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)
def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("budget")
    return b
def norm(v):
    if v is None:return None
    s=str(v).strip()
    return None if s=="" or s.lower() in {"na","nan","none","null","n/a"} else s
def col(ref):
    m=re.match(r"([A-Z]+)",ref or ""); return m.group(1) if m else None
def shared(z,needed):
    out={}; idx=-1
    if not needed:return out
    with z.open("xl/sharedStrings.xml") as fh:
        for _,e in ET.iterparse(fh,events=("end",)):
            if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
                idx+=1
                if idx in needed:out[idx]="".join(t.text or "" for t in e.findall(".//m:t",NS))
                e.clear()
    return out
def rows_selected(b,sheet,allowed):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml")); rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    target=None
    for sh in wb.findall("m:sheets/m:sheet",NS):
        if sh.attrib.get("name")==sheet:
            target=relmap[sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]].lstrip("/");break
    if not target:raise RuntimeError("sheet missing")
    if not target.startswith("xl/"):target="xl/"+target
    root=ET.fromstring(z.read(target)); rr=root.findall("m:sheetData/m:row",NS)
    hraw={}; need=set()
    for c in rr[0].findall("m:c",NS):
        cc=col(c.attrib.get("r")); typ=c.attrib.get("t"); v=c.find("m:v",NS)
        if typ=="inlineStr":
            t=c.find(".//m:t",NS);hraw[cc]=t.text if t is not None else None
        elif v is not None:
            if typ=="s":ix=int(v.text);need.add(ix);hraw[cc]=("S",ix)
            else:hraw[cc]=v.text
    sh=shared(z,need); heads={c:(sh[v[1]] if isinstance(v,tuple) else v) for c,v in hraw.items()}
    amap={c:h for c,h in heads.items() if h in allowed}
    if set(amap.values())!=allowed:raise RuntimeError(f"header drift {sheet}: {sorted(amap.values())}")
    tmp=[];need=set()
    for row in rr[1:]:
        d={}
        for c in row.findall("m:c",NS):
            cc=col(c.attrib.get("r"))
            if cc not in amap:continue
            typ=c.attrib.get("t");v=c.find("m:v",NS)
            if typ=="inlineStr":
                t=c.find(".//m:t",NS);d[amap[cc]]=t.text if t is not None else None
            elif v is not None:
                if typ=="s":ix=int(v.text);need.add(ix);d[amap[cc]]=("S",ix)
                else:d[amap[cc]]=v.text
        if d:tmp.append(d)
    sh=shared(z,need)
    return [{k:(sh[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()} for d in tmp]
def fetch(spec):
    fid,name,size,sha,sheet,allowed=spec
    m=get_json(f"{BASE}/datasets/{DS}/files/{fid}");cd=m.get("content_details") or {}
    b=get_bytes(cd["download_url"],size+4096)
    if len(b)!=size or hashlib.sha256(b).hexdigest()!=sha:raise RuntimeError(f"integrity {name}")
    return rows_selected(b,sheet,allowed)
def parse_date(v):
    s=norm(v)
    try:
        x=float(s)
        if 20000<x<70000:return (dt.datetime(1899,12,30)+dt.timedelta(days=x)).date()
    except Exception:pass
    for f in ("%Y-%m-%d","%d/%m/%Y","%m/%d/%Y","%Y/%m/%d"):
        try:return dt.datetime.strptime(s[:10],f).date()
        except Exception:pass
    return None

def main():
    base=fetch(FILES["baseline"]);out=fetch(FILES["outdoor"])
    bmap=collections.defaultdict(lambda:collections.defaultdict(set))
    for r in base:
        name=norm(r.get("Individual"))
        if name is None:continue
        for k in ("Season","Origin","Colony","Colony type","Bat_no"):
            v=norm(r.get(k))
            if v is not None:bmap[name][k].add(v)
    omap=collections.defaultdict(list)
    for r in out:
        n=norm(r.get("Bat_ID"))
        if n:omap[n].append(r)
    cross=[];conflicts=[];year_season=collections.defaultdict(set)
    for bat,rr in sorted(omap.items()):
        origins=sorted(set(norm(x.get("Origin")) for x in rr if norm(x.get("Origin"))))
        conds=sorted(set(norm(x.get("Environmental condition")) for x in rr if norm(x.get("Environmental condition"))))
        dates=sorted(set(parse_date(x.get("Date")) for x in rr if parse_date(x.get("Date"))))
        years=sorted(set(x.year for x in dates))
        bm=bmap.get(bat,{})
        seasons=sorted(bm.get("Season",set()));borig=sorted(bm.get("Origin",set()))
        if len(origins)==1 and len(borig)==1 and origins[0]!=borig[0]:conflicts.append({"bat":bat,"type":"origin","outdoor":origins,"baseline":borig})
        if len(years)==1 and len(seasons)==1:year_season[years[0]].add(seasons[0])
        resolved_origin=origins[0] if len(origins)==1 else (borig[0] if len(borig)==1 else None)
        resolved_season=seasons[0] if len(seasons)==1 else None
        cross.append({"Bat_ID":bat,"condition":conds[0] if len(conds)==1 else None,
                      "outdoor_origin":origins,"baseline_origin":borig,
                      "baseline_season":seasons,"years":years,
                      "resolved_origin":resolved_origin,"resolved_season":resolved_season,
                      "n_unique_dates":len(dates)})
    ymap={str(y):sorted(v) for y,v in sorted(year_season.items())}
    bij=(len(ymap)==2 and all(len(v)==1 for v in ymap.values()) and len(set(v[0] for v in ymap.values()))==2)
    bad=[x["Bat_ID"] for x in cross if x["condition"] is None or x["resolved_origin"] is None or x["resolved_season"] is None]
    e=sum(x["n_unique_dates"]>=10 and x["condition"]=="Enriched" for x in cross)
    im=sum(x["n_unique_dates"]>=10 and x["condition"]=="Impoverished" for x in cross)
    blocks=collections.Counter()
    for x in cross:
        if x["resolved_origin"] and x["resolved_season"] and x["condition"]:
            blocks[(x["resolved_season"],x["resolved_origin"],x["condition"])]+=1
    verdict="PASS_FREEZE_NIGHTLY_STRATEGY_ESTIMATOR" if not conflicts and not bad and bij and e>=5 and im>=5 else "STOP_RANDOMIZATION_LINKAGE"
    print(json.dumps({
      "contract":"RANDOMIZATION_LINKAGE_AMENDMENT_V1.md","behavioural_outcomes_opened":False,
      "baseline_rows_structural_only":len(base),"outdoor_rows_structural_only":len(out),
      "year_to_source_season":ymap,"year_season_bijection":bij,"conflicts":conflicts,
      "unresolved_bats":bad,"bat_crosswalk":cross,
      "eligible_ge10":{"Enriched":e,"Impoverished":im},
      "block_counts":[{"season":k[0],"origin":k[1],"condition":k[2],"n_bats":v} for k,v in sorted(blocks.items())],
      "verdict":verdict
    },ensure_ascii=False,indent=2))
if __name__=="__main__":main()
