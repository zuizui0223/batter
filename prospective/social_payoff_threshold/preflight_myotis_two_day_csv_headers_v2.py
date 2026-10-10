#!/usr/bin/env python3
"""Read at most the first header LINE of two explicitly allowed OSF CSV files.

This code DOES NOT inspect rows 2+, bat tag values, detections or geography.
All resource IDs and header-only rules were frozen in a prior contract.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

FILES=(
 ("0A62_20240515.csv","698dad850d35ac498ec72cd3"),
 ("0A62_20240516.csv","698dadb876b09fd62fe255fe"),
)
ALLOWED_HOSTS=("api.osf.io","osf.io","files.osf.io")
UA="batter-myotis-2026-two-day-CSV-header-v2/1.0"


class RestrictedRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,request,fp,code,msg,headers,newurl):
        p=urllib.parse.urlsplit(newurl)
        if p.scheme!="https" or p.hostname not in ALLOWED_HOSTS:
            raise ValueError("DISALLOWED_REDIRECT_HOST")
        return super().redirect_request(request,fp,code,msg,headers,newurl)


def opener():
    return urllib.request.build_opener(RestrictedRedirect())


def metadata(name,rid):
    url=f"https://api.osf.io/v2/files/{rid}/"
    req=urllib.request.Request(url,headers={"Accept":"application/vnd.api+json","User-Agent":UA})
    try:
        with opener().open(req,timeout=18) as response:
            text=response.read(200001)
            status=response.status
    except urllib.error.HTTPError as e:
        return {"ok":False,"http_status":e.code,"error":"HTTP_ERROR"}
    except Exception as e:
        return {"ok":False,"http_status":None,"error":type(e).__name__}
    try:
        obj=json.loads(text)
        d=obj.get("data") or {}
        a=d.get("attributes") or {}
        reported=str(a.get("name") or "")
        confirmed=d.get("id")==rid and reported==name
        return {"ok":confirmed,"http_status":status,
                "source_name_confirmed":reported if confirmed else None,
                "error":None if confirmed else "IDENTITY_MISMATCH"}
    except Exception:
        return {"ok":False,"http_status":status,"error":"BAD_METADATA_JSON"}


def source_urls(rid):
    return (
       f"https://osf.io/download/{rid}/",
       f"https://files.osf.io/v1/resources/sg6dz/providers/osfstorage/{rid}?action=download",
    )


def parse_first_header_line(line):
    if len(line)>2048 or not line.endswith((b"\n",b"\r")):
        raise ValueError("NO_COMPLETE_HEADER_LINE")
    t=line.decode("utf-8-sig",errors="strict").strip()
    if not t or "\x00" in t:
        raise ValueError("INVALID_HEADER")
    fields=[x.strip() for x in next(csv.reader([t]))]
    if not 2<=len(fields)<=100 or not all(fields):
        raise ValueError("INVALID_FIELD_COUNT")
    if any(len(x)>110 for x in fields):
        raise ValueError("UNEXPECTED_FIELD_LENGTH")
    if all(re.fullmatch(r"[+-]?[0-9.]+",v) for v in fields):
        raise ValueError("NUMERIC_ROW_AS_HEADER")
    return fields


def read_one_header(url):
    req=urllib.request.Request(url,headers={"User-Agent":UA,"Range":"bytes=0-2047",
                              "Accept":"text/csv,text/plain,application/octet-stream"})
    try:
        with opener().open(req,timeout=18) as response:
            status=response.status
            first=response.readline(2049)
            final=urllib.parse.urlsplit(response.geturl())
        if final.hostname not in ALLOWED_HOSTS:
            return {"ok":False,"http_status":status,"error":"NON_OSF_HOST"}
        return {"ok":True,"http_status":status,"fields":parse_first_header_line(first)}
    except urllib.error.HTTPError as e:
        return {"ok":False,"http_status":e.code,"error":"HTTP_ERROR"}
    except Exception as e:
        return {"ok":False,"http_status":None,"error":type(e).__name__}


def flags(fields):
    text=" | ".join(s.lower() for s in fields)
    return {
     "receiver_key_header_possible":bool(re.search(r"receiver|station|sn.?id|stationary",text)),
     "mobile_sender_key_header_possible":bool(re.search(r"sender|mobile|tag|ml.?id",text)),
     "timestamp_header_possible":bool(re.search(r"time|date|timestamp|utc|posix",text)),
     "signal_strength_header_possible":bool(re.search(r"rssi|strength|signal",text)),
     "distinct_biological_bat_id_header_possible":bool(re.search(r"animal.?id|bat.?id|individual.?id",text)),
    }


def self_test():
    h=parse_first_header_line(b"receiver_id,sender_id,timestamp,rssi\n")
    assert h==["receiver_id","sender_id","timestamp","rssi"]
    assert flags(h)["mobile_sender_key_header_possible"]
    assert flags(h)["timestamp_header_possible"]
    try:
        parse_first_header_line(b"2,123,4,555\n")
        raise AssertionError("Numeric value line was not rejected")
    except ValueError:
        pass
    return "PASS_HEADER_ONLY_NO_VALUES"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_TWO_DAY_CSV_HEADERS_V2.json")
    opt=p.parse_args()
    check=self_test()
    if opt.self_test:
        print(json.dumps({"synthetic_check":check,"bat_events_opened":False}))
        return
    sources=[]
    for name,rid in FILES:
        m=metadata(name,rid)
        row={"source_name":name,"osf_id":rid,"metadata":m,
             "header_opened":False,"column_names":[],"header_flags":{}}
        if m["ok"]:
            row["paths_attempted"]=[]
            for url in source_urls(rid):
                attempt=read_one_header(url)
                row["paths_attempted"].append({
                   "path_type":"osf_download" if "osf.io/download" in url else "osf_resource",
                   "http_status":attempt["http_status"],
                   "header_ok":attempt["ok"],
                   "error":attempt.get("error")})
                if attempt["ok"]:
                    row["header_opened"]=True
                    row["column_names"]=attempt["fields"][:35]
                    row["header_flags"]=flags(attempt["fields"])
                    break
        sources.append(row)
    both=all(x["header_opened"] for x in sources)
    same=both and sources[0]["column_names"]==sources[1]["column_names"]
    support=same and all(x["header_flags"]["mobile_sender_key_header_possible"]
               and x["header_flags"]["timestamp_header_possible"] for x in sources)
    status=("HOLD_EVENT_SCHEMA_ONLY_REQUIRES_BAT_ID_CROSSWALK" if support
            else ("STOP_UNEXPECTED_CSV_HEADER_SCHEMA" if both
                  else "STOP_CSV_HEADER_ACCESS"))
    receipt={
      "source_id":"sg6dz",
      "contract":"MYOTIS_2026_TWO_DAY_CSV_HEADER_ONLY_CONTRACT_V2.md",
      "status":status,
      "source_files":sources,
      "header_compatibility_verified":same,
      "same_biological_bat_across_nights_verified":False,
      "joint_dyad_night_support_verified":False,
      "receiver_positions_or_bat_coordinates_opened":False,
      "data_cells_below_header_parsed":False,
      "biological_effects_computed":0,
      "self_test":check
    }
    Path(opt.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
       "status":status,
       "sources":[{"file":x["source_name"],
           "header_opened":x["header_opened"],
           "column_names":x["column_names"],
           "header_flags":x["header_flags"],
           "metadata_http":x["metadata"]["http_status"]}
           for x in sources],
       "read_bat_values":False
    },sort_keys=True))


if __name__=="__main__": main()
