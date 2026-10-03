#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,io,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
PANELS={
"hypsignathus":"contract/hypsignathus_replication_v1.json",
"phyllostomus_2022":"contract/phyllostomus_replication_v1.json",
"phyllostomus_2023":"contract/phyllostomus_2023_replication_v1.json",
"phyllostomus_2016":"contract/phyllostomus_2016_dry_architecture_v1.json"}
TOKENS=("wind","weather","temperature","temp","precip","rain","radiation","cloud","pressure","humidity","vertical","uplift","thermal")
def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"batter-strategy-maintenance-preflight/1.0"})
    with urllib.request.urlopen(req,timeout=300) as r:return r.read()
def main():
    out={"schema_version":1,"classification":"source-schema-only; no vertical numeric outcome opened","panels":{}}
    for panel,path in PANELS.items():
        c=json.loads((ROOT/path).read_text()); src=c["source"]["gps"]; blob=get(src["url"])
        if hashlib.md5(blob).hexdigest()!=src["md5"]:raise RuntimeError(panel+" md5 mismatch")
        txt=io.TextIOWrapper(io.BytesIO(blob),encoding="utf-8-sig",newline="")
        rd=csv.reader(txt); header=next(rd)
        low=[h.lower() for h in header]
        env=[h for h,l in zip(header,low) if any(t in l for t in TOKENS)]
        out["panels"][panel]={"columns":len(header),"environment_like_columns":env,
          "has_timestamp":any("timestamp" in l or l=="time" for l in low),
          "coordinate_columns":[h for h,l in zip(header,low) if ("lat" in l or "lon" in l or "long" in l)],
          "has_latitude":any(("lat" in l) for l in low),
          "has_longitude":any(("lon" in l or "long" in l) for l in low)}
    od=ROOT/"post_freeze_extensions/strategy_maintenance"; (od/"source_schema_preflight_v1.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps(out,sort_keys=True))
if __name__=="__main__":main()
