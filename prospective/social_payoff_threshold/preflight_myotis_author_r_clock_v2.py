#!/usr/bin/env python3
"""OSF ORIGINAL R-SCRIPT CLOCK GRAMMAR ONLY. No bat data, times or locations."""
from __future__ import annotations
import argparse,hashlib,json,re,urllib.request
from pathlib import Path
from preflight_myotis_two_day_csv_headers_v2 import opener,metadata,UA

NAME="func_cAKDE_amt_v2.R"
ID="698dbbf6a779a96a01e24de0"
URL=f"https://osf.io/download/{ID}/"
MAX_BYTES=80000
PAT=re.compile(r"(?i)timestamp|as\.POSIXct|ymd_hms|lubridate|timezone|\btz\s*=|\bUTC\b|\bGMT\b")
def sanitize(line):
    line=re.sub(r"https?://\S+","[URL]",line)
    line=re.sub(r"(?:[A-Za-z]:)?[/\\][^\s\"']+","[path]",line)
    line=re.sub(r"[-+]?\d+(?:\.\d+)?","[#]",line)
    line=re.sub(r"[A-Fa-f0-9]{16,}","[id]",line)
    return line.strip()[:180]
def run():
    meta=metadata(NAME,ID)
    res={"contract":"MYOTIS_2026_AUTHOR_R_CLOCK_SEMANTICS_CONTRACT_V2.md",
         "identity_verified":meta.get("ok"),"file_metadata_http":meta.get("http_status"),
         "status":"STOP_AUTHOR_CODE_SOURCE_INACCESSIBLE",
         "bat_event_values_opened":False,"location_or_individual_record_opened":False}
    if not meta.get("ok"):return res
    try:
        with opener().open(urllib.request.Request(URL,headers={"User-Agent":UA,
                     "Accept":"text/plain,*/*"}),timeout=25) as r:
            b=r.read(MAX_BYTES+1)
        if len(b)>MAX_BYTES:raise ValueError("SOURCE_OVERSIZE")
        t=b.decode("utf-8-sig",errors="strict")
        if "\x00" in t:raise ValueError("BINARY")
        matches=[]
        for line in t.splitlines():
            if PAT.search(line):
                safe=sanitize(line)
                if safe:matches.append(safe)
        res.update({"status":"HOLD_AUTHOR_SCRIPT_DOES_NOT_RESOLVE_TIMEZONE",
               "source_sha256":hashlib.sha256(b).hexdigest(),
               "source_size_bytes":len(b),
               "total_matching_source_lines":len(matches),
               "sanitized_source_code_lines":matches[:25],
               "keyword_count_only":{
                  "timezone":sum(bool(re.search(r"(?i)\btimezone\b|\btz\s*=",l)) for l in t.splitlines()),
                  "timestamp":sum(bool(re.search(r"(?i)timestamp",l)) for l in t.splitlines()),
                  "as_posixct":sum(bool(re.search(r"(?i)as\.POSIXct",l)) for l in t.splitlines()),
                  "utc":sum(bool(re.search(r"(?i)\bUTC\b",l)) for l in t.splitlines())
               }})
    except Exception as e:
        res["error_kind"]=type(e).__name__
    return res
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_AUTHOR_R_CLOCK_V2.json")
    a=p.parse_args()
    assert PAT.search("as.POSIXct(time, tz='UTC')")
    assert "[URL]" in sanitize("https://example.com secret")
    if a.self_test:
        print(json.dumps({"sanitizer":"PASS","bat_rows_accessed":False}));return
    x=run()
    Path(a.out).write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":x["status"],
          "source_keyword_counts":x.get("keyword_count_only",{}),
          "sanitized_clock_lines":x.get("sanitized_source_code_lines",[]),
          "bat_rows_accessed":False},sort_keys=True))
if __name__=="__main__":main()
