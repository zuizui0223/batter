#!/usr/bin/env python3
"""Source-structure only: original 2024 PNAS supplement alternate to inaccessible Mendeley.

NO biological numeric outcome values from worksheet rows >1 are opened.
Never follows arbitrary source links. Stops on corruption, unexpected hosts,
missing source and unsupported schema; cannot authorize an outcome analysis.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import posixpath
import re
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path

URLS=(
 "https://pmc.ncbi.nlm.nih.gov/articles/PMC11287165/bin/pnas.2321724121.sd01.xlsx",
 "https://www.pnas.org/doi/suppl/10.1073/pnas.2321724121/suppl_file/pnas.2321724121.sd01.xlsx",
)
MAX_BYTES=2_000_000
MAX_UNCOMPRESSED=12_000_000
MAX_XML=4_000_000
SS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RREL="{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
PACK="{http://schemas.openxmlformats.org/package/2006/relationships}"
ALLOWED=("ncbi.nlm.nih.gov","nih.gov","pnas.org")
USER_AGENT="batter-structural-PNAS-2024-v1/1.0"


def allowed(u):
    q=urllib.parse.urlparse(u)
    if q.scheme != "https":return False
    h=(q.hostname or "").lower()
    return any(h==s or h.endswith("."+s) for s in ALLOWED)


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        if not allowed(newurl):raise ValueError("STOP_REDIRECT_HOST")
        return super().redirect_request(request,fp,code,msg,headers,newurl)


def get(url):
    assert url in URLS
    op=urllib.request.build_opener(SafeRedirect())
    req=urllib.request.Request(url,headers={"User-Agent":USER_AGENT,
                 "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*"})
    try:
        with op.open(req,timeout=30) as response:
            body=response.read(MAX_BYTES+1)
            final=response.geturl()
            ct=response.headers.get("Content-Type","")
            status=response.status
    except urllib.error.HTTPError as e:
        return None,{"status":"HTTP_ERROR","http":e.code,"source_url":url}
    except Exception as e:
        return None,{"status":"DOWNLOAD_ERROR","error_type":type(e).__name__,"source_url":url}
    if len(body)>MAX_BYTES or not allowed(final):
        return None,{"status":"OVERSIZE_OR_BAD_REDIRECT","source_url":url}
    if not body.startswith(b"PK"):
        return None,{"status":"NOT_XLSX_ZIP","http":status,"source_url":url,
                     "content_type":ct[:100]}
    return body,{"status":"FETCHED","http":status,"size_bytes":len(body),
        "content_type":ct[:100],"source_url":url,"final_url":final,
        "sha256":hashlib.sha256(body).hexdigest()}


def first_row_xml(blob):
    # Never collect the <sheetData> rows after the first row.
    parser=ET.iterparse(io.BytesIO(blob),events=("end",))
    cells=[]
    for _ev,element in parser:
        if element.tag==SS+"row" and element.get("r")=="1":
            for c in element.findall(SS+"c"):
                value=c.find(SS+"v")
                istr=c.find(SS+"is")
                inline="".join(t.text or "" for t in (istr.iter(SS+"t") if istr is not None else []))
                cells.append((c.get("r"),c.get("t"),value.text if value is not None else None,inline))
            element.clear()
            break
        if element.tag==SS+"row":
            element.clear()
            break
        element.clear()
    return cells


def extract_safe(zf):
    names=set(zf.namelist())
    bad=[n for n in names if n.lower().endswith((".bin",".vba")) or
         "externallink" in n.lower() or n.startswith("/") or ".." in n.split("/")]
    total=sum(i.file_size for i in zf.infolist())
    if bad or total>MAX_UNCOMPRESSED or len(names)>150:
        raise ValueError("UNSAFE_XLSX_CONTAINER")
    for name in ("xl/workbook.xml","xl/_rels/workbook.xml.rels"):
        if name not in names:raise ValueError("MISSING_XLSX_WORKBOOK_XML")
    wb=ET.fromstring(zf.read("xl/workbook.xml"))
    rel=ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    targets={}
    for item in rel.findall(PACK+"Relationship"):
        rid=item.get("Id")
        target=item.get("Target","")
        if target.startswith("/"):full=target.lstrip("/")
        elif target.startswith("xl/"):full=target
        else:full=posixpath.normpath(posixpath.join("xl",target))
        targets[rid]=full
    ss_path="xl/sharedStrings.xml"
    shared=[]
    if ss_path in names:
        if zf.getinfo(ss_path).file_size>MAX_XML:raise ValueError("OVERSIZE_SHARED_STRINGS")
        root=ET.fromstring(zf.read(ss_path))
        shared=["".join(t.text or "" for t in item.iter(SS+"t"))
                for item in root.findall(SS+"si")]
    sheets=[]
    known_roots=wb.find(SS+"sheets")
    if known_roots is None:raise ValueError("NO_SHEETS")
    for sheet in known_roots.findall(SS+"sheet"):
        sheet_name=sheet.get("name","")
        path=targets.get(sheet.get(RREL))
        if path not in names or zf.getinfo(path).file_size>MAX_XML:
            raise ValueError("MISSING_OR_OVERSIZE_WORKSHEET")
        # Workbook XML sheet dimension is metadata; read only first row elements.
        payload=zf.read(path)
        root=ET.fromstring(payload)
        dimension=root.find(SS+"dimension")
        dim=dimension.get("ref","") if dimension is not None else ""
        # iterparse extracts only first row labels; never traverses values below.
        col=[]
        for cell,t,v,inline in first_row_xml(payload):
            if t=="s" and v is not None:
                idx=int(v)
                val=shared[idx] if 0<=idx<len(shared) else "MISSING_SHARED_STRING"
            elif t=="inlineStr":val=inline
            elif t=="str":val=v or ""
            elif t is None and v is not None:
                val="NUMERIC_HEADER_PRESENT" # Do not reproduce numeric values
            else:val=""
            col.append({"column":re.match(r"^[A-Z]+",cell or "").group(0)
                if re.match(r"^[A-Z]+",cell or "") else "",
                "label":str(val).strip()[:90]})
        labels=[x["label"].lower() for x in col]
        checks={
            "possible_physical_bat_key":any(re.search(r"bat.?id|individual|animal.?id|identity",x) for x in labels),
            "possible_date_bout_key":any(re.search(r"date|night|session|bout|recording|flight.?id|day",x) for x in labels),
            "possible_call_exposure":any(re.search(r"call|conspecific|social|density",x) for x in labels),
            "possible_success_outcome":any(re.search(r"success|capture|chew",x) for x in labels),
            "possible_attack_outcome":any(re.search(r"attack|buzz|attempt",x) for x in labels)
        }
        sheets.append({"sheet_name":sheet_name[:100],"declared_range":dim[:50],
                       "row1_headers":col[:65],"header_flags":checks})
    return sheets


def self_test():
    assert not allowed("http://pmc.ncbi.nlm.nih.gov/bad")
    assert not allowed("https://evil.example.org/xlsx")
    assert allowed(URLS[0]) and allowed(URLS[1])
    example=b'<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Bat ID</t></is></c></row><row r="2"><c r="A2"><v>12345</v></c></row></sheetData></worksheet>'
    assert len(first_row_xml(example))==1
    assert first_row_xml(example)[0][3]=="Bat ID"
    return "PASS_HEADER_ONLY_TEST"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="PNAS_2024_SUPPLEMENT_HEADER_RECEIPT_V1.json")
    a=p.parse_args()
    checks=self_test()
    if a.self_test:
        print(json.dumps({"self_test":checks,"opened_real_outcomes":False}));return
    tries=[]
    workbook=None
    for u in URLS:
        payload,meta=get(u)
        tries.append(meta)
        if payload:
            try:
                with zipfile.ZipFile(io.BytesIO(payload)) as z:
                    workbook=extract_safe(z)
                break
            except Exception as e:
                tries[-1]["status"]="STOP_UNEXPECTED_SOURCE_SCHEMA_OR_SIZE"
                tries[-1]["parse_error_type"]=type(e).__name__
                break
    if workbook is None:
        st="STOP_UNEXPECTED_SOURCE_SCHEMA_OR_SIZE" if any(
            x["status"]=="STOP_UNEXPECTED_SOURCE_SCHEMA_OR_SIZE" for x in tries
            ) else "STOP_ALTERNATE_SUPPLEMENT_INACCESSIBLE"
    else:
        could=any(s["header_flags"]["possible_physical_bat_key"] and
            s["header_flags"]["possible_date_bout_key"] for s in workbook)
        st=("HOLD_HEADERS_ONLY_INDEPENDENT_BOUTS_NOT_YET_VERIFIED"
            if could else "STOP_NO_BAT_BOUT_STRUCTURE_IN_SUPPLEMENT")
    receipt={"source_doi":"10.1073/pnas.2321724121",
       "metadata_source":"PMC11287165 advertised pnas.2321724121.sd01.xlsx",
       "contract":"PNAS_2024_SUPPLEMENT_HEADER_ONLY_GATE_CONTRACT_V1.md",
       "status":st,"source_attempts":tries,"tabs":workbook or [],
       "biological_numeric_values_or_bat_outcomes_opened":False,
       "independent_bat_bouts_confirmed":False,
       "self_test":checks,"eligible_for_biological_analysis":False}
    Path(a.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":st,"tabs":len(workbook or []),
      "file_download_succeeded":workbook is not None,"numeric_outcomes_opened":False,
      "receipt":a.out},sort_keys=True))


if __name__=="__main__":main()
