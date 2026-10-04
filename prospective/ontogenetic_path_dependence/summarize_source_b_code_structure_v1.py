#!/usr/bin/env python3
"""Read only Source B source files frozen in SOURCE_B_CODE_OPENING_AMENDMENT_V1.md.

No movement arrays or result MAT files are opened.
"""
from __future__ import annotations
import hashlib, json, re, urllib.request

BASE="https://data.mendeley.com/public-api"
DS="n9d8gbz3xr"
UA="batter-source-b-structural-code/1.0"

FILES={
"loadData.m":("8fcdb7d8-f802-4942-9b2d-1d304d4e0593",297,"744ff2b5690e6bf888c887811b138a20626a8754288c53d2e679229eeb53c87c"),
"createRealDays.m":("ef369033-3219-4d7f-bca7-be8792035954",480,"a4d086fa97b2b03424e50bd548f62a3583013416b83c4cb93613bf79da7b6dfd"),
"createDaysToProccess.m":("907386a2-6583-4bf5-97e5-2a538e708395",314,"cab76f4d95c5450bd1e1c5cb4d4401bdee115ee525919baaa2cf659fd81128fd"),
"postProccess.m":("4de4c495-e0f7-496d-9a6d-3a7fc74fc0f9",12830,"994c2c001c47077ce99eb3c812e9edb4ee37c9ad62e5bdb46a6cdfb9a3296f1d"),
"proccessTable.m":("84d6eecf-2d6e-488e-86e8-4c3ae8fd2a2f",16020,"d39e0a344a9dfb2b00974ccbc59d7000e6a6507adb5403b0789c979f7a9cc57e"),
"setZonesWithDay.m":("7299ad40-f175-4c52-9d75-cc4d9a40f39e",1100,"cc26e7f260860ea9ca22e70d5a74e3c4f0903ff3d8d9ead929b6452e381d32db"),
"batTrees2016.m":("1eaaeead-b86e-4a7e-b9bd-874adea3b76e",1766,"d93859174c5b51bff76360895619bd80cf067bdd277d1bf137507001ee20c6cb"),
"batTrees2017.m":("b3901e8b-ee36-49d0-8e82-6308625c98ed",2016,"25aa20cbfe281540f62f3cfb5381ab63ade6cd6fef79ea760d797c78e3d7f0d3"),
"checkData.m":("72080888-91e6-43d7-8af1-fa7120dcebf2",4676,"386c98629426922c36af653b2bba05f3e336457d6757da22d7c7d86149a8d08c"),
"main.m":("a024f599-d57f-4945-9374-eb4c2f3b52f1",8217,"ea064b6111d579c61cbdf39cbae52d090027b93a95862e5524a02cdc3175f184"),
}
PAT=re.compile(
 r"(load\(|save\(|fullfile|dir\(|field|date|day|night|time|flight|tree|forag|commut|"
 r"track|data\.|zone|bat|name|start|end|first|last|gps|lat|lon|utm|coordinate|"
 r"table|struct|folder|year|realDays|daysTo|transloc)", re.I)

def meta(fid):
    req=urllib.request.Request(f"{BASE}/datasets/{DS}/files/{fid}",headers={"User-Agent":UA,"Accept":"application/vnd.mendeley-public-dataset.1+json"})
    with urllib.request.urlopen(req,timeout=30) as r:return json.load(r)

def fetch(url,n):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Accept":"*/*"})
    with urllib.request.urlopen(req,timeout=30) as r:return r.read(n+1)

def main():
    out={}
    for name,(fid,size,sha) in FILES.items():
        m=meta(fid); cd=m.get("content_details") or {}
        if m.get("filename")!=name: raise RuntimeError(f"name mismatch {name}")
        b=fetch(cd["download_url"],size)
        if len(b)!=size: raise RuntimeError(f"size mismatch {name}: {len(b)} != {size}")
        if hashlib.sha256(b).hexdigest()!=sha: raise RuntimeError(f"sha mismatch {name}")
        txt=b.decode("utf-8",errors="replace")
        rows=[]
        for no,line in enumerate(txt.splitlines(),1):
            clean=line.strip()
            if not clean: continue
            if PAT.search(clean):
                # Strip only huge literal numeric arrays, retain structural constants.
                clean=re.sub(r"\[(?:[\d\s,;\.\-]+){40,}\]","[long-numeric-vector-omitted]",clean)
                rows.append({"line":no,"text":clean[:800]})
        out[name]=rows
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
