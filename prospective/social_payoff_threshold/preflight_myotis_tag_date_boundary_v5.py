#!/usr/bin/env python3
"""Categorical-only recheck: keep OSF source date warnings separate from RFID/TX equality.

No capture, signal, event-time, receiver, coordinate, or dyad values accessed.
Raw RFID and transmitter identifiers remain transient and NEVER printed.
"""
from __future__ import annotations
import argparse
import csv
from datetime import date,timedelta
import hashlib
import io
import json
import re
import urllib.request
from pathlib import Path
from preflight_myotis_two_day_csv_headers_v2 import metadata,opener,UA

ALLOWLIST=(
 ("0A62_20240515.csv","698dad850d35ac498ec72cd3","20240515",
  "f195f91f90dbf564dc96f0a8849078bca3ca4af3523aadedb5a35da67bf46e58"),
 ("0A62_20240516.csv","698dadb876b09fd62fe255fe","20240516",
  "7a9d2f6bfac6ed127d4ca4297026269101bca902af103850aebb41e7f550683b")
)
MAX_BYTES=900000
REQUIRED=("rfid","tx","date")
MISSING={"","NA","N/A","NULL","NONE"}


def normalized_date(raw):
    val=raw.strip()
    if re.fullmatch(r"\d{8}",val):
        val=f"{val[:4]}-{val[4:6]}-{val[6:8]}"
    elif re.fullmatch(r"\d{4}/\d{2}/\d{2}",val):
        val=val.replace("/","-")
    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}",val):
        return None
    try:return date.fromisoformat(val)
    except ValueError:return None


def counts_for_file(name,rid,filename_date,sha):
    report={"filename":name,"osf_resource_id":rid,"metadata_access":False,
            "status":"STOP_SOURCE_INACCESSIBLE"}
    m=metadata(name,rid)
    report["metadata_access"]=bool(m.get("ok"))
    if not m.get("ok"):
        report["source_metadata_http"]=m.get("http_status")
        return report,None,None
    req=urllib.request.Request(f"https://osf.io/download/{rid}/",
                               headers={"User-Agent":UA,"Accept":"text/csv,*/*"})
    try:
        with opener().open(req,timeout=25) as r:
            raw=r.read(MAX_BYTES+1)
            report["data_http_status"]=r.status
        if len(raw)>MAX_BYTES:raise ValueError("OVERSIZE")
        digest=hashlib.sha256(raw).hexdigest()
        report["source_sha256_verified"]=(digest==sha)
        if digest!=sha:
            report["status"]="STOP_SOURCE_HASH_DRIFT"
            return report,None,None
        reader=csv.reader(io.StringIO(raw.decode("utf-8-sig",errors="strict"),newline=""))
        header=[c.strip().lower() for c in next(reader)]
        if len(header)!=len(set(header)) or not all(c in header for c in REQUIRED):
            raise ValueError("COLUMN_SCHEMA_DRIFT")
        indices={k:header.index(k) for k in REQUIRED}
        rfids=set()
        transmitters=set()
        declared_days=set()
        nrows=missing_rfid=missing_tx=invalid_day=0
        for row in reader:
            if not row:continue
            if len(row)!=len(header):raise ValueError("COLUMN_COUNT_DRIFT")
            nrows+=1
            # Only three *categorical* original cells accessed.
            rfid=row[indices["rfid"]].strip()
            tx=row[indices["tx"]].strip()
            dt=row[indices["date"]].strip()
            if rfid.upper() in MISSING:missing_rfid+=1
            else:rfids.add(rfid)
            if tx.upper() in MISSING:missing_tx+=1
            else:transmitters.add(tx)
            converted=normalized_date(dt)
            if converted is None:invalid_day+=1
            else:declared_days.add(converted)
        folder_day=normalized_date(filename_date)
        allowed={folder_day-timedelta(days=1),folder_day,
                 folder_day+timedelta(days=1)}
        near=not invalid_day and declared_days.issubset(allowed)
        report.update({
          "status":"CATEGORICAL_ONLY_PARSED",
          "n_technical_rows":nrows,
          "n_unique_rfid":len(rfids),
          "n_unique_transmitters":len(transmitters),
          "n_missing_rfid":missing_rfid,
          "n_missing_tx":missing_tx,
          "n_invalid_date_labels":invalid_day,
          "n_distinct_declared_calendar_dates":len(declared_days),
          "source_folder_date_is_in_dates":folder_day in declared_days,
          "declared_dates_within_adjacent_calendar_days":bool(near),
          "calendar_label_span_needs_author_interpretation":len(declared_days)>1,
          "raw_identifiers_or_behavior_values_printed":False
        })
        return report,rfids,transmitters
    except Exception as e:
        report["status"]="STOP_SOURCE_OR_SCHEMA_ERROR"
        report["error_type"]=type(e).__name__
        return report,None,None


