#!/usr/bin/env python3
from __future__ import annotations

import io, json, os
from pathlib import Path
import openpyxl
import requests

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"post_freeze_extensions/leptonycteris_external_validation/WORKBOOK_SCHEMA_AUDIT_V1.md"
OUTJ=ROOT/"post_freeze_extensions/leptonycteris_external_validation/workbook_schema_audit_v1.json"
FILE_ID=4192796

def main():
    token=os.environ.get("DRYAD_API_TOKEN","").strip()
    if not token:
        raise RuntimeError("DRYAD_API_TOKEN missing")
    r=requests.get(
        f"https://datadryad.org/api/v2/files/{FILE_ID}/download",
        headers={
            "Authorization":f"Bearer {token}",
            "Accept":"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
            "User-Agent":"batter-leptonycteris-workbook-schema-audit-v1/1.0",
        },
        timeout=180,allow_redirects=True
    )
    r.raise_for_status()
    wb=openpyxl.load_workbook(io.BytesIO(r.content),read_only=True,data_only=False)
    sheets=[]
    for ws in wb.worksheets:
        string_rows=[]
        for ri,row in enumerate(ws.iter_rows(min_row=1,max_row=min(20,ws.max_row),values_only=True),start=1):
            strings=[]
            for ci,v in enumerate(row,start=1):
                if isinstance(v,str) and v.strip():
                    strings.append({"column_index":ci,"value":v.strip()})
            if strings:
                string_rows.append({"row_index":ri,"string_cells":strings})
        sheets.append({
            "title":ws.title,
            "max_row":ws.max_row,
            "max_column":ws.max_column,
            "first_20_rows_string_cells_only":string_rows
        })
    payload={
        "schema_version":1,
        "study_id":"batter-leptonycteris-workbook-schema-audit-v1",
        "numeric_cells_reported":False,
        "altitude_values_read_or_reported":False,
        "sheets":sheets
    }
    OUTJ.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    lines=[
        "# Leptonycteris workbook schema audit v1","",
        "**Only string-valued cells from the first 20 rows are reported. Numeric cell values, including altitude, are never emitted.**",""
    ]
    for s in sheets:
        lines += [f"## {s['title']}","",f"- dimensions: {s['max_row']} rows x {s['max_column']} columns",""]
        for rr in s["first_20_rows_string_cells_only"]:
            cells=" | ".join(f"C{x['column_index']}: {x['value']}" for x in rr["string_cells"])
            lines.append(f"- row {rr['row_index']}: {cells}")
        lines.append("")
    OUT.write_text("\n".join(lines))
    print(json.dumps(payload,sort_keys=True))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
