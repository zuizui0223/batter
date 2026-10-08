#!/usr/bin/env python3
"""Public source-only metadata/header audit for Mendeley 10.17632/4y98p5y8fc.1.

NO CF2 values are opened. No personal trait or statistical result is computed.
Designed to fail closed if API, stable ID documentation or tabular schema missing.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import re
import tempfile
import zipfile
import xml.etree.ElementTree as ET

import requests

ID = "4y98p5y8fc"
VERSION = 1
DOI = "10.17632/4y98p5y8fc.1"
API = "https://api.data.mendeley.com"
CAP = 15 * 1024 * 1024
HEADERS = {"Accept": "application/json, application/vnd.mendeley-public-dataset.1+json",
           "User-Agent": "batter-cf-colony-schema-audit/1.0 (public-source-only)"}
XLSX_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS = {"x": XLSX_NS}
TIMEOUT = (10, 20)
ENDPOINTS = [
    f"{API}/datasets/{ID}?version={VERSION}",
    f"{API}/datasets/{ID}/files?version={VERSION}",
    f"{API}/datasets/publics/{ID}/files?version={VERSION}",
]


def fingerprint(url):
    # Log only the official endpoint, never signed download URL tokens.
    return url.replace(API, "api.data.mendeley.com")


def try_json(session, url):
    record = {"endpoint": fingerprint(url), "http_status": None, "ok": False}
    try:
        res = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=False)
        record["http_status"] = res.status_code
        if res.status_code == 200:
            out = res.json()
            record["ok"] = True
            return record, out
        record["error"] = "HTTP_" + str(res.status_code)
    except Exception as exc:
        record["error"] = type(exc).__name__ + ":" + str(exc)[:140]
    return record, None


def file_records(x):
    if isinstance(x, list):
        return [k for k in x if isinstance(k, dict)]
    if isinstance(x, dict):
        for key in ("files", "items", "results", "data"):
            if isinstance(x.get(key), list):
                return [k for k in x[key] if isinstance(k, dict)]
    return []


def metadata(f):
    details = f.get("content_details") or {}
    if not isinstance(details, dict):
        details = {}
    out = {
      "name": f.get("filename") or f.get("name"),
      "file_uuid": f.get("id"),
      "announced_size": f.get("size") or details.get("size"),
      "published_sha256": details.get("sha256_hash"),
      "type": details.get("content_type") or f.get("media_type"),
    }
    return out


def xlsx_headers(raw):
    output = {"format": "xlsx", "sheets": [], "worksheet_headers": [],
              "values_beyond_first_row_opened": False}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        keys = set(z.namelist())
        if "xl/workbook.xml" in keys:
            root = ET.fromstring(z.read("xl/workbook.xml"))
            output["sheets"] = [x.attrib.get("name") for x in root.findall(".//x:sheet", NS)]
        shared = []
        if "xl/sharedStrings.xml" in keys:
            root = ET.fromstring(z.read("xl/sharedStrings.xml"))
            for si in root.findall("x:si", NS):
                shared.append("".join(x.text or "" for x in si.findall(".//x:t", NS)))
        for member in sorted(keys):
            if not re.fullmatch(r"xl/worksheets/sheet[0-9]+\.xml", member):
                continue
            root = ET.fromstring(z.read(member))
            headers = []
            for row in root.findall(".//x:sheetData/x:row", NS):
                # Only the first row; do not inspect any numeric CF2 values.
                for c in row.findall("x:c", NS):
                    rawvalue = c.find("x:v", NS)
                    if c.attrib.get("t") == "s" and rawvalue is not None:
                        try:
                            val = shared[int(rawvalue.text)]
                        except Exception:
                            val = "<invalid shared string>"
                    elif c.attrib.get("t") == "inlineStr":
                        val = "".join(v.text or "" for v in c.findall(".//x:t", NS))
                    elif c.attrib.get("t") in ("str",):
                        val = rawvalue.text if rawvalue is not None else ""
                    else:
                        # No actual numeric first row opened either.
                        val = "<nontext header>"
                    headers.append(str(val)[:120])
                break
            output["worksheet_headers"].append({"sheet_member": member, "first_row_header": headers[:150]})
    return output


def tabular_header(raw, name):
    if name.lower().endswith(".xlsx"):
        return xlsx_headers(raw)
    if name.lower().endswith((".csv", ".tsv", ".txt")):
        s = raw[:min(len(raw), 8000)].decode("utf-8-sig", errors="replace")
        firstline = s.splitlines()[0] if s.splitlines() else ""
        sep = "\t" if name.lower().endswith(".tsv") else ("," if firstline.count(",") >= firstline.count("\t") else "\t")
        parsed = next(csv.reader([firstline], delimiter=sep), [])
        return {"format": "delimited_text", "delimiter": "\\t" if sep=="\t" else ",",
                "first_line_header": [v[:120] for v in parsed[:150]],
                "values_beyond_first_row_opened": False}
    if name.lower().endswith(".mat"):
        try:
            import scipy.io
            with tempfile.NamedTemporaryFile(suffix=".mat") as f:
                f.write(raw)
                f.flush()
                variables = scipy.io.whosmat(f.name)
            return {"format": "mat_v5_headers_only",
                    "variables": [{"name": n, "shape": list(shape), "class": cls}
                                  for n, shape, cls in variables],
                    "numeric_values_opened": False}
        except Exception as exc:
            return {"format": "mat_unreadable", "error_type": type(exc).__name__,
                    "numeric_values_opened": False}
    if name.lower().endswith(".zip"):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            files = [{"name": member.filename[:120], "size": member.file_size}
                     for member in z.infolist()[:100]]
        return {"format": "zip_file_list_only", "members": files, "values_opened": False}
    return {"format": "unsupported_header_type", "values_opened": False}


def streaming_download(session, f):
    details = f.get("content_details") or {}
    name = f.get("filename") or f.get("name")
    file_id = f.get("id")
    if not name or not file_id:
        return None, {"status": "NO_PUBLIC_FILE_UUID_OR_NAME"}
    declared_size = f.get("size") or details.get("size") if isinstance(details, dict) else f.get("size")
    if declared_size is not None and int(declared_size) > CAP:
        return None, {"status": "SKIP_GT_15_MIB", "announced_size": declared_size}
    if not name.lower().endswith((".csv", ".tsv", ".xlsx", ".mat", ".txt", ".zip")):
        return None, {"status": "SKIP_NON_TABULAR_FILE"}
    # Explicit official link OR officially documented redirect, never guessed opaque UUID.
    url = details.get("download_url") if isinstance(details, dict) else None
    if not url:
        url = f"{API}/datasets/{ID}/files/{file_id}/file_downloaded?version={VERSION}"
    if not url.startswith("https://"):
        return None, {"status": "SKIP_NON_HTTPS_DOWNLOAD"}
    try:
        # Download response may redirect to signed temporary blob; redact that URL.
        with session.get(url, timeout=TIMEOUT, stream=True, allow_redirects=True,
                         headers={"User-Agent": HEADERS["User-Agent"]}) as response:
            status = response.status_code
            if status != 200:
                return None, {"status": "DOWNLOAD_HTTP_" + str(status)}
            size=0
            sha=hashlib.sha256()
            chunks=[]
            for chunk in response.iter_content(chunk_size=65536):
                if not chunk:
                    continue
                size+=len(chunk)
                if size>CAP:
                    return None, {"status": "STOP_DOWNLOADED_FILE_EXCEEDS_15_MIB"}
                sha.update(chunk)
                chunks.append(chunk)
        return b"".join(chunks), {"status": "DOWNLOADED_SCHEMA_ONLY", "size_bytes": size,
                                 "sha256": sha.hexdigest()}
    except Exception as exc:
        return None, {"status": "DOWNLOAD_ERROR_" + type(exc).__name__,
                      "error": str(exc)[:100]}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out", default="CF_COLONY_V1_SOURCE_SCHEMA_RECEIPT.json")
    args=parser.parse_args()
    doc={
      "source_DOI": DOI, "source_version": VERSION,
      "evidence_status": "STRUCTURAL_ONLY_NO_CF2_NUMERIC_VALUES_OPENED",
      "performed_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
      "source_api_checks": [], "public_dataset_meta": {}, "files": [], "download_schema_receipts": [],
      "status": "STOP_SOURCE_API_INACCESSIBLE",
      "note": "Published paper has 101 unique bats/177 event appearances; counts not verified from raw file.",
      "stable_animal_id_verification": "NOT_YET_ASSESSED",
      "gate_2_categorical_counts": "NOT_OPENED",
    }
    session=requests.Session()
    objects=[]
    for url in ENDPOINTS:
        receipt,obj=try_json(session,url)
        doc["source_api_checks"].append(receipt)
        if obj is not None:
            if isinstance(obj,dict) and ("name" in obj or "doi" in obj):
                doc["public_dataset_meta"] = {
                    k:obj.get(k) for k in ["id","name","version","publication_date"]
                    if k in obj
                }
            found=file_records(obj)
            if found:
                objects.extend(found)
    by_uuid={}
    for f in objects:
        ident=f.get("id") or f.get("filename") or f.get("name")
        by_uuid[str(ident)]=f
    records=list(by_uuid.values())
    doc["files"]=[metadata(f) for f in records]
    if not records:
        doc["status"]="STOP_SOURCE_API_INACCESSIBLE" if not any(x["ok"] for x in doc["source_api_checks"]) \
                      else "STOP_NO_PUBLIC_TABULAR_FILE_LIST"
    else:
        for f in records:
            name = f.get("filename") or f.get("name")
            raw,desc=streaming_download(session,f)
            entry={"filename":name, **desc}
            if raw is not None:
                if f.get("content_details",{}).get("sha256_hash"):
                    expected=f["content_details"]["sha256_hash"]
                    entry["published_hash_matches"]=expected.lower()==desc["sha256"].lower()
                try:
                    entry["schema"]=tabular_header(raw,name)
                except Exception as exc:
                    entry["schema_error"]=type(exc).__name__+":"+str(exc)[:100]
            doc["download_schema_receipts"].append(entry)
        ok=[x for x in doc["download_schema_receipts"] if "schema" in x and
            x["schema"].get("format") not in ("unsupported_header_type","mat_unreadable")]
        doc["status"]="PASS_SCHEMA_CANDIDATE_REQUIRES_STABLE_ID_DOCUMENTATION" if ok \
                      else "STOP_RAW_TABULAR_SCHEMA_UNAVAILABLE"
    pathlib.Path(args.out).write_text(json.dumps(doc,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({"status": doc["status"],
        "file_names": [x.get("name") for x in doc["files"]],
        "download_status": [{"name":x["filename"],"status":x["status"]}
                           for x in doc["download_schema_receipts"]],
        "endpoints": doc["source_api_checks"]},ensure_ascii=False))


if __name__=="__main__":
    main()
