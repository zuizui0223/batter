#!/usr/bin/env python3
"""Categorical-only, two source-frozen dated files: bat RFID/tag consistency.

No acoustic values, event times or GPS coordinates are inspected or emitted.
Read only columns RFID, TX and DATE and count technical rows.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

from preflight_myotis_two_day_csv_headers_v2 import metadata, opener, UA

FILES=(
 ("0A62_20240515.csv","698dad850d35ac498ec72cd3","20240515"),
 ("0A62_20240516.csv","698dadb876b09fd62fe255fe","20240516"),
)
MAX_BYTES=900000
REQUIRED=("rfid","tx","date")


def categorical_file(name,rid,expected_date):
    met=metadata(name,rid)
    row={"filename":name,"source_metadata_ok":met["ok"],"http_meta":met["http_status"]}
    if not met["ok"]:
        row["status"]="STOP_FILE_METADATA_IDENTITY"
        return row,None,None
    try:
        req=urllib.request.Request(f"https://osf.io/download/{rid}/",
                                   headers={"User-Agent":UA,"Accept":"text/csv,*/*"})
        with opener().open(req,timeout=22) as response:
            raw=response.read(MAX_BYTES+1)
            code=response.status
        if len(raw)>MAX_BYTES:raise ValueError("OVERSIZE")
        text=raw.decode("utf-8-sig",errors="strict")
        reader=csv.reader(io.StringIO(text,newline=""))
        header=[x.strip().lower() for x in next(reader)]
        if len(set(header))!=len(header) or not set(REQUIRED).issubset(header):
            raise ValueError("MISSING_REQUIRED_COLUMNS")
        indices={key:header.index(key) for key in REQUIRED}
        rfids=set()
        senders=set()
        valid_dates=set()
        missing_rfid=missing_sender=bad_date=technical_events=0
        for fields in reader:
            if not fields:continue
            technical_events+=1
            if len(fields)!=len(header):
                raise ValueError("CSV_FIELD_COUNT_DRIFT")
            # These are the ONLY accessed original cell values. We never touch
            # timestamp, RX, RSSI, lon/lat or dyad records.
            rfid=fields[indices["rfid"]].strip()
            tx=fields[indices["tx"]].strip()
            dt=fields[indices["date"]].strip()
            if not rfid:missing_rfid+=1
            else:rfids.add(rfid)
            if not tx:missing_sender+=1
            else:senders.add(tx)
            dt_digits=re.sub(r"[-/]","",dt)
            if len(dt_digits)==8 and dt_digits.isdecimal():
                valid_dates.add(dt_digits)
            else:bad_date+=1
        start=datetime.strptime(expected_date,"%Y%m%d").date()
        after=(start+timedelta(days=1)).strftime("%Y%m%d")
        allowed_dates={expected_date,after}
        row.update({"status":"CATEGORICAL_PARSED_ONLY",
            "http_data":code,
            "n_technical_rows":technical_events,
            "sha256_raw_source":hashlib.sha256(raw).hexdigest(),
            "n_distinct_rfid_values":len(rfids),
            "n_distinct_tx_values":len(senders),
            "n_missing_rfid":missing_rfid,
            "n_missing_tx":missing_sender,
            "all_civil_dates_within_sampling_night":bad_date==0 and
                  bool(valid_dates) and valid_dates.issubset(allowed_dates),
            "n_distinct_declared_date_values":len(valid_dates),
            "observations_or_geography_analyzed":False})
        # NOTE: actual identifying strings are returned ONLY into transient
        # function memory; they are never printed or written to JSON.
        return row,rfids,senders
    except Exception as e:
        row["status"]="STOP_CATEGORICAL_SOURCE_INACCESSIBLE"
        row["safe_error_type"]=type(e).__name__
        return row,None,None


def self_test():
    sample="timestamp,date,rx,tx,rfid,rssi\n2024-05-15,2024-05-15,A,CAT123,RFID7,-87\n"
    r=csv.reader(io.StringIO(sample))
    h=[v.lower() for v in next(r)]
    assert all(x in h for x in REQUIRED)
    assert re.sub(r"[-/]","","2024-05-15")=="20240515"
    start=datetime.strptime("20240515","%Y%m%d").date()
    assert (start+timedelta(days=1)).strftime("%Y%m%d")=="20240516"
    return "PASS_SELECT_ONLY_CATEGORICAL_COLUMNS"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_TWO_DAY_CATEGORICAL_GATE_V4.json")
    a=p.parse_args()
    check=self_test()
    if a.self_test:
        print(json.dumps({"test":check,"numeric_bat_outcomes_opened":False}))
        return
    detail=[]
    id_sets=[]
    tx_sets=[]
    for name,rid,date in FILES:
        x,r,t=categorical_file(name,rid,date)
        detail.append(x);id_sets.append(r);tx_sets.append(t)
    usable=all(r is not None for r in id_sets+tx_sets)
    source_consistent=(usable and all(d.get("n_distinct_rfid_values")==1
                      and d.get("n_distinct_tx_values")==1
                      and d.get("n_missing_rfid")==0
                      and d.get("n_missing_tx")==0
                      and d.get("all_civil_dates_within_sampling_night")
                      and d.get("n_technical_rows",0)>0 for d in detail))
    same_id=bool(source_consistent and id_sets[0]==id_sets[1])
    same_tx=bool(source_consistent and tx_sets[0]==tx_sets[1])
    status=("PASS_CATEGORICAL_SAME_TAG_TWO_DAYS_ONLY"
            if same_id and same_tx else
            ("STOP_NOT_STABLE_BIOLOGICAL_TAG" if usable
             else "STOP_CATEGORICAL_SOURCE_INACCESSIBLE"))
    receipt={
       "contract":"MYOTIS_2026_TWO_DAY_CATEGORICAL_TAG_GATE_V4.md",
       "source_project":"sg6dz",
       "status":status,
       "two_original_source_files":detail,
       "same_rfid_across_dated_files":same_id,
       "same_tx_across_dated_files":same_tx,
       "distinct_bat_rfid_values_printed":False,
       "same_dyad_across_nights_verified":False,
       "temporal_co_detection_estimated":False,
       "rssi_or_location_or_event_time_values_inspected":False,
       "biological_outcome_pvalues":0,
       "self_test":check
    }
    Path(a.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":status,
         "same_rfid_across_dated_files":same_id,
         "same_tx_across_dated_files":same_tx,
         "source_summaries":detail,
         "no_bat_behavior_values_inspected":True},sort_keys=True))


if __name__=="__main__":main()
