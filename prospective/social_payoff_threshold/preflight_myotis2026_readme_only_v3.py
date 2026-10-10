#!/usr/bin/env python3
"""Read only the original OSF README's text to clarify column semantics.

Never opens bat event rows, locations or sensor measurements.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from preflight_myotis_two_day_csv_headers_v2 import metadata, opener, UA

ID="698dc7add062fca4f5dfc63d"
URL=f"https://osf.io/download/{ID}/"
MAX=2048


def sanitized_definitions(raw):
    text=raw.decode("utf-8-sig",errors="strict")
    lines=[]
    for line in text.splitlines():
        if not re.search(r"(?i)\b(?:rx|tx|rfid|dyad|sn_prox|receiver|sender|bat|date)\b",line):
            continue
        if "https://" in line or "http://" in line:
            line=re.sub(r"https?://\S+","[original source link redacted]",line)
        # Strip numeric coordinates, arbitrary large identifiers and tokenlike strings.
        line=re.sub(r"[-+]?\d+(?:\.\d+)?","[#]",line)
        line=re.sub(r"[A-Fa-f0-9]{18,}","[identifier redacted]",line)
        lines.append(line.strip()[:200])
    return lines[:25]


def self_test():
    s=b"These are the rx receiver, tx sender and rfid bat identifiers.\nNext example 51.123 latitude 7.012.\n"
    a=sanitized_definitions(s)
    assert "receiver" in a[0]
    assert "51.123" not in json.dumps(a)
    assert len(a)==1
    return "PASS_README_TEXT_REDACTION"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--out",default="MYOTIS_2026_README_SCHEMA_ONLY_V3.json")
    a=p.parse_args()
    check=self_test()
    if a.self_test:
        print(json.dumps({"test":check,"bat_event_rows_opened":False}))
        return
    meta=metadata("README.md",ID)
    receipt={"source_file":"OSF sg6dz root README.md","source_id":ID,
        "source_meta_identity_ok":meta["ok"],
        "source_meta_http":meta["http_status"],
        "contract":"MYOTIS_2026_README_ONLY_SEMANTIC_GATE_V3.md",
        "no_event_rows_opened":True,
        "no_bat_detection_records_opened":True,
        "self_test":check}
    if not meta["ok"]:
        receipt["status"]="STOP_README_SOURCE_INACCESSIBLE"
    else:
        try:
            req=urllib.request.Request(URL,headers={"User-Agent":UA,
                      "Accept":"text/markdown,text/plain,*/*"})
            with opener().open(req,timeout=18) as response:
                raw=response.read(MAX+1)
                response_code=response.status
            if len(raw)>MAX or b"\x00" in raw:
                raise ValueError("README_BINARY_OR_TOO_LONG")
            receipt.update({"status":"HOLD_SEMANTICS_ONLY_NEEDS_BAT_NIGHT_GATE",
                "http_status":response_code,
                "size_bytes":len(raw),
                "source_sha256":hashlib.sha256(raw).hexdigest(),
                "schema_description_lines":sanitized_definitions(raw)})
        except Exception as e:
            receipt["status"]="STOP_README_SOURCE_INACCESSIBLE"
            receipt["error_kind"]=type(e).__name__
    Path(a.out).write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":receipt["status"],
        "schema_description_lines":receipt.get("schema_description_lines",[]),
        "original_readme_identity_ok":meta["ok"],
        "bat_event_rows_opened":False},sort_keys=True))


if __name__=="__main__":main()
