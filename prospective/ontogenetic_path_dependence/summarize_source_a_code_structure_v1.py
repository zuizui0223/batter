#!/usr/bin/env python3
"""Summarize only structural definitions from the already-authorized Source A Code.zip.

No GPS archive, spreadsheet outcome values, or route-similarity calculations are opened.
"""
from __future__ import annotations
import hashlib, io, json, re, urllib.request, zipfile

BASE="https://data.mendeley.com/public-api"
DATASET="gpcg9m5758"
FILE_ID="85077631-f5b9-469a-a628-1ce652944cf8"
EXPECTED_SHA="bfe2fe7a691c33a24b00a8cf56511c3668cce0ce3ebc33c8cc911df61579d773"
TARGETS={
    "Code/dataPrep_allPairs.m",
    "Code/dataPrep_movement.m",
    "Code/Figure5_SimilarPath.m",
    "Code/stats_mompup.m",
    "Code/Figures_mompups.m",
    "Code/Figure6_Exploration.m",
}
UA="batter-source-a-code-structure/1.0"

def get_json(url):
    import json
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:
        return json.load(r)

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=60) as r:
        return r.read(100_000)

def main():
    meta=get_json(f"{BASE}/datasets/{DATASET}/files/{FILE_ID}")
    cd=meta.get("content_details") or {}
    b=get_bytes(cd["download_url"])
    assert hashlib.sha256(b).hexdigest()==EXPECTED_SHA
    z=zipfile.ZipFile(io.BytesIO(b))
    out={}
    # Keep definitions and control flow likely to expose schema / segmentation;
    # exclude plot/statistic-only lines unless they name a structural variable.
    structural=re.compile(
        r"(readtable|load\(|dir\(|fullfile|fieldnames|Properties\.VariableNames|"
        r"allPairs\.|data\.|track\.|mom|pup|pair|flight|day|date|time|tree|"
        r"dropOff|dropoff|independ|folder|subFolder|GPS|start|end|Index|"
        r"lat|lon|name|Bat|ID|unique\(|find\(|table\(|struct\()",
        re.I
    )
    for name in sorted(TARGETS):
        txt=z.read(name).decode("utf-8",errors="replace")
        lines=[]
        for no,line in enumerate(txt.splitlines(),1):
            clean=line.strip()
            if not clean or clean.startswith("%") and not structural.search(clean):
                continue
            if structural.search(clean):
                # do not emit long numeric vectors
                clean=re.sub(r"\[[\d\s,;\.\-]+\]", "[numeric-vector-omitted]", clean)
                lines.append({"line":no,"text":clean[:700]})
        out[name]=lines
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
