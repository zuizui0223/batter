#!/usr/bin/env python3
"""Read source-method HH:MM constants only from one exact original author Quarto.

No raw animal CSV, receiver, GPS, bat IDs, dates or outcomes are opened.
Do not execute Quarto/R code.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from preflight_myotis_two_day_csv_headers_v2 import metadata,opener,UA

RESOURCE_ID="698dea461a7b213810c7311d"
FILENAME="Appendix1_anonym.qmd"
SIZE=68621
LIMIT=100000

ASSIGNMENT=re.compile(
    r"""^\s*(thresh_time_(?:start|end))\s*(?:<-|=)\s*
        ["']((?:[01]\d|2[0-3]):[0-5]\d)["']""",
    re.X
)
NAMED_REF=re.compile(r"\bthresh_time_(?:start|end)\b")
TIMEZONE=re.compile(r"(?i)\b(?:force_tz|with_tz|as\.POSIXct)\s*\(|\btz\s*=")
NO_MISSING=("start","end")

def source():
    out={"metadata_name_verified":False,
         "status":"STOP_ORIGINAL_CODE_INACCESSIBLE"}
    m=metadata(FILENAME,RESOURCE_ID)
    out["metadata_http"]=m.get("http_status")
    if not m.get("ok"):return out
    out["metadata_name_verified"]=True
    try:
        request=urllib.request.Request(
            "https://osf.io/download/"+RESOURCE_ID+"/",
            headers={"User-Agent":UA,"Accept":"text/plain,*/*"})
        with opener().open(request,timeout=23) as response:
            raw=response.read(LIMIT+1)
        if len(raw)!=SIZE:
            raise ValueError("SOURCE_SIZE_DRIFT")
        txt=raw.decode("utf-8-sig",errors="strict")
        if "\x00" in txt:raise ValueError("BINARY_SOURCE")
        found=[]
        for line in txt.splitlines():
            m=ASSIGNMENT.search(line)
            if m:
                after=line[m.end():]
                hint=("two hours after sunset" if
                      re.search(r"(?i)two\s+hours?\s+af(?:t|e)er?\s+sunset",after)
                      else "three hours before sunrise" if
                      re.search(r"(?i)three\s+hours?\s+before\s+sunrise",after)
                      else "not_explicit")
                found.append({"source_var":m.group(1),
                              "method_clock_time":m.group(2),
                              "comment_semantics":hint})
        unique={
            k:sorted({x["method_clock_time"] for x in found
                      if x["source_var"]=="thresh_time_"+k})
            for k in NO_MISSING
        }
        ambiguous=any(len(x)!=1 for x in unique.values())
        out.update({
            "status":"HOLD_AUTHOR_TIME_BOUNDARIES_AMBIGUOUS"
                     if ambiguous else "AUTHOR_CLOCK_CONSTANTS_FOUND_METHOD_ONLY",
            "method_clock_assignments":found,
            "distinct_literal_clocks_per_variable":unique,
            "both_variables_referenced":all(
                len(re.findall(r"\bthresh_time_"+key+r"\b",txt))>=2
                for key in NO_MISSING),
            "any_explicit_timezone_assignment_in_original_source":bool(
                TIMEZONE.search(txt)),
            "sha256_of_original_author_code":hashlib.sha256(raw).hexdigest(),
            "source_size_bytes":len(raw),
            "source_file_id":RESOURCE_ID,
            "original_bat_event_values_opened":False,
            "other_source_contents_opened":False})
        return out
    except Exception as e:
        out["safe_error_type"]=type(e).__name__
        return out

def test():
    assert ASSIGNMENT.search('thresh_time_start = "23:10" # two hours after sunset')
    assert ASSIGNMENT.search('  thresh_time_end <- "02:15",')
    assert ASSIGNMENT.search('thresh_time_start = "25:00"') is None
    assert len(NO_MISSING)==2
    return "PASS_EXACT_TWO_CLOCK_LITERAL_KEYS_ONLY"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_AUTHOR_HHMM_CLOCK_CONSTANTS_V3.json")
    a=p.parse_args()
    guard=test()
    if a.self_test:
        print(json.dumps({"self_test":guard,"bat_event_rows_opened":False}))
        return
    x=source()
    result={
       "contract":"MYOTIS_2026_AUTHOR_FIXED_FORAGING_CLOCK_CONSTANTS_CONTRACT_V3.md",
       "status":x["status"],
       "author_code_method_only":x,
       "bat_events_read":0,
       "source_observational_pair_stats_calculated":0,
       "GPS_coordinates_or_roost_location_read":False,
       "true_timezone_verified":False,
       "station_uptime_verified":False,
       "self_test":guard}
    Path(a.out).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],
        "exact_author_source_clocks":x.get("method_clock_assignments",[]),
        "unique_values":x.get("distinct_literal_clocks_per_variable",{}),
        "timezone_syntax_seen":x.get("any_explicit_timezone_assignment_in_original_source"),
        "original_bat_data_opened":False},sort_keys=True))
if __name__=="__main__":main()
