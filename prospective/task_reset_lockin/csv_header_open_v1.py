#!/usr/bin/env python3
"""Header-only opening of Figshare CSV files for task-reset programme.

Requires HTTP partial content and parses only the first text line.
"""
from __future__ import annotations
import json,re,urllib.request

API="https://api.figshare.com/v2/articles/29209493"
UA="batter-task-reset-header-open/1.0"
PAT=re.compile(r"^Env\d+_Bat[A-Za-z]+_no.+\.csv$")

def get_article():
    req=urllib.request.Request(API,headers={"User-Agent":UA,"Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=60) as r:return json.load(r)

def header_from_range(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":"bytes=0-4095","Accept":"text/csv,text/plain,*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:
        status=getattr(r,"status",None)
        cr=r.headers.get("Content-Range")
        data=r.read(4096)
    if status!=206 or not cr:
        raise RuntimeError(f"range not honored: status={status} content-range={cr}")
    line=data.splitlines()[0] if data.splitlines() else b""
    return line.decode("utf-8-sig",errors="replace").strip()

def main():
    a=get_article()
    rows=[]
    for f in a.get("files") or []:
        name=f.get("name") or ""
        if not PAT.match(name):continue
        h=header_from_range(f["download_url"])
        rows.append({"id":f.get("id"),"name":name,"header":h,"columns":[x.strip() for x in h.split(",")]})
    sig={}
    for r in rows:
        key=tuple(r["columns"])
        sig.setdefault(key,[]).append(r["name"])
    out={
      "contract":"CSV_HEADER_OPENING_ALLOWLIST_V1.md",
      "trajectory_row_values_read":False,
      "n_csv":len(rows),
      "n_header_signatures":len(sig),
      "header_signatures":[{"columns":list(k),"n_files":len(v),"example_files":v[:8]} for k,v in sig.items()],
      "files":rows,
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
