"""One-shot public original Dryad HEADERS-ONLY access for two independent datasets.

Sources: authenticated original DOI + version + public file-ID metadata.
Attempt exactly two small public publisher file downloads ONCE in GitHub
Actions; never save raw bytes, coordinates, animal identifiers or XLSX rows.
Do NOT substitute mirroring or infer absence if a public file returns 401.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
import xml.etree.ElementTree as ET
import zipfile

from independent_resource_vertical_dryad_gate_v1 import audit_both,PASS as META_PASS

TARGETS={
    "chrotopterus_2026":("Raw_movement_data.zip",1_500_000),
    "ducke_bats_2018":("Bats_Ducke_data_metadata.xlsx",300_000),
}
PASS="ORIGINAL_SMALL_SOURCE_BYTES_AND_HEADERS_VERIFIED"
MAX_UNCOMPRESSED=30_000_000
MAX_ZIP_ENTRIES=1000


def get_bytes(file_id,expected,limit):
    if type(file_id) is not int or file_id<=0:
        raise ValueError("BAD_PUBLISHER_FILE_ID")
    if type(expected) is not int or not 0<expected<=limit:
        raise ValueError("SOURCE_BYTES_NOT_WITHIN_FROZEN_LIMIT")
    url=f"https://datadryad.org/api/v2/files/{file_id}/download"
    req=Request(url,headers={"User-Agent":"batter-independent-bat-resource-source-headers-only/1.0"})
    with urlopen(req,timeout=45) as response:
        if response.status!=200:
            raise RuntimeError("OFFICIAL_DRYAD_FILE_HTTP_NOT_200")
        dest=urlparse(response.url)
        if dest.scheme!="https" or not dest.hostname:
            raise RuntimeError("UNSAFE_PUBLISHER_REDIRECT")
        b=response.read(expected+1)
    if len(b)!=expected:
        raise RuntimeError("ORIGINAL_DRYAD_SOURCE_BYTE_LENGTH_MISMATCH")
    return b


def verify_digest(blob,meta):
    dtype=str(meta.get("digest_type") or "").lower().replace("-","")
    digest=str(meta.get("digest") or "").lower()
    if dtype=="md5":
        actual=hashlib.md5(blob).hexdigest()
    elif dtype=="sha256":
        actual=hashlib.sha256(blob).hexdigest()
    else:
        raise RuntimeError("ORIGINAL_PUBLISHER_DIGEST_UNSUPPORTED")
    if actual!=digest:
        raise RuntimeError("ORIGINAL_FILE_PUBLISHER_DIGEST_MISMATCH")
    return actual,dtype


def inspect_zip(blob,role):
    if not blob.startswith(b"PK\x03\x04"):
        raise RuntimeError("PUBLISHER_BUNDLE_NOT_ZIP")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        infos=z.infolist()
        if len(infos)>MAX_ZIP_ENTRIES or sum(x.file_size for x in infos)>MAX_UNCOMPRESSED:
            raise RuntimeError("ORIGINAL_ZIP_BOMB_LIMIT")
        if any(i.filename.startswith("/") or ".." in i.filename.split("/") for i in infos):
            raise RuntimeError("ZIP_UNSAFE_MEMBER_NAME")
        if role=="chrotopterus_2026":
            counts=Counter()
            header_union=set()
            header_sample=0
            for member in infos:
                if member.is_dir():
                    continue
                suffix=Path(member.filename).suffix.lower()
                counts[suffix]+=1
                # Inspect only first CSV line and NEVER persist member name.
                if suffix==".csv" and member.file_size < 2_000_000:
                    with z.open(member) as raw:
                        # CSV header may have a few metadata lines;
                        # no attempt to inspect data rows to resolve it.
                        first=raw.readline(65536).decode("utf-8-sig",errors="replace")
                    columns=next(csv.reader([first]),[])
                    header_union.update(c.strip() for c in columns if c.strip())
                    header_sample+=1
            return {"zip_file_member_count":sum(counts.values()),
                    "zip_member_extension_counts":dict(sorted(counts.items())),
                    "csv_header_files_inspected":header_sample,
                    "csv_first_line_column_names_union":sorted(header_union),
                    "original_member_paths_recorded":False,
                    "original_gps_rows_parsed":False}
    raise RuntimeError("ZIP_ROLE_NOT_IMPLEMENTED")


def inspect_xlsx(blob):
    if not blob.startswith(b"PK\x03\x04"):
        raise RuntimeError("ORIGINAL_EXCEL_NOT_ZIP")
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        infos=z.infolist()
        if len(infos)>MAX_ZIP_ENTRIES or sum(x.file_size for x in infos)>MAX_UNCOMPRESSED:
            raise RuntimeError("ORIGINAL_XLSX_ZIP_BOMB_LIMIT")
        names=set(z.namelist())
        if "xl/workbook.xml" not in names:
            raise RuntimeError("ORIGINAL_XLSX_WORKBOOK_MISSING")
        root=ET.fromstring(z.read("xl/workbook.xml"))
        ns="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        worksheets=root.findall(".//"+ns+"sheets/"+ns+"sheet")
        return {"workbook_worksheet_count":len(worksheets),
                "workbook_sheet_names_only":[x.get("name") for x in worksheets],
                "original_bat_capture_or_fruit_values_parsed":False}


def check_one(source_meta,get=get_bytes):
    if source_meta.get("status")!=META_PASS:
        raise RuntimeError("ORIGINAL_PUBLISHER_METADATA_NOT_QUALIFIED")
    key=source_meta["dataset"]
    name,cap=TARGETS[key]
    all_files=source_meta["source_files"]
    matching=[x for x in all_files if x["source_file_name"]==name]
    if len(matching)!=1:
        raise RuntimeError("ORIGINAL_REQUIRED_FILE_NOT_UNIQUE")
    filemeta=matching[0]
    data=get(filemeta["original_file_id"],filemeta["size_bytes"],cap)
    if not isinstance(data,bytes) or len(data)!=filemeta["size_bytes"]:
        raise RuntimeError("ORIGINAL_SOURCE_LENGTH_NOT_VERIFIED")
    digest,dtype=verify_digest(data,filemeta)
    schema=inspect_xlsx(data) if key=="ducke_bats_2018" else inspect_zip(data,key)
    return {"dataset":key,"status":PASS,"original_file":name,
            "verified_source_bytes":len(data),"digest_type":dtype,"verified_digest":digest,
            "structure":schema,"raw_source_bytes_committed":False,
            "original_bat_locations_or_ids_persisted":False,
            "biological_response_or_fruit_values_opened":False,
            "actual_resource_height_join":False,
            "new_ecological_height_resource_gain":None}


def run(meta_get=None,original_get=get_bytes):
    if meta_get is None:
        registry=audit_both()
    else:
        registry=audit_both(meta_get)
    results=[]
    for source in registry["results"]:
        key=source["dataset"]
        try:
            data=check_one(source,original_get)
        except Exception as exc:
            data={"dataset":key,"status":"ORIGINAL_SMALL_FILE_ACCESS_OR_SCHEMA_STOP",
                  "reason":(type(exc).__name__+":"+str(exc))[:240],
                  "biological_response_or_fruit_values_opened":False,
                  "new_ecological_height_resource_gain":None}
        results.append(data)
    return {"schema":"batter.independent_measured_food_and_vertical_public_file_gate.v1",
            "public_source_checks":results,
            "verified_original_file_count":sum(x["status"]==PASS for x in results),
            "two_studies_joined_into_one_observation":False,
            "new_ecological_5d_gain":None}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",default="prospective/resource_behavior_sdm/independent_resource_vertical_original_smallfile_v1.json")
    args=parser.parse_args()
    obj=run()
    dst=Path(args.out)
    dst.parent.mkdir(parents=True,exist_ok=True)
    dst.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    for x in obj["public_source_checks"]:
        print("ORIGINAL_SMALL_SOURCE",x["dataset"],x["status"],flush=True)
        if "reason" in x:
            print("ORIGINAL_FILE_STOP",x["reason"],flush=True)
        else:
            print("ORIGINAL_FILE_STRUCTURE",json.dumps(x["structure"],ensure_ascii=False),flush=True)
    return 0 if obj["verified_original_file_count"]==len(TARGETS) else 3

if __name__=="__main__":
    raise SystemExit(main())
