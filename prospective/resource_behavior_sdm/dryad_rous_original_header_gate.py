"""Original Rousettus Dryad three tiny CSVs: checksum + HEADER-ONLY preflight.

No numeric biological rows parsed or persisted. Never download 285 MB SQLite
tracks in this stage. The only permitted origin URL is the version-pinned
Dryad public file ID from the verified official REST file inventory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import pathlib
from urllib.request import Request, urlopen

from dryad_rous_source_manifest import DOI, STATUS as MANIFEST_PASS, audit

HEADER_FILES = (
    "Field_Manipulation_Table.csv",
    "manipulations_trees_locations.csv",
    "Tags_manipulated_and_visiting.csv",
)
MAX_BYTES_PER_FILE = 100_000
PASS = "ROUS_ORIGINAL_THREE_CSV_HEADERS_CHECKSUM_VERIFIED"


def original_bytes(file_id, expected_size):
    if type(file_id) is not int or file_id <= 0:
        raise ValueError("ORIGINAL_PUBLIC_FILE_ID_INVALID")
    if type(expected_size) is not int or not 0 < expected_size <= MAX_BYTES_PER_FILE:
        raise ValueError("ORIGINAL_SOURCE_BYTES_EXCEED_PREFROZEN_LIMIT")
    url = "https://datadryad.org/api/v2/files/"+str(file_id)+"/download"
    request = Request(url, headers={"User-Agent":"batter-rousettus-source-header-audit/1.0"})
    with urlopen(request,timeout=45) as response:
        if response.status != 200:
            raise RuntimeError("ORIGINAL_DRYAD_DOWNLOAD_HTTP_NOT_200")
        payload = response.read(expected_size + 1)
    if len(payload) != expected_size:
        raise RuntimeError("ORIGINAL_DRYAD_BYTES_MISMATCH")
    return payload


def header_audit(manifest, downloader=original_bytes):
    if manifest.get("status") != MANIFEST_PASS or manifest.get("dataset_doi") != DOI:
        raise RuntimeError("ORIGINAL_METADATA_NOT_AUTHENTICATED")
    indexed = {x["file_name"]:x for x in manifest["required_original_file_metadata"]}
    if any(name not in indexed for name in HEADER_FILES):
        raise RuntimeError("ORIGINAL_REQUIRED_CSV_NOT_IN_MANIFEST")
    reports=[]
    for name in HEADER_FILES:
        row=indexed[name]
        n=row["size_bytes"]
        if type(n) is not int or n <= 0 or n > MAX_BYTES_PER_FILE:
            raise RuntimeError("ORIGINAL_FILE_SIZE_EXCEEDS_FROZEN_LIMIT")
        buf=downloader(row["public_file_id"],n)
        if not isinstance(buf,bytes) or len(buf)!=n:
            raise RuntimeError("ORIGINAL_FILE_BYTES_NOT_VERIFIED")
        dtype=str(row["digest_type"]).strip().lower()
        if dtype in ("sha-256","sha256"):
            actual=hashlib.sha256(buf).hexdigest()
        elif dtype == "md5":
            actual=hashlib.md5(buf).hexdigest()
        else:
            raise RuntimeError("ORIGINAL_DIGEST_TYPE_NOT_SUPPORTED")
        if actual.lower()!=str(row.get("digest","")).strip().lower():
            raise RuntimeError("ORIGINAL_FILE_HASH_MISMATCH")
        # Parse only the FIRST CSV record (header), never a biological value row.
        text=buf.decode("utf-8-sig")
        columns=next(csv.reader(io.StringIO(text)),None)
        if not columns or any(not h.strip() for h in columns):
            raise RuntimeError("ORIGINAL_CSV_HEADER_EMPTY")
        if len(columns)!=len(set(columns)):
            raise RuntimeError("ORIGINAL_CSV_HEADER_DUPLICATE")
        reports.append({"file_name":name,"verified_source_digest":actual,
                        "digest_type":dtype,"original_bytes_verified":n,
                        "column_names_only":columns,
                        "biological_records_parsed":False})
    return {
        "schema":"batter.resource_behavior_sdm.rous_three_header_gate.v1",
        "status":PASS,
        "source_doi":DOI,
        "csv_files_verified":len(reports),
        "original_csv_header_schema":reports,
        "parsed_original_biological_rows":False,
        "sqlite_tracks_downloaded":False,
        "bat_tree_event_joined":False,
        "3d_altitude_measured":False,
        "empirical_resource_behavior_gain":None,
        "empirical_5d_gain":None,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="prospective/resource_behavior_sdm/rous_original_header_receipt.json")
    args=parser.parse_args()
    out=pathlib.Path(args.out);out.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=header_audit(audit())
    except Exception as exc:
        result={
          "schema":"batter.resource_behavior_sdm.rous_three_header_gate.v1",
          "status":"ORIGINAL_THREE_CSV_HEADER_STOP",
          "stop_reason":str(exc)[:250],
          "source_doi":DOI,
          "parsed_original_biological_rows":False,
          "sqlite_tracks_downloaded":False,
          "empirical_5d_gain":None,
        }
    out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ROUS_ORIGINAL_HEADER",result["status"],flush=True)
    if result["status"] != PASS:
        print("ROUS_ORIGINAL_HEADER_STOP_REASON",result.get("stop_reason","UNKNOWN"),flush=True)
    else:
        for r in result["original_csv_header_schema"]:
            print("VERIFIED_HEADER",r["file_name"],len(r["column_names_only"]),"columns",flush=True)
    return 0 if result["status"]==PASS else 3


if __name__=="__main__":
    raise SystemExit(main())
