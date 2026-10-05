#!/usr/bin/env python3
"""Outcome-blind structural support opening for Taub & Yovel clutter-recall data."""
from __future__ import annotations
import collections, datetime as dt, hashlib, io, json, math, re, time
import urllib.error, urllib.request, zipfile
import xml.etree.ElementTree as ET

BASE="https://data.mendeley.com/public-api"
DS="wccbjdrrsg"; VERSION=1
UA="batter-clutter-recall-structural/1.0"
FILE_ID="68317f75-3a03-4756-b7e5-3f5fd94853d5"
FILE_NAME="Clutter Chamber Data.xlsx"
FILE_SIZE=1435343
FILE_SHA="bc1b2b40c5e3198a2cccd9211fa1e001d8b23e71833b784a9803781a83b31032"

NS={
 "m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main",
 "r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

def _open(req,timeout):
    last=None
    for a in range(5):
        try:return urllib.request.urlopen(req,timeout=timeout)
        except urllib.error.HTTPError as e:
            last=e
            if e.code not in (429,500,502,503,504):raise
        except urllib.error.URLError as e:last=e
        if a<4:time.sleep(2**a)
    raise last

def get_json(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with _open(req,60) as r:return json.load(r)

def get_bytes(url,maxn):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/octet-stream"})
    with _open(req,90) as r:b=r.read(maxn+1)
    if len(b)>maxn:raise RuntimeError("download budget exceeded")
    return b

def fetch():
    url=f"{BASE}/datasets/{DS}/files?folder_id=root&version={VERSION}&$start=0&$limit=1000"
    rows=get_json(url)
    if isinstance(rows,dict):rows=rows.get("files") or rows.get("items") or rows.get("results") or []
    r=next((x for x in rows if x.get("id")==FILE_ID),None)
    if r is None:raise RuntimeError("pinned clutter workbook missing")
    cd=r.get("content_details") or {}
    if r.get("filename")!=FILE_NAME:raise RuntimeError("filename drift")
    if int(cd.get("size") or r.get("size") or 0)!=FILE_SIZE:raise RuntimeError("size drift")
    loc=cd.get("download_url") or r.get("download_url") or cd.get("url") or r.get("file_url")
    if not loc:
        loc=f"https://data.mendeley.com/public-files/datasets/{DS}/files/{FILE_ID}/file_downloaded"
    b=get_bytes(loc,FILE_SIZE+8192)
    if len(b)!=FILE_SIZE:raise RuntimeError("download size mismatch")
    if hashlib.sha256(b).hexdigest()!=FILE_SHA:raise RuntimeError("sha mismatch")
    return b

def workbook_paths(z):
    wb=ET.fromstring(z.read("xl/workbook.xml"))
    rel=ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
    relmap={x.attrib["Id"]:x.attrib["Target"] for x in rel}
    out={}
    for sh in wb.findall("m:sheets/m:sheet",NS):
        rid=sh.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
        p=relmap[rid].lstrip("/")
        if not p.startswith("xl/"):p="xl/"+p
        out[sh.attrib["name"]]=p
    return out

def shared(z):
    if "xl/sharedStrings.xml" not in z.namelist():return []
    root=ET.fromstring(z.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.findall(".//m:t",NS)) for si in root.findall("m:si",NS)]

def col(ref):
    m=re.match(r"([A-Z]+)",ref or "")
    return m.group(1) if m else None

def raw_cell(c,ss,allow_numeric):
    typ=c.attrib.get("t"); v=c.find("m:v",NS)
    if typ=="inlineStr":
        t=c.find(".//m:t",NS);return (t.text or "") if t is not None else ""
    if typ=="s" and v is not None:
        ix=int(v.text);return ss[ix] if 0<=ix<len(ss) else None
    if typ=="str" and v is not None:return v.text or ""
    if allow_numeric and v is not None:
        try:return float(v.text)
        except Exception:return v.text
    return None

def excel_date(v):
    if v is None:return None
    if isinstance(v,str):
        q=v.strip()
        for fmt in ("%Y-%m-%d","%d/%m/%Y","%m/%d/%Y","%d.%m.%Y","%d.%m.%y"):
            try:return dt.datetime.strptime(q,fmt).date().isoformat()
            except Exception:pass
        try:v=float(q)
        except Exception:return q
    if isinstance(v,(int,float)) and math.isfinite(v):
        base=dt.datetime(1899,12,30)
        try:return (base+dt.timedelta(days=float(v))).date().isoformat()
        except Exception:return str(v)
    return str(v)

def parse_bat_info(z,path,ss):
    root=ET.fromstring(z.read(path))
    rows=[]
    for row in root.findall("m:sheetData/m:row",NS):
        rn=int(row.attrib.get("r","0"))
        if rn<2:continue
        d={}
        for c in row.findall("m:c",NS):
            cc=col(c.attrib.get("r"))
            if cc not in set("ABCDEFGH"):continue
            d[cc]=raw_cell(c,ss,True)
        if any(v not in (None,"") for v in d.values()):
            for k in ("B","C","E","F","G"):
                if k in d:d[k]=excel_date(d[k])
            rows.append({"row":rn,**d})
    return rows

def parse_call_structure(z,path,ss):
    root=ET.fromstring(z.read(path))
    rows=[]
    for row in root.findall("m:sheetData/m:row",NS):
        rn=int(row.attrib.get("r","0"))
        if rn<2:continue
        d={}
        for c in row.findall("m:c",NS):
            cc=col(c.attrib.get("r"))
            if cc not in {"A","B","C","D"}:continue
            d[cc]=raw_cell(c,ss,True)
        if d:
            if "B" in d:d["B"]=excel_date(d["B"])
            rows.append(d)
    return rows

def looks_bat(x):
    if x is None:return None
    m=re.search(r"(?:bat\s*)?([1-5])",str(x),re.I)
    return int(m.group(1)) if m else None

def choose_info(info):
    # Return first structural row that names each Bat1..Bat5 in column A.
    out={}
    for r in info:
        b=looks_bat(r.get("A"))
        if b and b not in out:out[b]=r
    return out

def dparse(x):
    if x is None:return None
    q=str(x).strip()
    try:return dt.date.fromisoformat(q)
    except Exception:pass
    for fmt in ("%d.%m.%y","%d.%m.%Y","%d/%m/%y","%d/%m/%Y"):
        try:return dt.datetime.strptime(q,fmt).date()
        except Exception:pass
    return None

def summarize_calls(rows,first_start,first_end,second_start,second_end):
    bydate=collections.defaultdict(set)
    for r in rows:
        d=dparse(r.get("B"))
        if d is None:continue
        fid=r.get("C")
        if fid is None:continue
        bydate[d].add(str(fid))
    def count(a,b):
        dates=[d for d in bydate if a is not None and b is not None and a<=d<=b]
        return {"n_dates":len(dates),"n_files":sum(len(bydate[d]) for d in dates),
                "dates":[d.isoformat() for d in sorted(dates)]}
    s2=count(first_start,first_end)
    early2=count(first_start,min(first_end,first_start+dt.timedelta(days=13))) if first_start and first_end else {"n_dates":0,"n_files":0,"dates":[]}
    late2=count(max(first_start,first_end-dt.timedelta(days=13)),first_end) if first_start and first_end else {"n_dates":0,"n_files":0,"dates":[]}
    s4=count(second_start,second_end)
    first4={"n_dates":0,"n_files":0,"dates":[]}
    first7={"n_dates":0,"n_files":0,"dates":[]}
    if second_start and second_end:
        ds=[d for d in bydate if second_start<=d<=second_end]
        if ds:
            md=min(ds)
            first4={"n_dates":1,"n_files":len(bydate[md]),"dates":[md.isoformat()]}
        first7=count(second_start,min(second_end,second_start+dt.timedelta(days=6)))
    return {"stage2_all":s2,"stage2_first14d":early2,"stage2_last14d":late2,
            "stage4_all":s4,"stage4_first_recorded_date":first4,"stage4_first7d":first7}

def main():
    b=fetch();z=zipfile.ZipFile(io.BytesIO(b));paths=workbook_paths(z);ss=shared(z)
    info=parse_bat_info(z,paths["bat info"],ss)
    imap=choose_info(info)
    sheets={1:"calls tables-Bat1",2:"calls tables-Bat2",3:"calls tables-Bat3",
            4:"calls table-Bat4",5:"calls tables-Bat5"}
    bats=[]
    for bno in range(1,6):
        ir=imap.get(bno)
        if ir is None:
            bats.append({"bat":bno,"status":"MISSING_BAT_INFO"});continue
        s1=dparse(ir.get("C"));e1=dparse(ir.get("E"));s4=dparse(ir.get("F"));e4=dparse(ir.get("G"))
        date_integrity={
          "stage2_dates_valid":bool(s1 is not None and e1 is not None and e1>=s1),
          "stage4_dates_valid":bool(s4 is not None and e4 is not None and e4>=s4),
        }
        e1_use=e1 if date_integrity["stage2_dates_valid"] else None
        e4_use=e4 if date_integrity["stage4_dates_valid"] else None
        rr=parse_call_structure(z,paths[sheets[bno]],ss)
        sm=summarize_calls(rr,s1,e1_use,s4,e4_use)
        bats.append({"bat":bno,"status":"STRUCTURE_OPENED","date_integrity":date_integrity,
          "bat_info_row":ir,"first_clutter_start":ir.get("C"),"first_clutter_end":ir.get("E"),
          "second_clutter_start":ir.get("F"),"second_clutter_end":ir.get("G"),
          "new_box":ir.get("H"),"call_sheet":sheets[bno],**sm})
    eligible_late=sum(x.get("stage2_last14d",{}).get("n_files",0)>=2 for x in bats)
    eligible_s4=sum(x.get("stage4_all",{}).get("n_files",0)>=2 for x in bats)
    eligible_first=sum(x.get("stage4_first_recorded_date",{}).get("n_files",0)>=1 for x in bats)
    proceed=eligible_late>=4 and eligible_s4>=4 and eligible_first>=4
    print(json.dumps({
      "contract":"STRUCTURAL_ROW_VALUE_ALLOWLIST_V1.md",
      "acoustic_outcome_values_opened":False,
      "workbook_sha256":FILE_SHA,
      "bat_info_rows":info,
      "bats":bats,
      "gate":{"eligible_stage2_last14d":eligible_late,"eligible_stage4_all":eligible_s4,
              "eligible_stage4_first_date":eligible_first,
              "verdict":"PASS_STRUCTURAL_RECALL_SUPPORT" if proceed else "STOP_STRUCTURAL_RECALL_SUPPORT"}
    },ensure_ascii=False,indent=2))

if __name__=="__main__":main()