def decision(reports,rfid_sets,tx_sets):
    available=all(x is not None for x in rfid_sets+tx_sets)
    if not available:
        return "STOP_CATEGORICAL_SOURCE_INACCESSIBLE",False,False
    unique=all(r["n_unique_rfid"]==1 and r["n_unique_transmitters"]==1
               and r["n_missing_rfid"]==0 and r["n_missing_tx"]==0 and
               r["n_technical_rows"]>0 for r in reports)
    if not unique:
        return "STOP_INTRA_FILE_ID_HETEROGENEITY",False,False
    same_id=rfid_sets[0]==rfid_sets[1]
    same_tx=tx_sets[0]==tx_sets[1]
    if not (same_id and same_tx):
        return "STOP_CROSS_FILE_ID_MISMATCH",same_id,same_tx
    if not all(r["declared_dates_within_adjacent_calendar_days"] and
               r["source_folder_date_is_in_dates"] for r in reports):
        return "HOLD_SOURCE_DATE_CONSISTENCY",same_id,same_tx
    return "PASS_CATEGORICAL_CROSS_FILE_RFID_TX_STABILITY_ONLY",same_id,same_tx


def self_test():
    a=normalized_date("2024-05-15")
    assert a==normalized_date("20240515")==normalized_date("2024/05/15")
    assert normalized_date("2024-05-35") is None
    assert a+timedelta(days=1)==normalized_date("20240516")
    fake=[dict(n_unique_rfid=1,n_unique_transmitters=1,n_missing_rfid=0,
               n_missing_tx=0,n_technical_rows=4,
               declared_dates_within_adjacent_calendar_days=True,
               source_folder_date_is_in_dates=True)]*2
    state,x,y=decision(fake,[{"R1"},{"R1"}],[{"T1"},{"T1"}])
    assert state=="PASS_CATEGORICAL_CROSS_FILE_RFID_TX_STABILITY_ONLY" and x and y
    state,x,y=decision(fake,[{"R1"},{"R2"}],[{"T1"},{"T1"}])
    assert state=="STOP_CROSS_FILE_ID_MISMATCH" and not x and y
    return "PASS_GATED_ID_COMPARISON_AND_ADJACENT_DATE_PARSE"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_TWO_DAY_ID_DATE_AMENDMENT_V5.json")
    args=p.parse_args()
    check=self_test()
    if args.self_test:
        print(json.dumps({"synthetic_self_test":check,"animal_measurements_opened":False}))
        return
    reports=[]
    rfids=[]
    txs=[]
    for a,b,c,d in ALLOWLIST:
        summary,iset,tset=counts_for_file(a,b,c,d)
        reports.append(summary)
        rfids.append(iset)
        txs.append(tset)
    state,same_rfid,same_tx=decision(reports,rfids,txs)
    out={
        "contract":"MYOTIS_2026_TAG_DATE_BOUNDARY_AMENDMENT_V5.md",
        "source":"Official OSF sg6dz, two predetermined original CSV IDs",
        "status":state,
        "source_summaries":reports,
        "same_rfid_cross_file":same_rfid,
        "same_transmitter_cross_file":same_tx,
        "cross_midnight_or_dating_semantics_unresolved":any(
             r.get("calendar_label_span_needs_author_interpretation",False)
             for r in reports),
        "same_biological_bat_independently_verified":False,
        "independently_repeated_dyad_verified":False,
        "timestamp_or_location_or_rssi_or_dyad_values_accessed":False,
        "behavioral_outcomes_computed":0,
        "self_test":check,
    }
    Path(args.out).write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":state,"source_summaries":reports,
        "same_rfid_cross_file":same_rfid,"same_tx_cross_file":same_tx,
        "same_dyad_verified":False,"behavior_values_opened":False},sort_keys=True))


if __name__=="__main__":
    main()
