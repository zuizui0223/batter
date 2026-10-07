#!/usr/bin/env python3
from pathlib import Path
import json, urllib.parse, urllib.request

DATASET="h5ff9vv5pc"; VERSION=1; TARGET="PAF_AllBatsData.mat"
OUT=Path(__file__).resolve().parent/TARGET
URL="https://data.mendeley.com/api/datasets/"+DATASET+"/files?"+urllib.parse.urlencode({"version":VERSION,"$start":0,"$limit":1000})
HEAD={"User-Agent":"Mozilla/5.0 batter-paf-matlab-schema/1.0","Accept":"application/json,*/*"}

def get(url,accept="*/*"):
    req=urllib.request.Request(url,headers={**HEAD,"Accept":accept})
    with urllib.request.urlopen(req,timeout=240) as r:return r.read()

x=json.loads(get(URL,"application/json").decode())
rows=x if isinstance(x,list) else next((x[k] for k in ("items","files","results","data") if isinstance(x.get(k),list)),[])
for row in rows:
    if (row.get("filename") or row.get("name"))==TARGET:
        url=(row.get("content_details") or {}).get("download_url") or row.get("download_url")
        if not url: raise SystemExit("STOP_NO_DOWNLOAD_URL")
        OUT.write_bytes(get(url))
        print("downloaded "+TARGET+" bytes="+str(OUT.stat().st_size))
        break
else:
    raise SystemExit("STOP_TARGET_NOT_FOUND")
