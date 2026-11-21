"""Publisher-original PLOS 2016 Leptonycteris 3-D flower vs sham: xlsx SCHEMA gate.

Fetch only official PLOS supplementary DOI S1. Never persist fine-grained animal
tracks/identities, raw XLSX bytes, target coordinates, or source experimental values.
A publisher-initiated redirect is allowed only to matching publisher R2 object.
This run lists structural counts and first-row types, not biological outcomes.
"""
from __future__ import annotations

import hashlib
import io
import json
import re
import sys
import argparse
import zipfile
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

PAPER_DOI="10.1371/journal.pone.0163492"
FILE_DOI=PAPER_DOI+".s001"
URL=f"https://journals.plos.org/plosone/article/file?id={FILE_DOI}&type=supplementary"
PASS="PLOS_ORIGINAL_3D_SUPPLEMENT_XLSX_STRUCTURAL_PASS"
MAX_TRANSFER=1024*1024
MAX_ENTRY_TOTAL=25*1024*1024
MAX_ENTRIES=200
SHEET_NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"


def validate_redirect(destination):
    p=urlparse(destination)
    if p.scheme!="https" or p.username or p.password:
        raise ValueError("UNTRUSTED_SUPPLEMENT_REDIRECT_SCHEME")
    if p.hostname=="journals.plos.org":
        if "/plosone/article/file" not in p.path:
            raise ValueError("UNTRUSTED_SUPPLEMENT_PLOS_PATH")
        return
    if (not p.hostname or not p.hostname.endswith(".r2.cloudflarestorage.com")
            or "corpus-prod." not in p.hostname
            or f"/{PAPER_DOI}/" not in p.path
            or "pone.0163492.s001.xlsx" not in p.path):
        raise ValueError("UNTRUSTED_SUPPLEMENT_REDIRECT_HOST_OR_OBJECT")


def fetch_official():
    request=Request(URL,headers={"User-Agent":"batter-plos-original-schema-audit/1.0"})
    with urlopen(request,timeout=45) as response:
        if response.status!=200:
            raise RuntimeError("PLOS_ORIGINAL_HTTP_NOT_OK")
        validate_redirect(response.url)
        b=response.read(MAX_TRANSFER+1)
    if len(b)>MAX_TRANSFER:
        raise RuntimeError("PLOS_ORIGINAL_EXCEEDS_SIZE_CAP")
    if not b.startswith(b"PK\x03\x04"):
        raise RuntimeError("PLOS_ORIGINAL_NOT_ZIP_XLSX")
    return b


def structure_audit(payload):
    if not isinstance(payload,bytes) or len(payload)>MAX_TRANSFER:
        raise ValueError("PLOS_NOT_SMALL_ORIGINAL_BYTES")
    if not payload.startswith(b"PK\x03\x04"):
        raise ValueError("PLOS_XLSX_ZIP_SIGNATURE_MISSING")
    output=[]
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        entries=archive.infolist()
        if len(entries)>MAX_ENTRIES:
            raise ValueError("PLOS_XLSX_TOO_MANY_ENTRIES")
        if sum(x.file_size for x in entries)>MAX_ENTRY_TOTAL:
            raise ValueError("PLOS_XLSX_ZIP_BOMB_LIMIT")
        if any(".." in x.filename.split("/") or x.filename.startswith("/") for x in entries):
            raise ValueError("PLOS_XLSX_UNSAFE_PATH")
        allnames={x.filename for x in entries}
        if "xl/workbook.xml" not in allnames or "[Content_Types].xml" not in allnames:
            raise ValueError("PLOS_XLSX_WORKBOOK_STRUCTURE_MISSING")
        if any("vbaProject" in x.filename or "externalLinks" in x.filename for x in entries):
            raise ValueError("PLOS_XLSX_EXTERNAL_LINK_OR_MACRO_STOP")
        workbook=ET.fromstring(archive.read("xl/workbook.xml"))
        ns=SHEET_NS
        sheets=workbook.findall(".//"+ns+"sheets/"+ns+"sheet")
        if not sheets:
            raise ValueError("PLOS_XLSX_NO_SHEETS")
        wsfiles=sorted(x for x in allnames if re.fullmatch(r"xl/worksheets/sheet[0-9]+.xml",x))
        if not wsfiles:
            raise ValueError("PLOS_XLSX_NO_SHEET_DATA")
        for name in wsfiles:
            # Only XML metadata and FIRST row cell TYPE attributes are read.
            content=archive.read(name)
            root=ET.fromstring(content)
            dim=root.find(ns+"dimension")
            first=root.find(".//"+ns+"sheetData/"+ns+"row")
            celltypes={}
            firstlen=0
            if first is not None:
                cells=first.findall(ns+"c")
                firstlen=len(cells)
                for cell in cells:
                    key=cell.get("t","n") or "n"
                    celltypes[key]=celltypes.get(key,0)+1
            output.append({"schema_sheet_ordinal":len(output)+1,
                           "declared_excel_dimension":dim.get("ref") if dim is not None else None,
                           "first_row_cell_count":firstlen,
                           "first_row_storage_types":celltypes})
    return {
        "schema":"batter.plos_leptonycteris.original_s001.3d_structural.v1",
        "status":PASS,
        "paper_doi":PAPER_DOI,
        "supplement_doi":FILE_DOI,
        "original_bytes_sha256":hashlib.sha256(payload).hexdigest(),
        "original_bytes":len(payload),
        "worksheet_count":len(output),
        "worksheet_schema_aggregate":output,
        "raw_source_file_saved":False,
        "animal_individual_ids_extracted":False,
        "original_coordinates_or_height_values_read":False,
        "target_labels_derived_from_height":False,
        "publisher_reported_sample":"5 bats x 3 trials per target x 2 target types; original paper",
        "new_wild_food_abundance_test":False,
        "new_resource_conditional_3d_log_score":None,
        "same_study_as_Goldshtein_2020":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--out",default="prospective/resource_behavior_sdm/plos2016_original_3d_structure_v1.json")
    args=ap.parse_args()
    target=Path(args.out);target.parent.mkdir(parents=True,exist_ok=True)
    try:
        result=structure_audit(fetch_official())
    except Exception as exc:
        result={
            "schema":"batter.plos_leptonycteris.original_s001.3d_structural.v1",
            "status":"PLOS_ORIGINAL_XLSX_SOURCE_STOP",
            "reason":(type(exc).__name__+":"+str(exc))[:230],
            "paper_doi":PAPER_DOI,"supplement_doi":FILE_DOI,
            "raw_source_file_saved":False,
            "original_coordinates_or_height_values_read":False,
            "new_resource_conditional_3d_log_score":None,
        }
    target.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PLOS_3D_SOURCE",result["status"],flush=True)
    if result["status"]==PASS:
        print("PLOS_SOURCE_SCHEMA",json.dumps({"n_sheets":result["worksheet_count"],
                                            "sheets":result["worksheet_schema_aggregate"]},
                                            ensure_ascii=False),flush=True)
        return 0
    print("PLOS_SOURCE_STOP",result["reason"],flush=True)
    return 3


if __name__=="__main__":
    sys.exit(main())
