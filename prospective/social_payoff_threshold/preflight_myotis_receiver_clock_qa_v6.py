#!/usr/bin/env python3
"""OSF 2026 Myotis SOURCE CLOCK/RECEIVER QA ONLY. Never computes bat co-use.

Read only original timestamp, date and rx columns from 16 preallowed originals.
No actual dates/times/IDs/locations, co-detection, acoustic or capture results
are printed. No behavioral p-values.
"""
from __future__ import annotations
import argparse
import csv
from datetime import date,datetime,timezone,timedelta
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path
from preflight_myotis_eight_tag_two_day_v5 import FILE_PAIRS
from preflight_myotis_two_day_csv_headers_v2 import metadata,opener,UA

MAX_BYTES=900000
REQ=("timestamp","date","rx")
YEARS=(2024,2025)
MISSING={"","NA","N/A","NULL","NONE"}


def parse_clock(s):
    s=s.strip()
    if re.fullmatch(r"[0-9]{10}(?:\.[0-9]{1,6})?",s):
        try:dt=datetime.fromtimestamp(float(s),timezone.utc)
        except (ValueError,OverflowError):return None,"invalid"
        return (dt if dt.year in YEARS else None),"epoch_seconds"
    if re.fullmatch(r"[0-9]{13}",s):
        try:dt=datetime.fromtimestamp(int(s)/1000,timezone.utc)
        except (ValueError,OverflowError):return None,"invalid"
        return (dt if dt.year in YEARS else None),"epoch_milliseconds"
    try:
        dt=datetime.fromisoformat(s.replace("Z","+00:00"))
        if dt.year not in YEARS:return None,"invalid"
        if dt.tzinfo is None:return dt,"iso_timezone_unknown"
        return dt.astimezone(timezone.utc),"iso_with_timezone"
    except ValueError:return None,"invalid"


def parse_day(s):
    s=s.strip()
    if re.fullmatch(r"\d{8}",s):s=s[:4]+"-"+s[4:6]+"-"+s[6:]
    elif re.fullmatch(r"\d{4}/\d{2}/\d{2}",s):s=s.replace("/","-")
    try:return date.fromisoformat(s)
    except ValueError:return None


def one_file(prefix,day,rid):
    name=f"{prefix}_{day}.csv"
    info={"series_label":prefix,"sampling_night":day,"original_name":name,
          "original_resource_identity_ok":False,
          "status":"STOP_ORIGINAL_SOURCE_ACCESS"}
    m=metadata(name,rid)
    if not m.get("ok"):
        info["source_metadata_http"]=m.get("http_status")
        return info
    info["original_resource_identity_ok"]=True
    req=urllib.request.Request(f"https://osf.io/download/{rid}/",
                headers={"User-Agent":UA,"Accept":"text/csv,*/*"})
    try:
        with opener().open(req,timeout=25) as r:raw=r.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:raise ValueError("SOURCE_OVERSIZE")
        info["source_sha256"]=hashlib.sha256(raw).hexdigest()
        reader=csv.reader(io.StringIO(raw.decode("utf-8-sig",errors="strict"),newline=""))
        head=[x.strip().lower() for x in next(reader)]
        if len(set(head))!=len(head) or not all(k in head for k in REQ):
            raise ValueError("MISSING_REQUIRED_FIELDS")
        idx={k:head.index(k) for k in REQ}
        n=0
        parsed=0
        nonmissing_rx=0
        clock_kinds={}
        receiver_ids=set()
        invalid_civil=0
        date_bad_source=0
        duplicates=0
        monotonic_pairs=0
        comparable_pairs=0
        seen_clocks=set()
        last_clock=None
        base=parse_day(day)
        allowed={base,base+timedelta(days=1)}
        for row in reader:
            if not row:continue
            if len(row)!=len(head):raise ValueError("ROW_WIDTH_DRIFT")
            n+=1
            # The ONLY original values touched are these 3, as frozen.
            raw_time=row[idx["timestamp"]]
            raw_rx=row[idx["rx"]].strip()
            raw_date=row[idx["date"]]
            dt,kind=parse_clock(raw_time)
            clock_kinds[kind]=clock_kinds.get(kind,0)+1
            if dt is not None:
                parsed+=1
                # Retain timestamp in-process ONLY; never write it.
                key=dt.isoformat()
                if key in seen_clocks:duplicates+=1
                else:seen_clocks.add(key)
                if last_clock is not None and (
                   (last_clock.tzinfo is None)==(dt.tzinfo is None)
                ):
                    comparable_pairs+=1
                    monotonic_pairs+=int(dt>=last_clock)
                last_clock=dt
            if raw_rx.upper() not in MISSING:
                nonmissing_rx+=1
                receiver_ids.add(raw_rx)  # transient; never output values
            checkday=parse_day(raw_date)
            if checkday is None:invalid_civil+=1
            elif checkday not in allowed:date_bad_source+=1
        info.update({"status":"STRUCTURAL_QA_ONLY",
           "technical_rows":n,
           "parsed_clock_fraction":parsed/n if n else 0,
           "receiver_present_fraction":nonmissing_rx/n if n else 0,
           "distinct_receiver_count":len(receiver_ids),
           "timestamp_format_counts":clock_kinds,
           "date_invalid_count":invalid_civil,
           "date_outside_sampling_night_count":date_bad_source,
           "duplicate_parsed_timestamp_rows":duplicates,
           "nondecreasing_clock_adjacent_fraction":monotonic_pairs/comparable_pairs
                  if comparable_pairs else None,
           "no_receiver_id_or_clock_value_reported":True})
        return info
    except Exception as e:
        info["status"]="STOP_ORIGINAL_SOURCE_ACCESS_OR_CSV_SCHEMA"
        info["safe_error_kind"]=type(e).__name__
        return info


