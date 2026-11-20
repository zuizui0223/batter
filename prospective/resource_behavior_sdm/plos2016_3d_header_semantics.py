"""Publisher-original PLOS S1: first HEADER row strings only.

This does not open coordinate/height values or trajectories. It uses the
verified official-PLOS XLSX source retriever and shared-string sheet schema.
Outputs no per-animal data; shared-string entries are read only when referenced
by first-row header cells. Biological prediction is NOT run in this stage.
"""
from __future__ import annotations
import argparse
import io
import json
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET

from plos2016_3d_xlsx_source_gate import (
    PASS as STRUCTURE_PASS, FILE_DOI, fetch_official, structure_audit,
    SHEET_NS, MAX_TRANSFER
)

PASS="PLOS_ORIGINAL_HEADER_COLUMNS_SCHEMA_PASS"


def inspect_publisher_header(payload):
    base=structure_audit(payload)
    if base["status"] != STRUCTURE_PASS:
        raise RuntimeError("PLOS_STRUCTURE_NOT_QUALIFIED")
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        targets=sorted(x for x in archive.namelist()
                       if re.fullmatch(r"xl/worksheets/sheet[0-9]+.xml",x))
        active=[x for x in targets if x.endswith("/sheet1.xml")]
        if len(active)!=1:
            raise RuntimeError("PLOS_PRIMARY_SHEET_UNCERTAIN")
        root=ET.fromstring(archive.read(active[0]))
        first=root.find(".//"+SHEET_NS+"sheetData/"+SHEET_NS+"row")
        if first is None:
            raise RuntimeError("PLOS_FIRST_ROW_ABSENT")
        cells=first.findall(SHEET_NS+"c")
        if len(cells)!=7:
            raise RuntimeError("PLOS_SEVEN_HEADER_CELLS_NOT_FOUND")
        indices=[]
        for cell in cells:
            if cell.get("t")!="s":
                raise RuntimeError("PLOS_FIRST_ROW_IS_NOT_TEXT_HEADER")
            value=cell.find(SHEET_NS+"v")
            if value is None or not (value.text or "").isdigit():
                raise RuntimeError("PLOS_SHARED_STRING_INDEX_INVALID")
            indices.append(int(value.text))
        if "xl/sharedStrings.xml" not in archive.namelist():
            raise RuntimeError("PLOS_SHARED_STRINGS_MISSING")
        desired=set(indices)
        strings={}
        # Stream only until the referenced seven first-row strings are recovered.
        pos=0
        with archive.open("xl/sharedStrings.xml") as stream:
            for _, element in ET.iterparse(stream,events=("end",)):
                if element.tag!=SHEET_NS+"si":
                    continue
                if pos in desired:
                    chunks=[e.text or "" for e in element.iter(SHEET_NS+"t")]
                    strings[pos]="".join(chunks).strip()
                pos+=1
                element.clear()
                if len(strings)==len(desired):
                    break
        if set(strings)!=desired:
            raise RuntimeError("PLOS_HEADER_SHARED_STRING_UNRESOLVED")
        labels=[strings[i] for i in indices]
        if any(not h or len(h)>100 or not re.fullmatch(r"[\w \t./()\-+%°:,]+",h)
               for h in labels):
            raise RuntimeError("PLOS_HEADER_UNSAFE_OR_NONSTANDARD")
        if len(set(labels))!=len(labels):
            raise RuntimeError("PLOS_HEADER_DUPLICATE_COLUMNS")
    return {
      "schema":"batter.plos_2016_s001_original_header_semantics.v1",
      "status":PASS,
      "source_doi":FILE_DOI,
      "source_sha256":base["original_bytes_sha256"],
      "source_size_bytes":base["original_bytes"],
      "primary_worksheet_excel_dimension":base["worksheet_schema_aggregate"][0]["declared_excel_dimension"],
      "verified_original_first_row_column_names":labels,
      "number_of_original_columns":len(labels),
      "original_bat_trials_opened":False,
      "height_or_trajectory_values_opened":False,
      "new_predictive_3d_effect":None,
    }


def main():
    arg=argparse.ArgumentParser()
    arg.add_argument("--out",default="prospective/resource_behavior_sdm/plos2016_header_semantics_v1.json")
    args=arg.parse_args()
    dst=Path(args.out);dst.parent.mkdir(parents=True,exist_ok=True)
    try:
        r=inspect_publisher_header(fetch_official())
    except Exception as exc:
        r={
          "schema":"batter.plos_2016_s001_original_header_semantics.v1",
          "status":"PLOS_HEADER_SEMANTICS_STOP",
          "error":(type(exc).__name__+":"+str(exc))[:220],
          "height_or_trajectory_values_opened":False,
          "new_predictive_3d_effect":None,
        }
    dst.write_text(json.dumps(r,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("PLOS_HEADER",r["status"],flush=True)
    if r["status"]==PASS:
        print("PLOS_HEADER_FIELDS",json.dumps(r["verified_original_first_row_column_names"],ensure_ascii=False),flush=True)
        print("PLOS_SOURCE_SHA256",r["source_sha256"],flush=True)
    else:
        print("PLOS_HEADER_STOP",r["error"],flush=True)
    return 0 if r["status"]==PASS else 3

if __name__=="__main__":
    raise SystemExit(main())
