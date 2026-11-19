#!/usr/bin/env python3
"""Safi & Kerth 2007 publisher supplements source-only eligibility gate.

No phylogenetic associations are estimated. On 401/403, STOP explicitly.
The sources may be copyrighted; print only provenance and first header.
"""
import hashlib
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

BASE="https://www.journals.uchicago.edu/doi/suppl/10.1086/520116/suppl_file/"
FILES=("42248data.txt","42248data.xls")
OUTPUT=Path(os.environ.get("H1_MALE_SOCIALITY_SOURCE_RECEIPT","/tmp/h1_2007_original_source_gate.json"))

def fetch(url):
    req=urllib.request.Request(url,headers={
      "User-Agent":"Mozilla/5.0 (compatible; ecology source audit/1.0)",
      "Accept":"text/plain,application/vnd.ms-excel,application/octet-stream,*/*"})
    with urllib.request.urlopen(req,timeout=24) as r:
        return r.read(130000),r.status,r.headers.get("Content-Type","")

def header_only(data,ext):
    if ext==".txt":
        raw=data.decode("utf-8-sig",errors="replace")
        if "<html" in raw[:512].lower() or not raw.strip():
            raise ValueError("Publisher response is HTML, not original ASCII")
        lines=[x for x in raw.splitlines() if x.strip()]
        return {"nonempty_line_count":len(lines),
                "line_terminator":"CRLF" if "\r\n" in raw else "LF",
                "first_line_header_or_title":lines[0][:160]}
    if ext==".xls":
        if not data.startswith(bytes.fromhex("d0cf11e0a1b11ae1")):
            raise ValueError("Not original legacy XLS OLE2")
        return {"container":"legacy_xls_ole2","data_columns_unopened":True}
    raise ValueError("Unsupported ext")

def run():
    attempts=[]
    verified=[]
    for filename in FILES:
        url=BASE+filename
        try:
            payload,status,ctype=fetch(url)
            metadata=header_only(payload,(".txt" if filename.endswith(".txt") else ".xls"))
            verified.append({"name":filename,"url":url,"http_status":status,
                             "source_sha256":hashlib.sha256(payload).hexdigest(),
                             "source_bytes":len(payload),"mime":ctype,"format":metadata})
            attempts.append({"name":filename,"http_status":status,"decision":"VALID_FORMAT"})
        except Exception as ex:
            status=ex.code if isinstance(ex,urllib.error.HTTPError) else None
            attempts.append({"name":filename,"http_status":status,"decision":"SOURCE_STOP",
                             "error_type":type(ex).__name__,"error":str(ex)[:120]})
    out={"paper_doi":"10.1086/520116",
         "scientific_target":"original 2007 comparative bat male roost group formation; not direct social foraging",
         "status":"AT_LEAST_ONE_ORIGINAL_FORMAT_PASS" if verified else "STOP_PUBLISHER_ORIGINAL_NOT_AVAILABLE",
         "source_attempts":attempts,"original_format_receipts":verified,
         "species_data_rows_analyzed":False,"new_phylogenetic_results_computed":False,
         "cannot_treat_roost_group_as_foraging_information":True}
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(out,indent=2,ensure_ascii=False))
    if not verified:raise SystemExit(2)

if __name__=="__main__":
    run()
