#!/usr/bin/env python3
"""Source-only Zenodo 2026 bat pinna/flight CSV header probe. No numeric outcomes opened."""
import argparse
import csv
import datetime as dt
import io
import json
import re

import requests

RECORD_ID = "20927789"
API = f"https://zenodo.org/api/records/{RECORD_ID}"
RECORD_URL = f"https://zenodo.org/records/{RECORD_ID}"
DOI = "10.5281/zenodo.20927789"
HEADERS = {"User-Agent": "batter-public-pinna-source-gate/1.0"}
CANDIDATES = [
    "earTipSep_SSblin_500mmRange_full_nlme_vms_tm_CIbands_MC.csv",
    "mdau_basement_config_UCLOUD_01_collect_20241008_203617_processed_20251112_szred_lcs_20251114_PARTIALLY_export.csv",
    "ppyg_config_UCLOUD_01_collect_20241008_122450_processed_20251112_szred_lcs_20251114_export.csv",
]
CAP_BYTES = 16 * 1024 * 1024
MAX_HEADER = 16 * 1024
TIMEOUT = (10, 30)

def text_header(first):
    text = first.decode("utf-8-sig", errors="replace").lstrip("\ufeff")
    if "\n" not in text and len(first) >= MAX_HEADER:
        return {"gate": "STOP_HEADER_EXCEEDS_16K"}
    text = text.splitlines()[0] if text.splitlines() else ""
    delimiter = "\t" if text.count("\t") > text.count(",") else ","
    try:
        cols = next(csv.reader([text], delimiter=delimiter))
    except Exception:
        cols = []
    return {"gate": "HEADER_ONLY", "delimiter": delimiter,
            "n_columns": len(cols), "column_names": [str(c)[:100] for c in cols[:300]],
            "row_values_opened": False,
            "candidate_stable_id_columns": [c for c in cols
                if re.search(r"(?i)(bat.?id|individual|animal.?id|subject.?id|\\bid\\b)", c)],
            "candidate_independent_bout_columns": [c for c in cols
                if re.search(r"(?i)(recording|session|trial|bout|flight|date|timestamp)", c)]}

def do_probe():
    result = {
       "evidence": "SOURCE_CSV_HEADER_ONLY_NO_PHYSIOLOGICAL_VALUES",
       "record_id": RECORD_ID,
       "doi": DOI,
       "record_url": RECORD_URL,
       "when_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
       "api_http": None,
       "record_metadata": {},
       "listed_files": [],
       "requested_headers": [],
       "source_author_repo": "fhaefele/target-focused-hearing-of-echolocating-bats-pnas",
       "status": "STOP_ZENODO_SOURCE_INACCESSIBLE",
       "numeric_kinematic_ear_or_bat_measurements_opened": False,
       "categorical_support_counted": False
    }
    session = requests.Session()
    try:
        a = session.get(API, headers=HEADERS, timeout=TIMEOUT)
        result["api_http"] = a.status_code
        a.raise_for_status()
        payload = a.json()
        if str(payload.get("id")) != RECORD_ID:
            raise RuntimeError("Zenodo record ID mismatch")
        meta = payload.get("metadata") or {}
        result["record_metadata"] = {
            "record_id": payload.get("id"), "title": meta.get("title"),
            "version": meta.get("version"),
            "doi": payload.get("doi") or meta.get("doi"),
            "access_right": (meta.get("access_rights") or meta.get("access_right")),
        }
        if str(result["record_metadata"]["doi"]) != DOI:
            raise RuntimeError("Zenodo DOI mismatch, refusing mismatched source")
        files = payload.get("files") or []
        names = {}
        for f in files:
            key = f.get("key") or f.get("filename")
            info = {
                "filename": key,
                "bytes": f.get("size"),
                "checksum": f.get("checksum"),
                "download_host": None,
            }
            links = f.get("links") or {}
            url = links.get("content") or links.get("self")
            if url:
                from urllib.parse import urlsplit
                info["download_host"] = urlsplit(url).hostname
            result["listed_files"].append(info)
            names[key] = f
        result["status"] = "STOP_CSV_SCHEMA_UNAVAILABLE"
        for target in CANDIDATES:
            file = names.get(target)
            entry={"file": target, "status": "NOT_LISTED"}
            if not file:
                result["requested_headers"].append(entry)
                continue
            size=file.get("size")
            if size is None or int(size)>CAP_BYTES:
                entry["status"]="SKIP_GT_16MIB_OR_SIZE_UNKNOWN"
                result["requested_headers"].append(entry)
                continue
            links=file.get("links") or {}
            url=links.get("content") or links.get("self")
            if not url or not url.startswith("https://zenodo.org/"):
                entry["status"]="STOP_NO_OFFICIAL_ZENODO_LINK"
                result["requested_headers"].append(entry)
                continue
            try:
                with session.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True) as stream:
                    entry["http_status"]=stream.status_code
                    if stream.status_code!=200:
                        entry["status"]="DOWNLOAD_HTTP_"+str(stream.status_code)
                    else:
                        # Only retrieve the FIRST csv header line from response stream.
                        line=stream.raw.readline(MAX_HEADER)
                        entry.update(text_header(line))
                        entry["status"]=entry["gate"]
            except Exception as exc:
                entry["status"]="FETCH_ERROR_"+type(exc).__name__
                entry["error"]=str(exc)[:160]
            result["requested_headers"].append(entry)
        positive=[x for x in result["requested_headers"]
                  if x.get("status")=="HEADER_ONLY" and x.get("n_columns",0)>0]
        if positive:
            result["status"]="PASS_SCHEMA_CANDIDATE_REQUIRES_INDEPENDENT_BOUT_GATE"
    except Exception as exc:
        result["status"]="STOP_ZENODO_SOURCE_INACCESSIBLE"
        result["error"]=type(exc).__name__+": "+str(exc)[:180]
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",default="PINNA_FLIGHT_ZENODO_STRUCTURAL_RECEIPT_V1.json")
    args=p.parse_args()
    output=do_probe()
    with open(args.out, "w", encoding="utf-8") as fd:
        json.dump(output, fd, ensure_ascii=False, indent=2)
        fd.write("\n")
    print(json.dumps({
       "status":output["status"],
       "api_http":output["api_http"],
       "record_meta":output["record_metadata"],
       "listed_file_count":len(output["listed_files"]),
       "headers":output["requested_headers"],
       "error":output.get("error")
    },ensure_ascii=False))
    assert output["numeric_kinematic_ear_or_bat_measurements_opened"] is False
    assert output["categorical_support_counted"] is False

if __name__=="__main__":
    main()
