"""Publisher-hash compare of two PINNED, public author-GitHub CSV releases.

Official Dryad v2 dataset/version/file metadata verified first.
Raw public author files are fetched for digest/length and FIRST header only.
Not a new independent field dataset; no biological data rows are parsed,
saved, logged or committed. Dryad bytes themselves remain HTTP 401.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import pathlib
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from dryad_rous_source_manifest import DOI, STATUS, audit

AUTHOR_REPO="EmmLourie/Information-transfer-analysis"
AUTHOR_SHA="1d7edbdbb87d9df048ab42a0b425a1966d491e86"
TWO_FILES=("Field_Manipulation_Table.csv","Tags_manipulated_and_visiting.csv")
UNMATCHED_THIRD="manipulations_trees_locations.csv"
MAX_SIZE=50_000
VERIFIED="ROUS_TWO_AUTHOR_GITHUB_FILES_MATCH_ORIGINAL_DRYAD_DIGEST_AND_SIZE"


def get_original_author_bytes(name, expected):
    if name not in TWO_FILES or type(expected) is not int or not 0<expected<=MAX_SIZE:
        raise ValueError("SOURCE_AUTHOR_FILE_NOT_ALLOWLISTED_OR_TOO_LARGE")
    url=(f"https://raw.githubusercontent.com/{AUTHOR_REPO}/{AUTHOR_SHA}/"
         f"data_R/{name}")
    req=Request(url,headers={"User-Agent":"batter-rous-publisher-hash-verification/1.0"})
    with urlopen(req,timeout=35) as resp:
        parsed=urlparse(resp.url)
        if (parsed.scheme!="https" or parsed.netloc!="raw.githubusercontent.com" or
            resp.status!=200):
            raise RuntimeError("SOURCE_AUTHOR_URL_REDIRECT_OR_HTTP_MISMATCH")
        raw=resp.read(expected+1)
    if len(raw)!=expected:
        raise RuntimeError("SOURCE_AUTHOR_PUBLISHER_BYTES_MISMATCH")
    return raw


def audit_author_match(manifest, downloader=get_original_author_bytes):
    if manifest.get("status")!=STATUS or manifest.get("dataset_doi")!=DOI:
        raise RuntimeError("PUBLISHER_METADATA_NOT_VERIFIED")
    entries={x["file_name"]:x for x in manifest["required_original_file_metadata"]}
    reports=[]
    for name in TWO_FILES:
        entry=entries.get(name)
        if not entry:
            raise RuntimeError("PUBLISHER_CSV_MISSING_"+name)
        expected=entry["size_bytes"]
        if type(expected) is not int or not 0<expected<=MAX_SIZE:
            raise RuntimeError("PUBLISHER_CSV_TOO_BIG_OR_INVALID_"+name)
        raw=downloader(name,expected)
        if not isinstance(raw,bytes) or len(raw)!=expected:
            raise RuntimeError("AUTHOR_SOURCE_ORIGINAL_SIZE_MISMATCH_"+name)
        dtype=str(entry.get("digest_type") or "").lower().strip()
        if dtype in ("md5","md-5"):
            calc=hashlib.md5(raw).hexdigest()
        elif dtype in ("sha256","sha-256"):
            calc=hashlib.sha256(raw).hexdigest()
        else:
            raise RuntimeError("PUBLISHER_DIGEST_UNSUPPORTED_"+name)
        if calc.lower()!=str(entry.get("digest") or "").lower().strip():
            raise RuntimeError("AUTHOR_SOURCE_PUBLISHER_DIGEST_MISMATCH_"+name)
        first=next(csv.reader(io.StringIO(raw.decode("utf-8-sig"))),None)
        if not first or any(not x for x in first) or len(first)!=len(set(first)):
            raise RuntimeError("AUTHOR_CSV_HEADER_INVALID_"+name)
        reports.append({"file_name":name,"publisher_digest_type":dtype,
                        "publisher_exact_digest":calc, "publisher_exact_byte_count":expected,
                        "column_names_only":first, "biological_rows_read":False})
    return {
        "schema":"batter.resource_behavior_sdm.author_hash_comparison.v1",
        "status":VERIFIED,
        "original_Dryad_DOI":DOI,
        "author_GitHub_repo":AUTHOR_REPO,
        "author_GitHub_commit_sha":AUTHOR_SHA,
        "matched_original_files_count":len(reports),
        "original_author_exact_publisher_digest_matches":reports,
        "third_original_tree_location_table":UNMATCHED_THIRD,
        "third_original_tree_location_hash_confirmed":False,
        "original_Dryad_download_HTTP401_not_resolved":True,
        "original_biological_rows_read":False,
        "animal_tree_treatment_rows_joined":False,
        "3d_height_confirmed":False,
        "new_2d_behavior_coefficient":None,
        "new_5d_resource_behavior_coefficient":None,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="prospective/resource_behavior_sdm/rous_author_hash_comparison.json")
    args=parser.parse_args()
    dst=pathlib.Path(args.out);dst.parent.mkdir(parents=True,exist_ok=True)
    try:
        receipt=audit_author_match(audit())
    except Exception as exc:
        receipt={
            "schema":"batter.resource_behavior_sdm.author_hash_comparison.v1",
            "status":"AUTHOR_SOURCE_PUBLISHER_HASH_COMPARISON_STOP",
            "stop_reason":str(exc)[:250],
            "original_Dryad_DOI":DOI,
            "original_biological_rows_read":False,
            "third_original_tree_location_hash_confirmed":False,
            "new_5d_resource_behavior_coefficient":None,
        }
    dst.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("ROUS_AUTHOR_HASH",receipt["status"],flush=True)
    if "stop_reason" in receipt:
        print("ROUS_AUTHOR_HASH_STOP",receipt["stop_reason"],flush=True)
    return 0 if receipt["status"]==VERIFIED else 3


if __name__=="__main__":
    raise SystemExit(main())
