#!/usr/bin/env python3
"""Descriptive ONLY: shared receiving station within the same 60s clock bin.

No dyad IDs, receiving-station IDs, actual timestamps, RSSI values or positions
are printed. No randomization/permutation p-values or causal inference.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime,date,timedelta
import io
import json
import math
import urllib.request
from itertools import combinations
from pathlib import Path

from preflight_myotis_eight_tag_two_day_v5 import FILE_PAIRS
from preflight_myotis_two_day_csv_headers_v2 import metadata,opener,UA

DAYS=("20240515","20240516")
MAX_BYTES=900000
HEADER=("timestamp","rx","rssi")
MIN_RSSI=-90.0
MIN_VALID=.95

def parse_clock(raw):
    try:
        # Original author uses lubridate::ymd_hms() on naive source strings.
        # We compare only *relative wall-clock bins within the same night*.
        val=datetime.fromisoformat(raw.strip().replace("Z","+00:00"))
        if val.tzinfo is not None:
            raise ValueError("UNEXPECTED_TIMEZONE_MIX")
        if val.year!=2024:return None
        return val
    except ValueError:
        return None

def parse_events(name,rid,source_day):
    result={"source_label":name,"status":"STOP_SOURCE_OR_SCHEMA",
            "original_id_verified":False}
    m=metadata(name,rid)
    if not m.get("ok"):
        result["metadata_http"]=m.get("http_status")
        return result,None
    result["original_id_verified"]=True
    try:
        req=urllib.request.Request(f"https://osf.io/download/{rid}/",
             headers={"User-Agent":UA,"Accept":"text/csv,*/*"})
        with opener().open(req,timeout=25) as resp:payload=resp.read(MAX_BYTES+1)
        if len(payload)>MAX_BYTES:raise ValueError("OVERSIZE")
        reader=csv.reader(io.StringIO(payload.decode("utf-8-sig",errors="strict"),newline=""))
        h=[x.strip().lower() for x in next(reader)]
        if len(h)!=len(set(h)) or not all(k in h for k in HEADER):
            raise ValueError("HEADER_DRIFT")
        j={k:h.index(k) for k in HEADER}
        base=date.fromisoformat(source_day[:4]+"-"+source_day[4:6]+"-"+source_day[6:])
        allowed={base,base+timedelta(days=1)}
        rows=clockvalid=rxvalid=rssivalid=eligible=0
        minute_receiver={}
        for fields in reader:
            if not fields:continue
            if len(fields)!=len(h):raise ValueError("ROW_WIDTH_DRIFT")
            rows+=1
            rawtime=fields[j["timestamp"]]
            rawrx=fields[j["rx"]].strip()
            rawrssi=fields[j["rssi"]].strip()
            parsed=parse_clock(rawtime)
            if parsed is not None and parsed.date() in allowed:clockvalid+=1
            else:parsed=None
            if rawrx and rawrx.upper() not in ("NA","N/A","NULL"):rxvalid+=1
            else:rawrx=""
            try:
                level=float(rawrssi)
                if not math.isfinite(level):raise ValueError("NONFINITE_RSSI")
                rssivalid+=1
            except (ValueError,OverflowError):
                level=None
            if parsed is None or not rawrx or level is None or level <= MIN_RSSI:
                continue
            eligible+=1
            mk=(parsed.year,parsed.month,parsed.day,parsed.hour,parsed.minute)
            # Exact station receiver string transient only; NEVER serialize.
            minute_receiver.setdefault(mk,set()).add(rawrx)
        result.update({"status":"SOURCE_STRUCTURAL_QA_ONLY",
          "technical_rows":rows,
          "time_parse_rate":clockvalid/rows if rows else 0,
          "receiver_key_rate":rxvalid/rows if rows else 0,
          "rssi_numeric_rate":rssivalid/rows if rows else 0,
          "source_technical_rows_after_published_RSSI_filter":eligible,
          "distinct_recorded_minute_bins":len(minute_receiver),
          "no_original_identifiers_or_raw_times_printed":True})
        if rows==0 or min(result["time_parse_rate"],result["receiver_key_rate"],
                        result["rssi_numeric_rate"])<MIN_VALID or eligible==0:
            result["status"]="STOP_INADEQUATE_SOURCE_QA"
            return result,None
        return result,minute_receiver
    except Exception as e:
        result["error_kind"]=type(e).__name__
        return result,None

def joint_minutes(a,b):
    if not a or not b:return 0
    return sum(bool(a[tm].intersection(b[tm])) for tm in a.keys() & b.keys())

def q(vals,p):
    ordered=sorted(vals)
    if not ordered:return None
    idx=(len(ordered)-1)*p
    a=math.floor(idx);b=math.ceil(idx)
    return ordered[a]+(ordered[b]-ordered[a])*(idx-a)

def check_synthetic():
    a={(2024,5,15,23,11):{"RX1","RX2"},(2024,5,15,23,12):{"RX2"}}
    b={(2024,5,15,23,11):{"RX2"},(2024,5,15,23,13):{"RX2"}}
    assert joint_minutes(a,b)==1
    assert joint_minutes(a,{(2024,5,15,23,11):{"RX3"}})==0
    assert parse_clock("2024-05-15 23:10:01") is not None
    assert parse_clock("2024-05-15T23:10:01+02:00") is None
    assert len(FILE_PAIRS)==8
    return "PASS_ONE_MINUTE_SAME_RECEIVER_AND_ZERO_DEDUPLICATION"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_RECEIVER_MINUTE_COUSE_DESCRIPTIVE_V1A.json")
    args=p.parse_args()
    test=check_synthetic()
    if args.self_test:
        print(json.dumps({"synthetic_test":test,"original_event_values_opened":False}));return
    data={day:{} for day in DAYS}
    files=[]
    for prefix,rid15,rid16 in FILE_PAIRS:
        for day,rid in zip(DAYS,(rid15,rid16)):
            report,mapping=parse_events(prefix+"_"+day+".csv",rid,day)
            files.append(report)
            data[day][prefix]=mapping
    if any(x.get("status")!="SOURCE_STRUCTURAL_QA_ONLY" for x in files):
        status="STOP_SOURCE_CLOCK_OR_SIGNAL_QA"
        nights=[]
    else:
        status="DESCRIPTIVE_RECEIVER_MINUTE_COUSE_ONLY_NO_INFERENCE"
        nights=[]
        for day in DAYS:
            js=[]
            for a,b in combinations((x[0] for x in FILE_PAIRS),2):
                js.append(joint_minutes(data[day][a],data[day][b]))
            nights.append({"sampling_night_label":day,
               "n_tagged_bats":8,"possible_dyads":len(js),
               "dyads_with_at_least_one_joint_receiver_minute":sum(v>0 for v in js),
               "total_joint_receiver_minutes_over_dyads":sum(js),
               "co_receiver_minutes_per_dyad_median":q(js,.5),
               "co_receiver_minutes_per_dyad_p05":q(js,.05),
               "co_receiver_minutes_per_dyad_p95":q(js,.95)})
    result={
      "status":status,
      "contract":"MYOTIS_2026_DESCRIPTIVE_RECEIVER_MINUTE_AMENDMENT_V1A.md",
      "source":"Original OSF sg6dz, 8 tagged bats × 2 dated files",
      "file_QA":files,
      "nights":nights,
      "original_bat_ID_or_receiver_ID_or_clock_values_emitted":False,
      "lat_lon_or_dyad_column_inspected":False,
      "RSSI_used_only_for_predeclared_original_published_quality_filter":True,
      "no_p_values_or_causal_effects_calculated":True,
      "not_3D_not_contact_not_prey_captures":True,
      "self_test":test}
    Path(args.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"nights":nights,
          "bat_ID_or_receiver_identifiers_disclosed":False,
          "statistical_hypothesis_test_executed":False},sort_keys=True))
if __name__=="__main__":main()
