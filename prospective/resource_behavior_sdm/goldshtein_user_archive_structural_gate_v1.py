"""Goldshtein Mendeley v1 user-uploaded source: structural intake only.

This module NEVER executes archive code, imports source scripts, extracts source
files to disk, or inspects animal rows. Its only product is a privacy-safe
manifest of *potential* structural supports. ZIP upload is untrusted content.
An identified candidate table is NOT a joined or model-ready table.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import pathlib
import posixpath
import stat
import zipfile

DATASET_DOI = "10.17632/jxghjjsttw.1"
MAX_ARCHIVE_BYTES = 300_000_000
MAX_FILES = 900
MAX_TOTAL_UNCOMPRESSED = 1_500_000_000
MAX_SINGLE_UNCOMPRESSED = 300_000_000
MAX_HEADER_READ = 32_000
CANDIDATE_EXTENSIONS = {".csv", ".tsv", ".txt", ".xlsx", ".xls",
                        ".mat", ".rds", ".rdata", ".rda", ".json"}
NON_DATA_EXTENSIONS = {".m", ".r", ".py", ".pdf", ".jpg", ".png", ".mp4", ".mov"}
ACOUSTIC_HEIGHT_LEAKAGE_STOP = ("Altitude<20m visit labels cannot be used to "
    "predict altitude: original paper's visits require distance<15m and height<20m.")

def normalized_header(text):
    return " ".join(str(text).strip().lower().replace("_"," ").replace("."," ").split())

def candidate_semantics(header):
    fields = [normalized_header(x) for x in header]
    hit = lambda vals: any(any(v == f or v in f.split() for v in vals) for f in fields)
    gps_individual = hit({"animal", "individual", "bat", "tag", "id"})
    gps_time = hit({"time", "timestamp", "datetime", "date"})
    horizontal = (hit({"longitude", "lon", "x"}) and hit({"latitude", "lat", "y"}))
    height = hit({"height", "altitude", "agl"})
    flowers = hit({"flowers", "flower", "nectar", "resource", "bloom"})
    # These are name-based *suggestions*, never admissions.
    return {
        "possible_tracking_columns":bool(gps_individual and gps_time and horizontal and height),
        "possible_flower_columns":bool(horizontal and flowers),
        "has_explicit_date_column_name":bool(hit({"date", "day", "survey", "time"})),
        "not_sufficient_for_resource_height_join":True
    }

def audit_archive_bytes(blob):
    if not blob or len(blob)>MAX_ARCHIVE_BYTES:
        raise ValueError("STOP_MISSING_OR_OVERSIZE_ORIGINAL_ARCHIVE")
    with zipfile.ZipFile(io.BytesIO(blob)) as za:
        infos=za.infolist()
        if len(infos)>MAX_FILES:
            raise ValueError("STOP_TOO_MANY_ORIGINAL_ARCHIVE_FILES")
        if sum(i.file_size for i in infos)>MAX_TOTAL_UNCOMPRESSED:
            raise ValueError("STOP_ORIGINAL_ARCHIVE_DECOMPRESSION_CAP")
        report=[]
        seen=set()
        for idx,item in enumerate(infos,1):
            name=item.filename
            n=posixpath.normpath(name)
            if (not name or name.startswith("/") or name.startswith("\\")
                or "\\" in name or n.startswith("../") or n==".."
                or "\0" in name or n in seen):
                raise ValueError("STOP_UNSAFE_OR_DUPLICATE_ARCHIVE_ENTRY")
            seen.add(n)
            unixmode=item.external_attr>>16
            if stat.S_ISLNK(unixmode):
                raise ValueError("STOP_ARCHIVED_SYMLINK")
            if item.is_dir():
                continue
            if item.file_size>MAX_SINGLE_UNCOMPRESSED:
                raise ValueError("STOP_OVERSIZE_ORIGINAL_MEMBER")
            ext=pathlib.PurePosixPath(n).suffix.lower()
            item_report={
                "anonymous_member_ordinal":idx,
                "extension":ext or "(none)",
                "bytes":item.file_size,
                "read_original_data_rows":False
            }
            if ext in (".csv",".tsv",".txt"):
                with za.open(item) as stream:
                    first = stream.readline(MAX_HEADER_READ+1)
                    if len(first)>MAX_HEADER_READ:
                        item_report["header_status"]="HEADER_EXCEEDS_SAFE_CAP"
                    else:
                        try:
                            txt=first.decode("utf-8-sig").strip()
                            delimiter="\t" if ext==".tsv" else ","
                            if ext==".txt":
                                delimiter="\t" if txt.count("\t")>txt.count(",") else ","
                            hdr=next(csv.reader([txt],delimiter=delimiter))
                            if len(hdr)>200 or any(len(h)>180 for h in hdr):
                                item_report["header_status"]="HEADER_TOO_WIDE"
                            elif len(hdr)<2:
                                item_report["header_status"]="NO_TABULAR_COLUMNS"
                            else:
                                item_report["header_status"]="COLUMN_NAMES_ONLY"
                                # Never print original headers: can contain tag IDs.
                                item_report["header_count"]=len(hdr)
                                item_report["semantic_hints"]=candidate_semantics(hdr)
                        except (UnicodeDecodeError,csv.Error,StopIteration):
                            item_report["header_status"]="NON_UTF8_OR_NONTABULAR_HEADER"
            elif ext==".mat":
                with za.open(item) as stream:
                    prefix=stream.read(128)
                item_report["format_note"]=(
                    "MATLAB_V5_HEADER_ONLY" if b"MATLAB 5.0 MAT-file" in prefix
                    else "MATLAB_OR_OTHER_BINARY_SCHEMA_UNVERIFIED")
            elif ext in (".xlsx",".xls",".rds",".rdata",".rda",".json"):
                item_report["format_note"]="FORMAT_REQUIRES_LOCAL_SCHEMA_REVIEW"
            elif ext==".zip":
                item_report["format_note"]="NESTED_ARCHIVE_NOT_OPENED"
            elif ext in NON_DATA_EXTENSIONS:
                item_report["format_note"]="NONDATA_OR_SOURCE_CODE_NOT_EXECUTED"
            else:
                item_report["format_note"]="UNKNOWN_MEMBER_FORMAT"
            report.append(item_report)
    possible_gps=any(x.get("semantic_hints",{}).get("possible_tracking_columns") for x in report)
    possible_flower=any(x.get("semantic_hints",{}).get("possible_flower_columns") for x in report)
    return {
        "schema":"batter.goldshtein_user_archive_structural_gate.v1",
        "status":"ORIGINAL_UPLOAD_ZIP_STRUCTURALLY_AUDITED_NOT_JOINED",
        "source_doi_claim_from_user":DATASET_DOI,
        "original_publisher_digest_verified":False,
        "uploaded_archive_sha256":hashlib.sha256(blob).hexdigest(),
        "source_archive_not_committed":True,
        "source_table_rows_read":False,
        "source_animal_ids_printed":False,
        "anonymous_files":report,
        "csv_header_hints_possible_gps":possible_gps,
        "csv_header_hints_possible_flower_resource":possible_flower,
        "independent_resource_survey_dated_verified":False,
        "night_by_bat_resource_join_verified":False,
        "height_agl_semantics_verified_from_original":False,
        "independent_xy_only_state_assignment_verified":False,
        "source_original_3d_resource_gain":None,
        "response_leakage_stop":ACOUSTIC_HEIGHT_LEAKAGE_STOP,
        "next_gate":"Require original table schema, dated flower survey and per-fix tracking keys; never use height-derived visit labels."
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--archive",required=True)
    ap.add_argument("--out",required=True)
    opts=ap.parse_args()
    src=pathlib.Path(opts.archive)
    receipt=audit_archive_bytes(src.read_bytes())
    out=pathlib.Path(opts.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("GOLDSHTEIN_USER_ORIGINAL",receipt["status"])
    print("MEMBERS",len(receipt["anonymous_files"]))
    print("NO_BIOLOGICAL_ROWS_READ",not receipt["source_table_rows_read"])

if __name__=="__main__":
    main()
