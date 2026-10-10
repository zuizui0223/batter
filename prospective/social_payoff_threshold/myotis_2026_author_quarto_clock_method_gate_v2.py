#!/usr/bin/env python3
"""Source author Quarto method-keyword audit only, original OSF sg6dz.

Never reads OSF bat datasets, output tables, source maps, event rows or
individual identities. Quarto text is NOT rendered/executed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from preflight_myotis_two_day_csv_headers_v2 import metadata,opener,UA

FILENAMES=(
    ("Appendix1_anonym.qmd","698dea461a7b213810c7311d",68621),
    ("Appendix2_anonym.qmd","698dea4664f82861d0e2544a",13562),
)
LIMIT=100_000
PATTERNS={
  "solar":r"(?i)\bsunset\b|\bsunrise\b|\bdusk\b|\bdawn\b|\bsolar\b",
  "timezone":r"(?i)time.zone|time_zone|timezone|\btz\s*=|with_tz|force_tz|\bUTC\b|\bGMT\b|ymd_hms|as\.POSIXct",
  "session":r"(?i)\bnight\b|daylight|\bduration\b|batdate|two nights",
  "detector_coverage":r"(?i)uptime|offline|saturation|battery|\bmissing\b|logger|\bSL\b|receiver",
  "filter_or_ud":r"(?i)\bfilter\s*\(|group_by|UDOI|\brfid\b|threshold",
}
compiled={k:re.compile(v) for k,v in PATTERNS.items()}
IMPORTANT=("solar","timezone","detector_coverage")

def sanitized(line):
    # A source code *method* line, never raw source values/locations/identifiers.
    line=re.sub(r"https?://\S+","[link redacted]",line)
    line=re.sub(r"(?i)\b(?:lat\w*|lon\w*|coord\w*|roost\w*|box\w*)\b",
                "[site field redacted]",line)
    line=re.sub(r"(?i)\b[A-Fa-f0-9]{4,}\b","[identifier redacted]",line)
    line=re.sub(r"['\"][^'\"]{12,}['\"]","'[string redacted]'",line)
    line=re.sub(r"[-+]?\d+(?:\.\d+)?","[#]",line)
    line=re.sub(r"(?:[A-Za-z]:)?[/\\][A-Za-z0-9._/\\-]+","[path redacted]",line)
    return line.strip()[:180]

def inspect(name,rid,expected_size):
    check=metadata(name,rid)
    receipt={"filename":name,"source_identity_verified":bool(check.get("ok")),
             "metadata_http":check.get("http_status"),
             "status":"STOP_SOURCE_INACCESSIBLE"}
    if not check.get("ok"):return receipt
    try:
        request=urllib.request.Request(f"https://osf.io/download/{rid}/",
          headers={"User-Agent":UA,"Accept":"text/plain,text/markdown,*/*"})
        with opener().open(request,timeout=22) as response:
            b=response.read(LIMIT+1)
            status=response.status
        if len(b)>LIMIT:raise ValueError("SOURCE_TOO_BIG")
        if len(b)!=expected_size:raise ValueError("SOURCE_SIZE_DRIFT")
        s=b.decode("utf-8-sig",errors="strict")
        if "\0" in s:raise ValueError("BINARY")
        lines=s.splitlines()
        counts={k:sum(bool(p.search(x)) for x in lines) for k,p in compiled.items()}
        # Restrict extracts to methodological clauses likely relevant to time.
        extracts=[]
        for l in lines:
            if any(compiled[k].search(l) for k in IMPORTANT):
                safe=sanitized(l)
                if safe and len(extracts)<25:
                    extracts.append(safe)
        receipt.update({
             "status":"HOLD_SUN_CLOCK_AVAILABILITY_NOT_ESTABLISHED",
             "source_http":status,
             "source_bytes":len(b),
             "sha256":hashlib.sha256(b).hexdigest(),
             "lines_in_author_quarto":len(lines),
             "method_keyword_counts":counts,
             "sanitized_method_lines":extracts,
             "code_or_embedded_data_executed":False,
             "numeric_bat_outcomes_opened":False})
    except Exception as e:
        receipt["error_kind"]=type(e).__name__
    return receipt

def test():
    assert len(FILENAMES)==2
    demo="filter(timestamp > sunrise, site=lat_sn, tag='RFID1234', n=65)"
    x=sanitized(demo)
    assert "65" not in x and "lat_sn" not in x and "sunrise" in x
    assert compiled["solar"].search(demo)
    return "PASS_STRICT_AUTHOR_TEXT_METHOD_ONLY"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_QUARTO_METHOD_KEYWORDS_V2.json")
    args=p.parse_args()
    check=test()
    if args.self_test:
        print(json.dumps({"self_test":check,"bat_records_opened":False}))
        return
    results=[inspect(n,i,size) for n,i,size in FILENAMES]
    ok=all(x["status"]=="HOLD_SUN_CLOCK_AVAILABILITY_NOT_ESTABLISHED"
           for x in results)
    receipt={"contract":"MYOTIS_2026_AUTHOR_QUARTO_METHOD_KEYWORDS_CONTRACT_V2.md",
         "status":"HOLD_SUN_CLOCK_AVAILABILITY_NOT_ESTABLISHED" if ok
              else "STOP_AUTHOR_QUARTO_SOURCE_ACCESS_OR_SCHEMA",
         "files":results,
         "original_animal_CSV_files_opened":0,
         "social_detection_outcome_estimates":0,
         "station_coords_roost_sites_or_tag_values_disclosed":False,
         "source_code_executed":False,
         "self_test":check}
    Path(args.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":receipt["status"],
       "source_summary":[{"filename":x["filename"],
             "source_access":x["status"],
             "keyword_counts":x.get("method_keyword_counts",{}),
             "method_clauses":x.get("sanitized_method_lines",[])}
             for x in results],
       "bat_records_opened":False},sort_keys=True))

if __name__=="__main__":main()
