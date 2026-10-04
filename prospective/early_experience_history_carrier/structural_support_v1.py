#!/usr/bin/env python3
"""Outcome-blind structural support gate for Rachum et al. Outdoor data.xlsx.

Reads only row values authorized in STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md.
Never reads the three nightly behavioural outcome columns G/H/J.
"""
from __future__ import annotations
import collections, datetime as dt, hashlib, io, json, math, re, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
DS="wh7c636y3t"
FID="48df4e40-8f31-4bbd-a854-4078274e8fb1"
SIZE=52518
SHA="03a89b2c7de5db56b9776c34a1827f6063da1074909c081e1dbb942f88c9bd0f"
UA="batter-early-experience-structural-support/1.0"
ALLOWED={"Bat_ID","Sex","Environmental condition","Origin","Date","NumberDaysOut","Age (days)"}
FORBIDDEN={"Time Out (Minute)","Max distance (meters)","Explored area"}
NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships"}

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("download budget exceeded")
    return b

def col_letters(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def parse_shared(z,needed):
    out={}
    if not needed:return out
    idx=-1
    with z.open("xl/sharedStrings.xml") as fh:
        for ev,e in ET.iterparse(fh,events=("end",)):
            if e.tag=="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si":
                idx+=1
                if idx in needed:
                    out[idx]="".join(t.text or "" for t in e.findall(".//m:t",NS))
                e.clear()
    return out

def read_allowed_rows(b):
    z=zipfile.ZipFile(io.BytesIO(b))
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    target=None
    for sh in wb.findall("m:sheets/m:sheet",NS):
        if sh.attrib.get("name")=="exit_time_temp_new":
            rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target=relmap[rid].lstrip("/")
            break
    if target is None:raise RuntimeError("sheet missing")
    if not target.startswith("xl/"):target="xl/"+target
    root=ET.fromstring(z.read(target))
    rows=root.findall("m:sheetData/m:row",NS)
    if not rows:raise RuntimeError("empty sheet")

    # header row only, already opened under parent contract
    header_raw={}
    needed=set()
    for c in rows[0].findall("m:c",NS):
        col=col_letters(c.attrib.get("r")); typ=c.attrib.get("t")
        if typ=="inlineStr":
            t=c.find(".//m:t",NS); header_raw[col]=t.text if t is not None else None
        else:
            v=c.find("m:v",NS)
            if v is None: continue
            if typ=="s":
                ix=int(v.text); needed.add(ix); header_raw[col]=("S",ix)
            else: header_raw[col]=v.text
    shared=parse_shared(z,needed)
    headers={c:(shared[v[1]] if isinstance(v,tuple) else v) for c,v in header_raw.items()}
    allowed_cols={c:h for c,h in headers.items() if h in ALLOWED}
    forbidden_cols={c:h for c,h in headers.items() if h in FORBIDDEN}
    if set(allowed_cols.values())!=ALLOWED:
        raise RuntimeError(f"allowed column drift: {sorted(allowed_cols.values())}")
    if set(forbidden_cols.values())!=FORBIDDEN:
        raise RuntimeError("forbidden outcome headers drift")

    # collect only allowed cells. Forbidden outcome cell nodes are never dereferenced.
    temp=[]; needed=set()
    for row in rows[1:]:
        d={}
        for c in row.findall("m:c",NS):
            col=col_letters(c.attrib.get("r"))
            if col not in allowed_cols: continue
            name=allowed_cols[col]; typ=c.attrib.get("t")
            if typ=="inlineStr":
                t=c.find(".//m:t",NS); d[name]=t.text if t is not None else None
            else:
                v=c.find("m:v",NS)
                if v is None: continue
                if typ=="s":
                    ix=int(v.text); needed.add(ix); d[name]=("S",ix)
                elif typ=="b": d[name]="1" if v.text=="1" else "0"
                else: d[name]=v.text
        if d: temp.append(d)
    shared=parse_shared(z,needed)
    return [{k:(shared[v[1]] if isinstance(v,tuple) else v) for k,v in d.items()} for d in temp]

def norm(v):
    if v is None:return None
    s=str(v).strip()
    return None if s=="" or s.lower() in {"na","nan","none","null","n/a"} else s

def excel_date(v):
    s=norm(v)
    if s is None:return None
    # numeric Excel serial
    try:
        x=float(s)
        if 20000 < x < 70000:
            return (dt.datetime(1899,12,30)+dt.timedelta(days=x)).date()
    except Exception:
        pass
    fmts=["%Y-%m-%d","%d/%m/%Y","%m/%d/%Y","%Y/%m/%d","%d-%m-%Y"]
    for f in fmts:
        try:return dt.datetime.strptime(s[:10],f).date()
        except Exception:pass
    try:return dt.datetime.fromisoformat(s.replace("Z","")).date()
    except Exception:return None

def main():
    meta=get_json(f"{BASE}/datasets/{DS}/files/{FID}")
    cd=meta.get("content_details") or {}
    if meta.get("filename")!="Outdoor data.xlsx":raise RuntimeError("filename drift")
    b=get_bytes(cd["download_url"],SIZE+4096)
    if len(b)!=SIZE:raise RuntimeError(f"size mismatch {len(b)}")
    if hashlib.sha256(b).hexdigest()!=SHA:raise RuntimeError("hash mismatch")
    rows=read_allowed_rows(b)

    # vocabularies
    vocab={}
    for col in ["Environmental condition","Origin","Sex"]:
        cnt=collections.Counter(norm(r.get(col)) for r in rows)
        vocab[col]={"values":sorted(x for x in cnt if x is not None),
                    "counts":{str(k):v for k,v in sorted(cnt.items(),key=lambda kv:str(kv[0]))}}

    by_bat=collections.defaultdict(list)
    bad_date=0
    for r in rows:
        bat=norm(r.get("Bat_ID"))
        d=excel_date(r.get("Date"))
        if d is None:bad_date+=1
        if bat is not None:
            rr=dict(r); rr["_date"]=d
            by_bat[bat].append(rr)

    summaries=[]
    years=set()
    for bat,rr in sorted(by_bat.items()):
        conds=sorted(set(norm(x.get("Environmental condition")) for x in rr if norm(x.get("Environmental condition")) is not None))
        origins=sorted(set(norm(x.get("Origin")) for x in rr if norm(x.get("Origin")) is not None))
        sexes=sorted(set(norm(x.get("Sex")) for x in rr if norm(x.get("Sex")) is not None))
        dates=sorted(set(x["_date"] for x in rr if x["_date"] is not None))
        ys=sorted(set(d.year for d in dates)); years.update(ys)
        # Also audit source NumberDaysOut structurally without treating it as outcome.
        ndo=[]
        for x in rr:
            v=norm(x.get("NumberDaysOut"))
            try: ndo.append(float(v)) if v is not None else None
            except Exception: pass
        summaries.append({
            "Bat_ID":bat,
            "conditions":conds,
            "origins":origins,
            "sexes":sexes,
            "years":ys,
            "n_rows":len(rr),
            "n_unique_dates":len(dates),
            "number_days_out_min":min(ndo) if ndo else None,
            "number_days_out_max":max(ndo) if ndo else None,
            "pass_ge10_unique_dates":len(dates)>=10,
        })

    if len(years)==2:
        season_rule="calendar_year"
        block_status="PASS_TWO_YEAR_SOURCE_SEASONS"
    else:
        season_rule=None
        block_status="STOP_YEAR_DOES_NOT_RESOLVE_TWO_SEASONS"

    # treatment labels remain source-native; infer E/I only by unambiguous lexical names.
    def arm(cond):
        c=(cond or "").strip().lower()
        if "enrich" in c:return "enriched"
        if "impover" in c or "poor" in c:return "impoverished"
        return None

    arm_counts=collections.Counter()
    arm_ge10=collections.Counter()
    block_bats=collections.defaultdict(set)
    ambiguous=[]
    for x in summaries:
        if len(x["conditions"])!=1 or len(x["origins"])!=1 or len(x["years"])!=1:
            ambiguous.append(x["Bat_ID"]); continue
        a=arm(x["conditions"][0])
        if a is None:
            ambiguous.append(x["Bat_ID"]); continue
        arm_counts[a]+=1
        if x["pass_ge10_unique_dates"]:arm_ge10[a]+=1
        if season_rule:
            block_bats[(x["years"][0],x["origins"][0],a)].add(x["Bat_ID"])

    verdict=(
        "PASS_FREEZE_NIGHTLY_STRATEGY_ESTIMATOR"
        if block_status.startswith("PASS")
        and not ambiguous
        and arm_ge10["enriched"]>=5
        and arm_ge10["impoverished"]>=5
        else "STOP_STRUCTURAL_SUPPORT_OR_LINKAGE"
    )
    out={
        "contract":"STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md",
        "behavioural_outcome_values_opened":False,
        "n_rows":len(rows),
        "n_unique_bats":len(summaries),
        "bad_date_rows":bad_date,
        "vocabularies":vocab,
        "years":sorted(years),
        "season_rule":season_rule,
        "block_status":block_status,
        "bat_summaries":summaries,
        "ambiguous_identity_treatment_block_bats":ambiguous,
        "treatment_bats":dict(arm_counts),
        "treatment_bats_ge10_unique_dates":dict(arm_ge10),
        "block_counts":[
            {"year":k[0],"origin":k[1],"arm":k[2],"n_bats":len(v)}
            for k,v in sorted(block_bats.items())
        ],
        "frozen_minimum_per_arm_ge10":5,
        "verdict":verdict,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