def self_test():
    a,k=parse_clock("2024-05-15T21:22:12+02:00")
    assert k=="iso_with_timezone" and a.tzinfo==timezone.utc
    assert parse_clock("2024-05-15 21:22:12")[1]=="iso_timezone_unknown"
    assert parse_clock("bad")[0] is None
    assert parse_day("20240515")==date(2024,5,15)
    assert parse_day("2024/05/15")==date(2024,5,15)
    assert len(FILE_PAIRS)==8
    return "PASS_FIXED_TIMESTAMP_PARSER_AND_16_SOURCE_ALLOWLIST"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_EVENT_TIME_RECEIVER_QA_V6.json")
    args=p.parse_args()
    check=self_test()
    if args.self_test:
        print(json.dumps({"test":check,"animal_events_opened":False}))
        return
    detail=[]
    for prefix,rid1,rid2 in FILE_PAIRS:
        for day,rid in (("20240515",rid1),("20240516",rid2)):
            detail.append(one_file(prefix,day,rid))
    can=all(x.get("status")=="STRUCTURAL_QA_ONLY" and
          x.get("parsed_clock_fraction",0)>=.95 and
          x.get("receiver_present_fraction",0)>=.95 and
          x.get("technical_rows",0)>0 and
          not x.get("date_invalid_count") and
          not x.get("date_outside_sampling_night_count")
          for x in detail)
    has_naive=any(x.get("timestamp_format_counts",{}).get("iso_timezone_unknown",0)>0
            for x in detail)
    if any(x.get("status")!="STRUCTURAL_QA_ONLY" for x in detail):
        status="STOP_ORIGINAL_SOURCE_ACCESS"
    elif not can:status="STOP_UNUSABLE_TIMESTAMP_OR_RECEIVER_SCHEMA"
    elif has_naive:status="HOLD_TIMEZONE_AMBIGUITY"
    else:status="PASS_EVENT_TIME_RECEIVER_SCHEMA_ONLY"
    res={"source":"OSF sg6dz; frozen 16 source files",
         "contract":"MYOTIS_2026_EVENT_CLOCK_RECEIVER_SOURCE_QA_CONTRACT_V6.md",
         "status":status,
         "source_files_inspected":len(detail),
         "file_quality":detail,
         "event_clock_or_receiver_raw_values_disclosed":False,
         "co_detection_or_station_sharing_calculated":False,
         "rssi_or_coordinates_or_dyad_column_accessed":False,
         "bat_behavioral_p_values_computed":0,
         "biological_dyad_repeatability_not_verified":True,
         "self_test":check}
    Path(args.out).write_text(json.dumps(res,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"files":len(detail),
        "files_with_parseability_95pct":sum(x.get("parsed_clock_fraction",0)>=.95 for x in detail),
        "files_with_receiver_key_95pct":sum(x.get("receiver_present_fraction",0)>=.95 for x in detail),
        "timestamp_formats_observed":sorted(set(k for x in detail
                                  for k in x.get("timestamp_format_counts",{}))),
        "no_co_detection_computed":True},sort_keys=True))


if __name__=="__main__":main()
